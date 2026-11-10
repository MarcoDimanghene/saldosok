import os
import tempfile

import fitz
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from back import models
from back.crud import companies
from database.database import get_db
from database.security import get_current_user
from engine.extract import (
    DocumentLimitError,
    MAX_PDF_PAGES,
    get_text,
    parse_invoice_data,
)
import back.schemas as schemas

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
)

# Formatos aceptados: PDFs y los formatos de imagen más comunes
EXTENSIONES_VALIDAS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000
UPLOAD_CHUNK_SIZE = 1024 * 1024


def _normalizar_cuit(cuit: str) -> str:
    """Quita guiones: '20-12345678-9' -> '20123456789'."""
    return cuit.replace("-", "").replace(" ", "")


def _buscar_por_cuit(db, tenant_id, cuit):
    """Busca una empresa del tenant por CUIT normalizado."""
    if not cuit:
        return None
    return companies.get_company_by_tax_id(db, tenant_id, _normalizar_cuit(cuit))


def _store_upload(file: UploadFile, extension: str) -> str:
    tmp_path = None
    total_size = 0
    success = False

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp:
            tmp_path = tmp.name
            while chunk := file.file.read(UPLOAD_CHUNK_SIZE):
                total_size += len(chunk)
                if total_size > MAX_UPLOAD_SIZE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail="El archivo supera el límite de 10 MB.",
                    )
                tmp.write(chunk)

        if total_size == 0:
            raise HTTPException(status_code=400, detail="El archivo está vacío.")
        success = True
        return tmp_path
    finally:
        if not success and tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _validate_image(path: str) -> None:
    with Image.open(path) as image:
        if image.width * image.height > MAX_IMAGE_PIXELS:
            raise HTTPException(
                status_code=413,
                detail="La imagen supera el límite de 40 megapíxeles.",
            )
        image.verify()


# ============================================================
# POST /invoices/extract
# Sube una factura (PDF o imagen) y devuelve el borrador con
# los campos ya extraídos (OCR). NO guarda nada: el usuario
# decide si confirma, edita o cancela.
# ============================================================
@router.post("/extract", response_model=schemas.InvoiceDraft)
def extract_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # ---------- 1. Validar extensión ----------
    extension = os.path.splitext(file.filename or "")[1].lower()
    if extension not in EXTENSIONES_VALIDAS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado '{extension}'. Usá PDF o imagen (png, jpg, webp, bmp, tiff).",
        )

    # ---------- 2. Guardar temporal y extraer texto ----------
    tmp_path = None
    try:
        tmp_path = _store_upload(file, extension)
        if extension != ".pdf":
            _validate_image(tmp_path)

        texto = get_text(tmp_path, pdf=(extension == ".pdf"))
        if not texto or len(texto.strip()) < 10:
            raise HTTPException(
                status_code=422,
                detail="No se pudo leer el archivo: está en blanco o el formato no es reconocible.",
            )
    except DocumentLimitError as error:
        raise HTTPException(
            status_code=413,
            detail=(
                f"{error} Límite: {MAX_PDF_PAGES} páginas y 40 megapíxeles "
                "por página procesada."
            ),
        ) from error
    except Image.DecompressionBombError as error:
        raise HTTPException(
            status_code=413,
            detail="La imagen supera el límite de procesamiento.",
        ) from error
    except (fitz.FileDataError, UnidentifiedImageError, OSError) as error:
        raise HTTPException(
            status_code=422,
            detail="No se pudo leer el archivo: el contenido no es válido para su formato.",
        ) from error
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    # ---------- 3. Parsear campos ----------
    datos = parse_invoice_data(texto)

    # ---------- 4. Resolver empresas (solo dentro del tenant) ----------
    tenant = db.query(models.Tenant).filter(models.Tenant.id == current_user.tenant_id).first()
    tenant_cuit = _normalizar_cuit(tenant.cuit) if tenant else None

    emisor_cuit_norm = _normalizar_cuit(datos["emisor_cuit"]) if datos["emisor_cuit"] else None
    receptor_cuit_norm = _normalizar_cuit(datos["receptor_cuit"]) if datos["receptor_cuit"] else None

    emisor_db = _buscar_por_cuit(db, current_user.tenant_id, datos["emisor_cuit"])
    receptor_db = _buscar_por_cuit(db, current_user.tenant_id, datos["receptor_cuit"])

    # ---------- 5. Detectar el tipo (venta / compra) ----------
    # - El emisor es una empresa emisora del tenant -> venta
    # - El receptor es el propio tenant          -> compra (nos vendió un proveedor)
    # - El emisor es un proveedor registrado     -> compra
    # - El receptor es un cliente registrado     -> venta
    draft = schemas.InvoiceDraft(
        issuer_cuit=datos["emisor_cuit"],
        receiver_cuit=datos["receptor_cuit"],
        letter=datos["letra"],
        point_of_sale=datos["punto_venta"],
        invoice_number=datos["nro_factura"],
        cae=datos["cae"],
        issue_date=datos["fecha_emision"],
        total_amount=datos["total"],
        tipo_comprobante=datos["tipo_comprobante"],
        moneda=datos["moneda"],
        missing_fields=datos["campos_faltantes"],
    )

    if receptor_cuit_norm and receptor_cuit_norm == tenant_cuit:
        draft.tipo = "compra"
        draft.receiver_id = tenant.id if tenant else None
        draft.receiver_name = tenant.razon_social if tenant else None
        if emisor_db:
            draft.issuer_id = emisor_db.id
            draft.issuer_name = emisor_db.razon_social
    elif emisor_db and emisor_db.es_emisor:
        draft.tipo = "venta"
        draft.issuer_id = emisor_db.id
        draft.issuer_name = emisor_db.razon_social
        if receptor_db:
            draft.receiver_id = receptor_db.id
            draft.receiver_name = receptor_db.razon_social
    elif emisor_cuit_norm and emisor_cuit_norm == tenant_cuit:
        draft.tipo = "venta"
        draft.issuer_id = emisor_db.id if emisor_db and emisor_db.es_emisor else None
        draft.issuer_name = emisor_db.razon_social if emisor_db else None
        if receptor_db:
            draft.receiver_id = receptor_db.id
            draft.receiver_name = receptor_db.razon_social
    elif emisor_db and emisor_db.es_proveedor:
        draft.tipo = "compra"
        draft.issuer_id = emisor_db.id
        draft.issuer_name = emisor_db.razon_social
    elif receptor_db and receptor_db.es_cliente:
        draft.tipo = "venta"
        draft.receiver_id = receptor_db.id
        draft.receiver_name = receptor_db.razon_social
        if emisor_db and emisor_db.es_emisor:
            draft.issuer_id = emisor_db.id
            draft.issuer_name = emisor_db.razon_social
    else:
        draft.tipo = "indeterminado"
        if emisor_db:
            draft.issuer_id = emisor_db.id
            draft.issuer_name = emisor_db.razon_social
        if receptor_db:
            draft.receiver_id = receptor_db.id
            draft.receiver_name = receptor_db.razon_social

    return draft
