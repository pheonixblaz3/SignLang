# Deployment Guide

## Prerequisites

- Python 3.10+ 
- pip or conda
- Git
- Modern browser (Chrome, Firefox, Safari, Edge)

## Local Development Setup

### 1. Clone & Setup Environment

```bash
git clone <repository>
cd SignSpeak_MAin
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env as needed
```

### 4. Verify Model Files

Ensure these models exist:

```
models/
├── landmark_mlp_recorded.joblib  (REQUIRED)
├── landmark_mlp.joblib
└── sign_model.pth
```

### 5. Run Application

```bash
python main.py
```

Server starts at `http://localhost:8000`

## Docker Deployment

### Build Image

```bash
docker build -t signspeak-v2:latest .
```

### Run Container

```bash
docker run -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  -e GPU_ENABLED=false \
  signspeak-v2:latest
```

### With GPU Support

```bash
docker run --gpus all -p 8000:8000 signspeak-v2:latest
```

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info
```

### Using systemd Service

Create `/etc/systemd/system/signspeak.service`:

```ini
[Unit]
Description=SignSpeak V2 Service
After=network.target

[Service]
Type=simple
User=signspeak
WorkingDirectory=/opt/signspeak
ExecStart=/opt/signspeak/.venv/bin/python main.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment="LOG_LEVEL=INFO"

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable signspeak
sudo systemctl start signspeak
```

### Using Nginx Reverse Proxy

```nginx
upstream signspeak {
    server localhost:8000;
}

server {
    listen 80;
    server_name signspeak.example.com;

    location / {
        proxy_pass http://signspeak;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Cloud Deployment

### AWS EC2

1. Launch Ubuntu 22.04 instance
2. SSH into instance
3. Run setup script:

```bash
curl -O https://example.com/setup.sh
bash setup.sh
```

### Heroku (Free Tier Deprecated)

Use alternative platforms like Render or Railway.

### DigitalOcean

1. Create Ubuntu Droplet
2. Install Python, pip, git
3. Clone repo and follow development setup
4. Use systemd service or Gunicorn

## Health Checks

### Endpoint Health

```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "camera": true, "model": true, ...}
```

### Monitor Logs

```bash
tail -f logs/signspeak.log
```

### Performance Stats

```bash
curl http://localhost:8000/stats
# Response: {"fps": 24.5, "avg_inference_ms": 45, ...}
```

## SSL/TLS Setup

### Let's Encrypt with Certbot

```bash
sudo certbot certonly --standalone -d signspeak.example.com
```

Update Nginx config:

```nginx
listen 443 ssl;
ssl_certificate /etc/letsencrypt/live/signspeak.example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/signspeak.example.com/privkey.pem;
```

## Monitoring

### Application Logs

Monitor with:

```bash
# Real-time
journalctl -u signspeak -f

# Or directly
tail -f logs/signspeak.log
```

### System Resources

Check with:

```bash
htop
nvidia-smi  # For GPU
```

### Uptime Monitoring

Use Uptime Robot or similar service to monitor `/health` endpoint.

## Backup Strategy

### Model Files

Backup to cloud storage:

```bash
aws s3 cp models/ s3://backup-bucket/signspeak/models/ --recursive
```

### Logs

Archive old logs:

```bash
find logs/ -name "*.log" -mtime +30 -delete
```

## Update Procedure

### Zero-Downtime Deployment

1. Pull updates in new directory
2. Install dependencies
3. Run tests
4. Switch DNS/load balancer to new version
5. Verify health endpoints
6. Keep old version as rollback

## Performance Optimization

### Enable GPU

```env
GPU_ENABLED=true
```

### Increase Workers (Gunicorn)

```bash
gunicorn main:app -w 8  # More workers
```

### Caching Headers

Nginx:

```nginx
location /static/ {
    expires 1d;
    add_header Cache-Control "public, immutable";
}
```

## Troubleshooting Deployment

### Port Already in Use

```bash
lsof -i :8000
kill -9 <PID>
```

### Camera Access Issues

```bash
# Check permissions
ls -la /dev/video0

# Fix if needed
sudo usermod -a -G video $USER
```

### WebSocket Connection Errors

1. Check firewall rules
2. Verify Nginx WebSocket config
3. Check browser console for errors

### Out of Memory

Monitor with:

```bash
free -h
watch -n 1 'free -h'
```

Restart service if needed:

```bash
sudo systemctl restart signspeak
```

## Security Checklist

- [ ] Use HTTPS with valid certificate
- [ ] Enable CORS restrictions
- [ ] Set strong log levels (WARNING minimum)
- [ ] Use environment variables for secrets
- [ ] Run with least privilege user
- [ ] Keep Python and dependencies updated
- [ ] Monitor access logs for anomalies
- [ ] Regular security scans

## Performance Benchmarks

Expected performance on modern hardware:

- **CPU Mode**: 15-30 FPS
- **GPU Mode**: 30-60+ FPS
- **Latency**: 40-80ms
- **Accuracy**: 90-95%

Actual performance depends on:
- Hardware capabilities
- Network latency
- Configuration tuning
- Model complexity

## Support & Troubleshooting

1. Check logs: `logs/signspeak.log`
2. Run health check: `curl http://localhost:8000/health`
3. Review tests: `pytest tests/ -v`
4. Check configuration: `curl http://localhost:8000/model-info`

## References

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Gunicorn Configuration](https://gunicorn.org/#docs)
- [Nginx Reverse Proxy](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
