# Scalable Machine Learning Model Deployment - Complete Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [How It Works](#how-it-works)
5. [Why Kubernetes](#why-kubernetes)
6. [File Structure](#file-structure)
7. [Kubernetes Resources](#kubernetes-resources)
8. [Deployment Guide](#deployment-guide)
9. [Monitoring & Observability](#monitoring--observability)

---

## 🎯 Project Overview

This is a **scalable machine learning deployment project** that predicts **car resale prices** using multiple ML models. The project demonstrates enterprise-grade deployment practices using Kubernetes (K8s) for orchestration, containerization with Docker, and monitoring with Prometheus & Grafana.

### Key Purpose
- **Predict** car resale prices based on car features (brand, engine capacity, mileage, fuel type, etc.)
- **Scale automatically** based on traffic using Kubernetes HPA (Horizontal Pod Autoscaler)
- **Monitor performance** using Prometheus metrics and Grafana dashboards
- **Serve predictions** via multiple interfaces (REST API and Web UI)

### Tech Stack
```
Frontend:          Streamlit (Interactive Web UI)
Backend API:       FastAPI (High-performance REST API)
ML Models:         Random Forest & Gradient Boosting
Container:         Docker
Orchestration:     Kubernetes (K8s)
Monitoring:        Prometheus + Grafana
Server:            Uvicorn
Dependencies:      NumPy, Pandas, Scikit-learn, Joblib
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     External Users / Clients                      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │   NGINX Ingress Controller  │  (Routes traffic)
        │    (Single Entry Point)     │
        └──────┬─────────────┬────────┘
               │             │
        ┌──────▼──┐    ┌─────▼──────┐
        │ API     │    │ Streamlit   │
        │ Service │    │ Service     │
        └──────┬──┘    └─────┬───────┘
               │             │
        ┌──────▼──────────────▼──────┐
        │      Kubernetes Cluster     │
        │  (Multiple Pods/Replicas)   │
        ├─────────────────────────────┤
        │ FastAPI Pods   │ Streamlit  │
        │ (Min: 2, Max:5)│ Pod (x2)   │
        └─────────────────────────────┘
               │
        ┌──────▼──────────────┐
        │  ML Models Storage   │
        │ (Shared Volume)      │
        └──────────────────────┘
               │
        ┌──────▼──────────────────────┐
        │ Monitoring Stack             │
        ├──────────────────────────────┤
        │ Prometheus (Metrics Store)   │
        │ Grafana (Dashboard & Viz)    │
        └──────────────────────────────┘
```

---

## 🔧 Components

### 1. **Streamlit Application** (`app/app.py`)
**Purpose:** Provides an interactive user interface for making predictions

**Features:**
- User-friendly forms for inputting car details
- Dropdown menus for categorical features
- Real-time prediction display
- Support for multiple ML models selection

**Input Parameters:**
```
- Registered Year (2000-2025)
- Engine Capacity (500-5000 cc)
- Kilometers Driven
- Owner Type (First, Second, etc.)
- Max Power (bhp)
- Seats (2-10)
- Mileage (kmpl)
- Transmission Type (Manual/Automatic)
- Fuel Type (Diesel/Petrol/CNG/LPG/Electric)
- Body Type (Hatchback, Sedan, SUV, etc.)
- Brand Average Resale Price
- Model Popularity (Frequency)
```

**Output:** Predicted car resale price

---

### 2. **FastAPI Backend** (`app/app_api.py`)
**Purpose:** RESTful API for programmatic access to prediction models

**Key Features:**
- High-performance asynchronous API
- Model loading and caching
- Request validation using Pydantic
- Prometheus metrics integration
- Health check endpoint

**Endpoints:**
- `GET /health` - Health status check
- `POST /predict` - Make predictions via API
- `GET /metrics` - Prometheus metrics

**Why FastAPI?**
- ✅ Faster than Flask/Django for ML inference
- ✅ Automatic API documentation (Swagger UI)
- ✅ Built-in data validation
- ✅ Async/await support for concurrent requests
- ✅ Better performance for CPU-bound ML tasks

---

### 3. **ML Models**
**Two Prediction Models:**

a) **Random Forest** - Ensemble of decision trees
   - Pros: Robust, handles non-linear relationships
   - Use case: General-purpose predictions

b) **Gradient Boosting** - Sequential boosting ensemble
   - Pros: Often more accurate, reduces bias
   - Use case: High-accuracy predictions

**Model Lifecycle:**
```
Training (offline) → Serialization (joblib) → Deployment (loaded at startup)
```

Model files stored in: `models/` directory
- `rf_model.pkl` - Random Forest model
- `gb_model.pkl` - Gradient Boosting model
- `scaler.pkl` - Feature scaler for normalization

---

### 4. **Docker Containers**

#### **Dockerfile** (Main app image)
```dockerfile
FROM python:3.11-slim        # Lightweight Python base
WORKDIR /app
COPY requirements.txt .       # Install dependencies
RUN pip install -r requirements.txt
COPY app/ .                   # Copy application code
EXPOSE 5000
CMD ["python", "app.py"]      # Run Streamlit app
```

#### **Dockerfile-api** (FastAPI image)
```dockerfile
# Similar structure but runs:
CMD ["uvicorn", "app_api:app", "--host", "0.0.0.0", "--port", "5000"]
```

#### **Dockerfile-streamlit** (Streamlit image)
```dockerfile
# Similar structure but runs:
CMD ["streamlit", "run", "app.py"]
```

**Why Multiple Dockerfiles?**
- Separation of concerns (API vs UI)
- Independent scaling
- Targeted resource allocation

---

## 🔄 How It Works

### **Request Flow for API Prediction:**

```
1. User sends HTTP POST to /predict
   └─ Contains car features

2. FastAPI endpoint receives request
   └─ Validates data using Pydantic

3. Features are preprocessed
   └─ Scaled using loaded scaler
   └─ Categorical values encoded

4. Selected model makes prediction
   └─ Random Forest OR Gradient Boosting

5. Response returned to user
   └─ JSON with predicted price

6. Prometheus metrics recorded
   └─ Request count, latency, status
```

### **Request Flow for Streamlit UI:**

```
1. User fills form in Streamlit UI
   └─ Browser connects to Streamlit pod

2. Form submission triggers prediction
   └─ Data mapped to model format

3. Model inference happens in-container
   └─ Uses loaded RF or GB model

4. Result displayed in UI
   └─ User sees predicted price
```

---

## 🚀 Why Kubernetes?

### **Problem Without Kubernetes:**
```
❌ Single server failure = complete downtime
❌ Manual scaling = slow and error-prone
❌ Resource management = inefficient
❌ Load balancing = complex configuration
❌ Updates = potential downtime
❌ Monitoring = scattered and manual
```

### **Solution With Kubernetes:**
```
✅ Automated replication → High availability
✅ HPA scales pods automatically based on CPU/memory
✅ Self-healing → Restarts failed containers
✅ Rolling updates → Zero-downtime deployments
✅ Load balancing → Built-in service discovery
✅ Resource limits → Prevent resource hogging
✅ Monitoring → Native metrics collection
```

### **Key Kubernetes Benefits for This Project:**

| Feature | Benefit |
|---------|---------|
| **Deployment** | Manages replica sets, ensures desired state |
| **Service** | Stable IP/DNS for load balancing |
| **Ingress** | Single entry point, URL routing |
| **HPA** | Auto-scales from 2-5 replicas based on CPU |
| **ConfigMaps** | Centralized configuration |
| **Secrets** | Secure credential storage |
| **Volumes** | Persistent storage for models |

---

## 📁 File Structure

```
Scalable ML deployment/
│
├── app/                              # Application code
│   ├── app.py                        # Streamlit UI application
│   ├── app_api.py                    # FastAPI backend
│   └── models/                       # Pre-trained ML models
│       ├── rf_model.pkl             # Random Forest model
│       ├── gb_model.pkl             # Gradient Boosting model
│       └── scaler.pkl               # Feature scaler
│
├── k8s/                             # Kubernetes configurations
│   ├── deploy-api.yaml              # FastAPI deployment (2 replicas)
│   ├── deploy-streamlit.yaml        # Streamlit deployment (2 replicas)
│   ├── service-api.yaml             # FastAPI service (ClusterIP)
│   ├── service-streamlit.yaml       # Streamlit service (ClusterIP)
│   ├── service.yaml                 # Load balancer service
│   ├── ingress.yaml                 # NGINX ingress routing
│   ├── hpa-api.yaml                 # HPA for API (2-5 pods, 50% CPU)
│   ├── deployment.yaml              # Generic deployment template
│   ├── prometheus-deployment.yaml   # Prometheus metrics server
│   ├── grafana-deployment.yaml      # Grafana dashboard
│
├── data/
│   └── car_resale_prices.csv        # Training data
│
├── Dockerfile                        # Main Docker image
├── Dockerfile-api                    # API-specific image
├── Dockerfile-streamlit              # Streamlit-specific image
│
├── requirements.txt                  # Python dependencies
├── README.md                         # Quick start guide
├── KUBERNETES_PROJECT_GUIDE.md       # This file
└── .git/                             # Version control
```

---

## ⚙️ Kubernetes Resources Explained

### **1. Deployment (deploy-api.yaml)**
**What it does:** Manages FastAPI pods, ensures availability

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-api-deployment

spec:
  replicas: 2                    # Always 2 pods running
  selector:
    matchLabels:
      app: model-api             # Find pods with this label
  
  template:
    metadata:
      labels:
        app: model-api
    
    spec:
      containers:
      - name: model-api
        image: carprice-api:local
        ports:
        - containerPort: 5000
        
        command: ["uvicorn", "app_api:app", "--host", "0.0.0.0", "--port", "5000"]
        
        readinessProbe:           # Checks if pod is ready
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 10
```

**Key Concepts:**
- `replicas: 2` → Always keep 2 FastAPI pods running
- `readinessProbe` → K8s checks `/health` endpoint before routing traffic
- `image: carprice-api:local` → Uses local Docker image

---

### **2. Service (service-api.yaml)**
**What it does:** Provides stable internal DNS and load balancing

```yaml
apiVersion: v1
kind: Service
metadata:
  name: model-api-service

spec:
  type: ClusterIP              # Internal service (not exposed externally)
  selector:
    app: model-api             # Routes to deployment with this label
  
  ports:
  - protocol: TCP
    port: 80                   # Service port (internal)
    targetPort: 5000           # Container port
```

**Why needed?**
- Pods are ephemeral (can die and respawn)
- Service provides stable DNS: `model-api-service.default.svc.cluster.local`
- Automatically load balances across all pods

---

### **3. Ingress (ingress.yaml)**
**What it does:** Routes external traffic to services based on URL paths

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: carprice-ingress
  annotations:
    kubernetes.io/ingress.class: nginx

spec:
  rules:
  - http:
      paths:
      - path: /api(/|$)(.*)
        backend:
          service:
            name: model-api-service
            port: 80
      
      - path: /prometheus(/|$)(.*)
        backend:
          service:
            name: prometheus-service
            port: 80
      
      - path: /grafana(/|$)(.*)
        backend:
          service:
            name: grafana-service
            port: 80
```

**Routing Logic:**
```
External Request
    ├─ /api/predict → model-api-service
    ├─ /api/health → model-api-service
    ├─ /prometheus → prometheus-service
    └─ /grafana → grafana-service
```

---

### **4. Horizontal Pod Autoscaler (hpa-api.yaml)**
**What it does:** Automatically adds/removes pods based on load

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: model-api-hpa

spec:
  scaleTargetRef:
    kind: Deployment
    name: model-api-deployment
  
  minReplicas: 2               # Minimum 2 pods
  maxReplicas: 5               # Maximum 5 pods
  
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        averageUtilization: 50  # Scale up if CPU > 50%
```

**Scaling Logic:**
```
CPU Usage < 50% → Stay at current replicas
CPU Usage = 50% → Consider scaling up
CPU Usage > 50% → Add more pods (up to 5)
CPU Usage low → Scale down (minimum 2)
```

**Example Scenario:**
```
Normal load (20% CPU)  → 2 pods
High load (60% CPU)    → 4 pods (auto-scaled)
Peak load (80% CPU)    → 5 pods (max reached)
Traffic drops          → 2 pods (scaled down)
```

---

### **5. Prometheus Deployment**
**What it does:** Collects metrics from all services

**Metrics collected:**
```
- carprice_api_requests_total       # Total API calls
- carprice_api_request_duration     # Response time
- carprice_api_predictions_total    # Predictions made
- pod_cpu_usage_seconds             # CPU consumption
- pod_memory_working_bytes          # Memory usage
```

---

### **6. Grafana Deployment**
**What it does:** Visualizes Prometheus metrics in dashboards

**Accessible at:** `http://<ingress-ip>/grafana`

---

## 🚀 Deployment Guide

### **Prerequisites**
```bash
- Kubernetes cluster running (minikube, Docker Desktop K8s, or cloud K8s)
- kubectl configured
- Docker daemon running
- Python 3.11+
```

### **Step 1: Build Docker Images**
```bash
cd "c:\Projects\Scalable ML deployment"

# Build API image
docker build -t carprice-api:local -f Dockerfile-api .

# Build Streamlit image
docker build -t carprice-streamlit:local -f Dockerfile-streamlit .
```

### **Step 2: Deploy to Kubernetes**
```bash
# Create namespace (optional)
kubectl create namespace ml-deployment

# Apply all K8s resources
kubectl apply -f k8s/ -n ml-deployment

# Or individually:
kubectl apply -f k8s/deploy-api.yaml
kubectl apply -f k8s/service-api.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa-api.yaml
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/grafana-deployment.yaml
```

### **Step 3: Verify Deployment**
```bash
# Check pods
kubectl get pods -n ml-deployment

# Check services
kubectl get svc -n ml-deployment

# Check ingress
kubectl get ingress -n ml-deployment

# View logs
kubectl logs -f deployment/model-api-deployment -n ml-deployment
```

### **Step 4: Access Application**
```bash
# Get ingress IP
kubectl get ingress -n ml-deployment

# API endpoint
http://<ingress-ip>/api

# Streamlit UI
http://<ingress-ip>/streamlit

# Prometheus metrics
http://<ingress-ip>/prometheus

# Grafana dashboards
http://<ingress-ip>/grafana
```

---

## 📊 Monitoring & Observability

### **Prometheus Metrics (Real-time)**
```
# API Request Count by Endpoint
sum(rate(carprice_api_requests_total[5m])) by (endpoint)

# Average Response Time
histogram_quantile(0.95, carprice_api_request_duration_seconds_bucket)

# Prediction Success Rate
carprice_api_predictions_total{status="success"} / sum(carprice_api_predictions_total)

# Pod CPU Usage
sum(rate(container_cpu_usage_seconds_total[5m])) by (pod)
```

### **Grafana Dashboards**
Dashboards provide visual monitoring of:
- Request rates (requests/minute)
- Response latency (p50, p95, p99)
- Prediction accuracy by model
- Pod resource consumption (CPU, memory)
- HPA scaling events

### **Health Checks**
```bash
# API health
curl http://localhost:5000/health

# Response indicates:
- Pod is running
- Models are loaded
- All dependencies are available
```

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Pods not starting | Check logs: `kubectl logs <pod-name>` |
| Metrics not showing | Verify Prometheus scrape configs |
| High latency | Check HPA metrics, verify load distribution |
| OOM errors | Increase resource requests/limits |
| Ingress not routing | Verify ingress class, check nginx controller |

---

## 📚 Learning Resources

1. **Kubernetes Official Docs:** https://kubernetes.io/docs/
2. **FastAPI Documentation:** https://fastapi.tiangolo.com/
3. **Docker Best Practices:** https://docs.docker.com/
4. **Prometheus Querying:** https://prometheus.io/docs/prometheus/latest/querying/
5. **Grafana Dashboards:** https://grafana.com/docs/

---

## ✨ Summary

This project demonstrates a **production-grade ML deployment** using Kubernetes. It combines:

- **ML Models** for prediction accuracy
- **Containerization** for consistency
- **Orchestration** for reliability and scalability
- **Monitoring** for observability
- **Auto-scaling** for cost efficiency

The architecture ensures high availability, automatic recovery, and efficient resource utilization while providing multiple interfaces (REST API + Web UI) for users and systems to access the ML models.

