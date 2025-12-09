# FraudGuard AI Pro - Deployment Guide

**Version:** 1.0.0  
**Last Updated:** January 20, 2024

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Configuration](#configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

**System Requirements:**
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- 4GB RAM minimum
- 20GB disk space

**Required Accounts:**
- GitHub account for repository access
- Docker Hub account (optional, for custom images)
- Cloud provider account (AWS, Azure, GCP) for production

---

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/aliop45448-afk/FraudGuard-AI-Pro.git
cd FraudGuard-AI-Pro
```

### 2. Install Dependencies

**Backend Services:**
```bash
# Install Python dependencies for each service
cd services/api-gateway
pip install -r requirements.txt

cd ../auth-service
pip install -r requirements.txt

# Repeat for all services
```

**Frontend:**
```bash
cd fraudguard-pro-app
npm install
```

### 3. Configure Environment Variables

```bash
# Copy environment templates
cp services/api-gateway/.env.example services/api-gateway/.env
cp services/auth-service/.env.example services/auth-service/.env
# Repeat for all services

# Edit configuration files
nano services/api-gateway/.env
```

### 4. Start Services Locally

**Using Docker Compose:**
```bash
docker-compose up -d
```

**Manual Start (Development):**
```bash
# Terminal 1 - API Gateway
cd services/api-gateway
python app.py

# Terminal 2 - Auth Service
cd services/auth-service
python app.py

# Terminal 3 - Frontend
cd fraudguard-pro-app
npm run dev
```

### 5. Verify Installation

```bash
# Check API Gateway
curl http://localhost:5000/health

# Check Auth Service
curl http://localhost:5001/health

# Check Frontend
curl http://localhost:5173
```

---

## Docker Deployment

### 1. Build Docker Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build api-gateway
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Database Setup

```bash
# Create database
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE fraudguard_db;"

# Run migrations (if applicable)
docker-compose exec api-gateway python migrate.py
```

### 4. Access Services

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:5173 | 5173 |
| API Gateway | http://localhost:5000 | 5000 |
| Auth Service | http://localhost:5001 | 5001 |
| Monitoring Service | http://localhost:5002 | 5002 |
| Inference Service | http://localhost:5003 | 5003 |
| API Service | http://localhost:5004 | 5004 |
| Security Service | http://localhost:5005 | 5005 |
| Reports Service | http://localhost:5006 | 5006 |
| AI Assistant | http://localhost:5007 | 5007 |
| Integrations Service | http://localhost:5008 | 5008 |

---

## Production Deployment

### 1. Cloud Provider Setup

**AWS Deployment:**
```bash
# Create ECR repository
aws ecr create-repository --repository-name fraudguard-ai-pro

# Push images
docker tag fraudguard-api-gateway:latest <account-id>.dkr.ecr.<region>.amazonaws.com/fraudguard-ai-pro:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/fraudguard-ai-pro:latest

# Deploy to ECS/EKS
aws ecs create-service --cluster fraudguard-cluster --service-name fraudguard-api-gateway ...
```

**Kubernetes Deployment:**
```bash
# Create namespace
kubectl create namespace fraudguard

# Deploy services
kubectl apply -f k8s/api-gateway.yaml -n fraudguard
kubectl apply -f k8s/auth-service.yaml -n fraudguard
# Repeat for all services

# Check deployment
kubectl get pods -n fraudguard
```

### 2. Database Setup

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier fraudguard-db \
  --db-instance-class db.t3.medium \
  --engine postgres

# Initialize database
psql -h <rds-endpoint> -U postgres -d fraudguard_db < schema.sql
```

### 3. Load Balancing

```bash
# Create load balancer
aws elbv2 create-load-balancer \
  --name fraudguard-alb \
  --subnets subnet-xxx subnet-yyy

# Create target groups
aws elbv2 create-target-group \
  --name fraudguard-api-gateway \
  --protocol HTTP \
  --port 5000
```

### 4. SSL/TLS Configuration

```bash
# Request certificate
aws acm request-certificate \
  --domain-name fraudguard.example.com

# Attach to load balancer
aws elbv2 modify-listener \
  --load-balancer-arn <alb-arn> \
  --listener-arn <listener-arn> \
  --protocol HTTPS \
  --certificates CertificateArn=<cert-arn>
```

### 5. Auto-Scaling

```bash
# Create auto-scaling group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name fraudguard-asg \
  --launch-configuration fraudguard-lc \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 3
```

---

## Configuration

### Environment Variables

**API Gateway (.env):**
```env
FLASK_ENV=production
SERVICE_PORT=5000
DATABASE_URL=postgresql://user:password@db:5432/fraudguard
REDIS_URL=redis://redis:6379/0
JWT_SECRET=your-secret-key
LOG_LEVEL=INFO
```

**Auth Service (.env):**
```env
FLASK_ENV=production
SERVICE_PORT=5001
JWT_EXPIRATION=3600
MFA_ENABLED=true
ENCRYPTION_KEY=your-encryption-key
```

**Inference Service (.env):**
```env
FLASK_ENV=production
SERVICE_PORT=5003
MODEL_PATH=/models
INFERENCE_TIMEOUT=150
BATCH_SIZE=32
```

### Database Configuration

**PostgreSQL Schema:**
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  amount DECIMAL(10, 2),
  merchant_id VARCHAR(255),
  fraud_probability DECIMAL(3, 2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  action VARCHAR(255),
  resource_type VARCHAR(255),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Check all services
for port in 5000 5001 5002 5003 5004 5005 5006 5007 5008; do
  curl -s http://localhost:$port/health | jq .
done
```

### Logging

```bash
# View logs
docker-compose logs -f api-gateway

# Export logs
docker-compose logs api-gateway > logs/api-gateway.log

# Centralized logging (ELK Stack)
docker-compose -f docker-compose.elk.yml up -d
```

### Metrics & Monitoring

```bash
# Prometheus metrics
curl http://localhost:9090/metrics

# Grafana dashboard
curl http://localhost:3000

# Performance monitoring
docker stats
```

### Backup & Recovery

```bash
# Database backup
pg_dump -h localhost -U postgres fraudguard_db > backup.sql

# Restore from backup
psql -h localhost -U postgres fraudguard_db < backup.sql

# Docker volume backup
docker run --rm -v fraudguard-data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/fraudguard-backup.tar.gz -C /data .
```

### Updates & Patches

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Update Docker images
docker-compose pull
docker-compose up -d

# Zero-downtime deployment
docker-compose up -d --no-deps --build api-gateway
```

---

## Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Find process using port
lsof -i :5000

# Kill process
kill -9 <PID>

# Or change port in .env
```

**Database Connection Error:**
```bash
# Check database status
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

**Service Not Starting:**
```bash
# Check logs
docker-compose logs api-gateway

# Check configuration
cat services/api-gateway/.env

# Rebuild service
docker-compose build --no-cache api-gateway
```

**Memory Issues:**
```bash
# Check memory usage
docker stats

# Increase Docker memory limit
# Edit Docker Desktop settings or docker-compose resource limits

# Optimize service
docker-compose up -d --scale api-gateway=2
```

### Performance Optimization

**Database Optimization:**
```sql
-- Create indexes
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM transactions WHERE user_id = 1;
```

**Caching:**
```bash
# Enable Redis caching
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Monitor cache
redis-cli INFO stats
```

**Load Balancing:**
```bash
# Scale services
docker-compose up -d --scale api-gateway=3

# Monitor load
docker stats
```

---

## Security Checklist

- [ ] Change default passwords
- [ ] Enable SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Enable authentication on all services
- [ ] Set up audit logging
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Backup encryption keys
- [ ] Regular security updates
- [ ] Penetration testing

---

## Support & Documentation

**Documentation:**
- API Documentation: http://localhost:5000/api/v1/docs
- System Architecture: SYSTEM_ARCHITECTURE.md
- Development Progress: DEVELOPMENT_PROGRESS.md

**Support:**
- GitHub Issues: https://github.com/aliop45448-afk/FraudGuard-AI-Pro/issues
- Email: support@fraudguard.example.com

---

**Deployment Version:** 1.0.0  
**Last Updated:** January 20, 2024
