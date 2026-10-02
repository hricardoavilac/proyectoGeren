"""Instala el módulo CRM en la instancia de Odoo."""
from odoo_api import call

ids = call("ir.module.module", "search", domain=[["name", "=", "crm"]])
print("antes:", call("ir.module.module", "read", ids=ids, fields=["state"]))
call("ir.module.module", "button_immediate_install", ids=ids)
print("después:", call("ir.module.module", "read", ids=ids, fields=["state"]))
