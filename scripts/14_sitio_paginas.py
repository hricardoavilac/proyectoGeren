"""Diseña las páginas del sitio: inicio, Care Box y Nosotros, y deja el menú principal con las secciones
de UrbanJungle. Las imágenes salen de los productos publicados. Es idempotente."""
from odoo_api import call

VERDE, TERRACOTA, CLARO, FONDO = "#1F6F50", "#C97B2E", "#D7E8DD", "#F4F7F5"
sitio = call("website", "search", domain=[], limit=1)[0]

prod = {p["default_code"]: p for p in call("product.template", "search_read", domain=[["default_code", "like", "UJ-P"]],
                                          fields=["default_code", "name", "list_price", "website_url"])}
cats = {c["name"]: c for c in call("product.public.category", "search_read", domain=[], fields=["name", "website_url"])}
img = lambda ref, size=1024: f"/web/image/product.template/{prod[ref]['id']}/image_{size}"
img_cat = lambda c: f"/web/image/product.public.category/{cats[c]['id']}/image_512"
q = lambda n: f"Q{n:,.2f}"


def boton(texto, url, claro=False):
    estilo = (f"background:#FFFFFF;color:{VERDE};" if claro else f"background:{TERRACOTA};color:#FFFFFF;")
    return (f'<a href="{url}" class="btn btn-lg rounded-pill me-2 mb-2" '
            f'style="{estilo}border:none;padding:12px 28px;font-weight:600;">{texto}</a>')


def tarjeta_producto(ref):
    p = prod[ref]
    return f"""
      <div class="col-6 col-lg-3 mb-4">
        <a href="{p['website_url']}" class="text-decoration-none">
          <div class="card h-100 border-0 shadow-sm" style="border-radius:16px;overflow:hidden;">
            <img src="{img(ref, 512)}" class="card-img-top" alt="{p['name']}" style="aspect-ratio:1/1;object-fit:cover;"/>
            <div class="card-body">
              <h6 class="mb-1" style="color:#1E2B24;">{p['name']}</h6>
              <span style="color:{VERDE};font-weight:700;">{q(p['list_price'])}</span>
            </div>
          </div>
        </a>
      </div>"""


def tarjeta_categoria(nombre):
    return f"""
      <div class="col-6 col-md-4 col-lg-2 mb-4 text-center">
        <a href="{cats[nombre]['website_url']}" class="text-decoration-none">
          <img src="{img_cat(nombre)}" alt="{nombre}" class="rounded-circle shadow-sm mb-2"
               style="width:120px;height:120px;object-fit:cover;border:4px solid {CLARO};"/>
          <h6 style="color:#1E2B24;">{nombre}</h6>
        </a>
      </div>"""


INICIO = f"""
<section class="pt-5 pb-5" style="background:{VERDE};">
  <div class="container">
    <div class="row align-items-center">
      <div class="col-lg-6 mb-4 mb-lg-0" style="color:#FFFFFF;">
        <p class="mb-2" style="letter-spacing:3px;color:{CLARO};">VIVERO EL JARDÍN URBANO · ZONA 15</p>
        <h1 class="display-4 fw-bold mb-3" style="color:#FFFFFF;">Plantas de interior con entrega a domicilio</h1>
        <p class="lead mb-4" style="color:#FFFFFF;">Plantas, macetas y sustratos del vivero, con entrega en 24 a 48 horas
          en la ciudad de Guatemala, Mixco, Villa Nueva, Santa Catarina Pinula, San Miguel Petapa y Fraijanes.</p>
        {boton("Ver la tienda", "/shop")}{boton("Conocer la Care Box", "/care-box", claro=True)}
      </div>
      <div class="col-lg-6">
        <div class="row g-3">
          <div class="col-7"><img src="{img('UJ-P01')}" alt="Monstera" class="img-fluid shadow" style="border-radius:20px;"/></div>
          <div class="col-5 d-flex flex-column gap-3">
            <img src="{img('UJ-P25', 512)}" alt="Orquídea" class="img-fluid shadow" style="border-radius:20px;"/>
            <img src="{img('UJ-P21', 512)}" alt="Pilea" class="img-fluid shadow" style="border-radius:20px;"/>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="pt-5 pb-4" style="background:{FONDO};">
  <div class="container">
    <h2 class="text-center fw-bold mb-4" style="color:{VERDE};">Compra por categoría</h2>
    <div class="row justify-content-center">
      {''.join(tarjeta_categoria(c) for c in ["Plantas de Interior", "Suculentas y Cactus", "Macetas y Colgantes",
                                              "Sustratos y Fertilizantes", "Herramientas y Accesorios", "Kits y Regalos"])}
    </div>
  </div>
</section>

<section class="pt-5 pb-5" style="background:#FFFFFF;">
  <div class="container">
    <h2 class="text-center fw-bold mb-5" style="color:{VERDE};">Cómo comprar</h2>
    <div class="row text-center">
      <div class="col-md-4 mb-4">
        <div class="mx-auto mb-3 d-flex align-items-center justify-content-center rounded-circle"
             style="width:72px;height:72px;background:{CLARO};color:{VERDE};font-size:28px;font-weight:700;">1</div>
        <h5 class="fw-bold">Elige tus plantas</h5>
        <p class="text-muted">Cada ficha indica luz, riego y tamaño. Al agregar una planta, la tienda sugiere maceta, sustrato y fertilizante.</p>
      </div>
      <div class="col-md-4 mb-4">
        <div class="mx-auto mb-3 d-flex align-items-center justify-content-center rounded-circle"
             style="width:72px;height:72px;background:{CLARO};color:{VERDE};font-size:28px;font-weight:700;">2</div>
        <h5 class="fw-bold">Crea tu cuenta y paga</h5>
        <p class="text-muted">Regístrate con tu correo, ingresa NIT y dirección, y paga por transferencia bancaria o contra entrega.</p>
      </div>
      <div class="col-md-4 mb-4">
        <div class="mx-auto mb-3 d-flex align-items-center justify-content-center rounded-circle"
             style="width:72px;height:72px;background:{CLARO};color:{VERDE};font-size:28px;font-weight:700;">3</div>
        <h5 class="fw-bold">Recibe en 24 a 48 horas</h5>
        <p class="text-muted">La flota del vivero entrega en cajas protegidas. Si una planta llega dañada, se repone sin costo.</p>
      </div>
    </div>
  </div>
</section>

<section class="pt-5 pb-5" style="background:#F4EBDD;">
  <div class="container">
    <div class="row align-items-center">
      <div class="col-lg-5 mb-4 mb-lg-0">
        <img src="{img('UJ-P20')}" alt="Care Box" class="img-fluid shadow" style="border-radius:20px;"/>
      </div>
      <div class="col-lg-7 ps-lg-5">
        <p class="mb-2" style="letter-spacing:3px;color:{TERRACOTA};">SUSCRIPCIÓN MENSUAL</p>
        <h2 class="fw-bold mb-3" style="color:{VERDE};">UrbanJungle Care Box</h2>
        <p class="lead">Cada mes llega a tu casa una caja con fertilizante orgánico, la guía de cuidado de la temporada
          y un accesorio. Cuesta {q(prod['UJ-P20']['list_price'])} al mes.</p>
        {boton("Ver la Care Box", "/care-box")}
      </div>
    </div>
  </div>
</section>

<section class="pt-5 pb-4" style="background:#FFFFFF;">
  <div class="container">
    <h2 class="text-center fw-bold mb-4" style="color:{VERDE};">Recién llegados al vivero</h2>
    <div class="row">{''.join(tarjeta_producto(r) for r in ["UJ-P25", "UJ-P21", "UJ-P24", "UJ-P29"])}</div>
    <div class="text-center mb-4">{boton("Ver los 30 productos", "/shop")}</div>
  </div>
</section>
"""

CARE_BOX = f"""
<section class="pt-5 pb-5" style="background:{VERDE};color:#FFFFFF;">
  <div class="container text-center">
    <p class="mb-2" style="letter-spacing:3px;color:{CLARO};">SUSCRIPCIÓN MENSUAL</p>
    <h1 class="display-5 fw-bold" style="color:#FFFFFF;">UrbanJungle Care Box</h1>
    <p class="lead" style="color:#FFFFFF;">{q(prod['UJ-P20']['list_price'])} al mes, con entrega a domicilio en el área metropolitana.</p>
  </div>
</section>
<section class="pt-5 pb-5" style="background:#FFFFFF;">
  <div class="container">
    <div class="row align-items-center">
      <div class="col-lg-5 mb-4"><img src="{img('UJ-P20')}" alt="Care Box" class="img-fluid shadow" style="border-radius:20px;"/></div>
      <div class="col-lg-7 ps-lg-5">
        <h3 class="fw-bold mb-3" style="color:{VERDE};">Qué trae cada caja</h3>
        <ul class="lead">
          <li>Fertilizante líquido orgánico para el mes.</li>
          <li>Guía impresa de cuidado según la temporada (lluvias o verano).</li>
          <li>Un accesorio: atomizador, tutor de musgo, maceta pequeña o una suculenta.</li>
        </ul>
        <h3 class="fw-bold mt-4 mb-3" style="color:{VERDE};">Cómo suscribirse</h3>
        <p>Agrega la Care Box al carrito y completa la compra. El equipo de UrbanJungle confirma el pedido y programa
          la entrega mensual a la dirección registrada en tu cuenta.</p>
        {boton("Agregar la Care Box", prod['UJ-P20']['website_url'])}
      </div>
    </div>
  </div>
</section>
"""

NOSOTROS = f"""
<section class="pt-5 pb-5" style="background:{VERDE};color:#FFFFFF;">
  <div class="container text-center">
    <h1 class="display-5 fw-bold" style="color:#FFFFFF;">Nosotros</h1>
    <p class="lead" style="color:#FFFFFF;">Vivero El Jardín Urbano, zona 15 de la ciudad de Guatemala.</p>
  </div>
</section>
<section class="pt-5 pb-5" style="background:#FFFFFF;">
  <div class="container">
    <div class="row align-items-center">
      <div class="col-lg-6 mb-4">
        <p class="lead">Vivero El Jardín Urbano vende plantas de interior, macetas e insumos desde hace 12 años en la
          zona 15. UrbanJungle es su tienda en línea: el mismo inventario del vivero, con pedidos por internet y
          entrega a domicilio.</p>
        <p>Atendemos de lunes a sábado de 8:00 a 18:00 en Blvd. Vista Hermosa 12-45, zona 15. Teléfono +502 2369 4580,
          correo ventas@urbanjungle.gt.</p>
        {boton("Escríbenos", "/contactus")}
      </div>
      <div class="col-lg-6"><img src="{img('UJ-P04')}" alt="Ficus Lyrata" class="img-fluid shadow" style="border-radius:20px;"/></div>
    </div>
  </div>
</section>
"""


def arch(titulo, contenido):
    return (f'<t t-name="{titulo}"><t t-call="website.layout">'
            f'<div id="wrap" class="oe_structure">{contenido}</div></t></t>')


# Inicio: vista específica del sitio
home = call("ir.ui.view", "search", domain=[["key", "=", "website.homepage"], ["website_id", "=", sitio]])
call("ir.ui.view", "write", ids=home, vals={"arch_db": arch("website.homepage", INICIO).replace(
    '<t t-call="website.layout">', '<t t-call="website.layout" pageName.f="homepage">')})

for url, nombre, contenido in (("/care-box", "Care Box", CARE_BOX), ("/nosotros", "Nosotros", NOSOTROS)):
    key = f"website.urbanjungle_{url.strip('/').replace('-', '_')}"
    vista = call("ir.ui.view", "search", domain=[["key", "=", key]])
    vals = {"name": nombre, "type": "qweb", "key": key, "website_id": sitio, "arch_db": arch(key, contenido)}
    if vista:
        call("ir.ui.view", "write", ids=vista, vals=vals)
    else:
        vista = call("ir.ui.view", "create", vals_list=[vals])
    if not call("website.page", "search", domain=[["url", "=", url], ["website_id", "=", sitio]]):
        call("website.page", "create", vals_list=[{"url": url, "view_id": vista[0], "website_id": sitio,
                                                   "is_published": True, "website_indexed": True}])

# Menú principal
raiz = call("website.menu", "search", domain=[["website_id", "=", sitio], ["parent_id", "=", False]])[0]
MENU = [("Inicio", "/", 10), ("Tienda", "/shop", 20), ("Care Box", "/care-box", 30), ("Nosotros", "/nosotros", 40),
        ("Contáctanos", "/contactus", 50)]
actuales = call("website.menu", "search_read", domain=[["parent_id", "=", raiz]], fields=["name", "url"])
for m in actuales:
    if m["url"] not in [u for _, u, _ in MENU]:
        call("website.menu", "unlink", ids=[m["id"]])
for nombre, url, seq in MENU:
    ids = call("website.menu", "search", domain=[["parent_id", "=", raiz], ["url", "=", url]])
    vals = {"name": nombre, "url": url, "sequence": seq, "parent_id": raiz, "website_id": sitio}
    if ids:
        call("website.menu", "write", ids=ids, vals=vals)
    else:
        call("website.menu", "create", vals_list=[vals])
print([m["name"] for m in call("website.menu", "search_read", domain=[["parent_id", "=", raiz]], fields=["name"], order="sequence")])
