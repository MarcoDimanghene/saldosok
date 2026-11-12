from pydantic import BaseModel
from typing import Optional, List


# =====================================================================
# BORRADOR DE FACTURA EXTRAÍDA (OCR / PDF)
# =====================================================================
# Es lo que devuelve POST /invoices/extract: la factura leída del archivo
# con todos los campos pre-llenados, listos para que el usuario confirme,
# edite o cancele. Nada de esto se guarda en la DB.
class InvoiceDraft(BaseModel):
    tipo: str = "indeterminado"          # "venta" | "compra" | "indeterminado"
    issuer_id: Optional[int] = None      # id de la empresa del tenant emisora de la venta
    issuer_name: Optional[str] = None
    issuer_cuit: Optional[str] = None
    receiver_id: Optional[int] = None    # cliente en venta / empresa destinataria en compra
    receiver_name: Optional[str] = None
    receiver_cuit: Optional[str] = None
    letter: Optional[str] = None         # 'A', 'B', 'C'
    point_of_sale: Optional[int] = None
    invoice_number: Optional[int] = None
    cae: Optional[str] = None
    issue_date: Optional[str] = None     # "AAAA-MM-DD"
    total_amount: Optional[float] = None
    tipo_comprobante: Optional[str] = "factura"
    moneda: Optional[str] = "ARS"
    missing_fields: List[str] = []       # qué no se pudo leer del archivo
