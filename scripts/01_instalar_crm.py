"""Instala las apps que usa el proyecto: CRM, Inventario y Compras.

Odoo agrega solo los módulos puente (sale_stock, purchase_stock, sale_crm).
"""
from odoo_api import call

MODULOS = ["crm", "stock", "purchase"]

ids = call("ir.module.module", "search", domain=[["name", "in", MODULOS], ["state", "!=", "installed"]])
if ids:
    call("ir.module.module", "button_immediate_install", ids=ids)
for m in call("ir.module.module", "search_read", fields=["name", "state"], domain=[
        ["name", "in", MODULOS + ["sale_stock", "purchase_stock", "sale_crm", "stock_sms"]]]):
    print(m["name"], m["state"])
