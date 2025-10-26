# 🚀 Deployment Guide - AI Security Testing Platform

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Production Deployment](#production-deployment)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### System Requirements
- **OS**: Linux/macOS/Windows
- **CPU**: 4+ cores recommended
- **RAM**: 8GB+ recommended
- **Storage**: 20GB+ free space
- **Network**: Internet access for API calls

### Software Requirements
- **Python**: 3.12+
- **Node.js**: 18+
- **Docker**: 20.10+
- **Kubernetes**: 1.25+ (for production)
- **Helm**: 3.0+ (for production)

### API Keys Required
- **OpenAI API Key**: For model testing and evaluation

---

## 🏠 Local Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd ai_crash_test_prototype
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-api-key-here"

# Start the unified API server
python unified_api_server.py
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Verify Installation
```bash
# Check API health
curl http://localhost:8000/health

# Check frontend
open http://localhost:3000/dashboard
```

---

## 🐳 Docker Deployment

### 1. Create Dockerfile for Backend
```dockerfile
# Dockerfile.backend
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY unified_api_server.py .
COPY data/ ./data/

EXPOSE 8000

CMD ["python", "unified_api_server.py"]
```

### 2. Create Dockerfile for Frontend
```dockerfile
# Dockerfile.frontend
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

### 3. Create Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

### 4. Deploy with Docker Compose
```bash
# Set environment variables
export OPENAI_API_KEY="your-api-key-here"

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

---

## ☸️ Kubernetes Deployment

### 1. Create Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-security-testing
```

### 2. Create ConfigMap
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-security-config
  namespace: ai-security-testing
data:
  API_URL: "http://ai-security-backend:8000"
  MAX_CONCURRENT_TESTS: "5"
  DEFAULT_TIMEOUT: "300"
```

### 3. Create Secret
```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: ai-security-secrets
  namespace: ai-security-testing
type: Opaque
data:
  openai-api-key: <base64-encoded-api-key>
```

### 4. Create Backend Deployment
```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-security-backend
  namespace: ai-security-testing
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-security-backend
  template:
    metadata:
      labels:
        app: ai-security-backend
    spec:
      containers:
      - name: backend
        image: ai-security-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-security-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 5. Create Frontend Deployment
```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-security-frontend
  namespace: ai-security-testing
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-security-frontend
  template:
    metadata:
      labels:
        app: ai-security-frontend
    spec:
      containers:
      - name: frontend
        image: ai-security-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          valueFrom:
            configMapKeyRef:
              name: ai-security-config
              key: API_URL
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
```

### 6. Create Services
```yaml
# k8s/services.yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-security-backend
  namespace: ai-security-testing
spec:
  selector:
    app: ai-security-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP

---
apiVersion: v1
kind: Service
metadata:
  name: ai-security-frontend
  namespace: ai-security-testing
spec:
  selector:
    app: ai-security-frontend
  ports:
  - port: 3000
    targetPort: 3000
  type: ClusterIP
```

### 7. Create Ingress
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-security-ingress
  namespace: ai-security-testing
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: ai-security.your-domain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: ai-security-backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ai-security-frontend
            port:
              number: 3000
```

### 8. Deploy to Kubernetes
```bash
# Apply all configurations
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n ai-security-testing

# Check services
kubectl get services -n ai-security-testing

# Check ingress
kubectl get ingress -n ai-security-testing
```

---

## 🏭 Production Deployment

### 1. Using Helm Charts

#### Create Helm Chart Structure
```
helm/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   └── secret.yaml
└── charts/
```

#### Chart.yaml
```yaml
apiVersion: v2
name: ai-security-testing
description: AI Security Testing Platform
version: 1.0.0
appVersion: "1.0.0"
```

#### values.yaml
```yaml
replicaCount: 3

image:
  repository: ai-security-testing
  tag: "latest"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8000

ingress:
  enabled: true
  className: "nginx"
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
  hosts:
    - host: ai-security.your-domain.com
      paths:
        - path: /
          pathType: Prefix

resources:
  limits:
    cpu: 500m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

#### Deploy with Helm
```bash
# Add Helm repository (if using external charts)
helm repo add stable https://charts.helm.sh/stable

# Install the chart
helm install ai-security-testing ./helm \
  --namespace ai-security-testing \
  --create-namespace \
  --set image.tag=v1.0.0 \
  --set ingress.hosts[0].host=ai-security.your-domain.com

# Upgrade deployment
helm upgrade ai-security-testing ./helm \
  --namespace ai-security-testing \
  --set image.tag=v1.1.0
```

### 2. Using Terraform

#### main.tf
```hcl
provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_namespace" "ai_security_testing" {
  metadata {
    name = "ai-security-testing"
  }
}

resource "kubernetes_deployment" "backend" {
  metadata {
    name      = "ai-security-backend"
    namespace = kubernetes_namespace.ai_security_testing.metadata[0].name
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        app = "ai-security-backend"
      }
    }

    template {
      metadata {
        labels = {
          app = "ai-security-backend"
        }
      }

      spec {
        container {
          image = "ai-security-backend:latest"
          name  = "backend"

          port {
            container_port = 8000
          }

          env {
            name = "OPENAI_API_KEY"
            value_from {
              secret_key_ref {
                name = "ai-security-secrets"
                key  = "openai-api-key"
              }
            }
          }

          resources {
            limits = {
              cpu    = "500m"
              memory = "1Gi"
            }
            requests = {
              cpu    = "250m"
              memory = "512Mi"
            }
          }
        }
      }
    }
  }
}
```

#### Deploy with Terraform
```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply configuration
terraform apply

# Destroy resources (when needed)
terraform destroy
```

---

## 📊 Monitoring & Maintenance

### 1. Health Checks
```bash
# Check API health
curl http://localhost:8000/health

# Check Kubernetes pods
kubectl get pods -n ai-security-testing

# Check pod logs
kubectl logs -f deployment/ai-security-backend -n ai-security-testing
```

### 2. Monitoring Setup

#### Prometheus Configuration
```yaml
# monitoring/prometheus-config.yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai-security-backend'
    static_configs:
      - targets: ['ai-security-backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

#### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "AI Security Testing Platform",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Test Success Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(tests_completed_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### 3. Log Management

#### ELK Stack Configuration
```yaml
# logging/filebeat-config.yaml
filebeat.inputs:
- type: container
  paths:
    - /var/log/containers/*ai-security*.log
  processors:
  - add_kubernetes_metadata:
      host: ${NODE_NAME}
      matchers:
      - logs_path:
          logs_path: "/var/log/containers/"

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

### 4. Backup Strategy
```bash
# Backup Kubernetes resources
kubectl get all -n ai-security-testing -o yaml > backup.yaml

# Backup persistent volumes
kubectl exec -it <pod-name> -- tar czf /backup/data.tar.gz /app/data

# Backup configuration
kubectl get configmap,secret -n ai-security-testing -o yaml > config-backup.yaml
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. API Server Not Starting
```bash
# Check logs
python unified_api_server.py

# Check port availability
netstat -tulpn | grep :8000

# Check Python dependencies
pip list | grep fastapi
```

#### 2. Frontend Not Loading
```bash
# Check Node.js version
node --version

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

#### 3. Kubernetes Pod Issues
```bash
# Check pod status
kubectl describe pod <pod-name> -n ai-security-testing

# Check events
kubectl get events -n ai-security-testing

# Check resource usage
kubectl top pods -n ai-security-testing
```

#### 4. API Connection Issues
```bash
# Test API connectivity
curl -v http://localhost:8000/health

# Check CORS settings
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8000/api/v1/test/prompt-injection/start
```

### Performance Optimization

#### 1. Backend Optimization
```python
# Increase worker processes
uvicorn unified_api_server:app --workers 4 --host 0.0.0.0 --port 8000

# Enable gzip compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

#### 2. Frontend Optimization
```javascript
// Enable compression in Next.js
// next.config.js
module.exports = {
  compress: true,
  poweredByHeader: false,
}
```

#### 3. Database Optimization
```yaml
# Kubernetes resource limits
resources:
  limits:
    cpu: "1000m"
    memory: "2Gi"
  requests:
    cpu: "500m"
    memory: "1Gi"
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Build Docker image
      run: docker build -t ai-security-testing:${{ github.sha }} .
    - name: Push to registry
      run: docker push ai-security-testing:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/ai-security-backend \
          backend=ai-security-testing:${{ github.sha }} \
          -n ai-security-testing
```

---

## 📋 Maintenance Checklist

### Daily
- [ ] Check system health endpoints
- [ ] Monitor resource usage
- [ ] Review error logs
- [ ] Verify backup completion

### Weekly
- [ ] Update dependencies
- [ ] Review security patches
- [ ] Analyze performance metrics
- [ ] Test disaster recovery procedures

### Monthly
- [ ] Update base images
- [ ] Review and rotate secrets
- [ ] Capacity planning review
- [ ] Security audit

---

This deployment guide provides comprehensive instructions for deploying the AI Security Testing Platform across different environments, from local development to production Kubernetes clusters.
