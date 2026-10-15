"""Datos de la Fase 3: 10 productos nuevos (catálogo de 30) y clientes registrados por la tienda en línea."""

# (referencia, nombre, categoría, precio, costo, proveedores, stock inicial, (mín, máx), descripción para la tienda)
PRODUCTOS_FASE3 = [
    ("UJ-P21", "Pilea Peperomioides – Planta China del Dinero", "Plantas de Interior", 95.00, 42.00,
     ["Vivero Las Orquídeas de Amatitlán", "Plantas Ornamentales San Lucas"], 22, (8, 25),
     "Hojas redondas sobre tallos delgados. Luz indirecta brillante y riego cuando el sustrato esté seco."),
    ("UJ-P22", "Espatifilo – Cuna de Moisés", "Plantas de Interior", 110.00, 50.00,
     ["Tropical Plants Guatemala, S.A.", "Follajes de Escuintla"], 22, (8, 25),
     "Flor blanca y hojas verde oscuro. Tolera poca luz y avisa cuando necesita agua porque baja sus hojas."),
    ("UJ-P23", "Aloe Vera en Maceta", "Suculentas y Cactus", 55.00, 22.00,
     ["Suculentas y Cactus de Oriente", "Cactario Valle del Motagua"], 28, (10, 30),
     "Suculenta medicinal de bajo mantenimiento. Riego cada 2 o 3 semanas y mucha luz."),
    ("UJ-P24", "Helecho de Boston Colgante", "Plantas de Interior", 120.00, 55.00,
     ["Follajes de Escuintla", "Vivero El Cafetal"], 20, (8, 25),
     "Frondas largas para maceta colgante. Prefiere humedad alta y sustrato siempre húmedo."),
    ("UJ-P25", "Orquídea Phalaenopsis (maceta 12 cm)", "Plantas de Interior", 225.00, 110.00,
     ["Vivero Las Orquídeas de Amatitlán", "Tropical Plants Guatemala, S.A."], 18, (6, 20),
     "Orquídea en floración con varas de 8 a 12 flores. Riego por inmersión una vez por semana."),
    ("UJ-P26", "Kit de Inicio UrbanJungle", "Kits y Regalos", 249.00, 120.00,
     ["Empaques Kraft de Guatemala, S.A.", "Agroinsumos La Cosecha, S.A."], 20, (6, 20),
     "Planta de interior, maceta de barro, sustrato de 5 L y guía de cuidado impresa en una caja de regalo."),
    ("UJ-P27", "Cúpula de Vidrio con Planta Decorativa", "Kits y Regalos", 165.00, 75.00,
     ["Empaques Kraft de Guatemala, S.A.", "Distribuidora Plastigua, S.A."], 16, (6, 20),
     "Cúpula de vidrio con base de madera y una suculenta en maceta geométrica. Para escritorio o repisa."),
    ("UJ-P28", "Tutor de Musgo para Monstera 60 cm", "Herramientas y Accesorios", 70.00, 30.00,
     ["Ferretería Industrial El Martillo", "Agroservicio El Sembrador"], 24, (6, 20),
     "Poste de fibra de coco y musgo para que las plantas trepadoras crezcan hacia arriba."),
    ("UJ-P29", "Maceta Autorriego 16 cm", "Macetas y Colgantes", 135.00, 60.00,
     ["Distribuidora Plastigua, S.A.", "Alfarería Chinautla"], 22, (8, 25),
     "Depósito inferior con indicador de nivel. Mantiene la humedad hasta por dos semanas."),
    ("UJ-P30", "Lámpara LED de Cultivo para Interior", "Herramientas y Accesorios", 285.00, 140.00,
     ["Ferretería Industrial El Martillo", "Distribuidora Plastigua, S.A."], 15, (6, 20),
     "Luz LED de espectro completo de 20 W para plantas en espacios con poca luz natural."),
]

# Clientes que se registran desde la tienda en línea en octubre de 2026
# (nombre, nit base, teléfono, correo, dirección, ciudad, empleador)
CLIENTES_WEB = [
    ("Alejandra Beatriz Soto Monterroso", 5617203, "+502 5521 0846", "alejandra.soto@gmail.com", "Vista Hermosa II, 22 Avenida 3-15, Zona 15", "Guatemala", "Consultora Ambiental Ceiba"),
    ("Rodrigo Javier Pinto Lemus", 3486521, "+502 4402 7719", "rodrigo.pinto@outlook.com", "Condominio Los Álamos, Casa 9", "Mixco", "Tecnologías Quetzal, S.A."),
    ("Mónica Elizabeth Arana Cruz", 7202948, "+502 3290 5531", "monica.arana@gmail.com", "Colonia Lomas de San Rafael, 4a Calle", "Santa Catarina Pinula", "Clínica Dental Sonríe"),
    ("Gerardo Andrés Velásquez Ruiz", 2954187, "+502 5178 6620", "gerardo.velasquez@gmail.com", "Residenciales Villa Linda, Casa 14", "Villa Nueva", "Logística Express Centroamérica"),
    ("Silvia Carolina Morales Batz", 6148370, "+502 4720 1185", "silvia.morales@hotmail.com", "Avenida Las Américas 16-20, Zona 14", "Guatemala", "Hotel Boutique Casa Colonial"),
    ("Daniel Esteban Fuentes Ortiz", 4590326, "+502 3368 4902", "daniel.fuentes@gmail.com", "Km 17 Carretera a El Salvador, Condominio Arcos", "Fraijanes", "Startup EcoRuta"),
]

# Descripciones para la tienda de los 20 productos de la Fase 2
DESCRIPCIONES = {
    "UJ-P01": "Hojas grandes con perforaciones naturales. Luz indirecta y riego semanal. Se entrega en maceta de vivero de 14 cm.",
    "UJ-P02": "Pothos de hojas jaspeadas en blanco y verde. Crece colgante o trepadora y tolera poca luz.",
    "UJ-P03": "Hojas erguidas con borde amarillo. Riego cada 2 o 3 semanas; resiste olvidos y poca luz.",
    "UJ-P04": "Ficus de hojas en forma de violín, 60 cm de alto. Necesita luz brillante cerca de una ventana.",
    "UJ-P05": "Hojas brillantes y tallos gruesos que guardan agua. Riego cada 2 semanas; tolera sombra.",
    "UJ-P06": "Hojas redondas con franjas plateadas. Prefiere humedad alta y agua sin cloro.",
    "UJ-P07": "Hojas en forma de corazón para maceta colgante o repisa. Crece rápido con luz indirecta.",
    "UJ-P08": "Hojas gruesas y brillantes, tamaño compacto para escritorio. Riego moderado.",
    "UJ-P09": "Roseta azul verdosa. Pleno sol o luz brillante y riego escaso.",
    "UJ-P10": "Cactus en grupo con espinas cortas. Florece en primavera con poca agua y mucha luz.",
    "UJ-P11": "Maceta de cerámica negra mate con plato a juego. Diámetro 12 cm, con agujero de drenaje.",
    "UJ-P12": "Maceta de barro cocido de 18 cm. El barro deja respirar la raíz y evita el exceso de agua.",
    "UJ-P13": "Colgante tejido a mano en algodón para macetas de 12 a 18 cm. Largo total 90 cm.",
    "UJ-P14": "Mezcla de turba, perlita y fibra de coco para plantas de interior. Bolsa de 5 litros.",
    "UJ-P15": "Fertilizante orgánico líquido. Una tapa en 1 litro de agua cada 15 días.",
    "UJ-P16": "Abono de lombriz cernido, sin olor. Bolsa de 2 kg para mezclar con el sustrato.",
    "UJ-P17": "Regadera de metal con pico largo para regar sin mojar las hojas. Capacidad 1.5 litros.",
    "UJ-P18": "Atomizador de 500 ml para subir la humedad de helechos, calateas y orquídeas.",
    "UJ-P19": "Pala de acero inoxidable con mango de madera para trasplantes en maceta.",
    "UJ-P20": "Caja mensual con fertilizante, guía de cuidado de la temporada y un accesorio sorpresa. Entrega a domicilio cada mes.",
}
