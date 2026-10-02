"""Valida las entregas de clientes pendientes y les asigna la fecha simulada (pedido + 1 día)."""
from datetime import datetime, timedelta

from odoo_api import call

# Sin esto, validar una entrega abre el asistente "Confirmación por SMS" y la deja pendiente
call("res.company", "write", ids=[1], vals={"has_received_warning_stock_sms": True})
CTX = {"lang": "es_419", "tz": "America/Guatemala", "skip_sms": True}

pendientes = call("stock.picking", "search", order="id", domain=[
    ["picking_type_code", "=", "outgoing"], ["state", "not in", ["done", "cancel"]]])
for picking in pendientes:
    call("stock.picking", "action_assign", ids=[picking])
    for m in call("stock.move", "search_read", domain=[["picking_id", "=", picking]], fields=["product_uom_qty"]):
        call("stock.move", "write", ids=[m["id"]], vals={"quantity": m["product_uom_qty"], "picked": True})
    call("stock.picking", "button_validate", ids=[picking], context=CTX)

entregas = call("stock.picking", "search_read", order="id", fields=["name", "state", "sale_id"], domain=[
    ["picking_type_code", "=", "outgoing"], ["sale_id", "!=", False]])
for p in entregas:
    fecha = call("sale.order", "read", ids=[p["sale_id"][0]], fields=["date_order"])[0]["date_order"]
    entrega = (datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S") + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    call("stock.picking", "write", ids=[p["id"]], vals={"date_done": entrega, "scheduled_date": entrega})
    print(p["name"], p["state"], entrega)
