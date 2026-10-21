
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from urllib.request import urlopen
from urllib.parse import quote

from tkintermapview import TkinterMapView
from simulacion.simulador import ejecutar_simulacion


# Coordenadas aproximadas de los sectores de Ibagué
COORDENADAS = {
    "Centro": (4.44199, -75.23664),
    "La Pola": (4.44716, -75.24495),
    "Cadiz": (4.43743, -75.21848),
    "Piedra Pintada": (4.43436, -75.20827),
    "El Jordan": (4.44125, -75.19607),
    "Ambala": (4.45451, -75.20117),
    "Mirolindo": (4.41667, -75.18333),
    "El Salado": (4.44977, -75.14573),
    "La Samaria": (4.42683, -75.17652),
}


class Ventana:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Optimizador de flota y rutas - Ibagué")
        self.ventana.geometry("1250x780")
        self.ventana.minsize(1000, 650)

        self.resultado = None
        self.indice_vehiculo = 0
        self.paso = 0
        self.marcadores = []
        self.ruta_mapa = None
        self.cache_rutas = {}

        self.crear_interfaz()

    def crear_interfaz(self):
        encabezado = tk.Frame(self.ventana)
        encabezado.pack(fill="x", padx=14, pady=(12, 4))

        tk.Label(
            encabezado,
            text="Optimizador de flota y rutas",
            font=("Arial", 19, "bold")
        ).pack(anchor="w")

        tk.Label(
            encabezado,
            text="Planificación de entregas en Ibagué, Tolima · Mapa OpenStreetMap",
            font=("Arial", 10)
        ).pack(anchor="w", pady=(2, 0))

        controles = tk.Frame(self.ventana)
        controles.pack(fill="x", padx=14, pady=8)

        tk.Button(
            controles,
            text="Ejecutar optimización",
            command=self.ejecutar,
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=(0, 12))

        tk.Label(controles, text="Vehículo:").pack(
            side="left", padx=(0, 5)
        )

        self.selector = ttk.Combobox(
            controles, state="readonly", width=22
        )
        self.selector.pack(side="left")
        self.selector.bind(
            "<<ComboboxSelected>>", self.cambiar_vehiculo
        )

        contenido = tk.Frame(self.ventana)
        contenido.pack(
            fill="both", expand=True, padx=14, pady=(4, 10)
        )

        panel_mapa = tk.Frame(
            contenido, bd=1, relief="solid"
        )
        panel_mapa.pack(
            side="left", fill="both", expand=True
        )

        tk.Label(
            panel_mapa,
            text="Mapa y recorrido del vehículo",
            font=("Arial", 11, "bold")
        ).pack(pady=5)

        self.mapa = TkinterMapView(
            panel_mapa, corner_radius=0
        )
        self.mapa.pack(
            fill="both", expand=True, padx=2, pady=(0, 2)
        )
        self.mapa.set_position(4.4447, -75.2424)
        self.mapa.set_zoom(12)

        panel_datos = tk.Frame(
            contenido, width=350
        )
        panel_datos.pack(
            side="right", fill="y", padx=(12, 0)
        )
        panel_datos.pack_propagate(False)

        tk.Label(
            panel_datos,
            text="Información de la ruta",
            font=("Arial", 11, "bold")
        ).pack(pady=5)

        self.info = scrolledtext.ScrolledText(
            panel_datos,
            width=40,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=24
        )
        self.info.pack(fill="both", expand=True)

        navegacion = tk.Frame(self.ventana)
        navegacion.pack(pady=(0, 12))

        self.anterior = tk.Button(
            navegacion,
            text="← Anterior",
            command=self.retroceder,
            state="disabled"
        )
        self.anterior.pack(side="left", padx=8)

        self.estado = tk.Label(
            navegacion,
            text="Ejecuta la optimización para comenzar"
        )
        self.estado.pack(side="left", padx=8)

        self.siguiente = tk.Button(
            navegacion,
            text="Siguiente →",
            command=self.avanzar,
            state="disabled"
        )
        self.siguiente.pack(side="left", padx=8)

        self.mostrar_sectores()

        self.info.insert(
            tk.END,
            "Presiona 'Ejecutar optimización' para asignar "
            "paquetes y ver la ruta.\n\n"
            "El mapa necesita conexión a internet para cargar "
            "OpenStreetMap.\n"
            "Las coordenadas de los sectores son aproximadas."
        )

    def mostrar_sectores(self):
        """Muestra los sectores como marcadores en el mapa."""
        for marcador in self.marcadores:
            marcador.delete()

        self.marcadores.clear()

        for sector, coordenadas in COORDENADAS.items():
            marcador = self.mapa.set_marker(
                coordenadas[0],
                coordenadas[1],
                text=sector
            )
            self.marcadores.append(marcador)

    def obtener_ruta_por_calles(self, paradas):
        """Obtiene la ruta por calles mediante el servicio OSRM."""
        clave = tuple(paradas)

        if clave in self.cache_rutas:
            return self.cache_rutas[clave]

        if len(paradas) < 2:
            puntos = [
                COORDENADAS[s]
                for s in paradas
                if s in COORDENADAS
            ]
            self.cache_rutas[clave] = puntos
            return puntos

        try:
            # OSRM recibe longitud,latitud.
            coordenadas = ";".join(
                f"{COORDENADAS[sector][1]},"
                f"{COORDENADAS[sector][0]}"
                for sector in paradas
            )

            url = (
                "https://router.project-osrm.org/route/v1/driving/"
                + quote(coordenadas, safe=";,-.")
                + "?overview=full&geometries=geojson&steps=false"
            )

            with urlopen(url, timeout=12) as respuesta:
                datos = json.loads(
                    respuesta.read().decode("utf-8")
                )

            if datos.get("code") == "Ok" and datos.get("routes"):
                geometria = datos["routes"][0]["geometry"]["coordinates"]

                # El mapa utiliza latitud,longitud.
                puntos = [
                    (lat, lon) for lon, lat in geometria
                ]

                self.cache_rutas[clave] = puntos
                return puntos

        except Exception:
            # Si OSRM falla, se conectan los sectores en línea recta.
            pass

        puntos = [
            COORDENADAS[s]
            for s in paradas
            if s in COORDENADAS
        ]

        self.cache_rutas[clave] = puntos
        return puntos

    def dibujar_ruta(self, paradas):
        if self.ruta_mapa is not None:
            self.ruta_mapa.delete()
            self.ruta_mapa = None

        self.mostrar_sectores()
        puntos = self.obtener_ruta_por_calles(paradas)

        if len(puntos) >= 2:
            self.ruta_mapa = self.mapa.set_path(
                puntos,
                color="#087f5b",
                width=5
            )
            self.mapa.set_position(
                puntos[0][0], puntos[0][1]
            )
            self.mapa.set_zoom(12)

        if paradas:
            indice = min(self.paso, len(paradas) - 1)
            sector_actual = paradas[indice]

            if sector_actual in COORDENADAS:
                lat, lon = COORDENADAS[sector_actual]
                self.mapa.set_position(lat, lon)

    def ejecutar(self):
        try:
            self.resultado = ejecutar_simulacion()
        except Exception as error:
            messagebox.showerror("Error", str(error))
            return

        if not self.resultado["vehiculos"]:
            messagebox.showinfo(
                "Aviso", "No hay vehículos registrados."
            )
            return

        nombres = [
            r["vehiculo"].nombre
            for r in self.resultado["vehiculos"]
        ]

        self.selector["values"] = nombres
        self.selector.current(0)
        self.indice_vehiculo = 0
        self.paso = 0

        self.mostrar_ruta()

    def cambiar_vehiculo(self, evento=None):
        if self.resultado is None:
            return

        self.indice_vehiculo = self.selector.current()
        self.paso = 0
        self.mostrar_ruta()

    def mostrar_ruta(self):
        datos = self.resultado["vehiculos"][
            self.indice_vehiculo
        ]

        vehiculo = datos["vehiculo"]
        ruta = datos["paradas"]

        self.dibujar_ruta(ruta)

        self.info.delete("1.0", tk.END)

        self.info.insert(
            tk.END, f"VEHÍCULO: {vehiculo.nombre}\n"
        )
        self.info.insert(
            tk.END, f"Identificación: {vehiculo.id}\n"
        )
        self.info.insert(
            tk.END,
            f"Carga: {vehiculo.carga:g}/"
            f"{vehiculo.capacidad:g} kg\n"
        )

        restante = max(
            0, vehiculo.capacidad - vehiculo.carga
        )

        self.info.insert(
            tk.END,
            f"Capacidad disponible: {restante:g} kg\n"
        )
        self.info.insert(
            tk.END,
            f"Distancia estimada por grafo: "
            f"{datos['distancia']:.2f} km\n\n"
        )

        self.info.insert(
            tk.END, "ORDEN DE RECORRIDO:\n"
        )

        for i, parada in enumerate(ruta):
            marca = "➜ " if i == self.paso else "   "
            self.info.insert(
                tk.END, f"{marca}{i + 1}. {parada}\n"
            )

        self.info.insert(
            tk.END, "\nPAQUETES ASIGNADOS:\n"
        )

        for paquete in vehiculo.paquetes:
            self.info.insert(
                tk.END,
                f"{paquete.id} | {paquete.sector}\n"
                f"Peso: {paquete.peso:g} kg | "
                f"Prioridad: {paquete.prioridad}\n\n"
            )

        pendientes = self.resultado["pendientes"]

        self.info.insert(
            tk.END,
            f"Paquetes sin asignar: {len(pendientes)}\n"
        )

        for paquete in pendientes:
            self.info.insert(
                tk.END,
                f"{paquete.id} - {paquete.direccion}\n"
            )

        self.info.insert(
            tk.END,
            f"\nDistancia total estimada de la flota: "
            f"{self.resultado['distancia_total']:.2f} km\n"
        )

        self.info.insert(
            tk.END,
            "\nNota: Dijkstra usa las distancias del CSV "
            "del grafo. La línea del mapa sigue las calles "
            "cuando OSRM está disponible.\n"
            "Los sectores y coordenadas son datos de demostración."
        )

        self.anterior.config(
            state="normal" if self.paso > 0 else "disabled"
        )

        self.siguiente.config(
            state=(
                "normal"
                if self.paso < len(ruta) - 1
                else "disabled"
            )
        )

        total = len(ruta)
        parada_actual = self.paso + 1 if total else 0

        self.estado.config(
            text=f"Parada {parada_actual} de {total}"
        )

    def avanzar(self):
        ruta = self.resultado["vehiculos"][
            self.indice_vehiculo
        ]["paradas"]

        if self.paso < len(ruta) - 1:
            self.paso += 1
            self.mostrar_ruta()

    def retroceder(self):
        if self.paso > 0:
            self.paso -= 1
            self.mostrar_ruta()


def iniciar():
    ventana = tk.Tk()
    Ventana(ventana)
    ventana.mainloop()
