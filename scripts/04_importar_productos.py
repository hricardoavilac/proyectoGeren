"""Importa Productos.xlsx con el importador estándar de Odoo (base_import).

Uso: python 04_importar_productos.py [--real]   (sin --real solo valida)
"""
import base64
import os
import sys

from odoo_api import call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(ROOT, "Productos.xlsx")
DRYRUN = "--real" not in sys.argv

CAMPOS = ["default_code", "name", "type", "is_storable", "categ_id", "list_price",
          "standard_price", "barcode", "image_1920", False]  # "Vista previa" no se importa
COLUMNAS = ["Referencia interna", "Nombre", "Tipo de producto", "Rastrear inventario",
            "Categoría del producto", "Precio de venta", "Costo", "Código de barras", "Imagen",
            "Vista previa"]
OPCIONES = {
    "has_headers": True, "sheet": "Productos", "advanced": False, "keep_matches": False,
    "limit": 2000, "skip": 0, "tracking_disable": True, "quoting": '"', "separator": "",
    "encoding": "", "date_format": "", "datetime_format": "",
    "float_thousand_separator": ",", "float_decimal_separator": ".",
    "import_skip_records": [], "import_set_empty_fields": [], "fallback_values": {},
    "name_create_enabled_fields": {},
}

wiz = call("base_import.import", "create", vals_list=[{
    "res_model": "product.template",
    "file": base64.b64encode(open(XLSX, "rb").read()).decode(),
    "file_name": "Productos.xlsx",
    "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}])[0]
res = call("base_import.import", "execute_import", ids=[wiz], fields=CAMPOS,
           columns=COLUMNAS, options=OPCIONES, dryrun=DRYRUN)
print("modo:", "PRUEBA" if DRYRUN else "REAL")
print("mensajes:", res.get("messages"))
print("ids:", res.get("ids"))
