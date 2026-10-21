import csv
from pathlib import Path


class Grafo:
    def __init__(self):
        self.conexiones = {}

    @classmethod
    def cargar(cls):
        grafo = cls()
        archivo = (
            Path(__file__).resolve().parent.parent
            / "datos" / "grafo_rutas_ibague.csv"
        )

        with open(archivo, encoding="utf-8-sig", newline="") as f:
            for fila in csv.DictReader(f):
                origen = fila["origen"]
                destino = fila["destino"]
                distancia = float(fila["distancia_km"])

                grafo.conexiones.setdefault(origen, []).append(
                    (destino, distancia)
                )
                grafo.conexiones.setdefault(destino, []).append(
                    (origen, distancia)
                )

        return grafo
