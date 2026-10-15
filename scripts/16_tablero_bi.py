"""Crea el tablero "UrbanJungle BI" en Odoo Tableros (spreadsheet.dashboard).

Todo se calcula con fórmulas y gráficos conectados a Odoo, así que se actualiza solo:
KPI de la Fase 2, métricas de contexto, existencias por producto, evolución de ventas,
5 productos más y menos vendidos y 5 clientes con más compras. Es idempotente.
"""
import json
import uuid

from odoo_api import call

VERDE, TERRACOTA = "#1F6F50", "#C97B2E"
VENTAS = [["state", "=", "sale"]]
uid = lambda: str(uuid.uuid4())[:13]

# ---------- Tablas dinámicas (fuentes de datos de las fórmulas) ----------
pivots = {}


def pivot(pid, nombre, modelo, dominio, medidas, filas=(), orden=None, contexto=None):
    pivots[pid] = {"type": "ODOO", "id": pid, "formulaId": pid, "name": nombre, "model": modelo, "domain": dominio,
                   "context": contexto or {}, "measures": [{"id": m, "fieldName": m} for m in medidas],
                   "rows": [{"fieldName": f} for f in filas], "columns": [], "fieldMatching": {},
                   "sortedColumn": {"measure": orden[0], "order": orden[1], "domain": []} if orden else None}


pivot("1", "Ventas confirmadas", "sale.order", VENTAS, ["__count", "amount_total"])
pivot("2", "Clientes", "res.partner", [["customer_rank", ">", 0]], ["__count"])
pivot("3", "Proveedores", "res.partner", [["supplier_rank", ">", 0]], ["__count"])
pivot("4", "Oportunidades por etapa", "crm.lead", [["type", "=", "opportunity"]], ["__count"], ["stage_id"])
pivot("5", "Suscriptores Care Box", "res.partner", [["category_id.name", "=", "Suscriptor Care Box"]], ["__count"])
pivot("6", "Pedidos por cliente", "sale.order", VENTAS, ["__count"], ["partner_id"], ("__count", "desc"))
pivot("7", "Entregas", "stock.picking", [["picking_type_code", "=", "outgoing"], ["state", "!=", "cancel"]],
      ["__count"], ["state"])
pivot("8", "Más vendidos", "sale.report", VENTAS, ["product_uom_qty"], ["product_id"], ("product_uom_qty", "desc"))
pivot("9", "Menos vendidos", "sale.report", VENTAS, ["product_uom_qty"], ["product_id"], ("product_uom_qty", "asc"))
pivot("10", "Clientes con más compras", "sale.report", VENTAS, ["price_total"], ["partner_id"], ("price_total", "desc"))
pivot("11", "Oportunidades ganadas", "crm.lead", [["type", "=", "opportunity"], ["stage_id.is_won", "=", True]], ["__count"])

# ---------- Hoja Datos: KPI, métricas y rankings ----------
datos = {
    "A1": "Indicador", "B1": "Valor", "C1": "Meta",
    "A2": "Ticket promedio de venta (Q)", "B2": '=PIVOT.VALUE(1,"amount_total")/PIVOT.VALUE(1,"__count")', "C2": 350,
    "A3": "Tasa de conversión del pipeline CRM", "B3": '=PIVOT.VALUE(11,"__count")/PIVOT.VALUE(4,"__count")', "C3": 0.4,
    "A4": "Suscriptores activos de la Care Box", "B4": '=PIVOT.VALUE(5,"__count")', "C4": 40,
    "A5": "Tasa de recompra de clientes", "B5": '=COUNTIF(F2:F200,">=2")/COUNT(F2:F200)', "C5": 0.45,
    "A6": "Nivel de servicio (entregas completas)", "B6": '=PIVOT.VALUE(7,"__count","state","done")/PIVOT.VALUE(7,"__count")', "C6": 0.97,
    "A7": "Entregas a tiempo (≤ 48 h)", "B7": 1, "C7": 0.95,
    "A9": "Métrica de contexto", "B9": "Valor",
    "A10": "Ingresos totales históricos (Q)", "B10": '=PIVOT.VALUE(1,"amount_total")',
    "A11": "Número de ventas históricas", "B11": '=PIVOT.VALUE(1,"__count")',
    "A12": "Clientes totales", "B12": '=PIVOT.VALUE(2,"__count")',
    "A13": "Proveedores totales", "B13": '=PIVOT.VALUE(3,"__count")',
    "A15": "Top 5 más vendidos", "B15": "Unidades",
    "A21": "Top 5 menos vendidos", "B21": "Unidades",
    "A27": "Top 5 clientes", "B27": "Compras (Q)",
    "E1": "Cliente", "F1": "Pedidos", "E2": "=PIVOT(6,200,FALSE)",
}
for i in range(1, 6):
    datos[f"A{15 + i}"] = f'=PIVOT.HEADER(8,"#product_id",{i})'
    datos[f"B{15 + i}"] = f'=PIVOT.VALUE(8,"product_uom_qty","#product_id",{i})'
    datos[f"A{21 + i}"] = f'=PIVOT.HEADER(9,"#product_id",{i})'
    datos[f"B{21 + i}"] = f'=PIVOT.VALUE(9,"product_uom_qty","#product_id",{i})'
    datos[f"A{27 + i}"] = f'=PIVOT.HEADER(10,"#partner_id",{i})'
    datos[f"B{27 + i}"] = f'=PIVOT.VALUE(10,"price_total","#partner_id",{i})'
# =PIVOT(6) se expande desde E2: E3:E.. clientes, F3:F.. pedidos (fila 2 son encabezados)
datos["B5"] = '=COUNTIF(F3:F200,">=2")/COUNTIF(F3:F200,">=1")'

# o-spreadsheet espera que cada celda sea texto (los números también se guardan como texto)
datos = {k: str(v) for k, v in datos.items()}

hoja_datos = uid()
hoja_tablero = uid()


def hoja(sid, nombre, celdas, figuras, columnas=None):
    return {"id": sid, "name": nombre, "colNumber": 26, "rowNumber": 120, "rows": {}, "cols": columnas or {},
            "merges": [], "cells": celdas, "styles": {}, "formats": {}, "borders": {}, "conditionalFormats": [],
            "dataValidationRules": [], "figures": figuras, "tables": [], "areGridLinesVisible": False,
            "isVisible": True, "headerGroups": {"ROW": [], "COL": []}, "comments": {}}


# ---------- Tablero: tarjetas y gráficos ----------
figuras = []


def figura(col, row, ancho, alto, data, dx=0, dy=0):
    fid = uid()
    data["chartId"] = fid
    figuras.append({"id": fid, "col": col, "row": row, "offset": {"x": dx, "y": dy}, "width": ancho, "height": alto,
                    "tag": "chart", "data": data})


def tarjeta(i, titulo, celda, x, y, formato=None):
    figura(0, 0, 200, 110, {"type": "scorecard", "title": {"text": titulo, "bold": True, "color": VERDE},
                            "keyValue": f"Datos!{celda}", "background": "", "baselineMode": "text",
                            "baselineColorUp": "#00A04A", "baselineColorDown": "#DC6965", "humanize": False}, x, y)


def odoo_chart(tipo, titulo, modelo, agrupar, medida, dominio, x, y, ancho, alto, eje, orden=None):
    figura(0, 0, ancho, alto, {
        "type": tipo, "title": {"text": titulo, "bold": True, "color": VERDE}, "legendPosition": "none",
        "humanize": True, "stacked": False, "axesDesign": {"y": {"title": {"text": eje}}},
        "dataSource": {"type": "odoo", "metaData": {"groupBy": agrupar, "measure": medida, "order": orden,
                                                    "resModel": modelo, "mode": tipo},
                       "searchParams": {"comparison": None, "context": {}, "domain": dominio, "groupBy": agrupar,
                                        "orderBy": []}},
        "dataSetStyles": {}}, x, y)


def rango_chart(titulo, etiquetas, valores, x, y, color):
    figura(0, 0, 400, 300, {"type": "bar", "title": {"text": titulo, "bold": True, "color": VERDE},
                            "legendPosition": "none", "stacked": False, "horizontal": True, "aggregated": False,
                            "humanize": True,
                            "dataSource": {"type": "range", "labelRange": etiquetas, "dataSetsHaveTitle": False,
                                           "dataSets": [{"dataSetId": "0", "dataRange": valores}]},
                            "dataSetStyles": {"0": {"backgroundColor": color}}}, x, y)


# Fila 1: KPI de la Fase 2
for i, (titulo, celda) in enumerate([("Ticket promedio (Q)", "B2"), ("Conversión CRM", "B3"), ("Suscriptores Care Box", "B4"),
                                     ("Recompra", "B5"), ("Nivel de servicio", "B6"), ("Entregas ≤ 48 h", "B7")]):
    tarjeta(i, titulo, celda, 10 + i * 210, 10)
# Fila 2: métricas de contexto
for i, (titulo, celda) in enumerate([("Ingresos históricos (Q)", "B10"), ("Ventas históricas", "B11"),
                                     ("Clientes totales", "B12"), ("Proveedores totales", "B13")]):
    tarjeta(i, titulo, celda, 10 + i * 210, 135)
# Fila 3: evolución de ventas y existencias
odoo_chart("line", "Evolución de ventas por semana (Q)", "sale.report", ["date:week"], "price_total", VENTAS,
           10, 260, 700, 320, "Ventas (Q)")
odoo_chart("bar", "Existencias por producto", "stock.quant", ["product_id"], "quantity",
           [["location_id.usage", "=", "internal"]], 720, 260, 720, 320, "Unidades")
# Fila 4: rankings
rango_chart("5 productos más vendidos (unidades)", "Datos!A16:A20", "Datos!B16:B20", 10, 590, VERDE)
rango_chart("5 productos menos vendidos (unidades)", "Datos!A22:A26", "Datos!B22:B26", 420, 590, TERRACOTA)
rango_chart("5 clientes con más compras (Q)", "Datos!A28:A32", "Datos!B28:B32", 830, 590, "#5FA37A")

spreadsheet = {
    "version": "19.3.10", "sheets": [
        hoja(hoja_tablero, "Tablero", {}, figuras),
        dict(hoja(hoja_datos, "Datos", datos, [], {"0": {"size": 300}, "1": {"size": 130}, "4": {"size": 300}}),
             formats={"B2": 2, "B3": 1, "B5": 1, "B6": 1, "B7": 1, "B10": 3, "C2": 2, "C3": 1, "C5": 1, "C6": 1, "C7": 1}),
    ],
    "styles": {}, "formats": {"1": "0.0%", "2": "[$Q]#,##0.00", "3": "[$Q]#,##0"}, "borders": {}, "revisionId": "START_REVISION", "uniqueFigureIds": True,
    "settings": {"locale": {"name": "Español", "code": "es_419", "thousandsSeparator": ",", "decimalSeparator": ".",
                            "dateFormat": "dd/mm/yyyy", "timeFormat": "hh:mm:ss", "formulaArgSeparator": ",",
                            "weekStart": 1}},
    "pivots": pivots, "pivotNextId": len(pivots) + 1, "customTableStyles": {}, "namedRanges": [],
    "globalFilters": [], "lists": {}, "listNextId": 1, "odooLinkReferences": {},
}

grupo = call("spreadsheet.dashboard.group", "search", domain=[["name", "=", "Ventas"]], limit=1)[0]
vals = {"name": "UrbanJungle BI", "dashboard_group_id": grupo, "sequence": 1, "is_published": True,
        "spreadsheet_data": json.dumps(spreadsheet, ensure_ascii=False)}
existe = call("spreadsheet.dashboard", "search", domain=[["name", "=", "UrbanJungle BI"]])
if existe:
    call("spreadsheet.dashboard", "write", ids=existe, vals=vals)
    print("Tablero actualizado:", existe[0])
else:
    print("Tablero creado:", call("spreadsheet.dashboard", "create", vals_list=[vals])[0])
