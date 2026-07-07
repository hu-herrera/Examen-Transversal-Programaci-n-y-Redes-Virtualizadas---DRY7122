#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Autenticación con Hash y SQLite
Autor: Hugo Herrera
Examen: DRY7122
Puerto: 5800
"""

import sqlite3
import hashlib
from flask import Flask, request, render_template_string

# ── CONFIGURACIÓN ─────────────────────────────────────────────
DB_NAME = 'usuarios.db'
PUERTO = 5800

# Integrantes del grupo (usuarios)
INTEGRANTES = [
    "Hugo Herrera"
    
    
    
]

# Contraseña predeterminada (puedes cambiarla)
PASSWORD_DEFAULT = "1234"

app = Flask(__name__)


# ══════════════════════════════════════════════════════════════
# BASE DE DATOS
# ══════════════════════════════════════════════════════════════

def get_db():
    """Retorna conexión a SQLite."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Crea la tabla y los usuarios si no existen."""
    conn = get_db()
    # Crear tabla
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # Insertar cada integrante con su hash
    for nombre in INTEGRANTES:
        # Calcular hash SHA256 de la contraseña
        hash_obj = hashlib.sha256(PASSWORD_DEFAULT.encode())
        hash_hex = hash_obj.hexdigest()

        # Insertar solo si no existe
        existing = conn.execute(
            "SELECT id FROM usuarios WHERE username = ?", (nombre,)
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO usuarios (username, password_hash) VALUES (?, ?)",
                (nombre, hash_hex)
            )

    conn.commit()
    conn.close()
    print(f"[+] Base de datos '{DB_NAME}' inicializada con {len(INTEGRANTES)} usuarios.")


# ══════════════════════════════════════════════════════════════
# VISTAS WEB
# ══════════════════════════════════════════════════════════════

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Autenticación DRY7122</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            width: 380px;
            text-align: center;
        }
        h2 {
            color: #1a1a2e;
            margin-bottom: 5px;
        }
        .subtitle {
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
        }
        input {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border: 1px solid #ddd;
            border-radius: 6px;
            box-sizing: border-box;
            font-size: 14px;
        }
        input:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }
        button {
            width: 100%;
            padding: 12px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            background: #0056b3;
        }
        .msg {
            margin-top: 15px;
            padding: 10px;
            border-radius: 6px;
            font-weight: 500;
        }
        .msg.success {
            background: #d4edda;
            color: #155724;
        }
        .msg.error {
            background: #f8d7da;
            color: #721c24;
        }
        .users-list {
            margin-top: 15px;
            font-size: 13px;
            color: #555;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 6px;
        }
        .users-list strong {
            color: #1a1a2e;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔐 Validación de Usuarios</h2>
        <p class="subtitle">Examen Transversal DRY7122</p>

        <form method="POST">
            <input type="text" name="username" placeholder="Nombre de usuario" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <button type="submit">Validar</button>
        </form>

        {% if mensaje %}
            <div class="msg {{ tipo }}">
                {{ mensaje }}
            </div>
        {% endif %}

        <div class="users-list">
            <strong>Usuarios registrados:</strong><br>
            {% for u in usuarios %}
                {{ u }}{% if not loop.last %} • {% endif %}
            {% endfor %}
            <br><small>Contraseña predeterminada: <strong>1234</strong></small>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    mensaje = ""
    tipo = "success"

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            mensaje = "❌ Complete todos los campos."
            tipo = "error"
        else:
            # Buscar usuario en la base de datos
            conn = get_db()
            user = conn.execute(
                "SELECT * FROM usuarios WHERE username = ?", (username,)
            ).fetchone()
            conn.close()

            if user:
                # Calcular hash de la contraseña ingresada
                hash_calc = hashlib.sha256(password.encode()).hexdigest()
                if hash_calc == user['password_hash']:
                    mensaje = f"✅ ¡Bienvenido {username}! Autenticación exitosa."
                    tipo = "success"
                else:
                    mensaje = "❌ Contraseña incorrecta."
                    tipo = "error"
            else:
                mensaje = "❌ Usuario no encontrado."
                tipo = "error"

    return render_template_string(
        HTML_FORM,
        mensaje=mensaje,
        tipo=tipo,
        usuarios=INTEGRANTES
    )


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    init_db()
    print(f"\n[+] Servidor web corriendo en: http://0.0.0.0:{PUERTO}")
    print(f"[+] Usuarios registrados: {', '.join(INTEGRANTES)}")
    print(f"[+] Contraseña predeterminada: {PASSWORD_DEFAULT}\n")
    app.run(host='0.0.0.0', port=PUERTO, debug=False)
