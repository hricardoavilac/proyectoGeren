"""Configura la tienda en línea: nombre y logo del sitio, categorías públicas, publicación de los 30
productos con descripción, cinta de productos nuevos, accesorios sugeridos y métodos de pago."""
import base64
import os

from datos_fase3 import DESCRIPCIONES, PRODUCTOS_FASE3
from odoo_api import call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
b64 = lambda rel: base64.b64encode(open(os.path.join(ROOT, rel), "rb").read()).decode()

sitio = call("website", "search", domain=[], limit=1)[0]
call("website", "write", ids=[sitio], vals={
    "name": "UrbanJungle", "logo": b64("assets/logo_urbanjungle.png"),
    "auth_signup_uninvited": "b2c", "account_on_checkout": "optional"})

# Categorías de la tienda: mismas líneas que las categorías internas
ORDEN = ["Plantas de Interior", "Suculentas y Cactus", "Macetas y Colgantes", "Sustratos y Fertilizantes",
         "Herramientas y Accesorios", "Kits y Regalos", "Suscripciones"]
IMAGEN_CAT = {"Plantas de Interior": "P01", "Suculentas y Cactus": "P09", "Macetas y Colgantes": "P12",
              "Sustratos y Fertilizantes": "P14", "Herramientas y Accesorios": "P17", "Kits y Regalos": "P26",
              "Suscripciones": "P20"}
publicas = {}
for seq, nombre in enumerate(ORDEN, start=1):
    vals = {"name": nombre, "sequence": seq, "image_1920": b64(f"assets/productos/{IMAGEN_CAT[nombre]}.jpg")}
    ids = call("product.public.category", "search", domain=[["name", "=", nombre]])
    if ids:
        call("product.public.category", "write", ids=ids, vals=vals)
    else:
        ids = call("product.public.category", "create", vals_list=[vals])
    publicas[nombre] = ids[0]

descripcion = dict(DESCRIPCIONES)
descripcion.update({p[0]: p[8] for p in PRODUCTOS_FASE3})
nuevo = call("product.ribbon", "search", domain=[["name", "=", "¡Nuevo!"]])
productos = {p["default_code"]: p for p in call("product.template", "search_read",
             domain=[["default_code", "like", "UJ-P"]], fields=["default_code", "categ_id"])}
ACCESORIOS = ["UJ-P12", "UJ-P14", "UJ-P15"]  # maceta, sustrato y fertilizante para la venta cruzada
for orden, (ref, p) in enumerate(sorted(productos.items()), start=1):
    cat = p["categ_id"][1].split(" / ")[-1]
    vals = {"is_published": True, "public_categ_ids": [[6, 0, [publicas[cat]]]], "website_sequence": orden * 10,
            "description_ecommerce": f"<p>{descripcion[ref]}</p>",
            "website_ribbon_id": nuevo[0] if nuevo and int(ref[-2:]) > 20 else False}
    if cat in ("Plantas de Interior", "Suculentas y Cactus"):
        vals["accessory_product_ids"] = [[6, 0, call("product.product", "search", domain=[["default_code", "in", ACCESORIOS]])]]
    call("product.template", "write", ids=[p["id"]], vals=vals)
print("Publicados:", call("product.template", "search_count", domain=[["is_published", "=", True], ["default_code", "like", "UJ-P"]]))

# Métodos de pago sin pasarela externa (el negocio cobra por transferencia o al entregar)
MENSAJE = {
    "wire_transfer": "<p>Transfiere el total a la cuenta monetaria de UrbanJungle en Banco Industrial y envía el comprobante a ventas@urbanjungle.gt indicando el número de pedido. El pedido se despacha al confirmar el pago.</p>",
    "cash_on_delivery": "<p>Pagas en efectivo o con tarjeta al recibir tu pedido. Disponible en el área metropolitana de Guatemala.</p>",
}
for modo, msg in MENSAJE.items():
    ids = call("payment.provider", "search", domain=[["custom_mode", "=", modo]])
    call("payment.provider", "write", ids=ids, vals={"is_live": True, "is_published": True, "pending_msg": msg})
print(call("payment.provider", "search_read", domain=[["is_published", "=", True]], fields=["name", "is_live"]))
