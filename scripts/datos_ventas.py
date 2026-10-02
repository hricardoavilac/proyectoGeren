"""Plan determinístico de las 50 ventas simuladas y del stock inicial.

Cada cliente compra al menos una vez; los clientes frecuentes, VIP y suscriptores
repiten. El stock inicial se calcula para que, tras las ventas, los productos de
REABASTECER queden bajo su mínimo y disparen la cotización automática al proveedor.
"""
import random
from collections import Counter

from datos_contactos import CLIENTES
from datos_productos import PRODUCTOS

TOTAL_VENTAS = 50
REFS = [p[0] for p in PRODUCTOS]
PLANTAS = [p[0] for p in PRODUCTOS if p[3] in ("Plantas de Interior", "Suculentas y Cactus")]
COMPLEMENTOS = [p[0] for p in PRODUCTOS if p[3] not in ("Plantas de Interior", "Suculentas y Cactus", "Suscripciones")]
CARE_BOX = "UJ-P20"

# Regla de reorden por categoría: (mínimo, máximo)
REGLA = {"Plantas de Interior": (8, 25), "Suculentas y Cactus": (10, 30), "Macetas y Colgantes": (8, 25),
         "Sustratos y Fertilizantes": (10, 30), "Herramientas y Accesorios": (6, 20), "Suscripciones": (8, 25)}
REGLAS = {p[0]: REGLA[p[3]] for p in PRODUCTOS}

# Productos que deben quedar bajo el mínimo al terminar las ventas (demostración del reordenamiento)
REABASTECER = {"UJ-P01", "UJ-P04", "UJ-P06", "UJ-P09", "UJ-P15", "UJ-P20"}


def plan_ventas():
    rnd = random.Random(2026)
    recurrentes = [c[0] for c in CLIENTES if c[7] in ("Cliente Frecuente", "Cliente VIP", "Suscriptor Care Box")]
    compradores = [c[0] for c in CLIENTES] + [rnd.choice(recurrentes) for _ in range(TOTAL_VENTAS - len(CLIENTES))]
    rnd.shuffle(compradores)
    clase = {c[0]: c[7] for c in CLIENTES}
    ventas = []
    for n, cliente in enumerate(compradores):
        lineas = {rnd.choice(PLANTAS): rnd.choice([1, 1, 1, 2, 2, 3])}
        # Venta cruzada: maceta, sustrato o accesorio
        for ref in rnd.sample(COMPLEMENTOS, rnd.choice([0, 1, 1, 2])):
            lineas[ref] = rnd.choice([1, 1, 2])
        if clase[cliente] == "Suscriptor Care Box" or rnd.random() < 0.12:
            lineas[CARE_BOX] = 1
        dia = 1 + n * 29 // TOTAL_VENTAS  # ventas repartidas del 1 al 29 de septiembre de 2026
        ventas.append({"cliente": cliente, "fecha": f"2026-09-{dia:02d} {rnd.randint(9, 18):02d}:{rnd.choice([0, 15, 30, 45]):02d}:00",
                       "lineas": lineas})
    return ventas


def stock_inicial(ventas):
    demanda = Counter()
    for v in ventas:
        demanda.update(v["lineas"])
    stock = {}
    for i, ref in enumerate(REFS):
        minimo = REGLAS[ref][0]
        sobrante = (minimo - 2 - i % 3) if ref in REABASTECER else (minimo + 6 + i % 7)
        stock[ref] = demanda[ref] + sobrante
    return stock, demanda
