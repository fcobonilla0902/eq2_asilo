from db.schema import init_db
from modules.actividades import (
    crear_actividad,
    listar_actividades,
    obtener_actividad,
    actualizar_actividad,
    eliminar_actividad,
    registrar_participacion,
    listar_participaciones_por_actividad,
)
from modules.residentes import listar_residentes

# Inicializar DB
init_db()

print("=== PRUEBA ACTIVIDADES ===")

# Crear actividad
print("\nCreando actividad...")
id_act = crear_actividad({
    "nombre": "Terapia grupal",
    "es_fija": "Sí",
    "fecha_programada": "2026-03-25",
    "hora_programada": "10:00"
})
print("ID creada:", id_act)

# Listar
print("\nListando actividades...")
acts = listar_actividades()
for a in acts:
    print(dict(a))

# Obtener
print("\nObteniendo actividad...")
act = obtener_actividad(id_act)
print(dict(act) if act else None)

# Actualizar
print("\nActualizando actividad...")
ok = actualizar_actividad(id_act, {
    "nombre": "Terapia ocupacional",
    "hora_programada": "11:00"
})
print("Actualizada:", ok)

# Ver residentes existentes
print("\nListando residentes...")
residentes = listar_residentes()
for r in residentes:
    print(dict(r))

# Participación
if residentes:
    id_residente_real = dict(residentes[0])["id_residente"]

    print("\nRegistrando participación...")
    id_part = registrar_participacion({
        "id_residente": id_residente_real,
        "id_actividad": id_act,
        "fecha": "2026-03-25",
        "hora": "11:00",
        "participo": 1
    })
    print("Participación ID:", id_part)

    print("\nParticipaciones por actividad...")
    parts = listar_participaciones_por_actividad(id_act)
    for p in parts:
        print(dict(p))
else:
    print("\nNo hay residentes registrados. No se pudo probar participación.")

# Eliminar
print("\nEliminando actividad...")
ok = eliminar_actividad(id_act)
print("Eliminada:", ok)

print("\n=== FIN ===")