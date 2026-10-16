// Genera Manual_Tecnico_Fase3_UrbanJungle.docx: operación del sitio de comercio electrónico.
// Uso: VIDEO_URL=<enlace> NODE_PATH=<carpeta con node_modules> node manual/generar_manual_fase3.js
// Las capturas del backend se incluyen solo si el archivo existe en assets/capturas.
const fs = require("fs");
const path = require("path");
const B = require("./base");
const { P, H1, H2, q, run, bullet, pasos, figura, tabla, ficha, espacio, enlace } = B;

const D = JSON.parse(fs.readFileSync(path.join(__dirname, "datos_fase3.json"), "utf8"));
const C = D.contexto;
const VIDEO_URL = process.env.VIDEO_URL || "https://drive.google.com/file/d/1R2NjcmlobDmDndXHG34Hk1iaLXp1ktwT/view";
const SITIO = D.url;
let nFig = 0;
const existe = (rel) => fs.existsSync(path.join(B.ROOT, rel));
const captura = (archivo, pie, alto = 338) => existe(`assets/capturas/${archivo}`)
  ? figura(`assets/capturas/${archivo}`, 600, alto, `Figura ${++nFig}. ${pie}`) : [];
const diagrama = (rel, w, h, pie) => figura(rel, w, h, `Figura ${++nFig}. ${pie}`);

const hijos = [
  ...B.portada("MANUAL TÉCNICO", "Sitio de comercio electrónico UrbanJungle", "Guatemala, 17 de octubre de 2026"),

  H1("Introducción"),
  P(`Este manual describe cómo funciona el sitio de comercio electrónico de UrbanJungle: la arquitectura cliente-servidor, las tecnologías, el flujo de datos entre la tienda y el ERP, la configuración realizada y el uso paso a paso del sitio por parte de un comprador y del personal del vivero.`),
  ficha([
    ["Sitio web", SITIO],
    ["Tienda en línea", `${SITIO}/shop`],
    ["Plataforma", "Odoo Online (SaaS) Enterprise, versión 20.0, base de datos usac-g3"],
    ["Módulos", "Sitio web, eCommerce, Ventas, Inventario, Compras, CRM, Contactos, Contabilidad y Tableros"],
    ["Catálogo publicado", `${C.productos} productos en 7 categorías`],
    ["Métodos de pago", "Transferencia bancaria y pago contra entrega"],
    ["Método de entrega", "Entrega a domicilio (24 a 48 h), sin costo en el área metropolitana"],
    ["Registro de clientes", "Abierto: cualquier visitante puede crear su cuenta desde el sitio"],
  ]),

  H1("Arquitectura e interacción cliente-servidor"),
  P("El sitio sigue el modelo cliente-servidor. El cliente es el navegador del comprador; el servidor es la instancia de Odoo Online, que aloja a la vez la tienda y el ERP. No hay un servidor web separado ni una base de datos propia de la tienda: los controladores web de Odoo atienden las páginas del sitio y usan el mismo ORM y la misma base de datos PostgreSQL que Ventas, Inventario, Compras y CRM."),
  ...diagrama("assets/arquitectura_web.png", 600, 274, "Arquitectura cliente-servidor del sitio."),
  P("Cuando el comprador abre una página, el navegador envía una petición HTTPS (por ejemplo GET /shop). El controlador de Odoo consulta los productos publicados con el ORM, arma la página con una plantilla QWeb y devuelve HTML con estilos de Bootstrap. Las acciones dentro de la página, como agregar al carrito o cambiar una cantidad, las envía el JavaScript de Odoo como peticiones JSON (por ejemplo a /shop/cart/add) y el servidor responde solo con los datos que cambian. La sesión del visitante se guarda en una cookie, que relaciona el navegador con su carrito y, si inició sesión, con su cuenta."),

  H1("Tecnologías utilizadas"),
  tabla(["Capa", "Tecnología", "Uso en el sitio"], [
    ["Servidor de aplicación", "Odoo 20 (Python)", "Controladores web, reglas de negocio, ORM y permisos"],
    ["Base de datos", "PostgreSQL", "Productos, clientes, pedidos, inventario, compras y oportunidades"],
    ["Plantillas", "QWeb (XML)", "Páginas del sitio: inicio, tienda, ficha de producto, carrito y checkout"],
    ["Presentación", "HTML5, SCSS y Bootstrap 5", "Diseño adaptable; paleta verde y terracota y fuente Montserrat de la marca"],
    ["Interacción", "JavaScript de Odoo y JSON-RPC", "Carrito, buscador y formularios sin recargar la página"],
    ["Comunicación", "HTTPS", "Cifrado entre el navegador y el servidor de Odoo Online"],
    ["Inteligencia de negocio", "Odoo Tableros (o-spreadsheet)", "Tablero UrbanJungle BI con datos en vivo"],
    ["Configuración", "Python y API JSON-2 de Odoo", "Scripts de carga de productos, ventas, páginas y tablero"],
  ], [2300, 2700, 4360]),

  H1("Flujo de datos"),
  P("La tienda no copia datos al ERP: ambos trabajan sobre los mismos registros. El recorrido de un pedido es el siguiente."),
  ...pasos([
    "Catálogo. La tienda lista los productos con la opción Publicado activa (product.template). El precio, la imagen y la descripción se leen del mismo producto que usa Ventas, así que un cambio de precio en el ERP aparece en el sitio al recargar.",
    "Carrito. Al agregar el primer producto, Odoo crea un pedido de venta en estado Cotización con el sitio web asignado (sale.order). Cada producto del carrito es una línea de ese pedido. Por eso cada carrito es también una cotización visible en Ventas.",
    "Registro y dirección. Al registrarse o llenar la dirección en el checkout, Odoo crea o actualiza el contacto del cliente (res.partner) con nombre, correo, teléfono, dirección y NIT. Ese contacto es el mismo que aparece en Contactos y CRM.",
    "Pago. Con transferencia bancaria o contra entrega, el pedido queda como cotización enviada con la transacción de pago pendiente. El personal confirma el pedido cuando recibe el pago o lo despacha contra entrega.",
    "Entrega. Al confirmar el pedido, Inventario genera la entrega WH/OUT y reserva el stock. Al validarla, las existencias bajan.",
    "Reabastecimiento. Si el pronóstico de un producto cae bajo el mínimo de su regla de reordenamiento, Compras genera una solicitud de cotización al proveedor configurado.",
    "Análisis. El tablero UrbanJungle BI lee pedidos, existencias y contactos directamente de la base de datos, así que el pedido nuevo aparece en los indicadores al recargar.",
  ]),

  H1("Configuración implementada"),
  P("La configuración se hizo con scripts de Python que usan la API JSON-2 de Odoo, para poder repetirla en otra base de datos. Están en la carpeta scripts del repositorio del proyecto."),
  tabla(["Script", "Qué configura"], [
    ["11_productos_fase3.py", "10 productos nuevos (catálogo de 30), sus proveedores, stock inicial y reglas de reordenamiento; 6 clientes registrados por el sitio"],
    ["12_ventas_fase3.py", "60 ventas de julio, agosto y octubre (110 en total con las de la Fase 2), entregas y 4 cotizaciones web"],
    ["13_tienda_catalogo.py", "Nombre y logo del sitio, 7 categorías de la tienda, publicación de los 30 productos, descripciones, cinta de productos nuevos, accesorios sugeridos y métodos de pago"],
    ["14_sitio_paginas.py", "Páginas de inicio, Care Box y Nosotros, y el menú principal"],
    ["15_sitio_textos.py", "Encabezado, pie de página y página de contacto con los datos de UrbanJungle"],
    ["16_tablero_bi.py", "Tablero UrbanJungle BI en Odoo Tableros"],
  ], [2600, 6760]),
  P("Los colores y la fuente del tema se definieron con las opciones de personalización del sitio (paleta de 5 colores y Montserrat). Los accesorios sugeridos de cada planta son la maceta de barro, el sustrato y el fertilizante, que aparecen en el carrito para la venta cruzada.", { before: 120 }),

  H1("Uso del sitio paso a paso"),
  H2("Navegar el catálogo"),
  P("La página de inicio muestra la portada, las categorías, los pasos de compra, la suscripción Care Box y los productos nuevos. El menú superior lleva a Tienda, Care Box, Nosotros y Contáctanos."),
  ...captura("01_inicio.jpg", "Página de inicio."),
  P("En Tienda se ven los 30 productos. Se puede filtrar por categoría con la barra superior, buscar por nombre y ordenar por precio o nombre."),
  ...captura("02_tienda.jpg", "Catálogo de la tienda con filtro por categoría."),
  H2("Agregar productos al carrito"),
  P("La ficha de cada producto tiene la foto, la descripción de cuidado y el precio con IVA incluido. Se elige la cantidad y se pulsa Agregar al carrito. Los productos nuevos llevan la cinta ¡Nuevo!."),
  ...captura("03_producto.jpg", "Ficha de producto."),
  P("El ícono del carrito muestra la cantidad de productos. En el carrito se cambian cantidades, se eliminan productos y aparecen los accesorios sugeridos. El resumen de la derecha muestra el total con el IVA desglosado y el botón Finalizar compra."),
  ...captura("05_carrito.jpg", "Carrito con accesorios sugeridos."),
  H2("Registrarse e iniciar sesión"),
  P("Desde Inicia sesión, en el encabezado, el comprador entra con su correo y contraseña. Si no tiene cuenta, el enlace ¿No tienes una cuenta? abre el registro, que pide nombre, correo y contraseña. La cuenta queda como contacto en Odoo y permite ver los pedidos anteriores desde Mi cuenta."),
  ...captura("04_registro.jpg", "Formulario de registro de clientes."),
  H2("Completar la compra"),
  P("Finalizar compra lleva a la página de dirección, donde el comprador sin sesión llena nombre, correo, teléfono, dirección y NIT, o inicia sesión para usar los datos guardados. El campo NIT valida el formato guatemalteco; un consumidor final escribe NA."),
  ...captura("06_checkout_direccion.jpg", "Datos del comprador en el checkout."),
  P("El siguiente paso muestra el método de entrega, Entrega a domicilio (24 a 48 h), y la dirección de entrega y facturación para revisarla antes de pagar."),
  ...captura("06b_entrega.jpg", "Método y dirección de entrega."),
  P("En la página de pago el comprador elige Transferencia bancaria o Pago contra entrega y pulsa Paga ahora. Pago contra entrega solo aparece con métodos de envío que lo permiten, y en UrbanJungle lo permite la entrega a domicilio."),
  ...captura("07_pago.jpg", "Selección del método de pago."),
  P("Al pagar, el sitio muestra el número de pedido, el monto y la referencia que el comprador debe indicar en la transferencia. El pedido queda en Ventas como cotización enviada con el pago pendiente hasta que el personal lo confirma."),
  ...captura("08_confirmacion.jpg", "Confirmación del pedido con los datos para la transferencia."),

  H1("Integración con el ERP y el CRM"),
  P(`El pedido del sitio aparece en Ventas, en Pedidos, con el sitio web como origen. Para el período analizado hay ${C.ventas_web} pedidos web confirmados y ${C.cotizaciones_web} cotizaciones web abiertas. El personal confirma el pedido, valida la entrega en Inventario y, si corresponde, emite la factura en Contabilidad.`),
  ...captura("09_pedidos_web.jpg", "Pedidos del sitio web en Ventas."),
  P(`Los clientes que se registran en el sitio quedan en Contactos con la etiqueta Registro web (hay ${C.clientes_web}), y se les puede crear una oportunidad en el pipeline del CRM y enviarles las plantillas de correo de la Fase 2.`),
  ...captura("10_tablero_bi.jpg", "Tablero UrbanJungle BI en Odoo Tableros."),

  ...(VIDEO_URL ? [H1("Video tutorial"), P(["El video está en ", enlace(VIDEO_URL), "."], { align: B.AlignmentType.LEFT }),
    P("Es el video tutorial del sitio de comercio electrónico de UrbanJungle, publicado en Google Drive con acceso para cualquier persona que tenga el enlace.")] : []),

  H1("Créditos de imágenes"),
  P("El logotipo, los banners, las ilustraciones del Kit de Inicio, el Tutor de Musgo, la Maceta Autorriego y la Care Box, y los diagramas son del equipo. Las fotografías de productos son de Wikimedia Commons con licencias libres; la lista completa con autor y licencia está en el Manual Técnico de la Fase 2 y en assets/productos/creditos.json del repositorio."),
];

if (!VIDEO_URL) console.warn("Aviso: sin VIDEO_URL, el manual no incluye la sección del video.");
B.guardar("Manual_Tecnico_Fase3_UrbanJungle.docx", "Manual Técnico UrbanJungle, Fase 3", "UrbanJungle · Manual Técnico · Fase 3 · SOG1", hijos);
