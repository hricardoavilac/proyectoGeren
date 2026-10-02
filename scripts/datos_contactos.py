"""Proveedores y clientes simulados de UrbanJungle (datos ficticios)."""


def nit(base):
    """NIT guatemalteco con dígito verificador (módulo 11; 10 -> K)."""
    digitos = str(base)
    total = sum(int(d) * p for d, p in zip(reversed(digitos), range(2, len(digitos) + 2)))
    dv = (11 - total % 11) % 11
    return f"{digitos}-{'K' if dv == 10 else dv}"


# (nombre, nit base, teléfono, correo, dirección, ciudad, etiqueta, productos [ref], días de entrega)
# El primer proveedor de cada producto (orden de esta lista) es el preferido para el reabastecimiento.
PROVEEDORES = [
    ("Viveros Mayoristas del Pacífico, S.A.", 4521873, "+502 7880 1520", "ventas@viverospacifico.gt",
     "Km 58.5 Carretera al Pacífico", "Escuintla", "Plantas", ["UJ-P01", "UJ-P02", "UJ-P05"], 3),
    ("Tropical Plants Guatemala, S.A.", 6817342, "+502 2479 3311", "pedidos@tropicalplants.gt",
     "Km 22 Carretera a El Salvador", "Fraijanes", "Plantas", ["UJ-P04", "UJ-P06", "UJ-P01"], 4),
    ("Vivero Las Orquídeas de Amatitlán", 3389015, "+502 6633 2047", "info@orquideasamatitlan.gt",
     "Calle del Lago 4-12", "Amatitlán", "Plantas", ["UJ-P03", "UJ-P07", "UJ-P08"], 3),
    ("Agroexportadora Verde Maya, S.A.", 8102457, "+502 7832 6690", "comercial@verdemaya.gt",
     "Finca El Retiro, Aldea San Mateo", "Antigua Guatemala", "Plantas", ["UJ-P05", "UJ-P04", "UJ-P06"], 5),
    ("Follajes de Escuintla", 2976431, "+502 7888 4102", "follajes.escuintla@gmail.com",
     "6a Avenida 3-45, Zona 1", "Escuintla", "Plantas", ["UJ-P02", "UJ-P08", "UJ-P07"], 4),
    ("Plantas Ornamentales San Lucas", 5730186, "+502 7830 9054", "ventas@ornamentalessanlucas.gt",
     "Km 29 Carretera Interamericana", "San Lucas Sacatepéquez", "Plantas", ["UJ-P06", "UJ-P03", "UJ-P01"], 2),
    ("Jardines de Antigua Mayoristas", 7364520, "+502 7832 1178", "mayoreo@jardinesantigua.gt",
     "Calle Ancha de los Herreros 27", "Antigua Guatemala", "Plantas", ["UJ-P08", "UJ-P02", "UJ-P04"], 4),
    ("Vivero El Cafetal", 1958742, "+502 7885 3360", "viveroelcafetal@gmail.com",
     "Aldea El Cafetal, Lote 9", "Palín", "Plantas", ["UJ-P07", "UJ-P05", "UJ-P03"], 3),
    ("Suculentas y Cactus de Oriente", 4415609, "+502 7941 2285", "ventas@suculentasoriente.gt",
     "Barrio El Centro, 2a Calle 5-20", "Zacapa", "Suculentas", ["UJ-P09", "UJ-P10", "UJ-P12"], 5),
    ("Cactario Valle del Motagua", 6093318, "+502 7934 5801", "cactario.motagua@gmail.com",
     "Km 126 Ruta al Atlántico", "Estanzuela", "Suculentas", ["UJ-P10", "UJ-P09", "UJ-P14"], 6),
    ("Cerámica Artesanal de Totonicapán", 3027764, "+502 7766 1029", "ceramica.toto@gmail.com",
     "Paraje Chuicruz, Zona 3", "Totonicapán", "Macetas", ["UJ-P11", "UJ-P12", "UJ-P13"], 6),
    ("Alfarería Chinautla", 2580491, "+502 2445 7613", "alfareriachinautla@gmail.com",
     "Aldea Santa Cruz Chinautla", "Chinautla", "Macetas", ["UJ-P12", "UJ-P11", "UJ-P13"], 3),
    ("Textiles y Macramé Atitlán", 9146205, "+502 7721 8840", "macrame.atitlan@gmail.com",
     "Cantón Chechimaj", "Santiago Atitlán", "Macetas", ["UJ-P13", "UJ-P11", "UJ-P12"], 7),
    ("Distribuidora Plastigua, S.A.", 5508923, "+502 2434 6075", "ventas@plastigua.gt",
     "Calzada San Juan 32-15, Zona 7", "Guatemala", "Accesorios", ["UJ-P18", "UJ-P17", "UJ-P12"], 2),
    ("Agroinsumos La Cosecha, S.A.", 7781046, "+502 2440 8812", "pedidos@lacosecha.gt",
     "Calzada Roosevelt 14-60, Zona 11", "Guatemala", "Insumos", ["UJ-P14", "UJ-P15", "UJ-P16"], 2),
    ("Lombricompost Chimaltenango", 3652870, "+502 7839 4416", "lombricompost.chimal@gmail.com",
     "Km 55 Carretera Interamericana", "Chimaltenango", "Insumos", ["UJ-P16", "UJ-P14", "UJ-P15"], 4),
    ("Fertilizantes Orgánicos del Altiplano", 8820357, "+502 7767 3301", "ventas@fertialtiplano.gt",
     "Zona 2, 4a Calle 8-31", "Quetzaltenango", "Insumos", ["UJ-P15", "UJ-P16", "UJ-P20"], 5),
    ("Agroservicio El Sembrador", 1407683, "+502 6630 5590", "elsembrador.agro@gmail.com",
     "Boulevard Villa Nueva 3-50, Zona 4", "Villa Nueva", "Insumos", ["UJ-P14", "UJ-P19", "UJ-P15"], 2),
    ("Ferretería Industrial El Martillo", 6239015, "+502 2251 0937", "ventas@elmartillo.gt",
     "Avenida Bolívar 28-80, Zona 3", "Guatemala", "Accesorios", ["UJ-P19", "UJ-P17", "UJ-P18"], 2),
    ("Empaques Kraft de Guatemala, S.A.", 4970528, "+502 2385 6620", "ventas@empaqueskraft.gt",
     "Km 16.5 Carretera a San Juan Sacatepéquez", "Mixco", "Accesorios", ["UJ-P20", "UJ-P18", "UJ-P17"], 3),
]

# (nombre, nit base, teléfono, correo, dirección, ciudad, empleador, etiqueta)
CLIENTES = [
    ("María José Castillo López", 2845019, "+502 5512 3348", "mjcastillo@gmail.com", "Bulevar Vista Hermosa 18-40, Zona 15", "Guatemala", "Banco Agrícola del Altiplano", "Suscriptor Care Box"),
    ("Carlos Andrés Méndez Ruiz", 3917024, "+502 4478 2091", "carlos.mendez@outlook.com", "12 Calle 1-25, Zona 10", "Guatemala", "Tecnologías Quetzal, S.A.", "Cliente Frecuente"),
    ("Ana Lucía Herrera Pineda", 4106385, "+502 3021 7745", "anaherrera@gmail.com", "Residenciales San Cristóbal, Sector B", "Mixco", "Hospital Integral Las Américas", "Cliente Frecuente"),
    ("José Pablo García Morales", 1983470, "+502 5590 1132", "jpgarcia@yahoo.com", "Condado Concepción, Casa 14", "Santa Catarina Pinula", "Consultores Asociados Maya", "Cliente Nuevo"),
    ("Sofía Alejandra Rodríguez Paz", 5274813, "+502 4120 8876", "sofia.rodriguez@gmail.com", "Avenida Las Américas 9-50, Zona 13", "Guatemala", "Universidad Panamericana del Norte", "Suscriptor Care Box"),
    ("Diego Fernando López Arriaga", 6630497, "+502 3345 2290", "diego.lopez@gmail.com", "Colonia Molino de las Flores, 3a Av", "Mixco", "Cervecería Artesanal Volcán", "Cliente Ocasional"),
    ("Valeria Isabel Martínez Cruz", 2209638, "+502 5876 4421", "valeria.martinez@hotmail.com", "Ciudad San Cristóbal, Sector A1", "Mixco", "Agencia Creativa Jade", "Cliente Frecuente"),
    ("Luis Eduardo Pérez Solórzano", 7458102, "+502 4009 3376", "luisperez@gmail.com", "Km 18.5 Carretera a El Salvador", "Fraijanes", "Exportadora Café Montaña", "Cliente VIP"),
    ("Gabriela Fernanda Ramírez Ochoa", 3561290, "+502 3218 6654", "gaby.ramirez@gmail.com", "Avenida Petapa 45-10, Zona 12", "Guatemala", "Farmacias Bienestar", "Cliente Nuevo"),
    ("Javier Alejandro Torres Monzón", 4893015, "+502 5734 0098", "jtorres@outlook.com", "Bosques de San Nicolás, Casa 22", "Mixco", "Constructora Pilares", "Cliente Ocasional"),
    ("Daniela Sofía Flores Barrios", 1592846, "+502 4466 7812", "daniela.flores@gmail.com", "Colonia Villa Hermosa I, Lote 8", "San Miguel Petapa", "Colegio Bilingüe El Roble", "Suscriptor Care Box"),
    ("Ricardo Antonio Gómez Estrada", 6025731, "+502 3390 5547", "rgomez@gmail.com", "6a Avenida 7-39, Zona 4", "Guatemala", "Café Barista Cuatro Grados", "Cliente Frecuente"),
    ("Andrea Paola Sánchez Ordóñez", 2738460, "+502 5021 9930", "andrea.sanchez@gmail.com", "Condominio Lomas de Pinula, Casa 5", "Santa Catarina Pinula", "Estudio Jurídico Sánchez & Asociados", "Cliente VIP"),
    ("Fernando José Morales Aguilar", 5389127, "+502 4187 2265", "fmorales@yahoo.com", "Calzada Aguilar Batres 34-70, Zona 11", "Guatemala", "Distribuidora Alimentos del Valle", "Cliente Ocasional"),
    ("Camila Beatriz Ortiz Villatoro", 3170594, "+502 3654 8810", "camila.ortiz@gmail.com", "Residenciales Las Luces, Casa 31", "Villa Nueva", "Clínica Dental Sonríe", "Cliente Nuevo"),
    ("Pablo Ernesto Chávez Lima", 4682093, "+502 5543 1176", "pablo.chavez@gmail.com", "Avenida Reforma 8-60, Zona 9", "Guatemala", "Seguros La Ceiba", "Cliente Frecuente"),
    ("Isabella María Juárez Cifuentes", 7031846, "+502 4298 7703", "isabella.juarez@hotmail.com", "Carretera a El Salvador Km 13, Condominio Vistas", "Santa Catarina Pinula", "Hotel Boutique Casa Colonial", "Suscriptor Care Box"),
    ("Andrés Felipe Reyes Batres", 1845372, "+502 3107 4459", "andres.reyes@gmail.com", "Colonia Monte Real, 2a Calle", "Mixco", "Logística Express Centroamérica", "Cliente Ocasional"),
    ("Mariana Lucía Castañeda Rivas", 6297015, "+502 5688 2234", "mariana.castaneda@gmail.com", "Calzada Atanasio Tzul 22-00, Zona 12", "Guatemala", "Panadería San Martín de Porres", "Cliente Frecuente"),
    ("Sebastián Alejandro Muñoz Girón", 3824601, "+502 4033 9987", "smunoz@outlook.com", "Residenciales Catalina, Casa 47", "Villa Nueva", "Desarrollos Inmobiliarios Altamira", "Cliente Nuevo"),
    ("Paula Andrea Vásquez Toledo", 5143928, "+502 3289 1145", "paula.vasquez@gmail.com", "Colonia Arrivillaga, 14 Calle", "San Miguel Petapa", "Escuela de Yoga Prana", "Suscriptor Care Box"),
    ("Emilio José Hernández Salazar", 2468139, "+502 5165 6603", "emilio.hernandez@gmail.com", "Diagonal 6 13-01, Zona 10", "Guatemala", "Agencia de Viajes Quetzaltour", "Cliente VIP"),
    ("Lucía Fernanda Aldana Mejía", 4370582, "+502 4551 3320", "lucia.aldana@gmail.com", "Condominio Puerta de Hierro, Casa 3", "Fraijanes", "Veterinaria Patitas Felices", "Cliente Ocasional"),
    ("Manuel Alejandro Recinos Paiz", 7915264, "+502 3476 9081", "manuel.recinos@yahoo.com", "Avenida Hincapié 20-55, Zona 13", "Guatemala", "Aerolíneas Mundo Maya", "Cliente Frecuente"),
    ("Natalia Sofía Girón Escobar", 1624793, "+502 5309 4478", "natalia.giron@gmail.com", "Colonia El Naranjo, 5a Avenida", "Mixco", "Estudio de Arquitectura Bioclima", "Suscriptor Care Box"),
    ("Héctor Daniel Ponce Alvarado", 5806147, "+502 4212 0056", "hector.ponce@gmail.com", "Boulevard Los Próceres 24-69, Zona 10", "Guatemala", "Corporación Financiera Atlántida", "Cliente Nuevo"),
    ("Regina Alejandra Molina Quiñónez", 3047285, "+502 3155 7792", "regina.molina@hotmail.com", "Residenciales Prados de Villa Nueva", "Villa Nueva", "Colegio Montessori Los Pinos", "Cliente Frecuente"),
    ("Óscar Rafael Cabrera Sandoval", 6573910, "+502 5432 8817", "oscar.cabrera@gmail.com", "Km 20 Carretera a El Salvador, Condominio Gardenias", "Fraijanes", "Ingenio Azucarero La Unión", "Cliente Ocasional"),
    ("Fernanda Gabriela Lemus Arévalo", 2915038, "+502 4378 6624", "fernanda.lemus@gmail.com", "13 Avenida 11-30, Zona 14", "Guatemala", "Restaurante Raíces Chapinas", "Cliente VIP"),
    ("Mateo Esteban Figueroa Duarte", 4250916, "+502 3027 5539", "mateo.figueroa@gmail.com", "Colonia Santa Inés, 3a Calle", "San Miguel Petapa", "Startup EcoRuta", "Cliente Nuevo"),
]
