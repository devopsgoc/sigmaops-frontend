# SigmaOps - Sistema de Gestión de Tickets de Infraestructura

Sistema de tickets para infraestructura desarrollado en Django, containerizado para despliegue en Docker y Kubernetes.

## 🚀 Despliegue Rápido

### Ejecución Standalone (sin Docker)

**Windows:**
```cmd
# 1. Copiar carpeta al servidor
# 2. Editar .env.example y renombrar a .env

# Primera vez (instalar dependencias)
run.bat setup

# Ejecutar servidor
run.bat
```

**Linux/MacOS:**
```bash
# 1. Copiar carpeta al servidor
# 2. Editar .env.example y renombrar a .env
chmod +x run.sh

# Primera vez (instalar dependencias)
./run.sh setup

# Ejecutar servidor desarrollo
./run.sh

# Ejecutar servidor producción (Gunicorn)
./run.sh run-prod

# Instalar como servicio systemd
sudo ./run.sh install-service
```

---

### Docker Compose (recomendado para desarrollo)

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd sigmaops_frontend

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de BD

# 3. Construir y ejecutar
docker-compose up -d

# 4. Acceder en http://localhost:8000
```

### Docker (imagen standalone)

```bash
# Construir imagen
docker build -t sigmaops-frontend:latest .

# Ejecutar contenedor
docker run -d \
  --name sigmaops \
  -p 8000:8000 \
  -e DB_HOST=10.68.12.31 \
  -e DB_NAME=claro_sigmaops \
  -e DB_USER=clarosigma \
  -e DB_PASSWORD=test123 \
  -e DEBUG=False \
  -e SECRET_KEY=clave-super-secreta \
  sigmaops-frontend:latest
```

### Kubernetes

```bash
# 1. Construir imagen y subirla a registry
docker build -t sigmaops-frontend:latest .
docker tag sigmaops-frontend:latest tu-registry/sigmaops-frontend:latest
docker push tu-registry/sigmaops-frontend:latest

# 2. Editar k8s/secret.yaml con tus credenciales

# 3. Aplicar manifests
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 4. (Opcional) Ingress
kubectl apply -f k8s/ingress.yaml

# 5. Verificar estado
kubectl get pods -l app=sigmaops
kubectl get svc sigmaops-service
```

## 📁 Estructura del Proyecto

```
sigmaops_frontend/
├── sigmaops/           # Configuración Django
├── tickets/            # App principal
├── templates/          # Templates HTML
├── static/             # CSS, JS
├── k8s/                # Manifests Kubernetes
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## ⚙️ Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DB_NAME` | Nombre de la base de datos | claro_sigmaops |
| `DB_USER` | Usuario de BD | clarosigma |
| `DB_PASSWORD` | Contraseña de BD | (requerido) |
| `DB_HOST` | Host de MariaDB | localhost |
| `DB_PORT` | Puerto de MariaDB | 3306 |
| `DEBUG` | Modo debug | False |
| `SECRET_KEY` | Clave secreta Django | (requerido) |
| `ALLOWED_HOSTS` | Hosts permitidos | * |

## 🔧 Desarrollo Local

```bash
# Crear ambiente virtual
python -m venv venv
.\venv\Scripts\Activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python manage.py runserver
```

## 📊 Funcionalidades

- Dashboard con KPIs
- Gestión de tickets (CRUD)
- Filtros por estado, categoría, prioridad, DC
- Timeline de observaciones
- Panel admin Django
- Diseño dark mode

## 🔒 Seguridad

- Variables sensibles en Secrets de K8s
- CSRF habilitado
- Cookies seguras en producción
- Whitenoise para static files
