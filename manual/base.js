// Bloques comunes de los documentos de la Fase 3 (mismo estilo que el Manual Técnico de la Fase 2).
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, Header, Footer,
  AlignmentType, HeadingLevel, WidthType, ShadingType, BorderStyle, PageNumber, LevelFormat,
  ExternalHyperlink, VerticalAlign,
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const FONT = "Montserrat";
const VERDE = "1F6F50", VERDE_CLARO = "D7E8DD", TERRACOTA = "C97B2E";
const ANCHO = 9360; // carta con márgenes de 1"

const img = (rel) => fs.readFileSync(path.join(ROOT, rel));
const q = (n) => "Q" + Number(n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const pct = (n) => (n * 100).toFixed(1).replace(".0", "") + "%";

const run = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || 20, bold: o.bold, italics: o.italics, color: o.color });
const P = (content, o = {}) => new Paragraph({
  children: (Array.isArray(content) ? content : [content]).map((c) => (typeof c === "string" ? run(c, o) : c)),
  alignment: o.align || AlignmentType.JUSTIFIED, spacing: { after: o.after ?? 120, before: o.before ?? 0, line: 276 },
  keepNext: o.keepNext,
});
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: FONT, size: 30, bold: true, color: VERDE })], spacing: { before: 240, after: 160 }, keepNext: true, pageBreakBefore: true });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: FONT, size: 25, bold: true, color: VERDE })], spacing: { before: 200, after: 100 }, keepNext: true });
const enlace = (url, texto) => new ExternalHyperlink({ link: url, children: [new TextRun({ text: texto || url, font: FONT, size: 20, style: "Hyperlink" })] });

const NUMERACIONES = [];
const bullet = (content) => new Paragraph({ numbering: { reference: "vinetas", level: 0 }, spacing: { after: 60, line: 276 },
  children: (Array.isArray(content) ? content : [content]).map((c) => (typeof c === "string" ? run(c) : c)) });
const pasos = (items) => {
  const ref = `pasos${NUMERACIONES.length}`; NUMERACIONES.push(ref);
  return items.map((t) => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 60, line: 276 },
    children: (Array.isArray(t) ? t : [t]).map((c) => (typeof c === "string" ? run(c) : c)) }));
};
const figura = (rel, w, h, pie, tipo) => [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 }, keepNext: true,
    children: [new ImageRun({ type: tipo || (rel.endsWith(".jpg") ? "jpg" : "png"), data: img(rel), transformation: { width: w, height: h } })] }),
  P(pie, { align: AlignmentType.CENTER, italics: true, size: 18, color: "555555", after: 200 }),
];

const borde = { style: BorderStyle.SINGLE, size: 4, color: "BFD6C8" };
const bordes = { top: borde, bottom: borde, left: borde, right: borde };
const celda = (contenido, ancho, o = {}) => new TableCell({
  borders: bordes, width: { size: ancho, type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
  shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
  margins: { top: 60, bottom: 60, left: 100, right: 100 },
  children: [new Paragraph({ alignment: o.align || AlignmentType.LEFT, children: [run(String(contenido), { size: o.size || 19, bold: o.bold, color: o.color })] })],
});
const tabla = (encabezados, filas, anchos, o = {}) => new Table({
  width: { size: ANCHO, type: WidthType.DXA }, columnWidths: anchos,
  rows: [
    new TableRow({ tableHeader: true, children: encabezados.map((h, i) => celda(h, anchos[i], { fill: VERDE, bold: true, color: "FFFFFF", size: o.size })) }),
    ...filas.map((f, r) => new TableRow({ cantSplit: true, children: f.map((v, i) => celda(v, anchos[i], {
      size: o.size, fill: r % 2 ? "F4F8F5" : undefined, align: (o.derecha || []).includes(i) ? AlignmentType.RIGHT : AlignmentType.LEFT })) })),
  ],
});
const ficha = (pares, anchos = [2600, ANCHO - 2600]) => new Table({
  width: { size: ANCHO, type: WidthType.DXA }, columnWidths: anchos,
  rows: pares.map(([k, v]) => new TableRow({ cantSplit: true, children: [
    celda(k, anchos[0], { fill: VERDE_CLARO, bold: true }), celda(v, anchos[1])] })),
});
const espacio = () => P("", { after: 80 });

const portada = (titulo, subtitulo, fecha) => [
  ...["Universidad de San Carlos de Guatemala", "Facultad de Ingeniería, Escuela de Ciencias y Sistemas",
      "Sistemas Organizacionales y Gerenciales 1", "Catedrático: Edwin Estuardo Zapeta Gómez"].map((t) => P(t, { align: AlignmentType.LEFT, after: 0 })),
  P("Auxiliar: Josue Daniel Solís Osorio", { align: AlignmentType.LEFT, after: 600 }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 300 },
    children: [new ImageRun({ type: "png", data: img("assets/logo_urbanjungle.png"), transformation: { width: 420, height: 121 } })] }),
  P([run("Proyecto Fase 3: Implementación de E-commerce y Análisis de Inteligencia de Negocios con Odoo", { bold: true, size: 24 })], { align: AlignmentType.CENTER, after: 200 }),
  P([run(titulo, { bold: true, size: 44, color: VERDE })], { align: AlignmentType.CENTER, after: 100 }),
  P([run(subtitulo, { size: 26, color: TERRACOTA })], { align: AlignmentType.CENTER, after: 600 }),
  P([run("Grupo No. 3", { bold: true, size: 22 })], { align: AlignmentType.CENTER, after: 120 }),
  ...[["Hernán Ricardo Ávila Castillo", "9516085"], ["Sebastián Gómez Lavarreda", "201602929"],
      ["Rodrigo Alejandro Tahuite Soria", "202202854"]].map(([n, c]) => P(`${n}, carné ${c}`, { align: AlignmentType.CENTER, after: 40 })),
  P("", { after: 600 }),
  P(fecha, { align: AlignmentType.CENTER }),
];

function guardar(nombreArchivo, tituloDoc, encabezado, hijos) {
  const doc = new Document({
    creator: "Grupo 3, SOG1", title: tituloDoc,
    fonts: [{ name: FONT, data: img("assets/fonts/Montserrat-Regular.ttf") }],
    styles: { default: { document: { run: { font: FONT, size: 20 } } } },
    numbering: { config: [
      { reference: "vinetas", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
      ...NUMERACIONES.map((ref) => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 300 } } } }] })),
    ] },
    sections: [{
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1300, bottom: 1200, left: 1440, right: 1440 } } },
      headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [run(encabezado, { size: 16, color: "777777" })] })] }) },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ font: FONT, size: 16, color: "777777", children: ["Página ", PageNumber.CURRENT] })] })] }) },
      children: hijos,
    }],
  });
  return Packer.toBuffer(doc).then((buf) => {
    fs.writeFileSync(path.join(ROOT, nombreArchivo), buf);
    console.log("Generado:", nombreArchivo);
  });
}

module.exports = { ROOT, VERDE, TERRACOTA, ANCHO, img, q, pct, run, P, H1, H2, enlace, bullet, pasos, figura,
  tabla, ficha, espacio, portada, guardar, AlignmentType };
