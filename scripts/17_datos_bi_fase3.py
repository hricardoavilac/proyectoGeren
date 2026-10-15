"""Extrae de Odoo los datos de BI de la Fase 3 y genera los gráficos estáticos para el informe ejecutivo.

Salida: manual/datos_fase3.json y assets/bi/*.png. Los mismos indicadores están en vivo en el
tablero "UrbanJungle BI" de Odoo Tableros.
"""
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

from odoo_api import URL, call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA_JSON = os.path.join(ROOT, "manual", "datos_fase3.json")
DIR_BI = os.path.join(ROOT, "assets", "bi")
os.makedirs(DIR_BI, exist_ok=True)

# Estilo: Montserrat, tinta neutra, una sola serie por gráfico (sin leyenda), grilla tenue
for f in ("Regular", "Bold"):
    ruta = os.path.join(ROOT, "assets", "fonts", f"Montserrat-{f}.ttf")
    if os.path.exists(ruta):
        font_manager.fontManager.addfont(ruta)
plt.rcParams.update({"font.family": "Montserrat", "font.size": 10, "axes.edgecolor": "#C9CFCB",
                     "axes.labelcolor": "#44544B", "xtick.color": "#44544B", "ytick.color": "#44544B",
                     "axes.spines.top": False, "axes.spines.right": False})
VERDE, TERRACOTA, TINTA, GRILLA = "#1A8A5E", "#C97B2E", "#1E2B24", "#E6EBE8"


def corto(nombre, n=34):
    nombre = nombre.split("] ", 1)[-1]
    return nombre if len(nombre) <= n else nombre[: n - 1] + "…"


def barras(etiquetas, valores, titulo, archivo, color, fmt="{:g}", alto=None):
    fig, ax = plt.subplots(figsize=(7.2, alto or (0.42 * len(etiquetas) + 0.9)), dpi=200)
    pos = range(len(etiquetas))[::-1]
    ax.barh(list(pos), valores, color=color, height=0.62)
    ax.set_yticks(list(pos), etiquetas)
    ax.xaxis.grid(True, color=GRILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    tope = max(valores) if valores else 1
    for y, v in zip(pos, valores):
        ax.text(v + tope * 0.01, y, fmt.format(v), va="center", fontsize=9, color=TINTA)
    ax.set_xlim(0, tope * 1.15)
    ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax.set_title(titulo, loc="left", fontsize=12, fontweight="bold", color=TINTA, pad=10)
    fig.tight_layout()
    fig.savefig(os.path.join(DIR_BI, archivo))
    plt.close(fig)


# ---------- Datos ----------
ventas = call("sale.order", "search_read", domain=[["state", "=", "sale"]], order="date_order",
              fields=["name", "partner_id", "date_order", "amount_total", "website_id", "picking_ids"])
cotizaciones_web = call("sale.order", "search_count", domain=[["state", "in", ["draft", "sent"]], ["website_id", "!=", False]])
lineas = call("sale.order.line", "search_read", domain=[["order_id.state", "=", "sale"]],
              fields=["product_id", "product_uom_qty", "price_total"])
productos = call("product.product", "search_read", domain=[["default_code", "like", "UJ-P"]], order="default_code",
                 fields=["default_code", "name", "qty_available"])
clientes = call("res.partner", "search_count", domain=[["customer_rank", ">", 0]])
clientes_web = call("res.partner", "search_count", domain=[["category_id.name", "=", "Registro web"]])
proveedores = call("res.partner", "search_count", domain=[["supplier_rank", ">", 0]])
oportunidades = call("crm.lead", "search_read", domain=[["type", "=", "opportunity"]], fields=["stage_id"])
ganadas = sum(1 for o in oportunidades if o["stage_id"] and "Ganado" in o["stage_id"][1])
suscriptores = call("res.partner", "search_count", domain=[["category_id.name", "=", "Suscriptor Care Box"]])
entregas = {p["id"]: p for p in call("stock.picking", "search_read", fields=["state", "date_done"],
                                     domain=[["picking_type_code", "=", "outgoing"]])}
compras = call("purchase.order", "search_read", domain=[], fields=["name", "partner_id", "state", "amount_total"])

unidades, ingresos_prod = Counter(), Counter()
for l in lineas:
    unidades[l["product_id"][1]] += l["product_uom_qty"]
    ingresos_prod[l["product_id"][1]] += l["price_total"]
por_cliente = defaultdict(float)
pedidos_cliente = Counter()
for v in ventas:
    por_cliente[v["partner_id"][1]] += v["amount_total"]
    pedidos_cliente[v["partner_id"][1]] += 1

completas = a_tiempo = 0
for v in ventas:
    est = [entregas[p] for p in v["picking_ids"] if p in entregas]
    if est and all(e["state"] == "done" for e in est):
        completas += 1
        horas = max((datetime.fromisoformat(e["date_done"]) - datetime.fromisoformat(v["date_order"])).total_seconds() / 3600 for e in est)
        a_tiempo += horas <= 48

# Ventas por semana (lunes) y por mes
semana = defaultdict(float)
mes = defaultdict(lambda: [0, 0.0])
for v in ventas:
    d = datetime.fromisoformat(v["date_order"]) - timedelta(hours=6)  # UTC -> Guatemala
    lunes = (d - timedelta(days=d.weekday())).date()
    semana[lunes] += v["amount_total"]
    mes[d.strftime("%Y-%m")][0] += 1
    mes[d.strftime("%Y-%m")][1] += v["amount_total"]

total = sum(v["amount_total"] for v in ventas)
vendidos = [(n, u) for n, u in unidades.items()]
sin_ventas = [p["name"] for p in productos if p["name"] not in {n.split("] ", 1)[-1] for n in unidades}
              and f"[{p['default_code']}] {p['name']}" not in unidades]
top5 = sorted(vendidos, key=lambda x: -x[1])[:5]
bottom5 = sorted(vendidos, key=lambda x: x[1])[:5]
top_clientes = sorted(por_cliente.items(), key=lambda x: -x[1])[:5]

datos = {
    "url": URL,
    "kpi": {"ticket_promedio": total / len(ventas), "conversion": ganadas / len(oportunidades),
            "suscriptores": suscriptores,
            "recompra": sum(1 for n in pedidos_cliente.values() if n >= 2) / len(pedidos_cliente),
            "nivel_servicio": completas / len(ventas), "entregas_a_tiempo": a_tiempo / max(completas, 1)},
    "contexto": {"ingresos": total, "ventas": len(ventas), "clientes": clientes, "proveedores": proveedores,
                 "clientes_web": clientes_web, "ventas_web": sum(1 for v in ventas if v["website_id"]),
                 "ingresos_web": sum(v["amount_total"] for v in ventas if v["website_id"]),
                 "cotizaciones_web": cotizaciones_web, "productos": len(productos),
                 "compras": len(compras), "compras_total": sum(c["amount_total"] for c in compras)},
    "meses": {k: {"ventas": v[0], "ingresos": v[1]} for k, v in sorted(mes.items())},
    "top5": [(corto(n, 60), u) for n, u in top5], "bottom5": [(corto(n, 60), u) for n, u in bottom5],
    "sin_ventas": sin_ventas,
    "top_clientes": [(n, round(t, 2), pedidos_cliente[n]) for n, t in top_clientes],
    "existencias": [(p["default_code"], p["name"], p["qty_available"]) for p in productos],
    "existencias_min": min(productos, key=lambda p: p["qty_available"])["name"],
}
json.dump(datos, open(SALIDA_JSON, "w"), ensure_ascii=False, indent=1, default=str)

# ---------- Gráficos ----------
semanas = sorted(semana)
fig, ax = plt.subplots(figsize=(7.2, 3.2), dpi=200)
ax.plot(semanas, [semana[s] for s in semanas], color=VERDE, linewidth=2, marker="o", markersize=4)
ax.yaxis.grid(True, color=GRILLA, linewidth=0.8)
ax.set_axisbelow(True)
ax.set_ylabel("Ventas por semana (Q)")
ax.set_title("Evolución de ventas, julio a octubre de 2026", loc="left", fontsize=12, fontweight="bold", color=TINTA, pad=10)
ultima = semanas[-1]
ax.annotate("semana parcial\n(12 y 13 de octubre)", (ultima, semana[ultima]), textcoords="offset points",
            xytext=(-12, 0), ha="right", va="center", fontsize=8, color="#44544B")
pico = max(semanas, key=lambda s: semana[s])
ax.annotate(f"Q{semana[pico]:,.0f}", (pico, semana[pico]), textcoords="offset points", xytext=(6, 4), fontsize=9, color=TINTA)
ax.tick_params(axis="x", labelsize=8)
fig.autofmt_xdate(rotation=0, ha="center")
import matplotlib.dates as mdates
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
fig.tight_layout()
fig.savefig(os.path.join(DIR_BI, "ventas_semana.png"))
plt.close(fig)

orden = sorted(productos, key=lambda p: -p["qty_available"])
barras([corto(p["name"]) for p in orden], [p["qty_available"] for p in orden], "Existencias por producto (unidades)",
       "existencias.png", VERDE)
barras([corto(n) for n, _ in top5], [u for _, u in top5], "5 productos más vendidos (unidades)", "top5_mas.png", VERDE)
barras([corto(n) for n, _ in bottom5], [u for _, u in bottom5], "5 productos menos vendidos (unidades)", "top5_menos.png", TERRACOTA)
barras([corto(n) for n, _ in top_clientes], [t for _, t in top_clientes], "5 clientes con más compras (Q)",
       "top5_clientes.png", VERDE, fmt="Q{:,.2f}")
print(json.dumps({k: datos[k] for k in ("kpi", "contexto", "meses", "top5", "bottom5", "sin_ventas", "top_clientes")},
                 ensure_ascii=False, indent=1))
