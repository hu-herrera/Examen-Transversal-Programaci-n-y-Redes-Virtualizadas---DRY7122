from netmiko import ConnectHandler
import time

# Datos de conexión al CSR1000v
dispositivo = {
    'device_type': 'cisco_ios',
    'host': '192.168.56.101',
    'username': 'cisco',
    'password': 'cisco123!',
    'secret': 'cisco123!',
    'port': 22,
}

print("=" * 60)
print("Conectando al router CSR1000v...")
print("=" * 60)

net_connect = ConnectHandler(**dispositivo)
net_connect.enable()
print("[OK] Conexion establecida\n")

# ─────────────────────────────────────────────────────────────
# CONFIGURACION EIGRP NOMBRADO IPv4 e IPv6 con AS 100
# La clave: passive-interface va dentro de af-interface
# NO se usa passive-interface directo como en EIGRP clasico
# ─────────────────────────────────────────────────────────────

comandos_eigrp = [
    # Habilitar IPv6 routing (necesario para EIGRP IPv6)
    'ipv6 unicast-routing',

    # EIGRP Nombrado - proceso llamado EXAMEN
    'router eigrp EXAMEN',

    # ── ADDRESS FAMILY IPv4 ──
    'address-family ipv4 unicast autonomous-system 100',
    'eigrp router-id 1.1.1.1',
    'network 0.0.0.0',                 # anuncia todas las redes IPv4

    # Interfaz pasiva IPv4 - metodo correcto en Named EIGRP
    'af-interface GigabitEthernet1',
    'passive-interface',               # <-- SIN nombre de interfaz aqui
    'exit-af-interface',

    # Tambien dejar Loopback11 pasiva (si existe del item 4)
    'af-interface Loopback11',
    'passive-interface',
    'exit-af-interface',

    'no shutdown',
    'exit-address-family',

    # ── ADDRESS FAMILY IPv6 ──
    'address-family ipv6 unicast autonomous-system 100',
    'eigrp router-id 1.1.1.1',

    # Interfaz pasiva IPv6 - mismo metodo
    'af-interface GigabitEthernet1',
    'passive-interface',
    'exit-af-interface',

    'no shutdown',
    'exit-address-family',
]

print("Aplicando configuracion EIGRP Nombrado IPv4/IPv6...")
output_config = net_connect.send_config_set(comandos_eigrp)
print(output_config)
time.sleep(3)

# ─────────────────────────────────────────────────────────────
# VERIFICACION 1: show running-config | section eigrp
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("VERIFICACION: show running-config | section eigrp")
print("=" * 60)
output_eigrp = net_connect.send_command('show running-config | section eigrp')
print(output_eigrp)

# ─────────────────────────────────────────────────────────────
# VERIFICACION 2: IP y estado de interfaces
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("VERIFICACION: show ip interface brief")
print("=" * 60)
output_interfaces = net_connect.send_command('show ip interface brief')
print(output_interfaces)

# ─────────────────────────────────────────────────────────────
# VERIFICACION 3: running-config completo
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("VERIFICACION: show running-config")
print("=" * 60)
output_running = net_connect.send_command(
    'show running-config',
    read_timeout=30
)
print(output_running)

# ─────────────────────────────────────────────────────────────
# VERIFICACION 4: show version
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("VERIFICACION: show version")
print("=" * 60)
output_version = net_connect.send_command('show version')
print(output_version)

net_connect.disconnect()
print("\n[OK] Desconectado del router.")
