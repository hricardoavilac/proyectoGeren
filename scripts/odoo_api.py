"""Cliente mínimo para la API JSON-2 de Odoo 19 (lee credenciales de .env)."""
import base64
import json
import os
import time
import urllib.request

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENV = dict(l.strip().split('=', 1) for l in open(os.path.join(_ROOT, '.env')) if '=' in l)
URL = _ENV['ODOO_URL'].rstrip('/')
DB = _ENV['ODOO_DB'].strip()
KEY = _ENV['ODOO_API_KEY'].strip()


def call(model, method, **kw):
    kw.setdefault("context", {"lang": "es_419", "tz": "America/Guatemala"})
    req = urllib.request.Request(
        f"{URL}/json/2/{model}/{method}",
        data=json.dumps(kw).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"bearer {KEY}",
                 "X-Odoo-Database": DB},
    )
    for intento in range(5):
        try:
            return json.load(urllib.request.urlopen(req, timeout=600))
        except urllib.error.HTTPError as e:
            body = json.loads(e.read().decode())
            raise RuntimeError(f"{model}.{method}: {body.get('message')}") from None
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            # Fallos de conexión (red inestable): reintentar con espera creciente.
            if intento == 4:
                raise
            time.sleep(3 * (intento + 1))


def adjunto_publico(nombre, ruta, mimetype="image/jpeg"):
    """Sube (o reutiliza) un adjunto público y devuelve su URL. En Odoo 19 el contenido va en "raw"."""
    datos = base64.b64encode(open(ruta, "rb").read()).decode()
    existentes = call("ir.attachment", "search_read", fields=["file_size"], domain=[
        ["name", "=", nombre], ["public", "=", True], ["res_model", "=", False]])
    if not existentes:
        att_id = call("ir.attachment", "create", vals_list=[{
            "name": nombre, "raw": datos, "mimetype": mimetype, "public": True}])[0]
    else:
        att_id = existentes[0]["id"]
        if not existentes[0]["file_size"]:
            call("ir.attachment", "write", ids=[att_id], vals={"raw": datos})
    return f"{URL}/web/image/{att_id}/{nombre}"
