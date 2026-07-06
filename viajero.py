#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VIAJERO - Calculadora de Distancias Chile <-> Argentina
Autor : Hugo Herrera
Examen: DRY7122

ORDEN:
  INICIO  - Medicion automatica Santiago->Buenos Aires (visual de bienvenida)
  PASO 2  - Solicitar Ciudad de Origen  (Chile)
  PASO 3  - Solicitar Ciudad de Destino (Argentina)
  PASO 4  - Elegir medio de transporte
  PASO 5  - Calcular y mostrar distancia en km, millas y duracion
  PASO 6  - Mostrar narrativa del viaje
  PASO 7  - Salir con 's'
"""

import requests
import time
import sys
import re
from typing import Optional, Dict, List

# ── API ───────────────────────────────────────────────────────
API_KEY     = "c7fe3c99-58bf-4dad-8b7f-864770084902"
GEOCODE_URL = "https://graphhopper.com/api/1/geocode"
ROUTE_URL   = "https://graphhopper.com/api/1/route"

# ── COLORES ───────────────────────────────────────────────────
R   = "\033[0m"
BLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GRN = "\033[92m"
YLW = "\033[93m"
BLU = "\033[94m"
MAG = "\033[95m"
CYN = "\033[96m"

N = 64   # ancho interior del cuadro

# ─────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────
def sin_ansi(t: str) -> str:
    return re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])").sub("", t)

def vlen(t: str) -> int:
    return len(sin_ansi(t))

def linea(c: str = "─", w: int = N + 2) -> None:
    print(DIM + c * w + R)

# ─────────────────────────────────────────────────────────────
# CUADRO ALINEADO
# Regla: │(1) + espacio(1) + texto(vlen) + padding + │(1) = N+2
#        => padding = N - vlen(texto) - 1
# ─────────────────────────────────────────────────────────────
def fila_caja(texto: str) -> str:
    pad = N - vlen(texto) - 1
    return CYN + "│ " + texto + " " * pad + CYN + "│" + R

def caja(titulo: str, filas: List[str]) -> None:
    print(CYN + "┌" + "─" * N + "┐" + R)
    print(fila_caja(BLD + titulo + R))
    print(CYN + "├" + "─" * N + "┤" + R)
    for f in filas:
        print(fila_caja(f))
    print(CYN + "└" + "─" * N + "┘" + R)

# ─────────────────────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────────────────────
def encabezado() -> None:
    print(CYN + "╔" + "═" * (N + 2) + "╗" + R)
    print(CYN + "║" + BLD + "  VIAJERO  –  Calculadora de Distancias".ljust(N + 2) + R + CYN + "║" + R)
    print(CYN + "║" + DIM + "  Chile  ↔  Argentina   |   GraphHopper API".ljust(N + 2) + R + CYN + "║" + R)
    print(CYN + "╚" + "═" * (N + 2) + "╝" + R)

# ─────────────────────────────────────────────────────────────
# SPINNER
# ─────────────────────────────────────────────────────────────
def spinner(seg: float, msg: str = "Calculando") -> None:
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    fin = time.time() + seg
    i = 0
    while time.time() < fin:
        sys.stdout.write(f"\r  {YLW}{chars[i % len(chars)]}  {msg}...{R}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * 55 + "\r")
    sys.stdout.flush()

# ─────────────────────────────────────────────────────────────
# API
# ─────────────────────────────────────────────────────────────
def geocodificar(ciudad: str, pais: str) -> Optional[str]:
    try:
        r = requests.get(GEOCODE_URL,
                         params={"q": f"{ciudad}, {pais}", "locale": "es",
                                 "limit": 1, "key": API_KEY},
                         timeout=10)
        if r.status_code == 200:
            hits = r.json().get("hits", [])
            if hits:
                p = hits[0]["point"]
                return f"{p['lat']},{p['lng']}"
    except requests.RequestException:
        pass
    return None

def obtener_ruta(origen: str, destino: str, vehiculo: str,
                 pais_o: str, pais_d: str) -> Optional[Dict]:
    co = geocodificar(origen, pais_o)
    cd = geocodificar(destino, pais_d)
    if not co:
        print(f"  {RED}✗ No se encontro '{origen}' en {pais_o}.{R}")
        return None
    if not cd:
        print(f"  {RED}✗ No se encontro '{destino}' en {pais_d}.{R}")
        return None
    try:
        r = requests.get(ROUTE_URL,
                         params={"point": [co, cd], "vehicle": vehiculo,
                                 "key": API_KEY, "locale": "es",
                                 "instructions": "true"},
                         timeout=20)
        if r.status_code == 200:
            return r.json()
        print(f"  {RED}✗ API error {r.status_code}.{R}")
    except requests.RequestException as e:
        print(f"  {RED}✗ Error de red: {e}{R}")
    return None

# ─────────────────────────────────────────────────────────────
# PASO 5: Mostrar cuadro con km, millas y duracion
# ─────────────────────────────────────────────────────────────
def mostrar_distancia(data: Dict, origen: str, destino: str,
                      transporte: str,
                      pais_o: str = "Chile",
                      pais_d: str = "Argentina") -> bool:
    if not data or not data.get("paths"):
        print(f"  {RED}Sin datos de ruta.{R}")
        return False

    path   = data["paths"][0]
    km     = path["distance"] / 1000
    millas = km * 0.621371
    seg    = path["time"] / 1000
    horas  = int(seg // 3600)
    mins   = int((seg % 3600) // 60)

    filas = [
        f"{BLD}Origen      :{R} {origen} ({pais_o})",
        f"{BLD}Destino     :{R} {destino} ({pais_d})",
        f"{BLD}Transporte  :{R} {transporte}",
        DIM + "─" * (N - 2) + R,
        f"{BLD}Kilometros  :{R}  {GRN}{km:>10.2f} km{R}",
        f"{BLD}Millas      :{R}  {YLW}{millas:>10.2f} millas{R}",
        f"{BLD}Duracion    :{R}  {CYN}aprox. {horas} h  {mins:02d} min{R}",
    ]
    caja("RESULTADO DEL VIAJE", filas)
    return True

# ─────────────────────────────────────────────────────────────
# PASO 6: Narrativa del viaje
# ─────────────────────────────────────────────────────────────
def mostrar_narrativa(data: Dict) -> None:
    pasos = data["paths"][0].get("instructions", [])
    if not pasos:
        print(f"  {YLW}(Sin instrucciones disponibles){R}")
        return

    print(f"\n{BLD}{CYN}  NARRATIVA DEL VIAJE{R}")
    linea("─")
    for n, paso in enumerate(pasos, 1):
        txt  = paso.get("text", "")
        dist = paso.get("distance", 0) / 1000
        tlow = txt.lower()

        if any(k in tlow for k in ("llegar", "fin", "destino", "arrive")):
            ico = f"{GRN}✔{R}"
        elif any(k in tlow for k in ("gira", "girar", "doblar")):
            ico = f"{YLW}↻{R}"
        elif n == 1:
            ico = f"{BLU}▶{R}"
        else:
            ico = f"{DIM}→{R}"

        ds = f"  {DIM}({dist:.1f} km){R}" if dist > 0 else ""
        print(f"  {YLW}{n:>3}.{R}  {ico}  {txt}{ds}")
    linea("─")

# ─────────────────────────────────────────────────────────────
# INICIO: medicion automatica solo visual (sin pedir nada)
# ─────────────────────────────────────────────────────────────
def bienvenida_automatica() -> None:
    print(f"\n{DIM}  Calculando distancia de referencia:"
          f" Santiago (Chile) → Buenos Aires (Argentina)...{R}\n")
    spinner(2.5, "Consultando GraphHopper")
    data = obtener_ruta("Santiago", "Buenos Aires", "car", "Chile", "Argentina")
    if data:
        path   = data["paths"][0]
        km     = path["distance"] / 1000
        millas = km * 0.621371
        seg    = path["time"] / 1000
        horas  = int(seg // 3600)
        mins   = int((seg % 3600) // 60)
        print(f"  {DIM}Distancia Chile → Argentina: "
              f"{GRN}{km:.0f} km{R}{DIM}  /  "
              f"{YLW}{millas:.0f} millas{R}")
    print()

# ─────────────────────────────────────────────────────────────
# TRANSPORTES
# ─────────────────────────────────────────────────────────────
TRANSPORTES = {
    "1": ("car",  "Auto"),
    "2": ("bike", "Bicicleta"),
    "3": ("foot", "Caminando"),
}

# ─────────────────────────────────────────────────────────────
# LOOP INTERACTIVO (pasos 2 al 7)
# ─────────────────────────────────────────────────────────────
def loop_interactivo() -> None:
    while True:
        linea("═")

        # ── PASO 2: Ciudad de Origen ──────────────────────
        print(f"\n{BLD}{CYN}  PASO 2  ·  CIUDAD DE ORIGEN  (Chile){R}")
        while True:
            origen = input(f"  {BLD}Ciudad de Origen en Chile :{R}  ").strip()
            if origen:
                break
            print(f"  {YLW}Por favor ingresa el nombre de la ciudad.{R}")

        # ── PASO 3: Ciudad de Destino ─────────────────────
        print(f"\n{BLD}{CYN}  PASO 3  ·  CIUDAD DE DESTINO  (Argentina){R}")
        while True:
            destino = input(f"  {BLD}Ciudad de Destino en Argentina :{R}  ").strip()
            if destino:
                break
            print(f"  {YLW}Por favor ingresa el nombre de la ciudad.{R}")

        # ── PASO 4: Medio de transporte ───────────────────
        print(f"\n{BLD}{CYN}  PASO 4  ·  MEDIO DE TRANSPORTE{R}")
        print(f"  {GRN}1.{R}  Auto")
        print(f"  {YLW}2.{R}  Bicicleta")
        print(f"  {BLU}3.{R}  Caminando")
        while True:
            op = input(f"  {BLD}Elige una opcion (1, 2 o 3) :{R}  ").strip()
            if op in TRANSPORTES:
                vehiculo, nombre = TRANSPORTES[op]
                break
            print(f"  {RED}Opcion no valida. Ingresa 1, 2 o 3.{R}")

        # ── Calcular ruta con el transporte elegido ───────
        print()
        spinner(2.0, f"Calculando ruta en {nombre}")
        data = obtener_ruta(origen, destino, vehiculo, "Chile", "Argentina")

        # ── PASO 5: Cuadro con km, millas y duracion ──────
        print(f"\n{BLD}{CYN}  PASO 5  ·  RESULTADO{R}\n")
        if not data:
            print(f"  {RED}No se pudo calcular la ruta.{R}")
            print(f"  {YLW}Verifica que los nombres de las ciudades sean correctos.{R}")
        else:
            ok = mostrar_distancia(data, origen, destino,
                                   nombre, "Chile", "Argentina")

            # ── PASO 6: Narrativa del viaje ────────────────
            if ok:
                mostrar_narrativa(data)

        # ── PASO 7: Salir con 's' (unico punto de salida) ─
        print()
        linea("─")
        resp = input(
            f"  {BLD}¿Calcular otra ruta?  "
            f"[Enter = continuar   |   s = salir]{R}  "
        ).strip().lower()
        if resp == "s":
            print(f"\n  {GRN}{BLD}¡Hasta luego! Gracias por usar VIAJERO.{R}\n")
            sys.exit(0)
        print()

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def main() -> None:
    encabezado()            # Header
    bienvenida_automatica() # Medicion de bienvenida (visual)
    loop_interactivo()      # Pasos 2 al 7

if __name__ == "__main__":
    main()
