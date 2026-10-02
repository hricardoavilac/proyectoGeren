"""Configura el pipeline CRM de UrbanJungle, una oportunidad por cliente y dos plantillas de correo.

Etapa simulada según la clasificación del cliente:
  Cliente Nuevo -> Nuevo prospecto      Cliente Ocasional -> Contactado
  Cliente Frecuente -> Cotización enviada / Ganado
  Cliente VIP -> Negociación            Suscriptor Care Box -> Ganado
"""
import os

from datos_contactos import CLIENTES
from odoo_api import adjunto_publico, call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

# ---------- Etapas del pipeline ----------
ETAPAS = [("Nuevo prospecto", 1, False), ("Contactado", 2, False), ("Cotización enviada", 3, False),
          ("Negociación", 4, False), ("Ganado – Cliente activo", 70, True)]
existentes = call("crm.stage", "search_read", domain=[], fields=["name", "sequence", "is_won"], order="sequence")
etapa = {}
for (nombre, seq, ganado), actual in zip(ETAPAS, existentes + [None] * len(ETAPAS)):
    if actual:
        call("crm.stage", "write", ids=[actual["id"]], vals={"name": nombre, "sequence": seq, "is_won": ganado})
        etapa[nombre] = actual["id"]
    else:
        etapa[nombre] = call("crm.stage", "create", vals_list=[{"name": nombre, "sequence": seq, "is_won": ganado}])[0]
# Las etapas originales sobrantes (si las hubiera) se ordenan al final
for actual in existentes[len(ETAPAS):]:
    call("crm.stage", "write", ids=[actual["id"]], vals={"sequence": 90})

equipo = call("crm.team", "search", domain=[], limit=1)[0]
call("crm.team", "write", ids=[equipo], vals={"name": "Ventas en línea UrbanJungle"})


def tag(nombre, color):
    ids = call("crm.tag", "search", domain=[["name", "=", nombre]])
    return ids[0] if ids else call("crm.tag", "create", vals_list=[{"name": nombre, "color": color}])[0]


TAGS = {"Suscripción": tag("Suscripción", 10), "Venta cruzada": tag("Venta cruzada", 4),
        "Corporativo": tag("Corporativo", 3), "Recompra": tag("Recompra", 7), "Primera compra": tag("Primera compra", 5)}

# ---------- Oportunidades (una por cliente) ----------
vendedores = call("res.users", "search", domain=[["share", "=", False]], order="id")
socios = {p["name"]: p["id"] for p in call("res.partner", "search_read",
          domain=[["name", "in", [c[0] for c in CLIENTES]]], fields=["name"])}
frecuentes = 0
for i, (nombre, _, tel, correo, _, _, empleador, clase) in enumerate(CLIENTES):
    pila = nombre.split()[0]
    if clase == "Suscriptor Care Box":
        datos = ("Suscripción mensual Care Box", "Ganado – Cliente activo", 179 * 12, ["Suscripción", "Recompra"], "2")
    elif clase == "Cliente VIP":
        datos = (f"Ambientación con plantas para oficina – {empleador}", "Negociación", 4500,
                 ["Corporativo", "Venta cruzada"], "3")
    elif clase == "Cliente Frecuente":
        frecuentes += 1
        destino = "Ganado – Cliente activo" if frecuentes % 2 else "Cotización enviada"
        datos = ("Recompra trimestral: plantas y fertilizante", destino, 850, ["Recompra", "Venta cruzada"], "2")
    elif clase == "Cliente Ocasional":
        datos = ("Reactivación: kit de cuidado de plantas", "Contactado", 320, ["Venta cruzada"], "1")
    else:
        datos = ("Primera compra: bienvenida UrbanJungle", "Nuevo prospecto", 250, ["Primera compra"], "1")
    titulo, nombre_etapa, ingreso, tags, prioridad = datos
    vals = {
        "name": f"{titulo} – {pila}", "type": "opportunity", "partner_id": socios[nombre],
        "contact_name": nombre, "email_from": correo, "phone": tel,
        "stage_id": etapa[nombre_etapa], "expected_revenue": ingreso, "priority": prioridad,
        "user_id": vendedores[i % len(vendedores)], "team_id": equipo,
        "tag_ids": [[6, 0, [TAGS[t] for t in tags]]],
    }
    existe = call("crm.lead", "search", domain=[["partner_id", "=", socios[nombre]], ["type", "=", "opportunity"]])
    if existe:
        call("crm.lead", "write", ids=existe, vals=vals)
    else:
        call("crm.lead", "create", vals_list=[vals])
    print(f"{nombre_etapa:<24} {vals['name']}")

# ---------- Plantillas de correo (modelo Oportunidad/Lead del CRM) ----------
logo = adjunto_publico("uj_logo.png", os.path.join(ASSETS, "logo_urbanjungle.png"), "image/png")
banner_promo = adjunto_publico("uj_banner_promocion.png", os.path.join(ASSETS, "banner_promocion.png"), "image/png")
banner_fide = adjunto_publico("uj_banner_fidelizacion.png", os.path.join(ASSETS, "banner_fidelizacion.png"), "image/png")


def cuerpo(banner, titulo, parrafos, boton, enlace):
    texto = "".join(f'<p style="margin:0 0 14px;font-size:15px;line-height:1.6;color:#333;">{p}</p>' for p in parrafos)
    return f"""
<div style="background:#F4F7F5;padding:24px 0;font-family:Helvetica,Arial,sans-serif;">
  <table align="center" width="600" cellpadding="0" cellspacing="0" style="background:#FFFFFF;border-radius:12px;overflow:hidden;border:1px solid #D7E8DD;">
    <tr><td style="padding:20px 28px;text-align:left;">
      <img src="{logo}" alt="UrbanJungle – Vivero El Jardín Urbano" width="230" style="display:block;"/>
    </td></tr>
    <tr><td><img src="{banner}" alt="{titulo}" width="600" style="display:block;width:100%;"/></td></tr>
    <tr><td style="padding:28px;">
      <h2 style="margin:0 0 16px;color:#1F6F50;font-size:24px;">{titulo}</h2>
      <p style="margin:0 0 14px;font-size:15px;color:#333;">Hola <strong><t t-out="object.partner_id.name or object.contact_name or 'amante de las plantas'"/></strong>,</p>
      {texto}
      <p style="margin:24px 0;text-align:center;">
        <a href="{enlace}" style="background:#1F6F50;color:#FFFFFF;text-decoration:none;padding:14px 32px;border-radius:30px;font-weight:bold;font-size:15px;display:inline-block;">{boton}</a>
      </p>
      <p style="margin:0;font-size:15px;color:#333;">Con cariño verde,<br/><strong>Equipo UrbanJungle</strong></p>
    </td></tr>
    <tr><td style="background:#1F6F50;color:#D7E8DD;padding:16px 28px;font-size:12px;text-align:center;">
      UrbanJungle – Vivero El Jardín Urbano · Blvd. Vista Hermosa 12-45, Zona 15, Guatemala<br/>
      +502 2369 4580 · ventas@urbanjungle.gt · urbanjungle.gt
    </td></tr>
  </table>
</div>"""


PLANTILLAS = [
    ("UrbanJungle – Promoción Especial: Semana Urban Jungle",
     "{{ object.partner_id.name or object.contact_name }}, tienes 20% de descuento en plantas de interior",
     cuerpo(banner_promo, "¡Llegó la Semana Urban Jungle!", [
         "Durante esta semana todas nuestras <strong>plantas de interior tienen 20% de descuento</strong>: "
         "Monstera, Ficus Lyrata, Calathea, Pothos y muchas más, listas para llenar tu hogar de vida.",
         "Usa el código <strong style=\"color:#C97B2E;\">JUNGLA20</strong> al pagar en urbanjungle.gt. "
         "Además, el envío es <strong>gratis</strong> en compras mayores a Q300 dentro del área metropolitana.",
         "Promoción válida hasta agotar existencias. ¡No dejes que te la cuenten!"],
         "Ver plantas en oferta", "https://urbanjungle.gt/ofertas")),
    ("UrbanJungle – Fidelización: Gracias por crecer con nosotros",
     "Gracias por ser parte de la familia UrbanJungle, {{ object.partner_id.name or object.contact_name }}",
     cuerpo(banner_fide, "¡Gracias por crecer con nosotros!", [
         "Queremos agradecerte por confiar en UrbanJungle. Clientes como tú hacen que cada planta "
         "encuentre un hogar lleno de cuidado.",
         "Te recordamos que tu próxima <strong>Care Box mensual</strong> (fertilizante orgánico, guía de cuidado "
         "y una sorpresa) se está preparando. Si deseas cambiar tu dirección de entrega o agregar una maceta, "
         "responde a este correo antes del día 25.",
         "Como agradecimiento, en tu próxima compra tienes <strong>un atomizador para plantas de regalo</strong>."],
         "Gestionar mi suscripción", "https://urbanjungle.gt/mi-cuenta")),
]
modelo_lead = call("ir.model", "search", domain=[["model", "=", "crm.lead"]])[0]
for nombre, asunto, html in PLANTILLAS:
    vals = {"name": nombre, "model_id": modelo_lead, "subject": asunto, "body_html": html,
            "email_from": "{{ (object.user_id.email_formatted or user.email_formatted) }}",
            "use_default_to": True, "lang": "{{ object.partner_id.lang }}"}
    existe = call("mail.template", "search", domain=[["name", "=", nombre]])
    if existe:
        call("mail.template", "write", ids=existe, vals=vals)
    else:
        call("mail.template", "create", vals_list=[vals])
    print("Plantilla:", nombre)
