# Sistema de Administración — Casa de Asilo
**Equipo 2 | Base de Datos y Lenguajes**

## Requisitos
- Python 3.11+
- `pip install -r requirements.txt`

### Dependencias principales
| Paquete | Uso |
|---|---|
| `customtkinter >= 5.2.2` | Interfaz gráfica |
| `Pillow >= 10.0.0` | Manejo de imágenes |
| `reportlab >= 4.0.0` | Generación de reportes PDF |
| `openpyxl >= 3.1.0` | Exportación a Excel (reserva) |
| `sqlite3` *(stdlib)* | Base de datos |
| `hashlib` *(stdlib)* | Autenticación / hashing |

## Arrancar
```bash
python main.py
```

## Estructura
```
eq2_asilo/
├── main.py                      # Punto de entrada: init BD, login, dashboard
│
├── db/
│   ├── connection.py            # Conexión SQLite y ruta a asilo.db
│   ├── schema.py                # Creación/migración de todas las tablas
│   └── backup_manager.py        # Motor de respaldo/restauración automático
│
├── modules/
│   ├── auth.py                  # Autenticación y gestión de usuarios
│   ├── residentes.py            # CRUD residentes
│   ├── habitaciones.py          # CRUD habitaciones
│   ├── medicacion.py            # CRUD medicación
│   ├── actividades.py           # CRUD actividades
│   └── signos_vitales.py        # CRUD signos vitales
│
├── ui/
│   └── screens/
│       ├── login.py             # Pantalla de inicio de sesión
│       ├── dashboard.py         # Pantalla principal / menú
│       ├── residentes_screen.py # Gestión de residentes
│       ├── habitaciones_screen.py # Gestión de habitaciones
│       ├── medicacion_screen.py # Gestión de medicación
│       ├── actividades_screen.py # Gestión de actividades
│       ├── signos_vitales_screen.py # Registro de signos vitales
│       ├── usuarios_screen.py   # Gestión de usuarios del sistema
│       └── respaldo_screen.py   # Respaldo y restauración de la BD
│
├── reports/
│   └── generador.py             # Generación de reportes PDF
│
├── uploads/
│   └── <CURP_residente>/        # Documentos por residente
│       ├── foto_ine.jpg
│       ├── foto_acta_nacimiento.jpg
│       ├── foto_comprobante_domicilio.png
│       ├── familiar_foto_ine.jpg/png
│       ├── cartilla_salud.jpeg
│       └── comprobante_servicio_medico.jpg
│
├── backups/
│   ├── backup.log               # Historial de respaldos
│   └── respaldo_<fecha>_<tipo>.db.gz  # Respaldos comprimidos
│
├── utils/
│   └── helpers.py               # Funciones auxiliares compartidas
│
├── asilo.db                     # Base de datos SQLite
├── asilo.spec                   # Configuración PyInstaller
├── compilar.bat                 # Script de compilación a .exe (Windows)
└── requirements.txt
```

## Convención de módulos
La UI importa directamente las funciones del módulo correspondiente:
```python
from modules.residentes import listar_residentes, crear_residente
```
No hay API ni servidor intermedio.

## Respaldo automático
El `backup_manager` arranca un scheduler en hilo secundario al iniciar la app. Los respaldos se guardan en `backups/` como archivos `.db.gz` con marca de tiempo. También se puede hacer un respaldo manual desde la pantalla de **Respaldo** en la UI.

## Compilar a ejecutable
```bat
compilar.bat
```
Genera `dist/Asilo/Asilo.exe` usando PyInstaller. El ejecutable incluye todas las dependencias y la base de datos inicial.