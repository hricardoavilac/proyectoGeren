"""Registra las 50 ventas simuladas: crea, confirma y valida la entrega de cada pedido.

Cada pedido lleva la referencia de cliente WEB-NNN para no duplicarlo si el script
se vuelve a ejecutar. Al validar las entregas el stock baja y las reglas de
reordenamiento generan las solicitudes de cotización a los proveedores.
"""
from datetime import datetime, timedelta

from datos_ventas import plan_ventas
from odoo_api import call

# Sin esto, validar una entrega abre el asistente "Confirmación por SMS" y la deja pendiente
call("res.company", "write", ids=[1], vals={"has_received_warning_stock_sms": True})
CTX = {"lang": "es_419", "tz": "America/Guatemala", "skip_sms": True}

ventas = plan_ventas()
clientes = {p["name"]: p["id"] for p in call("res.partner", "search_read",
            domain=[["name", "in", list({v["cliente"] for v in ventas})]], fields=["name"])}
variantes = {p["default_code"]: p["id"] for p in call("product.product", "search_read",
             domain=[["default_code", "like", "UJ-P"]], fields=["default_code"])}
vendedores = call("res.users", "search", domain=[["share", "=", False]], order="id")
equipo = call("crm.team", "search", domain=[], limit=1)

for n, venta in enumerate(ventas, start=1):
    ref = f"WEB-{n:03d}"
    if call("sale.order", "search", domain=[["client_order_ref", "=", ref]]):
        continue
    so = call("sale.order", "create", vals_list=[{
        "partner_id": clientes[venta["cliente"]],
        "client_order_ref": ref,
        "user_id": vendedores[n % len(vendedores)],
        "team_id": equipo[0] if equipo else False,
        "order_line": [[0, 0, {"product_id": variantes[r], "product_uom_qty": q}]
                       for r, q in venta["lineas"].items()],
    }])[0]
    call("sale.order", "action_confirm", ids=[so])
    # action_confirm fija la fecha actual: se restablece la fecha simulada (hora de Guatemala -> UTC)
    fecha = datetime.strptime(venta["fecha"], "%Y-%m-%d %H:%M:%S") + timedelta(hours=6)
    call("sale.order", "write", ids=[so], vals={"date_order": fecha.strftime("%Y-%m-%d %H:%M:%S")})

    # Simulación de la entrega: reservar, marcar cantidades y validar
    pedido = call("sale.order", "read", ids=[so], fields=["name", "picking_ids", "amount_total"])[0]
    for picking in pedido["picking_ids"]:
        call("stock.picking", "action_assign", ids=[picking])
        movs = call("stock.move", "search_read", domain=[["picking_id", "=", picking]],
                    fields=["product_uom_qty"])
        for m in movs:
            call("stock.move", "write", ids=[m["id"]], vals={"quantity": m["product_uom_qty"], "picked": True})
        call("stock.picking", "button_validate", ids=[picking], context=CTX)
        entrega = (fecha + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        call("stock.picking", "write", ids=[picking], vals={"date_done": entrega, "scheduled_date": entrega})
    print(f"{ref} {pedido['name']} {venta['cliente']}: Q{pedido['amount_total']:.2f}")
