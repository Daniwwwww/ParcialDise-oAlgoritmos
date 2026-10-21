from algoritmos.mochila import seleccionar_paquetes


def asignar_paquetes(paquetes, vehiculos):
    pendientes = sorted(
        paquetes,
        key=lambda p: (p.prioridad, -p.peso),
        reverse=True
    )

    for vehiculo in vehiculos:
        seleccionados = seleccionar_paquetes(
            pendientes, vehiculo.capacidad
        )

        for paquete in seleccionados:
            if vehiculo.agregar(paquete):
                pendientes.remove(paquete)

    return pendientes
