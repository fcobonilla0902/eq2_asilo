"""Módulo de autenticación — Responsable: P4"""
# TODO Sprint 1 - P4
#para que el programa valla a la base de datos y confirme si son correctos los usuarios
import getpass
import hashlib  # <--- hasing para contrseñas
from db.connection import get_connection

def inicializar_modulo_auth():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Lista de tablas que se tienen que crear si no exiten
    tablas = ["usuarios_admin", "enfermeros", "doctores"]
    
    for nombre_tabla in tablas:
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {nombre_tabla} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
    
    # usuario de prueba ENCRIPTADO para cada rol
    password_secreta = hashlib.sha256("123".encode()).hexdigest()
    
    usuarios_prueba = [
        ("usuarios_admin", "admin_edson"),
        ("enfermeros", "enfermero_edson"),
        ("doctores", "edson")
    ]
    
    for tabla, user in usuarios_prueba:
        try:
            cursor.execute(f"INSERT INTO {tabla} (usuario, password_hash) VALUES (?, ?)", 
                           (user, password_secreta))
        except:
            pass 
            
    conn.commit()
    conn.close()

inicializar_modulo_auth()
# -- CAPTURAR DATOS --
def capturar_datos():
    print("--- BIENVENIDO AL SISTEMA DEL ASILO ---")
    print("Seleccione su rol:")
    print("1. Administrador")
    print("2. Enfermero")
    print("3. Doctor")
    
    opcion = input("Elija una opción (1-3): ")
    
    rol = ""
    if opcion == "1":
        rol = "admin"
    elif opcion == "2":
        rol = "enfermero"
    elif opcion == "3":
        rol = "doctor"
    else:
        print("Opción no válida.")
        return None, None, None

    usuario = input("Introduce tu nombre de usuario: ")
    password = getpass.getpass("Introduce tu contraseña: ")
    
    return usuario, password, rol

# -- VALIDAR EN BASE DE DATOS --
def validar_usuario(usuario, password, rol):
    # Convertir la contraseña escrita a hash para poder comparar
    password_encrip = hashlib.sha256(password.encode()).hexdigest()
    conn = get_connection()
    cursor = conn.cursor()
    
    # se elige la tabla según el rol
    tabla = ""
    if rol == "admin":
        tabla = "usuarios_admin"
    elif rol == "enfermero":
        tabla = "enfermeros"
    elif rol == "doctor":
        tabla = "doctores"
    
    # se busca al usuario
# Buscamos que coincidan tanto el usuario como el hash de la contraseña
    query = f"SELECT * FROM {tabla} WHERE usuario = ? AND password_hash = ?"
    cursor.execute(query, (usuario, password_encrip))
    resultado = cursor.fetchone()
    
    conn.close()
    
    if resultado:
        return True
    return False

# --- PRUEBA FINAL ---
user, pwd, role = capturar_datos()
if user:
    if validar_usuario(user, pwd, role):
        print(f"¡Acceso concedido! Bienvenido {user}.")
    else:
        print("Usuario o contraseña incorrectos.")