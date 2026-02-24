# Sistema de Administración — Casa de Asilo
**Equipo 2 | Base de Datos y Lenguajes**

## Requisitos
- Python 3.11+
- `pip install -r requirements.txt`

## Arrancar
```bash
python main.py
```

## Estructura
```
asilo/
├── main.py               # Punto de entrada
├── db/
│   ├── connection.py     # Conexión SQLite
│   └── schema.py         # Creación de tablas
├── modules/
│   ├── residentes.py     # CRUD residentes ← P1
│   ├── medicacion.py     # CRUD medicación ← P2
│   ├── actividades.py    # CRUD actividades ← P3
│   ├── signos_vitales.py # CRUD signos vitales ← P3
│   ├── auth.py           # Autenticación ← P4
│   └── enfermeros.py     # CRUD enfermeros ← P4
├── ui/
│   ├── screens/          # Pantallas completas ← P5, P6
│   └── components/       # Componentes reutilizables ← P5, P6
├── reports/
│   └── generador.py      # Reportes PDF ← P7
└── utils/
    └── helpers.py        # Funciones auxiliares
```

## Convención de módulos
La UI importa directamente las funciones del módulo correspondiente:
```python
from modules.residentes import listar_residentes, crear_residente
```
No hay API ni servidor intermedio.
