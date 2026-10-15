"""Agrega los 10 productos de la Fase 3 (catálogo de 30) con proveedores, stock inicial y regla de reorden,
y registra los clientes que llegan por la tienda en línea. Es idempotente."""
import base64
import os

from datos_contactos import nit
from datos_fase3 import CLIENTES_WEB, PRODUCTOS_FASE3
from datos_productos import CATEGORIA_PADRE, ean13
from odoo_api import call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

padre = call("product.category", "search", domain=[["name", "=", CATEGORIA_PADRE], ["parent_id", "=", False]])[0]


def categoria(nombre):
    ids = call("product.category", "search", domain=[["name", "=", nombre], ["parent_id", "=", padre]])
    return ids[0] if ids else call("product.category", "create", vals_list=[{"name": nombre, "parent_id": padre}])[0]


WH = call("stock.warehouse", "search", domain=[], limit=1)[0]
STOCK = call("stock.warehouse", "read", ids=[WH], fields=["lot_stock_id"])[0]["lot_stock_id"][0]
COMPRAR = call("stock.route", "search", domain=[["name", "in", ["Buy", "Comprar"]]], limit=1)[0]

for ref, nombre, cat, precio, costo, proveedores, stock, (minimo, maximo), _ in PRODUCTOS_FASE3:
    n = int(ref[-2:])
    imagen = base64.b64encode(open(os.path.join(ROOT, "assets", "productos", f"P{n:02d}.jpg"), "rb").read()).decode()
    vals = {"default_code": ref, "name": nombre, "type": "consu", "is_storable": True, "categ_id": categoria(cat),
            "list_price": precio, "standard_price": costo, "barcode": ean13(n), "image_1920": imagen}
    existe = call("product.template", "search", domain=[["default_code", "=", ref]])
    if existe:
        call("product.template", "write", ids=existe, vals=vals)
        tmpl = existe[0]
    else:
        tmpl = call("product.template", "create", vals_list=[vals])[0]
    variante = call("product.product", "search", domain=[["product_tmpl_id", "=", tmpl]])[0]

    for seq, prov in enumerate(proveedores, start=1):
        pid = call("res.partner", "search", domain=[["name", "=", prov]])[0]
        if not call("product.supplierinfo", "search", domain=[["partner_id", "=", pid], ["product_tmpl_id", "=", tmpl]]):
            call("product.supplierinfo", "create", vals_list=[{
                "partner_id": pid, "product_tmpl_id": tmpl, "price": round(costo * (0.97 + seq * 0.02), 2),
                "min_qty": 1, "delay": 2 + seq, "sequence": seq}])

    hay = sum(q["quantity"] for q in call("stock.quant", "search_read", fields=["quantity"], domain=[
        ["product_id", "=", variante], ["location_id", "=", STOCK]]))
    if not hay:
        q = call("stock.quant", "create", vals_list=[{"product_id": variante, "location_id": STOCK, "inventory_quantity": stock}])
        call("stock.quant", "action_apply_inventory", ids=q)

    regla = {"product_id": variante, "warehouse_id": WH, "location_id": STOCK, "product_min_qty": minimo,
             "product_max_qty": maximo, "trigger": "auto", "route_id": COMPRAR}
    op = call("stock.warehouse.orderpoint", "search", domain=[["product_id", "=", variante], ["location_id", "=", STOCK]])
    if op:
        call("stock.warehouse.orderpoint", "write", ids=op, vals=regla)
    else:
        call("stock.warehouse.orderpoint", "create", vals_list=[regla])
    print(f"{ref} {nombre}: stock {stock}, regla {minimo}/{maximo}, {len(proveedores)} proveedores")

GT = call("res.country", "search", domain=[["code", "=", "GT"]])[0]
DEPTO = call("res.country.state", "search", domain=[["country_id", "=", GT], ["name", "=", "Guatemala"]])[0]
tags = {t["name"]: t["id"] for t in call("res.partner.category", "search_read", domain=[], fields=["name"])}
if "Registro web" not in tags:
    tags["Registro web"] = call("res.partner.category", "create", vals_list=[{"name": "Registro web", "color": 9}])[0]
web = call("website", "search", domain=[], limit=1)[0]
for nombre, base, tel, correo, calle, ciudad, empleador in CLIENTES_WEB:
    vat = nit(base)
    vals = {"name": nombre, "is_company": False, "vat": vat, "phone": tel, "email": correo, "street": calle,
            "city": ciudad, "state_id": DEPTO, "country_id": GT, "x_empleador": empleador, "customer_rank": 1,
            "website_id": web,
            "category_id": [[6, 0, [tags["Cliente"], tags["Cliente Nuevo"], tags["Registro web"]]]]}
    existe = call("res.partner", "search", domain=[["vat", "in", [vat, vat.replace("-", "")]]])
    if existe:
        call("res.partner", "write", ids=existe, vals=vals)
    else:
        call("res.partner", "create", vals_list=[vals])
    print("Cliente web:", nombre)
