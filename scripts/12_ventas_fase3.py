"""Ventas de la Fase 3: 60 pedidos confirmados (julio, agosto y octubre de 2026) más 4 cotizaciones web.

Con las 50 ventas de septiembre (Fase 2) el histórico llega a 110 ventas. Los pedidos de octubre
se registran en el sitio web. Cuando el stock no alcanza para una entrega, se confirman y reciben
las solicitudes de cotización que generaron las reglas de reordenamiento. Es idempotente
(referencia de cliente F3-NNN).
"""
import random
from datetime import datetime, timedelta

from datos_contactos import CLIENTES
from datos_fase3 import CLIENTES_WEB
from odoo_api import call

CTX = {"lang": "es_419", "tz": "America/Guatemala", "skip_sms": True}
call("res.company", "write", ids=[1], vals={"has_received_warning_stock_sms": True})

rnd = random.Random(3030)
clase = {c[0]: c[7] for c in CLIENTES}
suscriptores = [n for n, k in clase.items() if k == "Suscriptor Care Box"]
recurrentes = [n for n, k in clase.items() if k in ("Cliente Frecuente", "Cliente VIP")]
web = [c[0] for c in CLIENTES_WEB]
PLANTAS = [f"UJ-P{i:02d}" for i in list(range(1, 11)) + [21, 22, 23, 24, 25]]
COMPLEMENTOS = [f"UJ-P{i:02d}" for i in list(range(11, 20)) + [26, 27, 28, 29, 30]]
NUEVOS = {f"UJ-P{i:02d}" for i in range(21, 31)}


def pedido(cliente, mes, dia, en_web):
    nuevos_ok = mes >= 8  # los productos nuevos entran al catálogo en agosto
    plantas = [p for p in PLANTAS if nuevos_ok or p not in NUEVOS]
    compl = [p for p in COMPLEMENTOS if nuevos_ok or p not in NUEVOS]
    lineas = {rnd.choice(plantas): rnd.choice([1, 1, 1, 2])}
    for ref in rnd.sample(compl, rnd.choice([0, 1, 1, 2])):
        lineas[ref] = 1
    if cliente in suscriptores:
        lineas["UJ-P20"] = 1
    hora = f"{rnd.randint(9, 19):02d}:{rnd.choice([0, 10, 25, 40, 55]):02d}:00"
    return {"cliente": cliente, "fecha": f"2026-{mes:02d}-{dia:02d} {hora}", "lineas": lineas, "web": en_web}


def plan():
    ventas = []
    for mes, total, dias in ((7, 15, 31), (8, 20, 31), (10, 25, 13)):
        compradores = list(suscriptores)  # la Care Box es mensual
        if mes == 10:
            compradores += web
        while len(compradores) < total:
            compradores.append(rnd.choice(recurrentes + recurrentes + list(clase)))
        rnd.shuffle(compradores)
        for i, c in enumerate(compradores):
            ventas.append(pedido(c, mes, 1 + i * dias // total, mes == 10))
    cotizaciones = [pedido(c, 10, 14, True) for c in rnd.sample(web + recurrentes, 4)]
    return ventas, cotizaciones


def reabastecer():
    """Confirma las solicitudes de cotización en borrador y recibe la mercadería."""
    borradores = call("purchase.order", "search", domain=[["state", "in", ["draft", "sent"]]])
    if borradores:
        call("purchase.order", "button_confirm", ids=borradores)
    recepciones = call("stock.picking", "search", domain=[["picking_type_code", "=", "incoming"],
                                                          ["state", "not in", ["done", "cancel"]]])
    for r in recepciones:
        for m in call("stock.move", "search_read", domain=[["picking_id", "=", r]], fields=["product_uom_qty"]):
            call("stock.move", "write", ids=[m["id"]], vals={"quantity": m["product_uom_qty"], "picked": True})
        call("stock.picking", "button_validate", ids=[r], context=CTX)
    return len(borradores)


def entregar(so, fecha):
    for picking in call("sale.order", "read", ids=[so], fields=["picking_ids"])[0]["picking_ids"]:
        call("stock.picking", "action_assign", ids=[picking])
        movs = call("stock.move", "search_read", domain=[["picking_id", "=", picking]], fields=["product_uom_qty", "state"])
        if any(m["state"] != "assigned" for m in movs):
            print("  sin stock suficiente: se reciben", reabastecer(), "compras")
            call("stock.picking", "action_assign", ids=[picking])
        for m in movs:
            call("stock.move", "write", ids=[m["id"]], vals={"quantity": m["product_uom_qty"], "picked": True})
        call("stock.picking", "button_validate", ids=[picking], context=CTX)
        entrega = (fecha + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        call("stock.picking", "write", ids=[picking], vals={"date_done": entrega, "scheduled_date": entrega})


socios = {p["name"]: p["id"] for p in call("res.partner", "search_read", fields=["name"],
          domain=[["name", "in", list(clase) + web]])}
variantes = {p["default_code"]: p["id"] for p in call("product.product", "search_read",
             domain=[["default_code", "like", "UJ-P"]], fields=["default_code"])}
vendedores = call("res.users", "search", domain=[["share", "=", False]], order="id")
sitio = call("website", "search", domain=[], limit=1)[0]

ventas, cotizaciones = plan()
print("Compras recibidas antes de empezar:", reabastecer())
for n, v in enumerate(ventas + cotizaciones, start=1):
    ref = f"F3-{n:03d}"
    if call("sale.order", "search", domain=[["client_order_ref", "=", ref]]):
        continue
    vals = {"partner_id": socios[v["cliente"]], "client_order_ref": ref, "user_id": vendedores[n % len(vendedores)],
            "order_line": [[0, 0, {"product_id": variantes[r], "product_uom_qty": q}] for r, q in v["lineas"].items()]}
    if v["web"]:
        vals["website_id"] = sitio
    so = call("sale.order", "create", vals_list=[vals])[0]
    fecha = datetime.strptime(v["fecha"], "%Y-%m-%d %H:%M:%S") + timedelta(hours=6)  # Guatemala -> UTC
    if n <= len(ventas):
        call("sale.order", "action_confirm", ids=[so])
        call("sale.order", "write", ids=[so], vals={"date_order": fecha.strftime("%Y-%m-%d %H:%M:%S")})
        entregar(so, fecha)
        estado = "venta"
    else:
        call("sale.order", "write", ids=[so], vals={"date_order": fecha.strftime("%Y-%m-%d %H:%M:%S")})
        estado = "cotización"
    total = call("sale.order", "read", ids=[so], fields=["name", "amount_total"])[0]
    print(f"{ref} {total['name']} {v['fecha'][:10]} {'web ' if v['web'] else ''}{estado} {v['cliente']}: Q{total['amount_total']:.2f}")
