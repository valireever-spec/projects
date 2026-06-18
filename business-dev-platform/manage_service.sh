#!/bin/bash
# Business Dev Platform Service Management Script

SERVICE_NAME="business-dev-platform"
PROJECT_DIR="/home/vali/projects/business-dev-platform"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

function print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

function print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

function check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use 'sudo')"
        exit 1
    fi
}

function install_service() {
    print_status "Installing Business Dev Platform service..."

    # Copy startup script
    cp "$PROJECT_DIR/start_service.sh" /usr/local/bin/business-dev-start.sh
    chmod +x /usr/local/bin/business-dev-start.sh
    print_status "Startup script installed"

    # Copy systemd service file
    cp "$PROJECT_DIR/business-dev-platform.service" "$SERVICE_FILE"
    print_status "Systemd service file installed"

    # Reload systemd daemon
    systemctl daemon-reload
    print_status "Systemd daemon reloaded"

    # Create log directory
    mkdir -p /var/log/business-dev-platform
    chown vali:vali /var/log/business-dev-platform
    chmod 755 /var/log/business-dev-platform
    print_status "Log directory created"

    print_status "Service installed successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Start the service:   sudo systemctl start $SERVICE_NAME"
    echo "  2. Enable at startup:   sudo systemctl enable $SERVICE_NAME"
    echo "  3. Check status:        sudo systemctl status $SERVICE_NAME"
    echo "  4. View logs:           sudo tail -f /var/log/business-dev-platform/app.log"
}

function start_service() {
    check_root
    print_status "Starting $SERVICE_NAME..."
    systemctl start "$SERVICE_NAME"

    # Wait a moment for service to start
    sleep 2

    # Show status
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_status "Service started successfully!"

        # Try to get the port
        if [ -f "$PROJECT_DIR/.service_port" ]; then
            PORT=$(cat "$PROJECT_DIR/.service_port")
            print_status "Application is running on http://localhost:$PORT"
        fi
    else
        print_error "Failed to start service. Check logs with: sudo systemctl status $SERVICE_NAME"
    fi
}

function stop_service() {
    check_root
    print_status "Stopping $SERVICE_NAME..."
    systemctl stop "$SERVICE_NAME"
    print_status "Service stopped"
}

function restart_service() {
    check_root
    print_status "Restarting $SERVICE_NAME..."
    systemctl restart "$SERVICE_NAME"

    # Wait a moment for service to restart
    sleep 2

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_status "Service restarted successfully!"

        # Try to get the port
        if [ -f "$PROJECT_DIR/.service_port" ]; then
            PORT=$(cat "$PROJECT_DIR/.service_port")
            print_status "Application is running on http://localhost:$PORT"
        fi
    else
        print_error "Failed to restart service. Check logs with: sudo systemctl status $SERVICE_NAME"
    fi
}

function status_service() {
    echo ""
    systemctl status "$SERVICE_NAME"
    echo ""

    if [ -f "$PROJECT_DIR/.service_port" ]; then
        PORT=$(cat "$PROJECT_DIR/.service_port")
        echo -e "${GREEN}Port:${NC} http://localhost:$PORT"
    fi

    if [ -f "/var/log/business-dev-platform/app.log" ]; then
        echo -e "${GREEN}Last 5 log lines:${NC}"
        tail -5 "/var/log/business-dev-platform/app.log"
    fi
}

function enable_service() {
    check_root
    print_status "Enabling $SERVICE_NAME to start at boot..."
    systemctl enable "$SERVICE_NAME"
    print_status "Service enabled"
}

function disable_service() {
    check_root
    print_status "Disabling $SERVICE_NAME from starting at boot..."
    systemctl disable "$SERVICE_NAME"
    print_status "Service disabled"
}

function view_logs() {
    print_status "Viewing logs (Ctrl+C to exit)..."
    tail -f /var/log/business-dev-platform/app.log
}

function uninstall_service() {
    check_root
    print_warning "Uninstalling Business Dev Platform service..."

    # Stop service
    systemctl stop "$SERVICE_NAME" 2>/dev/null || true

    # Disable service
    systemctl disable "$SERVICE_NAME" 2>/dev/null || true

    # Remove files
    rm -f "$SERVICE_FILE"
    rm -f /usr/local/bin/business-dev-start.sh

    # Reload systemd
    systemctl daemon-reload

    print_status "Service uninstalled successfully"
}

# Main command handling
case "${1:-status}" in
    install)
        check_root
        install_service
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        status_service
        ;;
    enable)
        enable_service
        ;;
    disable)
        disable_service
        ;;
    logs)
        view_logs
        ;;
    uninstall)
        uninstall_service
        ;;
    *)
        echo "Business Dev Platform Service Manager"
        echo ""
        echo "Usage: sudo $0 <command>"
        echo ""
        echo "Commands:"
        echo "  install      - Install the service (run this first)"
        echo "  start        - Start the service"
        echo "  stop         - Stop the service"
        echo "  restart      - Restart the service"
        echo "  status       - Show service status"
        echo "  enable       - Enable service at boot"
        echo "  disable      - Disable service at boot"
        echo "  logs         - View live logs"
        echo "  uninstall    - Uninstall the service"
        echo ""
        echo "Examples:"
        echo "  sudo $0 install      # First time setup"
        echo "  sudo $0 start        # Start the service"
        echo "  sudo $0 status       # Check if running"
        echo "  sudo $0 logs         # Watch logs in real-time"
        exit 1
        ;;
esac
