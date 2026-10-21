import heapq


def camino_mas_corto(grafo, inicio, fin):
    if inicio == fin:
        return [inicio], 0.0

    distancias = {inicio: 0.0}
    anteriores = {}
    cola = [(0.0, inicio)]

    while cola:
        distancia, actual = heapq.heappop(cola)

        if distancia > distancias.get(actual, float("inf")):
            continue

        if actual == fin:
            break

        for vecino, costo in grafo.conexiones.get(actual, []):
            nueva = distancia + costo

            if nueva < distancias.get(vecino, float("inf")):
                distancias[vecino] = nueva
                anteriores[vecino] = actual
                heapq.heappush(cola, (nueva, vecino))

    if fin not in distancias:
        return [], float("inf")

    camino = [fin]

    while camino[-1] != inicio:
        camino.append(anteriores[camino[-1]])

    camino.reverse()
    return camino, distancias[fin]
