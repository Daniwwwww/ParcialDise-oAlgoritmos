class Paquete:
    def __init__(self, id, sector, peso, prioridad, direccion):
        self.id = id
        self.sector = sector
        self.peso = float(peso)
        self.prioridad = int(prioridad)
        self.direccion = direccion

    def __str__(self):
        return f"{self.id} - {self.direccion}"
