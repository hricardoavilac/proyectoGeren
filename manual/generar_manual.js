// Genera Manual_Tecnico_UrbanJungle.docx a partir de manual/datos_manual.json (extraído de Odoo).
// Uso: NODE_PATH=<carpeta con node_modules> node manual/generar_manual.js
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, Header, Footer,
  AlignmentType, HeadingLevel, WidthType, ShadingType, BorderStyle, PageNumber, PageBreak,
  LevelFormat, ExternalHyperlink, VerticalAlign,
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const D = JSON.parse(fs.readFileSync(path.join(__dirname, "datos_manual.json"), "utf8"));
const VIDEO_URL = process.env.VIDEO_URL || "https://drive.google.com/file/d/1U9puodkh6hHJLbrxdnaB5DVH6SQKWzxX/view?usp=sharing";
const FONT = "Montserrat";
const VERDE = "1F6F50", VERDE_CLARO = "D7E8DD", TERRACOTA = "C97B2E";
const ANCHO = 9360; // carta con márgenes de 1"

const img = (rel) => fs.readFileSync(path.join(ROOT, rel));
const q = (n) => "Q" + Number(n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const pct = (n) => (n * 100).toFixed(1).replace(".0", "") + "%";

// ---------- Bloques básicos ----------
const run = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || 20, bold: o.bold, italics: o.italics, color: o.color, highlight: o.highlight });
const P = (content, o = {}) => new Paragraph({
  children: (Array.isArray(content) ? content : [content]).map((c) => (typeof c === "string" ? run(c, o) : c)),
  alignment: o.align || AlignmentType.JUSTIFIED, spacing: { after: o.after ?? 120, before: o.before ?? 0, line: 276 },
  keepNext: o.keepNext,
});
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: FONT, size: 30, bold: true, color: VERDE })], spacing: { before: 240, after: 160 }, keepNext: true, pageBreakBefore: true });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: FONT, size: 25, bold: true, color: VERDE })], spacing: { before: 200, after: 100 }, keepNext: true });
const bullet = (content) => new Paragraph({ numbering: { reference: "vinetas", level: 0 }, spacing: { after: 60, line: 276 },
  children: (Array.isArray(content) ? content : [content]).map((c) => (typeof c === "string" ? run(c) : c)) });
let listaNum = 0;
const pasos = (items) => { const ref = `pasos${listaNum++}`; NUMERACIONES.push(ref);
  return items.map((t) => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 60, line: 276 },
    children: (Array.isArray(t) ? t : [t]).map((c) => (typeof c === "string" ? run(c) : c)) })); };
const NUMERACIONES = [];
const salto = () => new Paragraph({ children: [new PageBreak()] });
const figura = (rel, w, h, pie, tipo = "png") => [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 }, keepNext: true,
    children: [new ImageRun({ type: tipo, data: img(rel), transformation: { width: w, height: h } })] }),
  P(pie, { align: AlignmentType.CENTER, italics: true, size: 19, color: "555555", after: 200 }),
];

// ---------- Tablas ----------
const borde = { style: BorderStyle.SINGLE, size: 4, color: "BFD6C8" };
const bordes = { top: borde, bottom: borde, left: borde, right: borde };
const celda = (contenido, ancho, o = {}) => new TableCell({
  borders: bordes, width: { size: ancho, type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
  shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
  margins: { top: 60, bottom: 60, left: 100, right: 100 },
  children: (Array.isArray(contenido) ? contenido : [contenido]).map((c) => (c instanceof Paragraph ? c :
    new Paragraph({ alignment: o.align || AlignmentType.LEFT, children: [typeof c === "string" || typeof c === "number" ?
      run(String(c), { size: o.size || 20, bold: o.bold, color: o.color }) : c] }))),
});
// Tabla con fila de encabezado verde
const tabla = (encabezados, filas, anchos, o = {}) => new Table({
  width: { size: ANCHO, type: WidthType.DXA }, columnWidths: anchos,
  rows: [
    new TableRow({ tableHeader: true, children: encabezados.map((h, i) => celda(h, anchos[i], { fill: VERDE, bold: true, color: "FFFFFF", size: o.size || 20 })) }),
    ...filas.map((f, r) => new TableRow({ cantSplit: true, children: f.map((v, i) => celda(v, anchos[i], {
      size: o.size || 20, fill: r % 2 ? "F4F8F5" : undefined, align: (o.derecha || []).includes(i) ? AlignmentType.RIGHT : AlignmentType.LEFT })) })),
  ],
});
// Tabla de dos columnas etiqueta / valor (estilo Fase 1)
const ficha = (pares, anchos = [2600, ANCHO - 2600]) => new Table({
  width: { size: ANCHO, type: WidthType.DXA }, columnWidths: anchos,
  rows: pares.map(([k, v]) => new TableRow({ cantSplit: true, children: [
    celda(k, anchos[0], { fill: VERDE_CLARO, bold: true, size: 19 }),
    celda(typeof v === "string" ? v : v, anchos[1], { size: 19 }) ] })),
});
const espacio = () => P("", { after: 80 });

// ---------- Contenido ----------
const K = D.kpi;
const kpis = [
  { nombre: "Ticket promedio de venta", objetivo: "Medir el valor promedio de cada pedido en línea. Mide el efecto de la venta cruzada (planta + maceta + sustrato o fertilizante) que la Fase 1 planteó como beneficio esperado del canal digital.",
    formula: "Ventas totales confirmadas (Q, IVA incluido) ÷ número de pedidos de venta confirmados del período.",
    fuente: "Ventas › Informes › Ventas (medidas «Total» y «# de pedidos»), filtrado por fecha de pedido.",
    frecuencia: "Mensual", meta: "≥ Q350.00 por pedido", base: q(K.ticket_promedio),
    smart: "Realista: sostiene la rentabilidad del canal digital sin abrir nuevos locales físicos." },
  { nombre: "Tasa de conversión del pipeline CRM", objetivo: "Medir qué proporción de las oportunidades gestionadas en el pipeline se convierte en clientes activos. Permite evaluar la efectividad del seguimiento comercial y de las campañas de correo.",
    formula: "Oportunidades en etapa «Ganado – Cliente activo» ÷ total de oportunidades del período × 100.",
    fuente: "CRM › Informes › Pipeline (agrupado por etapa) o vista Kanban del pipeline.",
    frecuencia: "Mensual", meta: "≥ 40%", base: pct(K.conversion),
    smart: "Medible: mide el avance hacia la meta de 150 clientes registrados en los primeros 3 meses." },
  { nombre: "Suscriptores activos de la Care Box", objetivo: "Dar seguimiento al modelo de ingresos recurrentes, principal diferenciador de UrbanJungle frente a la competencia informal.",
    formula: "Número de clientes con la etiqueta «Suscriptor Care Box» y pedido del producto UJ-P20 en el mes.",
    fuente: "Contactos (filtro por etiqueta) y Ventas › Informes › Ventas filtrado por el producto UJ-P20.",
    frecuencia: "Mensual", meta: "40 suscriptores activos al cierre del primer trimestre", base: `${K.suscriptores} suscriptores`,
    smart: "Medible y a tiempo: es la meta SMART de la Fase 1 (40 suscriptores en 3 meses)." },
  { nombre: "Tasa de recompra de clientes", objetivo: "Medir la fidelización: qué porcentaje de clientes vuelve a comprar. Orienta el uso de la plantilla de fidelización y del programa de referidos.",
    formula: "Clientes con 2 o más pedidos confirmados ÷ clientes con al menos 1 pedido × 100.",
    fuente: "Ventas › Pedidos agrupado por cliente (conteo de pedidos por cliente).",
    frecuencia: "Trimestral", meta: "≥ 45%", base: pct(K.recompra),
    smart: "Realista: reduce la dependencia de ventas puntuales estacionales." },
  { nombre: "Nivel de servicio (pedidos entregados completos)", objetivo: "Medir la disponibilidad de inventario: porcentaje de pedidos entregados completos sin faltantes. Su complemento es la tasa de quiebre de stock, que las reglas de reordenamiento buscan mantener cerca de cero.",
    formula: "Pedidos con todas sus entregas en estado «Hecho» sin pedidos pendientes ÷ total de pedidos × 100.",
    fuente: "Inventario › Operaciones › Entregas y Ventas › Pedidos (estado de entrega).",
    frecuencia: "Semanal", meta: "≥ 97% (quiebre de stock < 3%)", base: pct(K.nivel_servicio),
    smart: "Alcanzable: depende de la integración Ventas–Inventario–Compras implementada en Odoo." },
  { nombre: "Entregas a tiempo (≤ 48 horas)", objetivo: "Verificar el cumplimiento de la promesa logística de última milla de la Fase 1 (entregas en 24–48 h en el área metropolitana).",
    formula: "Entregas validadas dentro de las 48 h posteriores a la confirmación del pedido ÷ total de entregas × 100.",
    fuente: "Inventario › Entregas (fecha efectiva) comparada con la fecha del pedido de venta.",
    frecuencia: "Semanal", meta: "≥ 95%", base: pct(K.entregas_a_tiempo),
    smart: "Realista: la Fase 1 promete entregas en 24 a 48 horas y este KPI verifica si se cumple." },
];

const modulos = [
  ["Ventas", "ERP", "Cotizaciones y pedidos de venta de los 30 clientes; 50 ventas simuladas con IVA 12% incluido.", "Ticket promedio, recompra, suscriptores"],
  ["Inventario", "ERP / SCM", "Bodega Zona 15, existencias, entregas a clientes y 20 reglas de reordenamiento mín/máx.", "Nivel de servicio, entregas a tiempo"],
  ["Compras", "ERP / SCM", "20 proveedores con lista de precios por producto; solicitudes de cotización automáticas.", "Nivel de servicio (evita quiebres)"],
  ["CRM", "CRM", "Pipeline de 5 etapas con una oportunidad por cliente y plantillas de correo de marketing.", "Conversión, suscriptores"],
  ["Contactos", "Base común", "Ficha única de clientes (NIT, empleador, etiqueta) y proveedores, compartida por todos los módulos.", "Todos"],
  ["Contabilidad / Facturación", "ERP", "Moneda GTQ, impuesto IVA 12% en ventas y compras, valoración del inventario.", "Ticket promedio (montos)"],
  ["Conversaciones (Discuss) y Correo", "CRM", "Motor de envío de las plantillas de correo y del historial (chatter) de cada registro.", "Recompra, conversión"],
];

const portada = [
  P("Universidad de San Carlos de Guatemala", { align: AlignmentType.LEFT, after: 0 }),
  P("Facultad de Ingeniería, Escuela de Ciencias y Sistemas", { align: AlignmentType.LEFT, after: 0 }),
  P("Sistemas Organizacionales y Gerenciales 1", { align: AlignmentType.LEFT, after: 0 }),
  P("Catedrático: Edwin Estuardo Zapeta Gómez", { align: AlignmentType.LEFT, after: 0 }),
  P("Auxiliar: Josue Daniel Solís Osorio", { align: AlignmentType.LEFT, after: 600 }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 300 },
    children: [new ImageRun({ type: "png", data: img("assets/logo_urbanjungle.png"), transformation: { width: 420, height: 121 } })] }),
  P([run("Proyecto Fase 2: Integración de Soluciones Empresariales (ERP, SCM y CRM) con Odoo", { bold: true, size: 26 })], { align: AlignmentType.CENTER, after: 200 }),
  P([run("MANUAL TÉCNICO", { bold: true, size: 44, color: VERDE })], { align: AlignmentType.CENTER, after: 100 }),
  P([run("UrbanJungle – Vivero El Jardín Urbano", { size: 28, color: TERRACOTA })], { align: AlignmentType.CENTER, after: 600 }),
  P([run("Grupo No. 3", { bold: true, size: 24 })], { align: AlignmentType.CENTER, after: 120 }),
  ...[["Hernán Ricardo Ávila Castillo", "9516085"], ["Sebastián Gómez Lavarreda", "201602929"],
      ["Rodrigo Alejandro Tahuite Soria", "202202854"]].map(([n, c]) => P(`${n}, carné ${c}`, { align: AlignmentType.CENTER, after: 40 })),
  P("", { after: 600 }),
  P("Guatemala, 2 de octubre de 2026", { align: AlignmentType.CENTER }),
];

const indice = [
  H1("Contenido"),
  ...["Introducción y datos de la instalación", "Indicadores de rendimiento (KPI)",
      "Módulos de Odoo implementados y relación con los objetivos SMART", "Implementación ERP: productos, proveedores, clientes, ventas e inventario dinámico",
      "Gestión de relaciones con los clientes (CRM): pipeline y plantillas de correo", "Video tutorial",
      "Guía rápida de operación en Odoo", "Créditos de imágenes"].map((t) => P(t, { align: AlignmentType.LEFT, after: 80 })),
];

const seccionIntro = [
  H1("Introducción y datos de la instalación"),
  H2("Objetivo del manual"),
  P("Este manual técnico documenta la implementación de la plataforma modular Odoo para UrbanJungle, la propuesta de transformación digital de Vivero El Jardín Urbano presentada en la Fase 1. Define los indicadores de rendimiento (KPI) con los que se medirá el éxito del canal digital y describe los módulos ERP, SCM y CRM configurados, los datos cargados y los procedimientos de operación para el personal del vivero."),
  P("La implementación simula la cadena de suministro completa: carga masiva del catálogo desde Excel, registro de proveedores y clientes, 50 ventas con su entrega, reglas de reordenamiento que generan automáticamente solicitudes de cotización a los proveedores, un pipeline comercial y plantillas de correo de marketing."),
  H2("Datos de la instancia"),
  ficha([
    ["URL de acceso", D.url],
    ["Base de datos", "usac"],
    ["Edición y versión", "Odoo Online (SaaS) Enterprise, serie 19.4"],
    ["Empresa", D.empresa],
    ["Moneda e impuestos", "Quetzal (GTQ); IVA 12% incluido en precios de venta y compra"],
    ["Almacén", "UrbanJungle – Bodega Zona 15 (recepción y entrega en 1 paso)"],
    ["Idioma / zona horaria", "Español (Latinoamérica) / America/Guatemala"],
    ["Usuarios internos", "Hernán Ávila, Rodrigo Tahuite y Sebastián Gómez (administradores)"],
  ]),
  espacio(),
  H2("Resumen de lo implementado"),
  tabla(["Requisito del enunciado", "Implementado en Odoo"], [
    ["20 productos cargados desde Excel", `${D.productos.length} productos importados desde Productos.xlsx con tipo, nombre, imagen, precio, costo, categoría y código de barras EAN-13`],
    ["Mínimo 20 proveedores, cada uno con ≥ 3 productos", `${D.proveedores.length} proveedores; ${D.proveedores.reduce((a, p) => a + p.productos.length, 0)} relaciones entre proveedor y producto (mínimo ${Math.min(...D.proveedores.map((p) => p.productos.length))} por proveedor)`],
    ["Mínimo 30 clientes con nombre, teléfono, dirección y NIT", `${D.clientes.length} clientes con nombre, teléfono, dirección, NIT, empleador y etiqueta de clasificación`],
    ["50 ventas registradas con entrega", `${D.ventas.cantidad} pedidos confirmados de ${D.ventas.clientes} clientes (${D.ventas.desde} a ${D.ventas.hasta}), total ${q(D.ventas.total)}, entregas validadas`],
    ["Reordenamiento con cotización automática", `${D.productos.filter((p) => p.minimo).length} reglas mín/máx; ${D.compras.length} solicitudes de cotización generadas automáticamente`],
    ["Pipeline CRM", `${D.pipeline.length} etapas; ${D.pipeline.reduce((a, e) => a + e.cantidad, 0)} oportunidades (una por cliente)`],
    ["Dos plantillas de correo", D.plantillas.join("; ")],
  ], [3300, 6060]),
];

const seccionKpis = [
  H1("Indicadores de rendimiento (KPI)"),
  P("Se definieron seis KPIs ligados a los objetivos estratégicos y operativos de UrbanJungle. Todos se calculan con información que ya registra Odoo, sin hojas de cálculo paralelas. La «línea base» corresponde a los datos simulados de septiembre de 2026 cargados en la instancia y es el punto de partida para medir el avance hacia la meta."),
  tabla(["#", "KPI", "Frecuencia", "Meta", "Línea base (sep-2026)"],
    kpis.map((k, i) => [String(i + 1), k.nombre, k.frecuencia, k.meta, k.base]), [450, 3400, 1300, 2410, 1800]),
  espacio(),
  ...kpis.flatMap((k, i) => [
    H2(k.nombre),
    ficha([["Nombre del KPI", k.nombre], ["Objetivo", k.objetivo], ["Fórmula", k.formula], ["Fuente en Odoo", k.fuente],
           ["Frecuencia de medición", k.frecuencia], ["Meta o valor objetivo", k.meta], ["Línea base", k.base], ["Relación con el SMART", k.smart]]),
    espacio(),
  ]),
];

const seccionModulos = [
  H1("Módulos de Odoo implementados"),
  P("UrbanJungle utiliza Odoo como un sistema único: el mismo registro de cliente, producto o proveedor fluye entre el CRM, las ventas, el inventario y las compras. Los módulos implementados son:"),
  tabla(["Módulo", "Tipo", "Uso en UrbanJungle", "KPIs que alimenta"], modulos, [1900, 1100, 4160, 2200]),
  espacio(),
  ...figura("assets/flujo_odoo.png", 600, 240, "Figura 1. Flujo integrado de información entre los módulos de Odoo."),
  H2("Relación con los objetivos SMART de la Fase 1"),
  ficha([
    ["Específico", "La Fase 1 planteó lanzar UrbanJungle con catálogo, carrito, checkout y suscripción mensual. En Odoo, Ventas e Inventario modelan el catálogo de 20 productos (incluida la Care Box de suscripción) y el ciclo pedido–entrega."],
    ["Medible", "La meta de 150 clientes registrados y 40 suscriptores se mide en Contactos y CRM (etiquetas y pipeline); los KPIs 2 y 3 la siguen mes a mes."],
    ["Alcanzable", "Compras y las reglas de reordenamiento automatizan el abastecimiento con los proveedores existentes del vivero y reducen el trabajo manual que hoy se hace por WhatsApp."],
    ["Realista", "La integración elimina el inventario desincronizado entre tienda física y redes (problema del diagnóstico de la Fase 1) y permite crecer sin abrir nuevos locales."],
    ["A tiempo", "Los KPIs tienen frecuencia semanal o mensual para dar seguimiento al plan de 24 semanas y a la meta del primer trimestre posterior al lanzamiento."],
  ]),
];

const credMap = JSON.parse(fs.readFileSync(path.join(ROOT, "assets/productos/creditos.json"), "utf8"));
const seccionErp = [
  H1("Implementación ERP"),
  H2("Configuración inicial"),
  ...[
    "Se instaló el módulo CRM (Ventas, Inventario, Compras y Contabilidad ya estaban activos).",
    "Se renombró la compañía a «UrbanJungle – Vivero El Jardín Urbano», con logotipo, dirección en zona 15 y datos de contacto, que aparecen en cotizaciones, órdenes de compra y correos.",
    "Se renombró el almacén a «UrbanJungle – Bodega Zona 15»; la ruta «Comprar» está activa para reabastecer el almacén.",
    "Se creó la jerarquía de categorías «UrbanJungle / …» (Plantas de Interior, Suculentas y Cactus, Macetas y Colgantes, Sustratos y Fertilizantes, Herramientas y Accesorios, Suscripciones).",
    "Se agregó al formulario de contacto el campo «Empleador» para registrar la empresa donde labora cada cliente sin perder su NIT individual.",
  ].map(bullet),
  H2("Carga masiva de productos (Productos.xlsx)"),
  P("El archivo Productos.xlsx contiene los 20 productos de la propuesta de negocio. Sus encabezados coinciden con las etiquetas de Odoo, por lo que el importador asigna las columnas automáticamente:"),
  tabla(["Columna del Excel", "Campo de Odoo", "Descripción"], [
    ["Referencia interna", "default_code", "Código UJ-P01 … UJ-P20"],
    ["Nombre", "name", "Nombre comercial del producto"],
    ["Tipo de producto", "type", "«Bienes» (producto físico)"],
    ["Rastrear inventario", "is_storable", "VERDADERO: Odoo controla existencias y permite reglas de reorden"],
    ["Categoría del producto", "categ_id", "Ruta completa, p. ej. «UrbanJungle / Plantas de Interior»"],
    ["Precio de venta / Costo", "list_price / standard_price", "En quetzales, IVA incluido"],
    ["Código de barras", "barcode", "EAN-13 con prefijo GS1 de Guatemala (740) y dígito verificador"],
    ["Imagen", "image_1920", "URL pública de la imagen; Odoo la descarga al importar"],
  ], [2500, 2500, 4360]),
  P("Pasos de importación: Inventario › Productos › Productos › Acciones (ícono de engranaje) › Importar registros › Cargar archivo › seleccionar Productos.xlsx › verificar el mapeo de columnas (la columna «Vista previa» se deja sin importar) › Probar › Importar.", { before: 120 }),
  tabla(["Ref.", "Producto", "Categoría", "Precio", "Costo", "Código de barras"],
    D.productos.map((p) => [p.ref, p.nombre, p.categoria, q(p.precio), q(p.costo), p.barcode]),
    [900, 3060, 1900, 1000, 900, 1600], { size: 18, derecha: [3, 4] }),
  H2("Proveedores y productos que surten"),
  P(`Se registraron ${D.proveedores.length} proveedores únicos (empresas guatemaltecas simuladas) con NIT, teléfono, correo, dirección y etiqueta por rubro. Cada proveedor está vinculado a por lo menos tres productos distintos en la pestaña «Compra» del producto, con su precio de compra y plazo de entrega. La relación es lógica: los viveros surten plantas, los alfareros y artesanos surten macetas y colgantes, los agroservicios surten sustratos y fertilizantes, y la ferretería y la empresa de empaques surten herramientas y la Care Box.`),
  tabla(["#", "Proveedor", "NIT", "Ciudad", "Productos que surte"],
    D.proveedores.map((p, i) => [String(i + 1), p.nombre, p.nit, p.ciudad, p.productos.join("; ")]),
    [400, 2500, 1100, 1400, 3960], { size: 17 }),
  H2("Clientes"),
  P(`Se registraron ${D.clientes.length} clientes personas individuales del área metropolitana con nombre completo, teléfono, dirección, NIT, empleador y una etiqueta de clasificación (Cliente Nuevo, Ocasional, Frecuente, VIP o Suscriptor Care Box) que se usa para segmentar campañas y priorizar el pipeline.`),
  tabla(["Cliente", "NIT", "Teléfono", "Dirección", "Empleador", "Etiqueta"],
    D.clientes.map((c) => [c.nombre, c.nit, c.telefono, c.direccion, c.empleador, c.etiqueta]),
    [1900, 1000, 1250, 2160, 1750, 1300], { size: 16 }),
  H2("Ventas y entregas"),
  P(`Se registraron ${D.ventas.cantidad} pedidos de venta de ${D.ventas.clientes} clientes distintos entre el ${D.ventas.desde} y el ${D.ventas.hasta}, con ${D.ventas.lineas} líneas de producto y un total de ${q(D.ventas.total)}. Cada cliente compró al menos una vez y los clientes frecuentes, VIP y suscriptores repitieron compra; los suscriptores incluyen siempre la Care Box. Cada pedido se confirmó y su entrega (WH/OUT) se validó con fecha del día siguiente a la compra, que es el plazo de despacho de la flota de última milla.`),
  P(`Los productos más vendidos, en unidades, fueron ${D.ventas.top.map(([n, u]) => `${n} (${u})`).join("; ")}.`),
  H2("Inventario dinámico: reglas de reordenamiento"),
  P("Cada producto tiene una regla de reordenamiento mín/máx en WH/Stock con la ruta «Comprar» y disparo automático. Cuando el stock pronosticado cae por debajo del mínimo (por ejemplo, al confirmar o entregar una venta), Odoo crea automáticamente una solicitud de cotización al proveedor configurado del producto por la cantidad necesaria para llegar al máximo. Si ya existe una solicitud en borrador para el mismo proveedor, agrega la línea a esa misma solicitud."),
  tabla(["Ref.", "Producto", "Mín.", "Máx.", "Existencia", "Pronóstico"],
    D.productos.map((p) => [p.ref, p.nombre, String(p.minimo ?? "-"), String(p.maximo ?? "-"), String(p.existencia), String(p.pronostico ?? "-")]),
    [900, 4060, 800, 800, 1400, 1400], { size: 18, derecha: [2, 3, 4, 5] }),
  P("Solicitudes de cotización generadas automáticamente por las reglas durante la simulación de ventas:", { before: 160, keepNext: true }),
  tabla(["Documento", "Proveedor", "Origen (regla)", "Productos y cantidades", "Total"],
    D.compras.map((c) => [c.nombre, c.proveedor, c.origen || "-", c.lineas.join("; "), q(c.total)]),
    [1100, 2400, 1500, 3160, 1200], { size: 18, derecha: [4] }),
];

const seccionCrm = [
  H1("Gestión de relaciones con los clientes (CRM)"),
  H2("Pipeline comercial"),
  P("Se configuró el equipo «Ventas en línea UrbanJungle» con un pipeline de cinco etapas. Cada uno de los 30 clientes tiene una oportunidad con un estado simulado según su clasificación, ingreso esperado, prioridad (estrellas), vendedor responsable y etiquetas (Suscripción, Venta cruzada, Corporativo, Recompra, Primera compra)."),
  tabla(["Etapa", "Criterio de asignación (simulado)", "Oportunidades"], D.pipeline.map((e) => [e.etapa, ({
    "Nuevo prospecto": "Cliente nuevo: primera compra, bienvenida a la marca",
    "Contactado": "Cliente ocasional: campaña de reactivación con kit de cuidado",
    "Cotización enviada": "Cliente frecuente con cotización de recompra trimestral pendiente",
    "Negociación": "Cliente VIP: proyecto de ambientación con plantas para su empresa",
    "Ganado – Cliente activo": "Suscriptores de la Care Box y clientes frecuentes con recompra cerrada",
  })[e.etapa] || "-", String(e.cantidad)]), [2400, 5560, 1400], { derecha: [2] }),
  H2("Plantillas de correo electrónico"),
  P("Se crearon dos plantillas en el modelo Oportunidad del CRM, con diseño HTML adaptable, logotipo y nombre de UrbanJungle, un banner con la imagen de la campaña y el nombre del cliente insertado dinámicamente. Se usan desde una oportunidad con el botón «Enviar correo» › seleccionar plantilla, o en lote, al seleccionar varias oportunidades en la vista de lista."),
  P("La plantilla de promoción especial, «Semana Urban Jungle», anuncia 20% de descuento en plantas de interior con el código JUNGLA20 y envío gratis en compras mayores a Q300. Tiene un botón «Ver plantas en oferta»."),
  ...figura("assets/banner_promocion.png", 470, 172, "Figura 2. Banner de la plantilla de promoción especial."),
  P("La plantilla de fidelización, «Gracias por crecer con nosotros», va dirigida a clientes frecuentes y suscriptores. Agradece su preferencia, recuerda la preparación de la próxima Care Box y ofrece un atomizador de regalo en la siguiente compra. Tiene un botón «Gestionar mi suscripción»."),
  ...figura("assets/banner_fidelizacion.png", 470, 172, "Figura 3. Banner de la plantilla de fidelización."),
];

const enlaceVideo = new ExternalHyperlink({ link: VIDEO_URL, children: [new TextRun({ text: VIDEO_URL, font: FONT, size: 22, style: "Hyperlink" })] });
const seccionVideo = [
  H1("Video tutorial"),
  P(["El video está en ", enlaceVideo, "."], { align: AlignmentType.LEFT }),
  P("El video demuestra, en la instancia de UrbanJungle, el proceso completo solicitado:"),
  ...pasos([
    "Agregar un nuevo cliente (nombre, teléfono, dirección, NIT, empleador y etiqueta).",
    "Agregar un nuevo proveedor (empresa, NIT, contacto y dirección).",
    "Agregar un nuevo producto almacenable con imagen, precio, costo, categoría, código de barras y el proveedor en la pestaña «Compra».",
    "Crear la regla de reordenamiento del producto (mínimo y máximo) y demostrar que, al bajar el stock por debajo del mínimo, Odoo genera automáticamente la solicitud de cotización al proveedor.",
  ]),
];

const seccionGuia = [
  H1("Guía rápida de operación en Odoo"),
  H2("Crear un cliente"),
  ...pasos(["Contactos › Nuevo.", "Seleccionar «Persona» y escribir el nombre completo.",
    "Completar dirección (calle, ciudad, departamento, país Guatemala), teléfono, correo, NIT, Empleador y Etiquetas (p. ej. «Cliente» + «Cliente Nuevo»).", "Guardar."]),
  H2("Crear un proveedor"),
  ...pasos(["Compras › Pedidos › Proveedores › Nuevo.", "Seleccionar «Empresa», escribir la razón social y completar NIT, dirección, teléfono y correo.",
    "Agregar las etiquetas «Proveedor» y «Proveedor de …» según el rubro.", "Guardar."]),
  H2("Crear un producto y vincular su proveedor"),
  ...pasos(["Inventario › Productos › Productos › Nuevo.", "Escribir el nombre, cargar la imagen, Tipo «Bienes» y activar «Rastrear inventario».",
    "Registrar precio de venta, costo, categoría, referencia interna y código de barras.",
    "Pestaña «Compra»: agregar el proveedor con su precio y plazo de entrega (se pueden agregar varios; el primero es el preferido).", "Guardar."]),
  H2("Crear una regla de reordenamiento"),
  ...pasos(["Desde el producto: botón inteligente «Mín/Máx» (o Inventario › Operaciones › Reabastecimiento) › Nuevo.",
    "Seleccionar almacén y ubicación WH/Stock, cantidad mínima y cantidad máxima, ruta «Comprar» y activador «Auto».", "Guardar."]),
  H2("Comprobar la cotización automática"),
  ...pasos(["Crear y confirmar un pedido de venta (Ventas › Nuevo) que deje el stock del producto por debajo del mínimo, o ajustar la existencia en Inventario › Productos › «Disponible».",
    "Si la solicitud no aparece de inmediato, ejecutar Inventario › Operaciones › Reabastecimiento › «Pedir» (o «Ejecutar planificador»).",
    "Ir a Compras › Solicitudes de cotización: aparece la solicitud en borrador al proveedor del producto, con origen OP/xxxxx (la regla), por la cantidad necesaria para llegar al máximo.",
    "Confirmar el pedido de compra y validar la recepción para reponer el inventario."]),
  H2("Registrar una venta y su entrega"),
  ...pasos(["Ventas › Pedidos › Nuevo: seleccionar el cliente y agregar productos.", "Confirmar: se genera la entrega WH/OUT.",
    "Botón «Entrega» › Validar: el stock disminuye y se actualiza el pronóstico de las reglas de reordenamiento."]),
  H2("Enviar una plantilla de correo"),
  ...pasos(["CRM › abrir una oportunidad › «Enviar mensaje» › ícono de expandir (redactor completo).",
    "En «Cargar plantilla» elegir la plantilla de Promoción o de Fidelización; revisar la vista previa y Enviar."]),
];

const seccionCreditos = [
  H1("Créditos de imágenes"),
  P("El logotipo, los banners, la imagen de la Care Box y el diagrama de flujo fueron diseñados por el equipo. Las fotografías de productos provienen de Wikimedia Commons bajo licencias libres:"),
  tabla(["Ref.", "Archivo en Wikimedia Commons", "Autor", "Licencia"],
    Object.entries(credMap).map(([k, c]) => [`UJ-${k}`, c.title.replace("File:", ""), (c.author || "No indicado").slice(0, 60), c.license || "No indicada"]),
    [800, 4260, 2700, 1600], { size: 16 }),
];

const doc = new Document({
  creator: "Grupo 3, SOG1", title: "Manual Técnico UrbanJungle, Fase 2",
  // Montserrat (OFL) va incrustada para que el .docx se vea igual en equipos sin la fuente instalada
  fonts: [{ name: FONT, data: img("assets/fonts/Montserrat-Regular.ttf") }],
  styles: { default: { document: { run: { font: FONT, size: 20 } } } },
  numbering: { config: [
    { reference: "vinetas", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    ...Array.from({ length: 20 }, (_, i) => ({ reference: `pasos${i}`, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 300 } } } }] })),
  ] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1300, bottom: 1200, left: 1440, right: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [run("UrbanJungle · Manual Técnico · SOG1", { size: 17, color: "777777" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
      new TextRun({ font: FONT, size: 18, color: "777777", children: ["Página ", PageNumber.CURRENT] })] })] }) },
    children: [...portada, ...indice, ...seccionIntro, ...seccionKpis, ...seccionModulos, ...seccionErp, ...seccionCrm, ...seccionVideo, ...seccionGuia, ...seccionCreditos],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  const salida = path.join(ROOT, "Manual_Tecnico_UrbanJungle.docx");
  fs.writeFileSync(salida, buf);
  console.log("Generado:", salida);
});
