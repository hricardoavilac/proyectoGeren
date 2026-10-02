"""Renombra la empresa a UrbanJungle y carga logo y datos de contacto."""
import base64
import os

from odoo_api import call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logo = base64.b64encode(open(os.path.join(ROOT, "assets", "logo_urbanjungle.png"), "rb").read()).decode()

gt = call("res.country", "search", domain=[["code", "=", "GT"]])[0]
state = call("res.country.state", "search", domain=[["country_id", "=", gt], ["name", "ilike", "Guatemala"]], limit=1)

call("res.company", "write", ids=[1], vals={
    "name": "UrbanJungle – Vivero El Jardín Urbano",
    "logo": logo,
    "street": "Blvd. Vista Hermosa 12-45, Zona 15",
    "city": "Ciudad de Guatemala",
    "state_id": state[0] if state else False,
    "zip": "01015",
    "country_id": gt,
    "phone": "+502 2369 4580",
    "email": "ventas@urbanjungle.gt",
    "website": "https://urbanjungle.gt",
})
print(call("res.company", "read", ids=[1], fields=["name", "street", "city", "phone", "email", "currency_id"]))
