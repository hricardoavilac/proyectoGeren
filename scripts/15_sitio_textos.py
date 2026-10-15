"""Reemplaza los textos de ejemplo de Odoo (encabezado, pie de página y página de contacto) con los datos de
UrbanJungle. Las vistas genéricas se escriben con el contexto del sitio para que Odoo cree una copia
solo para este sitio (copy-on-write) y la plantilla base no cambie."""
import re

from odoo_api import call

SITIO = call("website", "search", domain=[], limit=1)[0]
CTX = {"lang": "es_419", "website_id": SITIO}
TEL, TEL_LINK, CORREO = "+502 2369 4580", "tel:+50223694580", "ventas@urbanjungle.gt"
DIRECCION = "Blvd. Vista Hermosa 12-45, zona 15, ciudad de Guatemala"
VERDE = "#1F6F50"


def vista_del_sitio(key):
    """Devuelve la copia de la vista para este sitio; la crea escribiendo con el contexto del sitio."""
    propia = call("ir.ui.view", "search", domain=[["key", "=", key], ["website_id", "=", SITIO]])
    if propia:
        return propia[0]
    base = call("ir.ui.view", "search", domain=[["key", "=", key], ["website_id", "=", False]])[0]
    arch = call("ir.ui.view", "read", ids=[base], fields=["arch_db"])[0]["arch_db"]
    call("ir.ui.view", "write", ids=[base], vals={"arch_db": arch}, context=CTX)
    return call("ir.ui.view", "search", domain=[["key", "=", key], ["website_id", "=", SITIO]])[0]


def reemplazar_contacto(arch):
    arch = arch.replace("tel:+1 555-555-5556", TEL_LINK).replace("+1 555-555-5556", TEL)
    arch = arch.replace("mailto:info@yourcompany.example.com", f"mailto:{CORREO}")
    return arch.replace("info@yourcompany.example.com", CORREO).replace("info@tuempresa.ejemplo.com", CORREO)


# Encabezado
v = vista_del_sitio("website.header_text_element")
arch = call("ir.ui.view", "read", ids=[v], fields=["arch_db"])[0]["arch_db"]
call("ir.ui.view", "write", ids=[v], vals={"arch_db": reemplazar_contacto(arch)})

# Pie de página
footer = call("ir.ui.view", "search", domain=[["key", "=", "website.footer_custom"], ["website_id", "=", SITIO]])[0]
call("ir.ui.view", "write", ids=[footer], vals={"arch_db": f"""<data name="Default">
    <xpath expr="//div[@id='footer']" position="replace">
        <div id="footer" class="oe_structure oe_structure_solo text-break" t-ignore="true" t-if="not no_footer">
            <section class="s_text_block pt40 pb16" data-snippet="s_text_block" data-name="Container">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-2 pt24 pb24">
                            <h5>Secciones</h5>
                            <ul class="list-unstyled">
                                <li><a href="/">Inicio</a></li>
                                <li><a href="/shop">Tienda</a></li>
                                <li><a href="/care-box">Care Box</a></li>
                                <li><a href="/nosotros">Nosotros</a></li>
                                <li><a href="/contactus">Contáctanos</a></li>
                            </ul>
                        </div>
                        <div class="col-lg-5 pt24 pb24">
                            <h5>UrbanJungle</h5>
                            <p>Tienda en línea de Vivero El Jardín Urbano. Plantas de interior, macetas, sustratos y la
                            suscripción mensual Care Box, con entrega en 24 a 48 horas en el área metropolitana de Guatemala.</p>
                        </div>
                        <div class="col-lg-4 offset-lg-1 pt24 pb24">
                            <h5>Contacto</h5>
                            <ul class="list-unstyled">
                                <li><i class="oi oi-filled oi-fw me-2" data-icon="location_on"/>{DIRECCION}</li>
                                <li><i class="oi oi-filled oi-fw me-2" data-icon="mail"/><a href="mailto:{CORREO}">{CORREO}</a></li>
                                <li><i class="oi oi-filled oi-fw me-2" data-icon="phone"/><a href="{TEL_LINK}"><span class="o_force_ltr">{TEL}</span></a></li>
                                <li><i class="oi oi-filled oi-fw me-2" data-icon="schedule"/>Lunes a sábado, 8:00 a 18:00</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </xpath>
</data>"""})

# Página de contacto: se conserva el formulario y se reemplazan los bloques de ejemplo
v = vista_del_sitio("website.contactus")
arch = call("ir.ui.view", "read", ids=[v], fields=["arch_db"])[0]["arch_db"]
arch = reemplazar_contacto(arch)
arch = arch.replace("Contáctanos sobre cualquier cosa relacionada con nuestra empresa o servicios.",
                    "Escríbenos por pedidos, entregas o cuidado de plantas. Respondemos el mismo día hábil.")
arch = arch.replace('placeholder="John Doe"', 'placeholder="Nombre completo"')
arch = re.sub(r'placeholder="[^"]*@example\.com"', 'placeholder="correo@dominio.com"', arch)
arch = arch.replace("/web/image/website.s_form_aside_default_image",
                    "/web/image/product.template/" + str(call("product.template", "search", domain=[["default_code", "=", "UJ-P24"]])[0]) + "/image_1024")
inicio = arch.find('<section class="s_title')
fin = arch.rfind("</div>", 0, arch.rfind("</t>"))
INFO = f"""<section class="pt48 pb48" style="background:#F4F7F5;">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-4 pb24">
                                <h2 class="h4-fs" style="color:{VERDE};">Visítanos</h2>
                                <p>{DIRECCION}<br/>Lunes a sábado, 8:00 a 18:00<br/>{TEL}<br/>{CORREO}</p>
                            </div>
                            <div class="col-lg-8">
                                <h2 class="h4-fs" style="color:{VERDE};">Preguntas frecuentes</h2>
                                <div class="row">
                                    <div class="col-md-6 pb16"><h3 class="h6-fs"><strong>¿A dónde entregan?</strong></h3>
                                        <p>Ciudad de Guatemala, Mixco, Villa Nueva, Santa Catarina Pinula, San Miguel Petapa y Fraijanes, en 24 a 48 horas.</p></div>
                                    <div class="col-md-6 pb16"><h3 class="h6-fs"><strong>¿Cómo puedo pagar?</strong></h3>
                                        <p>Por transferencia bancaria o contra entrega, en efectivo o con tarjeta.</p></div>
                                    <div class="col-md-6 pb16"><h3 class="h6-fs"><strong>¿Qué pasa si la planta llega dañada?</strong></h3>
                                        <p>Envíanos una foto el mismo día y la reponemos sin costo en la siguiente entrega.</p></div>
                                    <div class="col-md-6 pb16"><h3 class="h6-fs"><strong>¿Puedo cancelar la Care Box?</strong></h3>
                                        <p>Sí. Avísanos antes del día 25 y no se prepara la caja del mes siguiente.</p></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            """
if inicio != -1:
    arch = arch[:inicio] + INFO + arch[fin:]
call("ir.ui.view", "write", ids=[v], vals={"arch_db": arch})
print("Encabezado, pie de página y contacto actualizados")
