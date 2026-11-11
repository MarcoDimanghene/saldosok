# Importamos las funciones del CRUD de empresas

from .companies import (
    get_company_by_tax_id,
    create_company,
    get_companies,
    get_company_by_name,
    update_company,
    delete_company
)

# --- USERS ---
from .users import (
    get_user_by_email_and_tenant,
    get_user_by_username,
    create_user,
    get_users,
    count_users,
    get_user,
    update_user,
    delete_user
)

# --- TENANTS ---
from .tenants import (
    get_tenant_by_cuit,
    get_tenant,
    get_tenants,
    create_tenant,
    create_tenant_with_admin,
    MAX_USERS_PER_TENANT,
    update_tenant,
    delete_tenant
)

# --- ACTUALIZADO CON TUS TABLAS REALES ---
from .invoices import (
    get_sales_invoice_by_cae,
    get_sales_invoice,
    get_listsales_invoices,
    create_sales_invoice,
    update_sales_invoice,
    get_purchase_by_cae,
    get_purchase_invoice,
    get_listpurchase_invoice,
    create_purchase_invoice,
    update_purchase_invoice
)

# --- COBROS Y PAGOS ---
from .payments import (
    create_collection,
    get_collections_by_invoice_id,
    update_collection,
    delete_collection,
    create_payment,
    get_payments_by_invoice_id,
    update_payment,
    delete_payment
)

# --- DASHBOARD ---
from .dashboard import get_dashboard_summary
