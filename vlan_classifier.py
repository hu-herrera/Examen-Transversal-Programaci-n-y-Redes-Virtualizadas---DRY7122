#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clasificador de VLANs con capacidades interactivas y de línea de comandos.
Cumple con el estándar IEEE 802.1Q y proporciona información extendida.
"""

import sys
import re
import argparse
from typing import Dict, Optional, Tuple


# Configuración de colores ANSI para terminales compatibles
COLOR = {
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "cyan": "\033[96m",
    "bold": "\033[1m",
    "reset": "\033[0m"
}

# Base de datos simulada de VLANs conocidas (puede ampliarse)
KNOWN_VLANS: Dict[int, Dict[str, str]] = {
    1: {"name": "Default", "status": "active"},
    10: {"name": "Management", "status": "active"},
    20: {"name": "VoIP", "status": "active"},
    30: {"name": "Data", "status": "active"},
    100: {"name": "Guest", "status": "inactive"},
    999: {"name": "Native", "status": "active"},
}


def classify_vlan(vlan_id: int) -> Dict[str, str]:
    """
    Clasifica una VLAN según su número y retorna información detallada.

    Args:
        vlan_id: Número de VLAN (1-4094)

    Returns:
        Diccionario con campos: vlan_id, range_type, color, name, status
    """
    if 1 <= vlan_id <= 1005:
        range_type = "NORMAL"
        color = COLOR["green"]
    elif 1006 <= vlan_id <= 4094:
        range_type = "EXTENDIDO"
        color = COLOR["yellow"]
    else:
        range_type = "OUT_OF_RANGE"
        color = COLOR["red"]

    known = KNOWN_VLANS.get(vlan_id, {})
    name = known.get("name", "unknown")
    status = known.get("status", "undefined")

    return {
        "vlan_id": str(vlan_id),
        "range_type": range_type,
        "color": color,
        "name": name,
        "status": status,
    }


def print_vlan_info(info: Dict[str, str]) -> None:
    """
    Imprime la información de la VLAN con formato tabulado y colores.
    """
    color = info["color"]
    reset = COLOR["reset"]
    bold = COLOR["bold"]

    print("\n" + "=" * 52)
    print(f"{bold}VLAN {info['vlan_id']}{reset}")
    print(f"  Range: {color}{info['range_type']}{reset}")
    print(f"  Name:  {info['name']}")
    print(f"  Status:{info['status']}")
    print("=" * 52)


def interactive_mode() -> None:
    """
    Bucle interactivo para consultar múltiples VLANs.
    """
    print(COLOR["cyan"] + "VLAN Classifier - Interactive Mode" + COLOR["reset"])
    print("Enter a VLAN number (1-4094) or 'q' to quit.\n")

    while True:
        try:
            raw = input("vlan> ").strip()
            if raw.lower() in ("q", "quit", "exit"):
                break

            if not re.match(r"^\d+$", raw):
                print(COLOR["red"] + "Error: numeric value required." + COLOR["reset"])
                continue

            vlan_id = int(raw)
            if vlan_id < 1 or vlan_id > 4094:
                print(COLOR["red"] + f"Error: {vlan_id} out of range (1-4094)." + COLOR["reset"])
                continue

            info = classify_vlan(vlan_id)
            print_vlan_info(info)

            # Consejos contextuales (mejora la experiencia)
            if vlan_id == 1:
                print(COLOR["yellow"] + "Tip: VLAN 1 is the default VLAN on Cisco devices." + COLOR["reset"])
            elif vlan_id in (10, 20, 30):
                use = "management" if vlan_id == 10 else "VoIP" if vlan_id == 20 else "data"
                print(COLOR["yellow"] + f"Tip: VLAN {vlan_id} is commonly used for {use}." + COLOR["reset"])

        except KeyboardInterrupt:
            print("\n")
            break
        except Exception as e:
            print(COLOR["red"] + f"Unexpected error: {e}" + COLOR["reset"])

    print(COLOR["cyan"] + "Goodbye." + COLOR["reset"])


def main() -> None:
    """
    Punto de entrada principal. Soporta modo interactivo o consulta única.
    """
    parser = argparse.ArgumentParser(
        description="Classify VLAN numbers according to IEEE 802.1Q."
    )
    parser.add_argument(
        "vlan",
        nargs="?",
        type=int,
        help="single VLAN number to classify (omit for interactive mode)"
    )
    args = parser.parse_args()

    if args.vlan is not None:
        try:
            if args.vlan < 1 or args.vlan > 4094:
                print(COLOR["red"] + f"Error: {args.vlan} out of range." + COLOR["reset"])
                sys.exit(1)
            info = classify_vlan(args.vlan)
            print_vlan_info(info)
        except Exception as e:
            print(COLOR["red"] + f"Error: {e}" + COLOR["reset"])
            sys.exit(1)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
