// Genera Informe_Ejecutivo_Fase3_UrbanJungle.docx con los datos de manual/datos_fase3.json (extraídos de Odoo).
// Uso: NODE_PATH=<carpeta con node_modules> node manual/generar_informe_fase3.js
const fs = require("fs");
const path = require("path");
const B = require("./base");
const { P, H1, H2, q, pct, run, bullet, figura, tabla, ficha, espacio, AlignmentType } = B;

const D = JSON.parse(fs.readFileSync(path.join(__dirname, "datos_fase3.json"), "utf8"));
const K = D.kpi, C = D.contexto, M = D.meses;
const cap = fs.existsSync(path.join(B.ROOT, "assets/capturas/10_tablero_bi.jpg"));
const nombreMes = { "2026-07": "Julio", "2026-08": "Agosto", "2026-09": "Septiembre", "2026-10": "Octubre (1 al 13)" };
const lista = (xs) => xs.length > 1 ? xs.slice(0, -1).join(", ") + " y " + xs[xs.length - 1] : xs[0];

const kpis = [
  ["Ticket promedio de venta", q(K.ticket_promedio), "≥ Q350.00", K.ticket_promedio >= 350],
  ["Tasa de conversión del pipeline CRM", pct(K.conversion), "≥ 40%", K.conversion >= 0.4],
  ["Suscriptores activos de la Care Box", String(K.suscriptores), "40 al cierre del primer trimestre", K.suscriptores >= 40],
  ["Tasa de recompra de clientes", pct(K.recompra), "≥ 45%", K.recompra >= 0.45],
  ["Nivel de servicio (pedidos entregados completos)", pct(K.nivel_servicio), "≥ 97%", K.nivel_servicio >= 0.97],
  ["Entregas a tiempo (≤ 48 horas)", pct(K.entregas_a_tiempo), "≥ 95%", K.entregas_a_tiempo >= 0.95],
];
const cumplidos = kpis.filter((k) => k[3]).map((k) => k[0].toLowerCase());
const pendientes = kpis.filter((k) => !k[3]).map((k) => k[0].toLowerCase());

const hijos = [
  ...B.portada("INFORME EJECUTIVO", "UrbanJungle – Vivero El Jardín Urbano", "Guatemala, 17 de octubre de 2026"),

  H1("Resumen ejecutivo"),
  P(`UrbanJungle es la tienda en línea de Vivero El Jardín Urbano. En la Fase 3 se publicó el sitio de comercio electrónico sobre la misma instancia de Odoo que ya tenía Ventas, Inventario, Compras y CRM desde la Fase 2, de modo que cada pedido web llega como cotización o venta al mismo flujo de entrega y reabastecimiento. El catálogo en línea tiene ${C.productos} productos y el sitio permite registrarse, armar el carrito y pagar por transferencia o contra entrega.`),
  P(`Entre julio y el 13 de octubre de 2026 hay ${C.ventas} ventas confirmadas por ${q(C.ingresos)}. De ellas, ${C.ventas_web} entraron por la tienda en línea en sus primeras dos semanas (${q(C.ingresos_web)}), y ${C.clientes_web} clientes nuevos se registraron desde el sitio. Los datos son simulados para el proyecto, cargados en Odoo con los mismos procesos que usaría el vivero.`),
  P(`De los seis KPI definidos en la Fase 2 se cumplen ${cumplidos.length}: ${lista(cumplidos)}. No se alcanzan ${lista(pendientes)}. La suscripción Care Box es el producto más vendido y sus suscriptores son los clientes que más compran, pero con ${K.suscriptores} suscriptores la meta de 40 está lejos y es la prioridad comercial del siguiente trimestre.`),

  H1("Análisis de inteligencia de negocio"),
  P(`El análisis usa el tablero "UrbanJungle BI" de Odoo Tableros, en ${D.url}, dentro del grupo Ventas. El tablero se calcula con fórmulas y gráficos conectados a los modelos de Odoo (pedidos de venta, reporte de ventas, existencias, contactos y oportunidades), así que se actualiza con cada pedido nuevo. Los gráficos de este informe salen de los mismos datos con corte al 14 de octubre de 2026.`),
  ...(cap ? B.figura("assets/capturas/10_tablero_bi.jpg", 600, 338, "Figura 1. Tablero UrbanJungle BI en Odoo Tableros.") : []),
  H2("Métricas de contexto"),
  tabla(["Métrica", "Valor", "Detalle"], [
    ["Ingresos totales históricos", q(C.ingresos), `${q(C.ingresos_web)} por la tienda en línea`],
    ["Número de ventas históricas", String(C.ventas), `${C.ventas_web} por la tienda en línea y ${C.cotizaciones_web} cotizaciones web abiertas`],
    ["Clientes totales", String(C.clientes), `${C.clientes_web} registrados desde el sitio`],
    ["Proveedores totales", String(C.proveedores), `${C.compras} órdenes de compra por ${q(C.compras_total)} generadas por las reglas de reordenamiento`],
  ], [3000, 1800, 4560]),
  H2("KPI de la Fase 2 frente a su meta"),
  tabla(["KPI", "Valor actual", "Meta", "Estado"], kpis.map((k) => [k[0], k[1], k[2], k[3] ? "Cumple" : "No cumple"]), [3700, 1500, 2500, 1660]),
  P(`El ticket promedio de ${q(K.ticket_promedio)} queda ${q(350 - K.ticket_promedio)} por debajo de la meta. La mayoría de pedidos lleva una sola planta y a lo sumo un complemento, por eso el sitio sugiere maceta, sustrato y fertilizante en el carrito de cada planta. La conversión del pipeline es ${pct(K.conversion)}: de las oportunidades del CRM, las ganadas son los suscriptores y parte de los clientes frecuentes; los clientes nuevos y ocasionales siguen en las primeras etapas.`, { before: 120 }),
  P(`La recompra de ${pct(K.recompra)} supera la meta porque la Care Box se compra cada mes y porque los clientes frecuentes y VIP repiten. El nivel de servicio y las entregas a tiempo están en ${pct(K.nivel_servicio)}: ninguna entrega quedó pendiente por falta de stock, ya que las reglas de reordenamiento pidieron a los proveedores antes de que el inventario se agotara.`),

  H2("Evolución de ventas"),
  ...figura("assets/bi/ventas_semana.png", 600, 267, "Figura 2. Ventas semanales en quetzales, del 1 de julio al 13 de octubre de 2026."),
  tabla(["Mes", "Ventas", "Ingresos"], Object.entries(M).map(([m, v]) => [nombreMes[m] || m, String(v.ventas), q(v.ingresos)]), [3600, 2400, 3360], { derecha: [1, 2] }),
  P(`Julio y agosto tienen ventas bajas y estables, todas anteriores al sitio web. Septiembre multiplica por 2.5 los ingresos de agosto con la puesta en marcha del ERP y el CRM, y la semana más alta del período es la que empieza el 21 de septiembre. En octubre todas las ventas registradas entraron por el sitio web: ${M["2026-10"] ? M["2026-10"].ventas : 0} pedidos en 13 días, un ritmo parecido al de septiembre. La última semana del gráfico solo tiene dos días y no indica una caída.`, { before: 120 }),

  H2("Existencias por producto"),
  ...figura("assets/bi/existencias.png", 560, 560, "Figura 3. Existencias actuales por producto en la bodega de zona 15."),
  P(`Ningún producto está bajo su mínimo. Las existencias van de ${Math.min(...D.existencias.map((e) => e[2]))} a ${Math.max(...D.existencias.map((e) => e[2]))} unidades porque las reglas de reordenamiento reponen hasta el máximo de cada producto. Los que tienen más unidades son el Aloe Vera, el Pothos y el fertilizante. El Aloe Vera entró con 28 unidades en agosto y solo vendió 2, así que antes de reponerlo conviene esperar a que baje su inventario.`),

  H2("Productos más y menos vendidos"),
  ...figura("assets/bi/top5_mas.png", 560, 250, "Figura 4. Los 5 productos con más unidades vendidas."),
  ...figura("assets/bi/top5_menos.png", 560, 250, "Figura 5. Los 5 productos con menos unidades vendidas entre los que tienen ventas."),
  P(`La Care Box lidera con ${D.top5[0][1]} unidades, casi el doble que el segundo producto. Entre los demás destacan accesorios de bajo precio y plantas de tamaño mediano. Los cinco menos vendidos son productos que entraron al catálogo en agosto y octubre, por lo que tienen menos tiempo a la venta. Además, ${lista(D.sin_ventas)} no registran ventas; conviene revisar su precio y mostrarlos en la portada o como regalo antes de comprar más inventario de ellos.`),

  H2("Clientes con más compras"),
  ...figura("assets/bi/top5_clientes.png", 560, 250, "Figura 6. Los 5 clientes con mayor monto comprado."),
  P(`Los cinco clientes con más compras son suscriptores de la Care Box. Suman ${q(D.top_clientes.reduce((a, c) => a + c[1], 0))}, el ${pct(D.top_clientes.reduce((a, c) => a + c[1], 0) / C.ingresos)} de los ingresos del período, con entre ${Math.min(...D.top_clientes.map((c) => c[2]))} y ${Math.max(...D.top_clientes.map((c) => c[2]))} pedidos cada uno. La suscripción concentra a los clientes de mayor valor, y cada suscriptor nuevo aporta ingresos todos los meses.`),

  H2("Decisiones propuestas"),
  bullet("Llevar la suscripción de 6 a 40 suscriptores con la plantilla de correo de fidelización a clientes frecuentes y VIP, y ofrecer el primer mes de la Care Box a quien se registre en el sitio."),
  bullet("Subir el ticket promedio hacia Q350 con paquetes de planta, maceta y sustrato a precio cerrado, además de los accesorios sugeridos que ya muestra el carrito."),
  bullet(`Pausar la recompra de ${lista(D.sin_ventas)} hasta probar una promoción, y mantener el resto del catálogo con las reglas de reordenamiento actuales.`),
  bullet("Mover a los clientes ocasionales del pipeline con la campaña de reactivación y medir la conversión cada mes."),

  H1("Escalabilidad y mantenimiento"),
  P("El plan parte de la configuración actual: una sola empresa, una bodega en zona 15, Odoo Online con Ventas, Inventario, Compras, CRM, Sitio web y Contabilidad, y entregas en el área metropolitana."),
  H2("Escenario 1: ampliación del catálogo con nuevas líneas"),
  P("UrbanJungle pasaría de 30 a cerca de 100 productos con tres líneas nuevas: plantas de exterior para balcones, macetas artesanales de proveedores de Totonicapán y Chinautla, y kits corporativos para oficinas. En Odoo esto requiere nuevas categorías internas y de tienda, variantes de producto para tamaños y colores, reglas de reordenamiento para cada producto y nuevos proveedores con su lista de precios. La carga se hace igual que en la Fase 2, con un Excel de importación. El límite práctico es la bodega: antes de ampliar hay que medir el espacio libre y la rotación, porque las plantas vivas no aguantan mucho tiempo almacenadas."),
  H2("Escenario 2: nuevas pasarelas de pago"),
  P("Hoy el sitio cobra por transferencia bancaria y contra entrega, dos métodos que no necesitan pasarela. El siguiente paso es el pago con tarjeta en línea, que además permite el cobro automático de la Care Box. Odoo trae conectores para pasarelas internacionales como PayPal y Stripe, que se activan desde Contabilidad; antes hay que confirmar cuál acepta comercios de Guatemala y sus comisiones. Una pasarela local que no esté en la lista de Odoo necesita un módulo propio, y Odoo Online no permite instalar módulos propios, así que ese caso implica pasar a Odoo.sh."),
  H2("Escenario 3: expansión a nuevos territorios"),
  P("La expansión empieza por cabeceras cercanas, como Antigua Guatemala y Quetzaltenango, con mensajería tercerizada y costo de envío por zona configurado en los métodos de entrega de Odoo. Una segunda etapa sería El Salvador, que exige precios en dólares (Odoo maneja varias monedas y listas de precios), impuestos del otro país, el sitio en una segunda lista de precios y un aliado logístico que pueda transportar plantas vivas entre países. Este escenario tiene sentido cuando las ventas web del área metropolitana se mantengan por varios meses."),
  H2("Recursos operacionales"),
  ficha([
    ["Infraestructura tecnológica", "Odoo Online incluye el servidor, la base de datos, las copias de seguridad y las actualizaciones de versión. Hace falta un dominio propio (urbanjungle.gt) apuntado al sitio, correo del dominio para enviar las plantillas y una conexión estable en la bodega. Si el volumen crece mucho o se necesitan módulos propios, la opción es Odoo.sh, donde se pueden agregar procesos de servidor."],
    ["Roles y equipos de soporte", "Un administrador de Odoo (usuarios, permisos, configuración y respaldos), un responsable de la tienda en línea (catálogo, precios, fotos y contenido), un responsable de logística (entregas, recepciones y reglas de reordenamiento) y soporte de primer nivel para clientes por teléfono y correo. Al inicio los tres integrantes del proyecto pueden cubrir estos roles."],
    ["Protocolos de actualización y seguridad", "Antes de cada cambio de versión, Odoo permite probar en una copia de la base de datos; se revisan la tienda, el carrito, el checkout y el tablero antes de aplicar. Las cuentas internas usan doble factor de autenticación, permisos por app según el rol y contraseñas propias. Las claves API tienen vencimiento y alcance limitado, y se revocan al terminar cada carga de datos."],
  ]),
  espacio(),
  H2("Riesgos y medidas de mitigación"),
  tabla(["Riesgo", "Efecto", "Medida preventiva"], [
    ["Sobrecarga del servidor en campañas", "El sitio se vuelve lento o no carga durante una promoción", "Imágenes optimizadas, catálogo paginado y pruebas antes de cada campaña. Si el tráfico sostenido supera lo que soporta el plan, migrar a Odoo.sh con más procesos de servidor."],
    ["Aumento incontrolado de costos operativos", "Las licencias por usuario, las comisiones de pasarela y el envío suben más rápido que las ventas", "Revisar cada mes el costo por pedido frente al ticket promedio, agregar usuarios solo cuando un rol lo requiera y cobrar el envío fuera del área metropolitana."],
    ["Seguridad de la información", "Exposición de datos personales y NIT de clientes o acceso indebido al ERP", "Doble factor en usuarios internos, permisos mínimos por rol, pagos con tarjeta solo por pasarelas certificadas sin guardar datos de tarjeta en Odoo, y revisión periódica de usuarios y claves API activas."],
    ["Quiebre de stock por crecimiento rápido", "Pedidos web que no se pueden entregar en 48 horas", "Revisar mínimos y máximos de las reglas de reordenamiento cada mes según las ventas reales y mantener dos proveedores por producto."],
  ], [2400, 2900, 4060]),

  H1("Retos"),
  P("Estos son los problemas que el equipo resolvió durante la implementación:"),
  bullet("La licencia de la primera instancia venció en plena entrega. Se creó una base nueva y se replicó toda la configuración de la Fase 2 con los scripts de carga, en lugar de volver a capturar los datos a mano."),
  bullet("La base nueva usa Odoo 20 y la anterior 19.4. Cambiaron detalles de la API: los adjuntos se guardan en otro campo, el NIT se guarda sin guion y los métodos de pago se activan de otra forma. Cada script se ajustó y se probó primero en modo de prueba."),
  bullet("Validar entregas desde la API abría un asistente de confirmación por SMS que dejaba las entregas pendientes. Se desactivó ese aviso para que el flujo de entrega fuera el mismo que en la interfaz."),
  bullet("Los integrantes no podían entrar al CRM aunque tenían rol de administrador, porque en Odoo los permisos de cada app se asignan aparte. Se asignaron por app a cada usuario."),
  bullet("Simular 110 ventas sin dejar stock negativo exigió confirmar y recibir las compras que generaban las reglas de reordenamiento a medida que avanzaban las ventas."),
  bullet("El sitio traía textos de ejemplo de Odoo (teléfono, correo, dirección y preguntas genéricas) y algunas frases sin traducir al español. Se reemplazaron por los datos de UrbanJungle y se agregaron las traducciones."),

  H1("Conclusiones"),
  P([run("Hernán Ricardo Ávila Castillo. ", { bold: true }), run(`Tener la tienda en línea sobre el mismo Odoo del ERP evitó duplicar trabajo: los ${C.productos} productos, sus precios y existencias se publicaron desde los mismos registros, y los ${C.ventas_web} pedidos web siguieron el flujo de entrega y reabastecimiento ya probado en la Fase 2. La meta de la Fase 1 de habilitar un canal de venta en línea integrado al vivero está cumplida; falta llevarla al volumen de clientes que se planteó.`)]),
  P([run("Sebastián Gómez Lavarreda. ", { bold: true }), run(`El tablero de BI mostró que la Care Box es el producto más vendido y que sus suscriptores son los cinco mejores clientes, pero solo hay ${K.suscriptores} suscriptores frente a la meta de 40. Los datos indican dónde poner el esfuerzo comercial: convertir clientes frecuentes en suscriptores aporta más que buscar clientes nuevos de una sola compra.`)]),
  P([run("Rodrigo Alejandro Tahuite Soria. ", { bold: true }), run(`Las reglas de reordenamiento sostuvieron ${C.ventas} ventas con ${pct(K.nivel_servicio)} de pedidos entregados completos, generando ${C.compras} órdenes de compra sin intervención manual. Para crecer en catálogo o en territorio, el punto a vigilar es la bodega y la logística de producto vivo, no la capacidad del sistema.`)]),
];

B.guardar("Informe_Ejecutivo_Fase3_UrbanJungle.docx", "Informe Ejecutivo UrbanJungle, Fase 3", "UrbanJungle · Informe Ejecutivo · Fase 3 · SOG1", hijos);
