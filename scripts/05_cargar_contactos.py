"""Crea el campo Empleador, las etiquetas, 20 proveedores (con sus productos) y 30 clientes.

Es idempotente: identifica contactos por NIT y relaciones proveedor-producto por par.
"""
from datos_contactos import CLIENTES, PROVEEDORES, nit
from datos_productos import PRODUCTOS
from odoo_api import call

DEPARTAMENTO = {
    "Escuintla": "Escuintla", "Palín": "Escuintla", "Antigua Guatemala": "Sacatepéquez",
    "San Lucas Sacatepéquez": "Sacatepéquez", "Zacapa": "Zacapa", "Estanzuela": "Zacapa",
    "Totonicapán": "Totonicapán", "Santiago Atitlán": "Sololá", "Chimaltenango": "Chimaltenango",
    "Quetzaltenango": "Quetzaltenango",
}  # el resto de municipios pertenece al departamento de Guatemala

GT = call("res.country", "search", domain=[["code", "=", "GT"]])[0]
ESTADOS = {e["name"]: e["id"] for e in call("res.country.state", "search_read",
                                             domain=[["country_id", "=", GT]], fields=["name"])}


def campo_empleador():
    modelo = call("ir.model", "search", domain=[["model", "=", "res.partner"]])[0]
    if not call("ir.model.fields", "search", domain=[["model", "=", "res.partner"], ["name", "=", "x_empleador"]]):
        call("ir.model.fields", "create", vals_list=[{
            "name": "x_empleador", "field_description": "Empleador", "model_id": modelo,
            "ttype": "char", "state": "manual"}])
    if not call("ir.ui.view", "search", domain=[["name", "=", "res.partner.form.empleador"]]):
        base = call("ir.ui.view", "search", domain=[["model", "=", "res.partner"], ["type", "=", "form"],
                                                   ["name", "=", "res.partner.form"], ["inherit_id", "=", False]])[0]
        call("ir.ui.view", "create", vals_list=[{
            "name": "res.partner.form.empleador", "model": "res.partner", "inherit_id": base,
            "arch_db": '<data><xpath expr="//field[@name=\'function\'][1]" position="before">'
                       '<field name="x_empleador" placeholder="Empresa donde labora el cliente"/>'
                       '</xpath></data>'}])


def etiqueta(nombre, color):
    ids = call("res.partner.category", "search", domain=[["name", "=", nombre]])
    return ids[0] if ids else call("res.partner.category", "create", vals_list=[{"name": nombre, "color": color}])[0]


def contacto(vals):
    ids = call("res.partner", "search", domain=[["vat", "=", vals["vat"]]])
    if ids:
        call("res.partner", "write", ids=ids, vals=vals)
        return ids[0]
    return call("res.partner", "create", vals_list=[vals])[0]


def direccion(calle, ciudad):
    return {"street": calle, "city": ciudad, "country_id": GT,
            "state_id": ESTADOS[DEPARTAMENTO.get(ciudad, "Guatemala")]}


campo_empleador()

productos = {p["default_code"]: p for p in call("product.template", "search_read",
             domain=[["default_code", "in", [p[0] for p in PRODUCTOS]]], fields=["default_code", "standard_price"])}

tag_prov = etiqueta("Proveedor", 4)
for i, (nombre, base, tel, correo, calle, ciudad, rubro, refs, dias) in enumerate(PROVEEDORES, start=1):
    pid = contacto({
        "name": nombre, "is_company": True, "vat": nit(base), "phone": tel, "email": correo,
        **direccion(calle, ciudad), "supplier_rank": 1,
        "category_id": [[6, 0, [tag_prov, etiqueta(f"Proveedor de {rubro}", 4)]]],
    })
    for ref in refs:
        prod = productos[ref]
        existe = call("product.supplierinfo", "search", domain=[
            ["partner_id", "=", pid], ["product_tmpl_id", "=", prod["id"]]])
        # Precio de compra levemente distinto por proveedor; secuencia = prioridad del proveedor.
        precio = round(prod["standard_price"] * (0.96 + (i % 4) * 0.02), 2)
        vals = {"partner_id": pid, "product_tmpl_id": prod["id"], "price": precio,
                "min_qty": 1, "delay": dias, "sequence": i}
        if existe:
            call("product.supplierinfo", "write", ids=existe, vals=vals)
        else:
            call("product.supplierinfo", "create", vals_list=[vals])
    print(f"Proveedor {i:02d}: {nombre} ({len(refs)} productos)")

COLORES = {"Cliente Frecuente": 10, "Cliente VIP": 3, "Suscriptor Care Box": 7,
           "Cliente Ocasional": 2, "Cliente Nuevo": 5}
tag_cli = etiqueta("Cliente", 10)
for i, (nombre, base, tel, correo, calle, ciudad, empleador, clase) in enumerate(CLIENTES, start=1):
    contacto({
        "name": nombre, "is_company": False, "vat": nit(base), "phone": tel, "email": correo,
        **direccion(calle, ciudad), "x_empleador": empleador, "customer_rank": 1,
        "category_id": [[6, 0, [tag_cli, etiqueta(clase, COLORES[clase])]]],
    })
    print(f"Cliente {i:02d}: {nombre} – {clase}")
