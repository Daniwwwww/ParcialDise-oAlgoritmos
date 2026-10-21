class Vehiculo:
    def __init__(self, id, nombre, capacidad):
        self.id = id
        self.nombre = nombre
        self.capacidad = float(capacidad)
        self.paquetes = []

    @property
    def carga(self):
        return sum(p.peso for p in self.paquetes)

    def agregar(self, paquete):
        if self.carga + paquete.peso <= self.capacidad:
            self.paquetes.append(paquete)
            return True
        return False
