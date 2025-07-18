# SGUL - Sistema de Gestión Universitaria

## Requisitos

- Python 3.10+
- PostgreSQL (recomendado, aunque puedes usar SQLite para pruebas)
- Git

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu_usuario/tu_repo.git
cd tu_repo
```

### 2. Crear y activar entorno virtual

#### En **Linux**:

```bash
python3 -m venv venv
source venv/bin/activate
```

#### En **Windows**:

```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos

#### Opción A: Usar PostgreSQL (recomendado)

1. Instala PostgreSQL.
2. Crea una base de datos y un usuario:
   ```sql
   CREATE DATABASE sgul;
   CREATE USER sguluser WITH PASSWORD 'sgulpass';
   GRANT ALL PRIVILEGES ON DATABASE sgul TO sguluser;
   ```
3. Modifica `crm/settings.py` con tus credenciales:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'sgul',
           'USER': 'sguluser',
           'PASSWORD': 'sgulpass',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

#### Opción B: Usar SQLite (solo para pruebas)

No necesitas hacer nada, pero asegúrate de que en `settings.py` esté configurado para usar SQLite.

### 5. Migrar y poblar la base de datos

```bash
python manage.py migrate
```

Si tienes un archivo de datos iniciales (por ejemplo, `gestion/fixtures/datos_iniciales.json`):

```bash
python manage.py loaddata gestion/fixtures/datos_iniciales.json
```

> **Nota:** Si tienes un script SQL de estructura y datos, puedes importarlo con:
> ```bash
> psql -U sguluser -d sgul -f scripts/estructura_y_datos.sql
> ```

### 6. Crear superusuario

```bash
python manage.py createsuperuser
```

### 7. Ejecutar el servidor

```bash
python manage.py runserver
```

Abre [http://localhost:8000/gestion/](http://localhost:8000/gestion/) en tu navegador.

---

## Notas adicionales

- Si usas Windows y tienes problemas con dependencias, instala [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
- Si usas Linux, asegúrate de tener instalados los headers de Python y PostgreSQL:
  ```bash
  sudo apt-get install python3-dev libpq-dev
  ```
- Si necesitas poblar la base de datos con datos reales, pide el archivo de volcado SQL o JSON a tu compañero/a.

---

## Estructura del proyecto

- `gestion/` - App principal
- `crm/` - Configuración Django
- `requirements.txt` - Dependencias
- `scripts/` - (Opcional) Scripts SQL para poblar la base de datos
- `gestion/fixtures/` - (Opcional) Datos iniciales en formato JSON

---

## Usuarios de prueba

- **Superadmin:**  
  Usuario: `superadmin`  
  Contraseña: `superadmin123`

- **Ventas:**  
  Usuario: `ventas1`  
  Contraseña: `ventas123`

---

## Contacto

Para dudas, contacta a: [tu_email@dominio.com] 