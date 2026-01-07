#!/bin/bash
# =============================================================================
# SigmaOps - Script de instalación y ejecución (Linux/MacOS)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  SigmaOps - Sistema de Tickets        ${NC}"
echo -e "${BLUE}========================================${NC}"

# Función para verificar si existe el ambiente virtual
check_venv() {
    if [ -d "venv" ]; then
        return 0
    else
        return 1
    fi
}

# Función para crear ambiente virtual e instalar dependencias
setup() {
    echo -e "\n${YELLOW}[1/4] Verificando Python...${NC}"
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python 3 no está instalado${NC}"
        exit 1
    fi
    python3 --version

    echo -e "\n${YELLOW}[2/4] Creando ambiente virtual...${NC}"
    python3 -m venv venv

    echo -e "\n${YELLOW}[3/4] Activando ambiente virtual...${NC}"
    source venv/bin/activate

    echo -e "\n${YELLOW}[4/4] Instalando dependencias...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt

    echo -e "\n${GREEN}✓ Instalación completada${NC}"
    echo -e "${YELLOW}Recuerda configurar el archivo .env con tus credenciales de BD${NC}"
}

# Función para ejecutar en modo desarrollo
run_dev() {
    echo -e "\n${YELLOW}Iniciando servidor de desarrollo...${NC}"
    
    if ! check_venv; then
        echo -e "${RED}Error: Ambiente virtual no encontrado. Ejecuta primero: $0 setup${NC}"
        exit 1
    fi

    source venv/bin/activate
    
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}Advertencia: Archivo .env no encontrado, copiando desde .env.example${NC}"
        cp .env.example .env
    fi

    echo -e "${GREEN}Servidor disponible en: http://127.0.0.1:8000${NC}"
    python manage.py runserver 0.0.0.0:8000
}

# Función para ejecutar en modo producción
run_prod() {
    echo -e "\n${YELLOW}Iniciando servidor de producción...${NC}"
    
    if ! check_venv; then
        echo -e "${RED}Error: Ambiente virtual no encontrado. Ejecuta primero: $0 setup${NC}"
        exit 1
    fi

    source venv/bin/activate
    
    if [ ! -f ".env" ]; then
        echo -e "${RED}Error: Archivo .env no encontrado${NC}"
        exit 1
    fi

    echo -e "${YELLOW}Recolectando archivos estáticos...${NC}"
    python manage.py collectstatic --noinput

    echo -e "${GREEN}Servidor disponible en: http://0.0.0.0:8000${NC}"
    gunicorn --bind 0.0.0.0:8000 --workers 3 sigmaops.wsgi:application
}

# Función para ejecutar como servicio systemd
install_service() {
    echo -e "\n${YELLOW}Instalando como servicio systemd...${NC}"
    
    SERVICE_FILE="/etc/systemd/system/sigmaops.service"
    
    sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=SigmaOps - Sistema de Tickets
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
Environment=PATH=$SCRIPT_DIR/venv/bin
ExecStart=$SCRIPT_DIR/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 sigmaops.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable sigmaops
    sudo systemctl start sigmaops

    echo -e "${GREEN}✓ Servicio instalado y ejecutándose${NC}"
    echo -e "Comandos útiles:"
    echo -e "  sudo systemctl status sigmaops"
    echo -e "  sudo systemctl restart sigmaops"
    echo -e "  sudo systemctl stop sigmaops"
}

# Menú de ayuda
show_help() {
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos:"
    echo "  setup          Instala ambiente virtual y dependencias"
    echo "  run            Ejecuta en modo desarrollo (default)"
    echo "  run-prod       Ejecuta en modo producción con Gunicorn"
    echo "  install-service Instala como servicio systemd (Linux)"
    echo "  help           Muestra esta ayuda"
    echo ""
}

# Main
case "${1:-run}" in
    setup)
        setup
        ;;
    run|dev)
        run_dev
        ;;
    run-prod|prod)
        run_prod
        ;;
    install-service|service)
        install_service
        ;;
    help|-h|--help)
        show_help
        ;;
    *)
        echo -e "${RED}Comando desconocido: $1${NC}"
        show_help
        exit 1
        ;;
esac
