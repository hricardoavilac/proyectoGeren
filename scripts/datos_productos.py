"""Catálogo de 20 productos de UrbanJungle (precios en GTQ, IVA incluido)."""

CATEGORIA_PADRE = "UrbanJungle"

# (referencia, nombre, tipo, categoría, precio de venta, costo)
PRODUCTOS = [
    ("UJ-P01", "Monstera Deliciosa (maceta 14 cm)", "Bienes", "Plantas de Interior", 185.00, 92.00),
    ("UJ-P02", "Pothos Marble Queen (maceta 12 cm)", "Bienes", "Plantas de Interior", 75.00, 34.00),
    ("UJ-P03", "Sansevieria Trifasciata – Lengua de Suegra", "Bienes", "Plantas de Interior", 95.00, 44.00),
    ("UJ-P04", "Ficus Lyrata – Pandurata (60 cm)", "Bienes", "Plantas de Interior", 265.00, 135.00),
    ("UJ-P05", "Zamioculca – Planta ZZ", "Bienes", "Plantas de Interior", 145.00, 68.00),
    ("UJ-P06", "Calathea Orbifolia", "Bienes", "Plantas de Interior", 135.00, 64.00),
    ("UJ-P07", "Philodendron Corazón Colgante", "Bienes", "Plantas de Interior", 85.00, 38.00),
    ("UJ-P08", "Peperomia Obtusifolia", "Bienes", "Plantas de Interior", 65.00, 29.00),
    ("UJ-P09", "Suculenta Echeveria Elegans", "Bienes", "Suculentas y Cactus", 35.00, 14.00),
    ("UJ-P10", "Cactus Mammillaria", "Bienes", "Suculentas y Cactus", 40.00, 17.00),
    ("UJ-P11", "Maceta de Cerámica Negra con Base 12 cm", "Bienes", "Macetas y Colgantes", 95.00, 42.00),
    ("UJ-P12", "Maceta de Barro Clásica 18 cm", "Bienes", "Macetas y Colgantes", 45.00, 18.00),
    ("UJ-P13", "Colgante de Macramé para Maceta", "Bienes", "Macetas y Colgantes", 110.00, 48.00),
    ("UJ-P14", "Sustrato Premium para Interior 5 L", "Bienes", "Sustratos y Fertilizantes", 60.00, 26.00),
    ("UJ-P15", "Fertilizante Líquido Orgánico 1 L", "Bienes", "Sustratos y Fertilizantes", 75.00, 33.00),
    ("UJ-P16", "Humus de Lombriz 2 kg", "Bienes", "Sustratos y Fertilizantes", 45.00, 19.00),
    ("UJ-P17", "Regadera Metálica 1.5 L", "Bienes", "Herramientas y Accesorios", 125.00, 58.00),
    ("UJ-P18", "Atomizador para Plantas 500 ml", "Bienes", "Herramientas y Accesorios", 35.00, 14.00),
    ("UJ-P19", "Pala de Trasplante de Acero", "Bienes", "Herramientas y Accesorios", 55.00, 24.00),
    ("UJ-P20", "UrbanJungle Care Box – Suscripción Mensual", "Bienes", "Suscripciones", 179.00, 82.00),
]


def ean13(n):
    """EAN-13 con prefijo GS1 de Guatemala (740) y dígito verificador."""
    base = f"74012026{n:04d}"
    total = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(base))
    return base + str((10 - total % 10) % 10)
