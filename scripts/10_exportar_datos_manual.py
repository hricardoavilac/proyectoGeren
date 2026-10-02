"""Extrae de Odoo los datos reales que documenta el Manual Técnico (tablas y línea base de KPIs)."""
import json
import os
from collections import Counter, defaultdict
from datetime import datetime

from datos_contactos import nit
from datos_contactos import PROVEEDORES
from odoo_api import URL, call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(ROOT, "manual", "datos_manual.json")

version = call("ir.module.module", "search_read", domain=[["name", "=", "base"]], fields=["latest_version"])
empresa = call("res.company", "read", ids=[1], fields=["name", "street", "city", "currency_id"])[0]

# Productos con existencias y reglas de reordenamiento
reglas = {r["product_id"][0]: r for r in call("stock.warehouse.orderpoint", "search_read", domain=[], fields=[
    "product_id", "product_min_qty", "product_max_qty", "qty_on_hand", "qty_forecast", "route_id", "trigger"])}
productos = []
for p in call("product.product", "search_read", domain=[["default_code", "like", "UJ-P"]], order="default_code",
              fields=["default_code", "name", "categ_id", "list_price", "standard_price", "barcode", "qty_available", "seller_ids"]):
    r = reglas.get(p["id"], {})
    productos.append({"ref": p["default_code"], "nombre": p["name"], "categoria": p["categ_id"][1].split(" / ")[-1],
                      "precio": p["list_price"], "costo": p["standard_price"], "barcode": p["barcode"],
                      "existencia": p["qty_available"], "pronostico": r.get("qty_forecast"),
                      "minimo": r.get("product_min_qty"), "maximo": r.get("product_max_qty")})

# Proveedores y sus productos
infos = call("product.supplierinfo", "search_read", domain=[], fields=["partner_id", "product_tmpl_id", "price", "delay"])
por_prov = defaultdict(list)
for s in infos:
    por_prov[s["partner_id"][0]].append(s["product_tmpl_id"][1].split("] ", 1)[-1])
proveedores = []
for v in PROVEEDORES:
    pid = call("res.partner", "search_read", domain=[["vat", "=", nit(v[1])]], fields=["name", "vat", "city", "phone"])[0]
    proveedores.append({"nombre": pid["name"], "nit": pid["vat"], "ciudad": pid["city"], "telefono": pid["phone"],
                        "rubro": v[6], "productos": por_prov[pid["id"]]})

# Clientes
clientes = []
for c in call("res.partner", "search_read", domain=[["category_id.name", "=", "Cliente"]], order="name",
              fields=["name", "vat", "phone", "street", "city", "x_empleador", "category_id"]):
    tags = [t["name"] for t in call("res.partner.category", "read", ids=c["category_id"], fields=["name"]) if t["name"] != "Cliente"]
    clientes.append({"nombre": c["name"], "nit": c["vat"], "telefono": c["phone"],
                     "direccion": f"{c['street']}, {c['city']}", "empleador": c["x_empleador"], "etiqueta": ", ".join(tags)})

# Ventas, entregas y KPIs
ventas = call("sale.order", "search_read", domain=[["state", "=", "sale"]], order="date_order",
              fields=["name", "partner_id", "date_order", "amount_total", "picking_ids"])
entregas = {p["id"]: p for p in call("stock.picking", "search_read", domain=[["picking_type_code", "=", "outgoing"]],
                                     fields=["state", "date_done"])}
compras_cliente = Counter(v["partner_id"][0] for v in ventas)
lineas = call("sale.order.line", "search_read", domain=[["order_id.state", "=", "sale"]],
              fields=["product_id", "product_uom_qty", "price_total"])
top = Counter()
for l in lineas:
    top[l["product_id"][1].split("] ", 1)[-1]] += l["product_uom_qty"]

completas = a_tiempo = 0
for v in ventas:
    estados = [entregas[p] for p in v["picking_ids"] if p in entregas]
    if estados and all(e["state"] == "done" for e in estados):
        completas += 1
        horas = max((datetime.fromisoformat(e["date_done"]) - datetime.fromisoformat(v["date_order"])).total_seconds() / 3600
                    for e in estados)
        a_tiempo += horas <= 48

oportunidades = call("crm.lead", "search_read", domain=[["type", "=", "opportunity"]],
                     fields=["name", "partner_id", "stage_id", "expected_revenue", "user_id"])
etapas = call("crm.stage", "search_read", domain=[], fields=["name", "sequence", "is_won"], order="sequence")
por_etapa = Counter(o["stage_id"][1] for o in oportunidades)
ganadas = sum(por_etapa[e["name"]] for e in etapas if e["is_won"])

compras = []
for po in call("purchase.order", "search_read", domain=[], order="name",
               fields=["name", "partner_id", "state", "origin", "amount_total", "order_line", "date_order"]):
    lin = call("purchase.order.line", "read", ids=po["order_line"], fields=["product_id", "product_qty"])
    compras.append({"nombre": po["name"], "proveedor": po["partner_id"][1], "estado": po["state"], "origen": po["origin"],
                    "total": po["amount_total"],
                    "lineas": [f"{l['product_id'][1].split('] ', 1)[-1]} × {l['product_qty']:g}" for l in lin]})

total = sum(v["amount_total"] for v in ventas)
datos = {
    "url": URL, "version": version[0]["latest_version"] if version else "", "empresa": empresa["name"],
    "productos": productos, "proveedores": proveedores, "clientes": clientes, "compras": compras,
    "ventas": {"cantidad": len(ventas), "total": total, "clientes": len(compras_cliente),
               "desde": ventas[0]["date_order"][:10], "hasta": ventas[-1]["date_order"][:10],
               "lineas": len(lineas), "top": top.most_common(5)},
    "pipeline": [{"etapa": e["name"], "cantidad": por_etapa[e["name"]], "ganado": e["is_won"]} for e in etapas],
    "plantillas": [t["name"] for t in call("mail.template", "search_read", domain=[["name", "like", "UrbanJungle –"]], fields=["name"])],
    "kpi": {
        "ticket_promedio": total / len(ventas),
        "conversion": ganadas / len(oportunidades),
        "suscriptores": sum(1 for c in clientes if "Suscriptor" in c["etiqueta"]),
        "recompra": sum(1 for n in compras_cliente.values() if n >= 2) / len(compras_cliente),
        "nivel_servicio": completas / len(ventas),
        "entregas_a_tiempo": a_tiempo / max(completas, 1),
        "productos_bajo_minimo": sum(1 for p in productos if p["minimo"] and p["existencia"] < p["minimo"]),
    },
}
os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
json.dump(datos, open(SALIDA, "w"), ensure_ascii=False, indent=1)
print(json.dumps(datos["kpi"], indent=1), "\nventas:", datos["ventas"]["cantidad"], "compras:", len(compras))
