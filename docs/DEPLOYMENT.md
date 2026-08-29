# Deployment

## Development Environment

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 20+
- Ollama (for local models)

### Quick Start

```bash
# 1. Clone and configure
git clone <repo>
cd agentic-multimodal-research-platform
cp .env.example .env
# Edit .env with your settings

# 2. Start infrastructure
docker-compose up -d

# 3. Backend
cd apps/api
pip install -e ".[dev]"
alembic upgrade head
uvicorn src.main:app --reload

# 4. Frontend
cd apps/web
npm install
npm run dev
```

### Docker Compose (Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: research
      POSTGRES_USER: research
      POSTGRES_PASSWORD: research
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U research"]
      interval: 5s
      timeout: 5s
      retries: 5

  chroma:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/data
    environment:
      - CHROMA_SERVER_HOST=0.0.0.0
      - ANONYMIZED_TELEMETRY=False

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

volumes:
  postgres_data:
  chroma_data:
  redis_data:
  ollama_data:
```

### Pull Models

```bash
# Pull required models
docker exec -it ollama ollama pull llama3.1
docker exec -it ollama ollama pull llava
docker exec -it ollama ollama pull nomic-embed-text
```

## Production Deployment

### Kubernetes

```yaml
# infrastructure/k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: research-platform
```

```yaml
# infrastructure/k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: research-config
  namespace: research-platform
data:
  LOG_LEVEL: "INFO"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  CHROMA_HOST: "chroma"
  CHROMA_PORT: "8000"
```

```yaml
# infrastructure/k8s/secrets.yaml (apply with kubectl apply -k or sealed-secrets)
apiVersion: v1
kind: Secret
metadata:
  name: research-secrets
  namespace: research-platform
type: Opaque
stringData:
  DATABASE_URL: "postgresql+asyncpg://user:pass@postgres:5432/research"
  REDIS_URL: "redis://redis:6379/0"
  SECRET_KEY: "generate-secure-key"
  OPENAI_API_KEY: "sk-..."
```

```yaml
# infrastructure/k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: research-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: research-platform/api:latest
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: research-config
            - secretRef:
                name: research-secrets
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "2Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /api/v1/health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /api/v1/health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
```

```yaml
# infrastructure/k8s/api-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: research-platform
spec:
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP
```

```yaml
# infrastructure/k8s/api-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
  namespace: research-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### Database (Production)

```yaml
# Use managed PostgreSQL (AWS RDS, Google Cloud SQL, Azure Database)
# Enable pgvector extension for embeddings
# Configure connection pooling (PgBouncer)
# Enable automated backups
# Set up read replicas for scaling
```

### Vector Store (Production)

```yaml
# Options:
# 1. ChromaDB in-cluster (small scale)
# 2. Pinecone (managed, scalable)
# 3. Weaviate (self-hosted or cloud)
# 4. Qdrant (self-hosted or cloud)
# 5. pgvector in PostgreSQL (simpler stack)
```

### File Storage (Production)

```yaml
# Use S3-compatible storage (AWS S3, MinIO, Cloudflare R2)
# Configure presigned URLs for uploads
# Set up CDN for public assets
# Implement lifecycle policies for cleanup
```

### Ingress & TLS

```yaml
# infrastructure/k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: research-ingress
  namespace: research-platform
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
spec:
  tls:
    - hosts:
        - research.example.com
      secretName: research-tls
  rules:
    - host: research.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api
                port:
                  number: 80
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web
                port:
                  number: 80
```

## CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build-api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          context: ./apps/api
          push: true
          tags: ghcr.io/org/research-api:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  build-web:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          context: ./apps/web
          push: true
          tags: ghcr.io/org/research-web:${{ github.sha }}

  deploy-staging:
    needs: [build-api, build-web]
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - uses: azure/k8s-set-context@v1
      - run: |
          kubectl set image deployment/api api=ghcr.io/org/research-api:${{ github.sha }} -n research-staging
          kubectl set image deployment/web web=ghcr.io/org/research-web:${{ github.sha }} -n research-staging
      - run: kubectl rollout status deployment/api -n research-staging
      - run: kubectl rollout status deployment/web -n research-staging

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: azure/k8s-set-context@v1
        with: {kubeconfig: ${{ secrets.KUBECONFIG_PROD }}}
      - run: |
          kubectl set image deployment/api api=ghcr.io/org/research-api:${{ github.sha }} -n research-platform
          kubectl set image deployment/web web=ghcr.io/org/research-web:${{ github.sha }} -n research-platform
      - run: kubectl rollout status deployment/api -n research-platform
      - run: kubectl rollout status deployment/web -n research-platform
```

## Monitoring & Observability

### Prometheus Metrics

```python
# apps/api/src/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

RESEARCH_JOBS_CREATED = Counter('research_jobs_created_total', 'Total research jobs created')
RESEARCH_JOBS_COMPLETED = Counter('research_jobs_completed_total', 'Total research jobs completed', ['status'])
RESEARCH_JOB_DURATION = Histogram('research_job_duration_seconds', 'Research job duration')
AGENT_RUN_DURATION = Histogram('agent_run_duration_seconds', 'Agent run duration', ['agent'])
MODEL_CALL_DURATION = Histogram('model_call_duration_seconds', 'Model call duration', ['provider', 'model'])
MODEL_CALL_TOKENS = Histogram('model_call_tokens_total', 'Model call tokens', ['provider', 'model', 'type'])
ACTIVE_JOBS = Gauge('research_active_jobs', 'Currently active research jobs')
```

### Grafana Dashboards

- Research job throughput
- Agent execution times
- Model provider latency
- Token usage/costs
- Error rates
- Queue depths

### Alerting

```yaml
# Alert rules
groups:
  - name: research-platform
    rules:
      - alert: HighJobFailureRate
        expr: rate(research_jobs_completed_total{status="failed"}[5m]) > 0.1
        for: 5m
        labels: {severity: critical}
        annotations:
          summary: "High research job failure rate"
      
      - alert: ModelProviderDown
        expr: up{job="ollama"} == 0
        for: 2m
        labels: {severity: critical}
        annotations:
          summary: "Ollama model provider is down"
      
      - alert: HighQueueDepth
        expr: redis_queue_depth > 100
        for: 5m
        labels: {severity: warning}
        annotations:
          summary: "Research task queue backing up"
```

## Backup & Disaster Recovery

- PostgreSQL: Automated daily backups, point-in-time recovery
- ChromaDB: Periodic snapshots to S3
- Redis: RDB snapshots + AOF
- File storage: Versioned S3 bucket with cross-region replication
- Test restore procedures monthly

## Scaling Considerations

| Component | Scaling Strategy |
|-----------|------------------|
| API | Horizontal (HPA), stateless |
| Workers (Celery) | Horizontal, queue-based |
| PostgreSQL | Read replicas, connection pooling |
| ChromaDB | Sharding, or managed service |
| Redis | Cluster mode |
| Ollama | GPU node pool, model parallelism |

---

*Start with Docker Compose. Move to Kubernetes when scale demands it.*