# Script para determinar si una VLAN es normal o extendida
try:
    vlan = int(input("Ingrese el número de VLAN: "))
    if 1 <= vlan <= 1005:
        print(f"La VLAN {vlan} pertenece al RANGO NORMAL.")
    elif 1006 <= vlan <= 4094:
        print(f"La VLAN {vlan} pertenece al RANGO EXTENDIDO.")
    else:
        print("Número de VLAN fuera de rango (1-4094).")
except ValueError:
    print("Por favor, ingrese un número válido.")
