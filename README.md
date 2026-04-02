# K8s AI Deployment 🚀☸️

Kubernetes deployment of the Enterprise AI Gateway with Redis and PostgreSQL, running on a local cluster via Docker Desktop.

## Overview

This project demonstrates how to take a production-ready AI application and deploy it on Kubernetes with proper configuration management, secrets handling, persistent storage, and high availability.

## Architecture
```
                    ┌─────────────────────────────────┐
                    │      Kubernetes Cluster          │
                    │         (ai-gateway ns)          │
                    │                                  │
Internet ──→ :30080 │  ┌──────────┐  ┌──────────┐    │
                    │  │ gateway  │  │ gateway  │    │
                    │  │ pod 1    │  │ pod 2    │    │
                    │  └────┬─────┘  └────┬─────┘    │
                    │       └──────┬───────┘          │
                    │         ┌────┴─────┐            │
                    │    ┌────┴────┐ ┌───┴────┐       │
                    │    │postgres │ │ redis  │       │
                    │    │  pod    │ │  pod   │       │
                    │    └─────────┘ └────────┘       │
                    └─────────────────────────────────┘
```

## Features

- ☸️ **Kubernetes native** — declarative YAML manifests for all resources
- 🔄 **High availability** — 2 replicas of the gateway running in parallel
- 🔐 **Secrets management** — API keys stored as K8s Secrets, never in code
- ⚙️ **ConfigMaps** — environment configuration decoupled from the image
- 💾 **Persistent storage** — PostgreSQL data survives pod restarts via PVC
- 🏥 **Health checks** — readiness and liveness probes for self-healing
- 🔒 **Network isolation** — internal services use ClusterIP, only gateway is exposed

## Prerequisites

- Docker Desktop with Kubernetes enabled
- kubectl CLI
- OpenAI API key

## Kubernetes Resources

| Resource | Kind | Description |
|----------|------|-------------|
| `ai-gateway` | Deployment | 2 replicas of the AI gateway |
| `postgres` | Deployment | PostgreSQL database |
| `redis` | Deployment | Redis cache |
| `postgres-pvc` | PersistentVolumeClaim | 1GB persistent storage for PostgreSQL |
| `gateway-config` | ConfigMap | Non-sensitive configuration |
| `gateway-secret` | Secret | API keys and passwords (not in repo) |
| `ai-gateway` | Service (NodePort) | Exposes gateway on port 30080 |
| `postgres` | Service (ClusterIP) | Internal database access |
| `redis` | Service (ClusterIP) | Internal cache access |

## Deployment

### 1. Create the namespace
```bash
kubectl apply -f k8s/monitoring/namespace.yaml
```

### 2. Create secrets (copy and fill in your values)
```bash
cp k8s/gateway/secret.yaml.example k8s/gateway/secret.yaml
# Edit secret.yaml with your base64-encoded values
kubectl apply -f k8s/gateway/secret.yaml
```

### 3. Deploy everything
```bash
kubectl apply -f k8s/postgres/pvc.yaml
kubectl apply -f k8s/postgres/deployment.yaml
kubectl apply -f k8s/postgres/service.yaml
kubectl apply -f k8s/redis/deployment.yaml
kubectl apply -f k8s/redis/service.yaml
kubectl apply -f k8s/gateway/configmap.yaml
kubectl apply -f k8s/gateway/deployment.yaml
kubectl apply -f k8s/gateway/service.yaml
```

### 4. Verify deployment
```bash
kubectl get all -n ai-gateway
```

Expected output:
```
NAME                             READY   STATUS    RESTARTS   AGE
pod/ai-gateway-xxx               1/1     Running   0          1m
pod/ai-gateway-yyy               1/1     Running   0          1m
pod/postgres-xxx                 1/1     Running   0          1m
pod/redis-xxx                    1/1     Running   0          1m

NAME                 TYPE        CLUSTER-IP     PORT(S)        AGE
service/ai-gateway   NodePort    10.x.x.x       80:30080/TCP   1m
service/postgres     ClusterIP   10.x.x.x       5432/TCP       1m
service/redis        ClusterIP   10.x.x.x       6379/TCP       1m
```

### 5. Test the deployment
```bash
# Health check
curl http://localhost:30080/health

# Get auth token
curl -X POST "http://localhost:30080/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "demo-key-12345"}'

# Chat request
curl -X POST "http://localhost:30080/api/v1/chat" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai", "model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hello!"}]}'
```

## Key Kubernetes Concepts Demonstrated

**Deployments** manage the lifecycle of pods and ensure the desired number of replicas is always running.

**Services** provide stable DNS names and load balancing across pods. ClusterIP for internal services, NodePort to expose externally.

**ConfigMaps** decouple configuration from container images — change config without rebuilding.

**Secrets** store sensitive data encrypted at rest. Values are base64-encoded and never committed to version control.

**PersistentVolumeClaims** request durable storage that survives pod restarts — essential for databases.

**Probes** let Kubernetes know when a pod is ready to serve traffic and when to restart it automatically.

## Project Structure
```
k8s-ai-deployment/
├── Dockerfile
├── app/                    # Enterprise AI Gateway source code
├── k8s/
│   ├── monitoring/
│   │   └── namespace.yaml
│   ├── gateway/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   └── secret.yaml     # Not in repo - contains sensitive data
│   ├── postgres/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── pvc.yaml
│   └── redis/
│       ├── deployment.yaml
│       └── service.yaml
└── requirements.txt
```

## License

MIT