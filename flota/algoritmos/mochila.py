def seleccionar_paquetes(paquetes, capacidad):
    seleccionados = []
    peso = 0.0

    ordenados = sorted(
        paquetes,
        key=lambda p: (p.prioridad, -p.peso),
        reverse=True
    )

    for paquete in ordenados:
        if peso + paquete.peso <= capacidad:
            seleccionados.append(paquete)
            peso += paquete.peso

    return seleccionados
