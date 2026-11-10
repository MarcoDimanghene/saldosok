import re
import os
import shutil
import io

import fitz  # PyMuPDF
from PIL import Image
import numpy as np

# ==================================================
# MOTOR DE EXTRACCIÓN DE FACTURAS
# ==================================================
# - PDFs con texto: PyMuPDF (fitz) extrae el texto directo.
# - PDFs escaneados / imágenes: RapidOCR (OCR onnxruntime, sin binarios externos).
#
# Se importa desde el backend (back/routes/extract.py) o se usa como script
# (python engine/extract.py) para procesar una carpeta de PDFs.

# ------------------------------------------------------------------
# 1. OCR (RapidOCR, carga perezosa: los modelos se descargan en el 1er uso)
# ------------------------------------------------------------------
_ocr_engine = None
MAX_PDF_PAGES = 20
MAX_PDF_PAGE_PIXELS = 40_000_000


class DocumentLimitError(ValueError):
    pass


class DocumentPageLimitError(DocumentLimitError):
    pass


class DocumentPixelLimitError(DocumentLimitError):
    pass


def _get_ocr():
    """Instancia única de RapidOCR (carga modelos solo la primera vez)."""
    global _ocr_engine
    if _ocr_engine is None:
        from rapidocr_onnxruntime import RapidOCR
        _ocr_engine = RapidOCR()
    return _ocr_engine


def ocr_image(image_bytes: bytes):
    """OCR de una imagen (bytes) -> texto plano."""
    img = Image.open(io.BytesIO(image_bytes))
    result, _ = _get_ocr()(np.array(img.convert("RGB")))
    if not result:
        return ""
    return "\n".join(line[1] for line in result)


def extract_text_pdf(file: str):
    """Extrae el texto de un PDF (capa de texto, sin OCR)."""
    with fitz.open(file) as doc:
        return "".join(page.get_text() for page in doc)


def ocr_pdf(file: str):
    """OCR de un PDF escaneado: renderiza cada página y la lee con RapidOCR."""
    with fitz.open(file) as doc:
        if len(doc) > MAX_PDF_PAGES:
            raise DocumentPageLimitError(
                f"El PDF supera el máximo de {MAX_PDF_PAGES} páginas."
            )
        texto = ""
        for page in doc:
            rendered_pixels = (
                page.rect.width
                * page.rect.height
                * (200 / 72) ** 2
            )
            if rendered_pixels > MAX_PDF_PAGE_PIXELS:
                raise DocumentPixelLimitError(
                    "Una página del PDF supera el límite de resolución para OCR."
                )
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            result, _ = _get_ocr()(np.array(img))
            if result:
                texto += "\n".join(line[1] for line in result) + "\n"
        return texto


def get_text(file: str, pdf: bool = True):
    """
    Punto de entrada: texto de un archivo PDF (o imagen).
    - PDF: intenta texto; si es escaneado (casi sin texto), pasa a OCR.
    - Imagen: OCR directo.
    """
    if pdf:
        with fitz.open(file) as doc:
            if len(doc) > MAX_PDF_PAGES:
                raise DocumentPageLimitError(
                    f"El PDF supera el máximo de {MAX_PDF_PAGES} páginas."
                )
        texto = extract_text_pdf(file)
        if len(texto.strip()) < 50:
            return ocr_pdf(file)
        return texto
    with open(file, "rb") as f:
        return ocr_image(f.read())


# ------------------------------------------------------------------
# 2. PARSING de los campos de la factura
# ------------------------------------------------------------------
def _limpiar_total(raw: str) -> float:
    """Convierte '922.583,76' o '922,583.76' o '1500,50' a 922583.76 / 1500.50."""
    if "," in raw and "." in raw:
        if raw.find(",") < raw.find("."):
            return float(raw.replace(",", ""))  # formato inglés: 922,583.76
        return float(raw.replace(".", "").replace(",", "."))  # hispano: 922.583,76
    return float(raw.replace(",", "."))


def _fecha_a_db(fecha_raw: str) -> str:
    """Convierte DD/MM/AAAA a AAAA-MM-DD."""
    partes = fecha_raw.split("/")
    return f"{partes[2]}-{partes[1]}-{partes[0]}"


def parse_invoice_data(texto_bruto: str):
    """
    Extrae los campos de una factura argentina a partir del texto (PDF u OCR).
    Devuelve un dict con todo lo reconocido (y None donde no se encontró).
    """
    data = {
        "emisor_cuit": None,
        "receptor_cuit": None,
        "cae": None,
        "fecha_emision": None,
        "total": None,
        "letra": None,
        "punto_venta": None,
        "nro_factura": None,
        "tipo_comprobante": "factura",
        "moneda": "ARS",
    }

    # ---- CUITs: el 1ro es el emisor, el 2do el receptor ----
    # Acepta las agrupaciones habituales: 20-12345678-9 (8 dígitos), 30-111111111-1 (9), etc.
    cuits = list(dict.fromkeys(re.findall(r"\d{2}-\d{7,9}-\d", texto_bruto)))
    if cuits:
        data["emisor_cuit"] = cuits[0]
        data["receptor_cuit"] = cuits[1] if len(cuits) > 1 else None

    # ---- CAE (14 dígitos) ----
    cae = re.search(r"CAE:\s*(\d{14})", texto_bruto)
    data["cae"] = cae.group(1) if cae else None

    # ---- Fecha ----
    fecha = re.search(r"(\d{2}/\d{2}/\d{4})", texto_bruto)
    data["fecha_emision"] = _fecha_a_db(fecha.group(1)) if fecha else None

    # ---- Total ----
    total = re.search(r"Total:\s*\$?\s*([\d.,]+)", texto_bruto)
    if total:
        try:
            data["total"] = _limpiar_total(total.group(1))
        except ValueError:
            data["total"] = None

    # ---- Tipo de comprobante (Factura / Nota de Crédito / Nota de Débito) ----
    texto_up = texto_bruto.upper()
    if "NOTA DE CRÉDITO" in texto_up or "NOTA DE CREDITO" in texto_up:
        data["tipo_comprobante"] = "nota_credito"
    elif "NOTA DE DÉBITO" in texto_up or "NOTA DE DEBITO" in texto_up:
        data["tipo_comprobante"] = "nota_debito"

    # ---- Letra + Punto de Venta + Número ----
    # Formato AFIP: "A-00004-00000147" (con o sin "N°" delante)
    comprobante = re.search(r"([A-D])\s*[-–]\s*(\d{4,5})\s*[-–]\s*(\d{3,8})(?!\d)", texto_bruto)
    if not comprobante:
        comprobante = re.search(
            r"(?:Punto de Venta|PTO\.?\s*VENTA)[.:\s]*(\d{4,5})[^\d]{0,40}?Comprobante[^\d]*(\d+)",
            texto_bruto, re.IGNORECASE,
        )
    if comprobante and len(comprobante.groups()) == 3:
        data["letra"] = comprobante.group(1).upper()
        data["punto_venta"] = int(comprobante.group(2))
        data["nro_factura"] = int(comprobante.group(3))
    elif comprobante and len(comprobante.groups()) == 2:
        data["punto_venta"] = int(comprobante.group(1))
        data["nro_factura"] = int(comprobante.group(2))

    # ---- Moneda ----
    if "DÓLAR" in texto_up or r"US\$" in texto_up or "USD" in texto_up:
        data["moneda"] = "USD"

    # ---- Campos faltantes (para mostrar en el front qué revisar) ----
    data["campos_faltantes"] = [k for k, v in data.items() if v is None]

    return data


# ==================================================
# 3. SCRIPT DE BATCH (solo si se ejecuta directamente)
# ==================================================
if __name__ == "__main__":
    # Igual que el script original: lee ./test, mueve los PDFs a processed
    # y genera un reporte Excel con lo extraído.
    file_input = os.path.join(os.path.dirname(__file__), "test")
    file_processed = os.path.join(file_input, "processed")
    results_list = []

    if not os.path.exists(file_processed):
        os.makedirs(file_processed)

    print("---Iniciando Proceso---")

    archive = os.listdir(file_input)
    pdfs = False

    for file in archive:
        if file.endswith(".pdf"):
            pdfs = True
            path = os.path.join(file_input, file)

            print(f"\n📄 Procesando archivo {file}...")

            texto = get_text(path, pdf=True)
            data = parse_invoice_data(texto)

            print(f"✅ Empresa que emite (CUIT): {data['emisor_cuit']}")
            print(f"✅ Cliente/Receptor (CUIT): {data['receptor_cuit']}")
            print(f"✅ Letra-PV-Nro: {data['letra']}-{data['punto_venta']}-{data['nro_factura']}")
            print(f"✅ Número de CAE: {data['cae']}")
            print(f"✅ Total procesado para DB: {data['total']}")
            print(f"✅ Fecha de emisión (AAAA-MM-DD): {data['fecha_emision']}")

            results_list.append(data)
            shutil.move(path, os.path.join(file_processed, file))

    if not pdfs:
        print("No se encuentran archivos PDF en la carpeta de entrada.")

    if results_list:
        print("\n📊 Generando reporte Excel...")
        import pandas as pd
        df = pd.DataFrame(results_list)
        df.to_excel(os.path.join(os.path.dirname(__file__), "reporte_facturas.xlsx"), index=False)
        print("✅ Archivo 'reporte_facturas.xlsx' creado con éxito.")

    print("\n --- Finalizo el Proceso ---")
