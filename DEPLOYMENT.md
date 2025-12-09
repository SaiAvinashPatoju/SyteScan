# SyteScan Progress Analyzer - Deployment Guide

This guide covers deployment options for the SyteScan Progress Analyzer application.

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- Node.js 18+ and Python 3.11+ (for native deployment)
- Reverse proxy (nginx recommended for production)

## Deployment Options

### Option 1: Docker Deployment (Recommended)

#### Production Deployment with Docker Compose

1. **Clone and prepare the repository:**
```bash
git clone <repository-url>
cd sytescan-progress-analyzer
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your production settings
```

3. **Build and start services:**
```bash
docker-compose up --build -d
```

4. **Verify deployment:**
```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs -f

# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:3000
```

#### Individual Container Deployment

**Backend:**
```bash
# Build backend image
docker build -f Dockerfile.backend -t sytescan-backend .

# Run backend container
docker run -d \
  --name sytescan-backend \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/backend/sytescan.db:/app/sytescan.db \
  -e DATABASE_URL=sqlite:///./sytescan.db \
  -e LOG_LEVEL=INFO \
  sytescan-backend
```

**Frontend:**
```bash
# Build frontend image
docker build -f Dockerfile.frontend -t sytescan-frontend .

# Run frontend container
docker run -d \
  --name sytescan-frontend \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  sytescan-frontend
```

### Option 2: Native Deployment

#### Backend Deployment

1. **Setup Python environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
export DATABASE_URL=sqlite:///./sytescan.db
export LOG_LEVEL=INFO
export UPLOAD_DIR=./uploads
```

3. **Start the backend:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Frontend Deployment

1. **Build the frontend:**
```bash
npm install
npm run build
```

2. **Start the frontend:**
```bash
npm start
```

### Option 3: Production with Reverse Proxy

#### Nginx Configuration

Create `/etc/nginx/sites-available/sytescan`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Handle large file uploads
        client_max_body_size 50M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Health checks
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }

    # Static files and uploads
    location /uploads/ {
        alias /path/to/sytescan/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/sytescan /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Environment Configuration

### Production Environment Variables

**Backend (.env):**
```bash
# Database
DATABASE_URL=sqlite:///./sytescan.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost:5432/sytescan

# File Storage
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=10485760  # 10MB

# Security
SECRET_KEY=your-production-secret-key-here
CORS_ORIGINS=https://your-domain.com

# Logging
LOG_LEVEL=INFO

# Performance
MAX_WORKERS=4
REQUEST_TIMEOUT=300
```

**Frontend:**
```bash
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://your-domain.com
```

## Monitoring and Health Checks

### Health Check Endpoints

- **Basic Health:** `GET /health`
- **Detailed Health:** `GET /health/detailed`
- **Metrics:** `GET /metrics`

### Monitoring Setup

#### Docker Health Checks

The Docker containers include built-in health checks:

```bash
# Check container health
docker ps
# Look for "healthy" status

# View health check logs
docker inspect sytescan-backend | grep -A 10 Health
```

#### External Monitoring

Configure your monitoring system to check:

1. **Application Health:**
   - `GET /health` - Should return 200 with `{"status": "healthy"}`
   - `GET /health/detailed` - Detailed system metrics

2. **Performance Metrics:**
   - `GET /metrics` - Application and system metrics
   - Response times and error rates

3. **System Resources:**
   - CPU usage < 80%
   - Memory usage < 85%
   - Disk space > 10% free

### Log Management

#### Structured Logging

The application uses structured logging with the following levels:
- **INFO:** Normal operations, request/response logging
- **WARNING:** Slow requests, recoverable errors
- **ERROR:** Application errors, failed requests
- **DEBUG:** Detailed debugging information (development only)

#### Log Aggregation

For production, consider using log aggregation tools:

```bash
# Docker logs
docker-compose logs -f --tail=100

# File-based logging
tail -f /var/log/sytescan/app.log
```

## Database Management

### SQLite (Default)

- Database file: `backend/sytescan.db`
- Automatic table creation on startup
- Backup: Copy the database file

```bash
# Backup database
cp backend/sytescan.db backup/sytescan_$(date +%Y%m%d_%H%M%S).db

# Restore database
cp backup/sytescan_20241004_120000.db backend/sytescan.db
```

### PostgreSQL (Production)

For production with higher load:

1. **Install PostgreSQL:**
```bash
sudo apt install postgresql postgresql-contrib
```

2. **Create database and user:**
```sql
CREATE DATABASE sytescan;
CREATE USER sytescan_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE sytescan TO sytescan_user;
```

3. **Update environment:**
```bash
DATABASE_URL=postgresql://sytescan_user:secure_password@localhost:5432/sytescan
```

## Security Considerations

### File Upload Security

- File type validation (JPEG, PNG only)
- File size limits (10MB default)
- Secure file storage outside web root
- Virus scanning (recommended for production)

### API Security

- CORS configuration for allowed origins
- Request rate limiting (implement with nginx)
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy

### SSL/TLS

For production, enable HTTPS:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # ... rest of configuration
}
```

## Scaling Considerations

### Horizontal Scaling

For higher loads:

1. **Load Balancer:** Use nginx or HAProxy
2. **Multiple Backend Instances:** Run multiple FastAPI workers
3. **Shared Storage:** Use network storage for uploads
4. **Database:** Migrate to PostgreSQL with connection pooling

### Performance Optimization

1. **Frontend:**
   - Enable Next.js static optimization
   - Use CDN for static assets
   - Implement caching strategies

2. **Backend:**
   - Increase worker processes
   - Implement Redis caching
   - Optimize database queries

3. **YOLOv8:**
   - Use GPU acceleration if available
   - Implement batch processing
   - Consider model optimization

## Troubleshooting

### Common Issues

1. **Port Conflicts:**
   - Check if ports 3000/8000 are available
   - Modify docker-compose.yml if needed

2. **File Upload Issues:**
   - Check upload directory permissions
   - Verify disk space availability
   - Check file size limits

3. **Database Connection:**
   - Verify database file permissions
   - Check DATABASE_URL format
   - Ensure database directory exists

4. **YOLOv8 Model Download:**
   - Ensure internet connectivity
   - Check available disk space
   - Verify model file integrity

### Log Analysis

```bash
# Check application logs
docker-compose logs backend | grep ERROR
docker-compose logs frontend | grep ERROR

# Monitor real-time logs
docker-compose logs -f --tail=50

# System resource usage
docker stats
```

## Backup and Recovery

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/sytescan"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
cp backend/sytescan.db $BACKUP_DIR/sytescan_$DATE.db

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz uploads/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Recovery Process

1. **Stop services:**
```bash
docker-compose down
```

2. **Restore database:**
```bash
cp backup/sytescan_20241004_120000.db backend/sytescan.db
```

3. **Restore uploads:**
```bash
tar -xzf backup/uploads_20241004_120000.tar.gz
```

4. **Restart services:**
```bash
docker-compose up -d
```

## Support and Maintenance

### Regular Maintenance Tasks

1. **Weekly:**
   - Check application logs for errors
   - Monitor system resource usage
   - Verify backup integrity

2. **Monthly:**
   - Update dependencies (security patches)
   - Clean up old log files
   - Review performance metrics

3. **Quarterly:**
   - Update base Docker images
   - Review and update security configurations
   - Performance optimization review

For additional support, refer to the development documentation in `DEVELOPMENT.md`.