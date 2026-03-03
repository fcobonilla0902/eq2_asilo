"""Módulo de autenticación — Responsable: P4"""
# TODO Sprint 1 - P4
#para que el programa valla a la base de datos y confirme si son correctos los usuarios
import getpass
from db.connection import get_connection
def inicializar_modulo_auth():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    # Usuario de prueba
    try:
        cursor.execute("INSERT INTO doctores (usuario, password_hash) VALUES (?, ?)", ("edson", "123"))
        conn.commit()
    except:
        pass 
    conn.close()

inicializar_modulo_auth() # Se ejecuta al abrir el archivo

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
    query = f"SELECT password_hash FROM {tabla} WHERE usuario = ?"
    cursor.execute(query, (usuario,))
    resultado = cursor.fetchone()
    
    conn.close()
    
    if resultado:
        # resultado[0] es la contraseña que está en la BD
        if resultado[0] == password:
            return True
    return False

# --- PRUEBA FINAL ---
user, pwd, role = capturar_datos()
if user:
    if validar_usuario(user, pwd, role):
        print(f"¡Acceso concedido! Bienvenido {user}.")
    else:
        print("Usuario o contraseña incorrectos.")