# Business Dev Platform — Service Setup Guide

This guide explains how to run the Business Dev Platform as a systemd service with automatic port detection.

## Quick Start (3 steps)

### 1. Install the Service
```bash
sudo /home/vali/projects/business-dev-platform/manage_service.sh install
```

This will:
- Copy the startup script to `/usr/local/bin/`
- Install the systemd service
- Create the log directory `/var/log/business-dev-platform/`
- Reload systemd

### 2. Start the Service
```bash
sudo /home/vali/projects/business-dev-platform/manage_service.sh start
```

The service will automatically:
- Find an available port (starting from 8000)
- Start the FastAPI application
- Create a log file at `/var/log/business-dev-platform/app.log`

### 3. Access the Application
Check which port was assigned:
```bash
sudo /home/vali/projects/business-dev-platform/manage_service.sh status
```

Visit the URL shown (e.g., `http://localhost:8001`)

## Service Management Commands

All commands use the management script:

```bash
sudo /home/vali/projects/business-dev-platform/manage_service.sh <command>
```

### Available Commands

| Command | Description |
|---------|-------------|
| `install` | Install the service (run first) |
| `start` | Start the service |
| `stop` | Stop the service |
| `restart` | Restart the service |
| `status` | Show service status and logs |
| `enable` | Enable service to start at boot |
| `disable` | Disable service from starting at boot |
| `logs` | View live logs (tail -f) |
| `uninstall` | Uninstall the service |

### Examples

```bash
# First time setup
sudo /home/vali/projects/business-dev-platform/manage_service.sh install

# Start the service
sudo /home/vali/projects/business-dev-platform/manage_service.sh start

# Check status
sudo /home/vali/projects/business-dev-platform/manage_service.sh status

# Enable to start on boot
sudo /home/vali/projects/business-dev-platform/manage_service.sh enable

# View real-time logs
sudo /home/vali/projects/business-dev-platform/manage_service.sh logs

# Stop the service
sudo /home/vali/projects/business-dev-platform/manage_service.sh stop
```

## Port Detection Logic

The service automatically finds an available port using this logic:

1. Check port 8000 (preferred)
2. If 8000 is in use, try 8001, 8002, 8003, etc.
3. Searches up to port 8010
4. If no port found, service fails with error

The assigned port is saved to: `/home/vali/projects/business-dev-platform/.service_port`

### Check Current Port
```bash
cat /home/vali/projects/business-dev-platform/.service_port
```

## Logs

All logs are written to: `/var/log/business-dev-platform/app.log`

### View Logs
```bash
# Last 20 lines
tail -20 /var/log/business-dev-platform/app.log

# Real-time logs (with management script)
sudo /home/vali/projects/business-dev-platform/manage_service.sh logs

# Real-time logs (manual)
sudo tail -f /var/log/business-dev-platform/app.log

# Search for errors
grep ERROR /var/log/business-dev-platform/app.log
```

## Systemd Service Details

The service runs as user `vali` and is configured in:
```
/etc/systemd/system/business-dev-platform.service
```

### Manual systemd Commands

If you prefer direct systemd control:

```bash
# Check service status
sudo systemctl status business-dev-platform

# Start/stop/restart
sudo systemctl start business-dev-platform
sudo systemctl stop business-dev-platform
sudo systemctl restart business-dev-platform

# Enable at boot / disable
sudo systemctl enable business-dev-platform
sudo systemctl disable business-dev-platform

# View detailed logs
sudo journalctl -u business-dev-platform -f
```

## Troubleshooting

### Service won't start
Check the logs:
```bash
sudo /home/vali/projects/business-dev-platform/manage_service.sh logs
```

Common issues:
- Port is already in use (service will try next available port)
- Virtual environment not activated properly
- Missing dependencies (run `pip install -r requirements.txt`)

### Can't connect to the application
1. Check which port it's running on:
   ```bash
   sudo /home/vali/projects/business-dev-platform/manage_service.sh status
   ```

2. Verify service is running:
   ```bash
   sudo systemctl is-active business-dev-platform
   ```

3. Try restarting:
   ```bash
   sudo /home/vali/projects/business-dev-platform/manage_service.sh restart
   ```

### Permission Denied
Make sure you run management commands with `sudo`:
```bash
sudo /home/vali/projects/business-dev-platform/manage_service.sh status
```

### Check if a specific port is in use
```bash
lsof -i :8000  # Check port 8000
lsof -i :8001  # Check port 8001
```

## Auto-Start at Boot

To have the service automatically start when the system boots:

```bash
sudo /home/vali/projects/business-dev-platform/manage_service.sh enable
```

To disable auto-start:
```bash
sudo /home/vali/projects/business-dev-platform/manage_service.sh disable
```

## Uninstall Service

To completely remove the service:

```bash
sudo /home/vali/projects/business-dev-platform/manage_service.sh uninstall
```

This will:
- Stop the service
- Remove systemd configuration
- Remove startup scripts
- Reload systemd

## Manual Start (without service)

If you prefer to run the application manually without the service:

```bash
cd /home/vali/projects/business-dev-platform
source venv/bin/activate
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Monitoring

To monitor the service health:

```bash
# Check if running
sudo systemctl is-active business-dev-platform

# Check CPU/memory usage
ps aux | grep uvicorn

# View real-time resource usage
watch 'ps aux | grep -E "uvicorn|PID"'
```

## Production Considerations

For production deployment, consider:

1. **Use a reverse proxy** (nginx/Apache) for SSL/TLS
2. **Run multiple workers** (gunicorn instead of uvicorn)
3. **Set up monitoring** (Prometheus, Grafana)
4. **Enable log rotation** (logrotate)
5. **Use environment variables** for configuration
6. **Set up automatic backups** for sessions JSON files

Example production setup:
```bash
# Use gunicorn with multiple workers
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 backend.api.main:app
```

## Support

For issues or questions:
- Check logs: `sudo tail -f /var/log/business-dev-platform/app.log`
- Review CLAUDE.md for architecture details
- Check test suite: `pytest tests/ -v`
