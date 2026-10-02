"""Renombra el almacén, aplica el inventario inicial y crea las reglas de reordenamiento.

Las reglas usan la ruta "Comprar" y disparo automático: cuando el pronóstico de un
producto cae bajo el mínimo, Odoo genera una solicitud de cotización al proveedor
preferido (el de menor secuencia en la pestaña Compra del producto).
"""
from datos_ventas import REGLAS, plan_ventas, stock_inicial
from odoo_api import call

WH = call("stock.warehouse", "search", domain=[], limit=1)[0]
call("stock.warehouse", "write", ids=[WH], vals={"name": "UrbanJungle – Bodega Zona 15"})
almacen = call("stock.warehouse", "read", ids=[WH], fields=["lot_stock_id"])[0]
STOCK = almacen["lot_stock_id"][0]
COMPRAR = call("stock.route", "search", domain=[["name", "in", ["Buy", "Comprar"]]], limit=1)[0]

variantes = {p["default_code"]: p["id"] for p in call("product.product", "search_read",
             domain=[["default_code", "in", list(REGLAS)]], fields=["default_code"])}

# Inventario inicial (ajuste de inventario), solo si el producto aún no tiene existencias
stock, _ = stock_inicial(plan_ventas())
quants = []
for ref, qty in stock.items():
    existentes = call("stock.quant", "search_read", fields=["quantity"], domain=[
        ["product_id", "=", variantes[ref]], ["location_id", "=", STOCK]])
    if sum(q["quantity"] for q in existentes):
        continue
    quants += call("stock.quant", "create", vals_list=[{
        "product_id": variantes[ref], "location_id": STOCK, "inventory_quantity": qty}])
if quants:
    call("stock.quant", "action_apply_inventory", ids=quants)
print(f"Inventario inicial aplicado a {len(quants)} productos")

# Reglas de reordenamiento mín/máx
for ref, (minimo, maximo) in REGLAS.items():
    vals = {"product_id": variantes[ref], "warehouse_id": WH, "location_id": STOCK,
            "product_min_qty": minimo, "product_max_qty": maximo, "trigger": "auto", "route_id": COMPRAR}
    existe = call("stock.warehouse.orderpoint", "search", domain=[
        ["product_id", "=", variantes[ref]], ["location_id", "=", STOCK]])
    if existe:
        call("stock.warehouse.orderpoint", "write", ids=existe, vals=vals)
    else:
        call("stock.warehouse.orderpoint", "create", vals_list=[vals])
    print(f"Regla {ref}: mín {minimo} / máx {maximo}")
