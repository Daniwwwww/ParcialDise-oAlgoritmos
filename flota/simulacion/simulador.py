import csv
from pathlib import Path

from modelos.paquete import Paquete
from modelos.vehiculo import Vehiculo
from algoritmos.grafo import Grafo
from algoritmos.dijkstra import camino_mas_corto
from algoritmos.greedy import asignar_paquetes


BASE = Path(__file__).resolve().parent.parent


def leer_paquetes():
    archivo = BASE / "datos" / "paquetes_ibague.csv"

    with open(archivo, encoding="utf-8-sig", newline="") as f:
        return [
            Paquete(
                fila["id"],
                fila["sector"],
                fila["peso_kg"],
                fila["prioridad"],
                fila["direccion"]
            )
            for fila in csv.DictReader(f)
        ]


def leer_vehiculos():
    archivo = BASE / "datos" / "vehiculos.csv"

    with open(archivo, encoding="utf-8-sig", newline="") as f:
        return [
            Vehiculo(
                fila["id"],
                fila["nombre"],
                fila["capacidad_kg"]
            )
            for fila in csv.DictReader(f)
        ]


def ejecutar_simulacion():
    paquetes = leer_paquetes()
    vehiculos = leer_vehiculos()
    grafo = Grafo.cargar()

    pendientes = asignar_paquetes(paquetes, vehiculos)
    resultados = []
    distancia_total = 0.0

    for vehiculo in vehiculos:
        actual = "Centro"
        destinos = [p.sector for p in vehiculo.paquetes]
        paradas = ["Centro"]
        distancia_ruta = 0.0

        while destinos:
            opciones = []

            for destino in set(destinos):
                camino, distancia = camino_mas_corto(
                    grafo, actual, destino
                )

                if camino and distancia != float("inf"):
                    opciones.append((distancia, destino, camino))

            if not opciones:
                break

            distancia, destino, camino = min(opciones)
            distancia_ruta += distancia

            for sector in camino[1:]:
                if sector != paradas[-1]:
                    paradas.append(sector)

            destinos.remove(destino)
            actual = destino

        if actual != "Centro" and vehiculo.paquetes:
            camino, distancia = camino_mas_corto(
                grafo, actual, "Centro"
            )

            if camino and distancia != float("inf"):
                distancia_ruta += distancia

                for sector in camino[1:]:
                    if sector != paradas[-1]:
                        paradas.append(sector)

        distancia_total += distancia_ruta

        resultados.append({
            "vehiculo": vehiculo,
            "paradas": paradas,
            "distancia": distancia_ruta
        })

    return {
        "vehiculos": resultados,
        "pendientes": pendientes,
        "distancia_total": distancia_total,
        "total_paquetes": len(paquetes)
    }
