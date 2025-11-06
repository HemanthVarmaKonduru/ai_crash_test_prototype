# 🏗️ AI Security Testing Platform - Complete System Architecture

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Architecture](#component-architecture)
4. [API Flow Diagrams](#api-flow-diagrams)
5. [Data Flow Architecture](#data-flow-architecture)
6. [Infrastructure & CI/CD](#infrastructure--cicd)
7. [Security Architecture](#security-architecture)
8. [Deployment Architecture](#deployment-architecture)

---

## 🎯 System Overview

The AI Security Testing Platform is a comprehensive system designed to evaluate Large Language Models (LLMs) against various security attack vectors. The platform consists of multiple microservices, a modern frontend, and robust infrastructure components.

### **Core Capabilities**
- **Prompt Injection Testing**: Evaluates model resistance to prompt injection attacks
- **Jailbreak Testing**: Tests model resistance to safety guideline bypasses
- **Real-time Monitoring**: Live progress tracking and status updates
- **Comprehensive Reporting**: Detailed analysis with AI-powered evaluation
- **Historical Analysis**: Persistent test history and trend analysis

---

## 🏗️ Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        FE[Next.js Frontend<br/>Port: 3000]
        FE_DASH[Dashboard]
        FE_PI[Prompt Injection Module]
        FE_JB[Jailbreak Module]
        FE_REPORTS[Reports Module]
    end

    subgraph "API Gateway Layer"
        API[Unified API Server<br/>Port: 8000]
        API_HEALTH[Health Check]
        API_PI[Prompt Injection Endpoints]
        API_JB[Jailbreak Endpoints]
    end

    subgraph "Core Services"
        PI_SERVICE[Prompt Injection Service]
        JB_SERVICE[Jailbreak Service]
        EVAL_SERVICE[Evaluation Service]
        STORAGE_SERVICE[Storage Service]
    end

    subgraph "External APIs"
        OPENAI[OpenAI API<br/>GPT-3.5-turbo<br/>GPT-4o-mini]
    end

    subgraph "Data Layer"
        PI_DATA[Prompt Injection Dataset<br/>30 samples]
        JB_DATA[Jailbreak Dataset<br/>15 samples]
        RESULTS[Test Results<br/>JSON Reports]
    end

    subgraph "Infrastructure"
        K8S[Kubernetes Cluster]
        HELM[Helm Charts]
        TERRAFORM[Terraform]
        MONITORING[Monitoring & Logging]
    end

    FE --> API
    API --> PI_SERVICE
    API --> JB_SERVICE
    PI_SERVICE --> OPENAI
    JB_SERVICE --> OPENAI
    EVAL_SERVICE --> OPENAI
    PI_SERVICE --> PI_DATA
    JB_SERVICE --> JB_DATA
    PI_SERVICE --> RESULTS
    JB_SERVICE --> RESULTS
    K8S --> API
    K8S --> PI_SERVICE
    K8S --> JB_SERVICE
    HELM --> K8S
    TERRAFORM --> K8S
```

---

## 🔧 Component Architecture

### **Frontend Components**

```mermaid
graph LR
    subgraph "Next.js Application"
        LAYOUT[Layout Component]
        DASHBOARD[Dashboard Page]
        
        subgraph "Testing Modules"
            PI_PAGE[Prompt Injection Page]
            JB_PAGE[Jailbreak Page]
            REPORTS_PAGE[Reports Page]
        end
        
        subgraph "Shared Components"
            UI_COMPONENTS[UI Components<br/>shadcn/ui]
            FORMS[Form Components]
            CHARTS[Chart Components]
            DIALOGS[Dialog Components]
        end
        
        subgraph "State Management"
            REACT_HOOKS[React Hooks]
            LOCAL_STORAGE[localStorage]
            API_CLIENT[API Client]
        end
    end
    
    LAYOUT --> DASHBOARD
    DASHBOARD --> PI_PAGE
    DASHBOARD --> JB_PAGE
    DASHBOARD --> REPORTS_PAGE
    PI_PAGE --> UI_COMPONENTS
    JB_PAGE --> UI_COMPONENTS
    REPORTS_PAGE --> UI_COMPONENTS
    PI_PAGE --> REACT_HOOKS
    JB_PAGE --> REACT_HOOKS
    REACT_HOOKS --> LOCAL_STORAGE
    REACT_HOOKS --> API_CLIENT
```

### **Backend Services Architecture**

```mermaid
graph TB
    subgraph "API Gateway (backend/api/main.py)"
        GATEWAY[FastAPI Application]
        CORS[CORS Middleware]
        ROUTES[Route Handlers]
        MIDDLEWARE[Authentication Middleware]
    end
    
    subgraph "Core Business Logic"
        PI_HANDLER[Prompt Injection Handler]
        JB_HANDLER[Jailbreak Handler]
        EVAL_HANDLER[Evaluation Handler]
        REPORT_HANDLER[Report Handler]
    end
    
    subgraph "Data Processing"
        DATASET_LOADER[Dataset Loader]
        RESPONSE_CAPTURE[Response Capture]
        AI_EVALUATION[AI Evaluation]
        RESULT_AGGREGATION[Result Aggregation]
    end
    
    subgraph "External Integrations"
        OPENAI_CLIENT[OpenAI Client]
        ASYNC_TASKS[Background Tasks]
    end
    
    GATEWAY --> PI_HANDLER
    GATEWAY --> JB_HANDLER
    PI_HANDLER --> DATASET_LOADER
    JB_HANDLER --> DATASET_LOADER
    DATASET_LOADER --> RESPONSE_CAPTURE
    RESPONSE_CAPTURE --> OPENAI_CLIENT
    RESPONSE_CAPTURE --> AI_EVALUATION
    AI_EVALUATION --> OPENAI_CLIENT
    AI_EVALUATION --> RESULT_AGGREGATION
    RESULT_AGGREGATION --> REPORT_HANDLER
    ASYNC_TASKS --> PI_HANDLER
    ASYNC_TASKS --> JB_HANDLER
```

---

## 🔄 API Flow Diagrams

### **Prompt Injection Test Flow**

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API Gateway
    participant O as OpenAI API
    participant D as Dataset

    U->>F: Configure test parameters
    F->>A: POST /api/v1/test/prompt-injection/start
    A->>D: Load prompt injection dataset
    D-->>A: Return 30 samples
    A->>A: Generate test_id
    A-->>F: Return test_id & initial status
    
    loop Real-time Progress Updates
        F->>A: GET /api/v1/test/prompt-injection/{test_id}/status
        A-->>F: Return current progress & step
    end
    
    loop For each prompt (30 samples)
        A->>O: Send prompt to GPT-3.5-turbo
        O-->>A: Return model response
        A->>O: Send response to GPT-4o-mini for evaluation
        O-->>A: Return evaluation result
        A->>A: Update progress & results
    end
    
    A->>A: Generate final report
    A-->>F: Test completed
    F->>A: GET /api/v1/test/prompt-injection/{test_id}/results
    A-->>F: Return complete results
    F->>U: Display results & analysis
```

### **Jailbreak Test Flow**

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API Gateway
    participant O as OpenAI API
    participant D as Dataset

    U->>F: Configure test parameters
    F->>A: POST /api/v1/test/jailbreak/start
    A->>D: Load jailbreak dataset
    D-->>A: Return 15 samples
    A->>A: Generate test_id
    A-->>F: Return test_id & initial status
    
    loop Real-time Progress Updates
        F->>A: GET /api/v1/test/jailbreak/{test_id}/status
        A-->>F: Return current progress & step
    end
    
    loop For each prompt (15 samples)
        A->>O: Send jailbreak prompt to GPT-3.5-turbo
        O-->>A: Return model response
        A->>O: Send response to GPT-4o-mini for evaluation
        O-->>A: Return evaluation result
        A->>A: Update progress & results
    end
    
    A->>A: Generate final report
    A-->>F: Test completed
    F->>A: GET /api/v1/test/jailbreak/{test_id}/results
    A-->>F: Return complete results
    F->>U: Display results & analysis
```

### **Real-time Status Polling Flow**

```mermaid
sequenceDiagram
    participant F as Frontend
    participant A as API Gateway
    participant S as Test Session

    F->>A: Start test (POST request)
    A->>S: Create test session
    A-->>F: Return test_id
    
    loop Every 2 seconds
        F->>A: GET /status/{test_id}
        A->>S: Get session data
        S-->>A: Return current state
        A-->>F: Return progress & status
        
        alt Test in progress
            F->>F: Update UI with progress
        else Test completed
            F->>F: Stop polling
            F->>F: Display final results
        else Test failed
            F->>F: Stop polling
            F->>F: Display error message
        end
    end
```

---

## 📊 Data Flow Architecture

### **Data Processing Pipeline**

```mermaid
graph LR
    subgraph "Input Data"
        PI_DATASET[Prompt Injection Dataset<br/>JSON: 30 samples]
        JB_DATASET[Jailbreak Dataset<br/>JSON: 15 samples]
        USER_CONFIG[User Configuration<br/>Model, API Key, etc.]
    end
    
    subgraph "Processing Pipeline"
        LOADER[Dataset Loader]
        FILTER[Sample Filter]
        CAPTURE[Response Capture]
        EVAL[AI Evaluation]
        AGGREGATE[Result Aggregation]
    end
    
    subgraph "Output Data"
        CAPTURED_RESPONSES[Captured Responses<br/>JSON]
        EVALUATED_RESPONSES[Evaluated Responses<br/>JSON]
        FINAL_REPORT[Comprehensive Report<br/>JSON]
        METRICS[Performance Metrics]
    end
    
    PI_DATASET --> LOADER
    JB_DATASET --> LOADER
    USER_CONFIG --> LOADER
    LOADER --> FILTER
    FILTER --> CAPTURE
    CAPTURE --> EVAL
    EVAL --> AGGREGATE
    AGGREGATE --> CAPTURED_RESPONSES
    AGGREGATE --> EVALUATED_RESPONSES
    AGGREGATE --> FINAL_REPORT
    AGGREGATE --> METRICS
```

### **Data Storage Architecture**

```mermaid
graph TB
    subgraph "Frontend Storage"
        LOCAL_STORAGE[localStorage<br/>Test History]
        SESSION_STATE[Session State<br/>Current Test Data]
    end
    
    subgraph "Backend Storage"
        MEMORY_STORAGE[In-Memory Storage<br/>Active Test Sessions]
        FILE_STORAGE[File System<br/>Test Reports]
    end
    
    subgraph "External Storage"
        OPENAI_API[OpenAI API<br/>Model Responses]
    end
    
    subgraph "Data Formats"
        JSON_FORMAT[JSON Format<br/>Structured Data]
        TIMESTAMP[Timestamped Files<br/>Unique Naming]
    end
    
    LOCAL_STORAGE --> JSON_FORMAT
    MEMORY_STORAGE --> JSON_FORMAT
    FILE_STORAGE --> TIMESTAMP
    FILE_STORAGE --> JSON_FORMAT
```

---

## 🚀 Infrastructure & CI/CD

### **Infrastructure Architecture**

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_LOCAL[Local Development<br/>Docker Compose]
        DEV_FRONTEND[Frontend: localhost:3000]
        DEV_BACKEND[Backend: localhost:8000]
    end
    
    subgraph "Container Orchestration"
        K8S[Kubernetes Cluster]
        PODS[Application Pods]
        SERVICES[Kubernetes Services]
        INGRESS[Ingress Controller]
    end
    
    subgraph "Configuration Management"
        HELM[Helm Charts<br/>Application Deployment]
        TERRAFORM[Terraform<br/>Infrastructure as Code]
        CONFIG_MAPS[ConfigMaps]
        SECRETS[Kubernetes Secrets]
    end
    
    subgraph "Monitoring & Observability"
        PROMETHEUS[Prometheus<br/>Metrics Collection]
        GRAFANA[Grafana<br/>Dashboards]
        JAEGER[Jaeger<br/>Distributed Tracing]
        ELK[ELK Stack<br/>Logging]
    end
    
    subgraph "CI/CD Pipeline"
        GITHUB[GitHub Repository]
        ACTIONS[GitHub Actions]
        DOCKER_REGISTRY[Docker Registry]
        K8S_DEPLOY[Kubernetes Deployment]
    end
    
    DEV_LOCAL --> K8S
    K8S --> PODS
    K8S --> SERVICES
    K8S --> INGRESS
    HELM --> K8S
    TERRAFORM --> K8S
    K8S --> PROMETHEUS
    K8S --> GRAFANA
    K8S --> JAEGER
    K8S --> ELK
    GITHUB --> ACTIONS
    ACTIONS --> DOCKER_REGISTRY
    ACTIONS --> K8S_DEPLOY
```

### **CI/CD Pipeline Flow**

```mermaid
graph LR
    subgraph "Source Control"
        CODE[Source Code]
        PR[Pull Request]
        MAIN[Main Branch]
    end
    
    subgraph "CI Pipeline"
        BUILD[Build & Test]
        LINT[Code Linting]
        UNIT_TEST[Unit Tests]
        INTEGRATION_TEST[Integration Tests]
        SECURITY_SCAN[Security Scan]
    end
    
    subgraph "CD Pipeline"
        BUILD_IMAGE[Docker Build]
        PUSH_REGISTRY[Push to Registry]
        DEPLOY_STAGING[Deploy to Staging]
        E2E_TEST[End-to-End Tests]
        DEPLOY_PROD[Deploy to Production]
    end
    
    subgraph "Monitoring"
        HEALTH_CHECK[Health Checks]
        ROLLBACK[Auto Rollback]
        ALERTS[Alerts & Notifications]
    end
    
    CODE --> PR
    PR --> BUILD
    BUILD --> LINT
    LINT --> UNIT_TEST
    UNIT_TEST --> INTEGRATION_TEST
    INTEGRATION_TEST --> SECURITY_SCAN
    SECURITY_SCAN --> BUILD_IMAGE
    BUILD_IMAGE --> PUSH_REGISTRY
    PUSH_REGISTRY --> DEPLOY_STAGING
    DEPLOY_STAGING --> E2E_TEST
    E2E_TEST --> DEPLOY_PROD
    DEPLOY_PROD --> HEALTH_CHECK
    HEALTH_CHECK --> ROLLBACK
    HEALTH_CHECK --> ALERTS
```

---

## 🔒 Security Architecture

### **Security Layers**

```mermaid
graph TB
    subgraph "Network Security"
        FIREWALL[Firewall Rules]
        VPN[VPN Access]
        WAF[Web Application Firewall]
    end
    
    subgraph "Application Security"
        AUTH[Authentication]
        AUTHZ[Authorization]
        CORS[CORS Policy]
        RATE_LIMIT[Rate Limiting]
    end
    
    subgraph "Data Security"
        ENCRYPTION[Data Encryption]
        API_KEY_MASK[API Key Masking]
        SECRET_MGMT[Secret Management]
    end
    
    subgraph "Infrastructure Security"
        K8S_RBAC[Kubernetes RBAC]
        NETWORK_POLICY[Network Policies]
        POD_SECURITY[Pod Security Policies]
    end
    
    FIREWALL --> WAF
    WAF --> AUTH
    AUTH --> AUTHZ
    AUTHZ --> CORS
    CORS --> RATE_LIMIT
    RATE_LIMIT --> ENCRYPTION
    ENCRYPTION --> API_KEY_MASK
    API_KEY_MASK --> SECRET_MGMT
    SECRET_MGMT --> K8S_RBAC
    K8S_RBAC --> NETWORK_POLICY
    NETWORK_POLICY --> POD_SECURITY
```

---

## 🚀 Deployment Architecture

### **Production Deployment**

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Load Balancer<br/>nginx/HAProxy]
    end
    
    subgraph "Kubernetes Cluster"
        subgraph "Frontend Pods"
            FE_POD1[Frontend Pod 1]
            FE_POD2[Frontend Pod 2]
            FE_POD3[Frontend Pod 3]
        end
        
        subgraph "Backend Pods"
            API_POD1[API Pod 1]
            API_POD2[API Pod 2]
            API_POD3[API Pod 3]
        end
        
        subgraph "Services"
            FE_SVC[Frontend Service]
            API_SVC[API Service]
        end
    end
    
    subgraph "External Services"
        OPENAI_PROD[OpenAI Production API]
        MONITORING[Monitoring Stack]
    end
    
    subgraph "Storage"
        PERSISTENT_VOL[Persistent Volumes]
        CONFIG_MAPS[ConfigMaps]
        SECRETS[Secrets]
    end
    
    LB --> FE_SVC
    LB --> API_SVC
    FE_SVC --> FE_POD1
    FE_SVC --> FE_POD2
    FE_SVC --> FE_POD3
    API_SVC --> API_POD1
    API_SVC --> API_POD2
    API_SVC --> API_POD3
    API_POD1 --> OPENAI_PROD
    API_POD2 --> OPENAI_PROD
    API_POD3 --> OPENAI_PROD
    FE_POD1 --> PERSISTENT_VOL
    API_POD1 --> CONFIG_MAPS
    API_POD1 --> SECRETS
    K8S --> MONITORING
```

---

## 📈 Performance & Scalability

### **Performance Metrics**

| Component | Metric | Target | Current |
|-----------|--------|--------|---------|
| Frontend | Load Time | < 2s | ~1.2s |
| API Response | Average Latency | < 500ms | ~300ms |
| Test Execution | Prompt Injection (30 samples) | < 10min | ~5-8min |
| Test Execution | Jailbreak (15 samples) | < 5min | ~3-5min |
| Concurrent Tests | Max Concurrent | 10 | 5 |

### **Scalability Architecture**

```mermaid
graph TB
    subgraph "Horizontal Scaling"
        HPA[Horizontal Pod Autoscaler]
        VPA[Vertical Pod Autoscaler]
        CLUSTER_AUTOSCALER[Cluster Autoscaler]
    end
    
    subgraph "Load Distribution"
        ROUND_ROBIN[Round Robin Load Balancing]
        LEAST_CONN[Least Connections]
        HEALTH_CHECK[Health-based Routing]
    end
    
    subgraph "Resource Management"
        CPU_LIMITS[CPU Limits & Requests]
        MEMORY_LIMITS[Memory Limits & Requests]
        STORAGE_QUOTAS[Storage Quotas]
    end
    
    HPA --> ROUND_ROBIN
    VPA --> LEAST_CONN
    CLUSTER_AUTOSCALER --> HEALTH_CHECK
    ROUND_ROBIN --> CPU_LIMITS
    LEAST_CONN --> MEMORY_LIMITS
    HEALTH_CHECK --> STORAGE_QUOTAS
```

---

## 🔧 Technology Stack

### **Frontend Stack**
- **Framework**: Next.js 15.2.4
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: React Hooks
- **HTTP Client**: Fetch API

### **Backend Stack**
- **Framework**: FastAPI
- **Language**: Python 3.12
- **Async Runtime**: asyncio
- **HTTP Server**: Uvicorn
- **API Documentation**: OpenAPI/Swagger

### **Infrastructure Stack**
- **Container Orchestration**: Kubernetes
- **Package Management**: Helm
- **Infrastructure as Code**: Terraform
- **Container Registry**: Docker Hub/ECR
- **CI/CD**: GitHub Actions

### **External Services**
- **AI Models**: OpenAI (GPT-3.5-turbo, GPT-4o-mini)
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack
- **Tracing**: Jaeger

---

## 📋 API Endpoints Summary

### **Core Endpoints**

| Method | Endpoint | Description | Response Time |
|--------|----------|-------------|---------------|
| GET | `/health` | Health check | < 100ms |
| POST | `/api/v1/test/prompt-injection/start` | Start PI test | < 500ms |
| GET | `/api/v1/test/prompt-injection/{id}/status` | Get PI status | < 200ms |
| GET | `/api/v1/test/prompt-injection/{id}/results` | Get PI results | < 300ms |
| GET | `/api/v1/test/prompt-injection/{id}/download` | Download PI report | < 500ms |
| POST | `/api/v1/test/jailbreak/start` | Start jailbreak test | < 500ms |
| GET | `/api/v1/test/jailbreak/{id}/status` | Get jailbreak status | < 200ms |
| GET | `/api/v1/test/jailbreak/{id}/results` | Get jailbreak results | < 300ms |
| GET | `/api/v1/test/jailbreak/{id}/download` | Download jailbreak report | < 500ms |

---

## 🎯 Key Features for Client Demo

### **1. Real-time Testing Experience**
- Live progress tracking with visual indicators
- Real-time status updates every 2 seconds
- Interactive result cards with detailed analysis

### **2. Comprehensive Security Testing**
- 30 prompt injection samples with various techniques
- 15 sophisticated jailbreak attempts
- AI-powered evaluation using GPT-4o-mini

### **3. Professional Reporting**
- Detailed JSON reports with timestamps
- Performance metrics and analysis
- Exportable results for further analysis

### **4. Scalable Architecture**
- Microservices-based design
- Kubernetes-ready deployment
- Horizontal scaling capabilities

### **5. Production-Ready Features**
- Health monitoring and alerting
- Comprehensive logging and tracing
- Security best practices implementation

---

## 🚀 Getting Started

### **Quick Start Commands**

```bash
# Start the unified API server
python backend/run.py

# Start the frontend (in separate terminal)
cd frontend && pnpm dev

# Access the application
# Frontend: http://localhost:3000/dashboard
# API Health: http://localhost:8000/health
# API Docs: http://localhost:8000/docs
```

### **Production Deployment**

```bash
# Deploy with Helm
helm install ai-security-testing ./infra/helm/

# Deploy infrastructure with Terraform
cd infra/terraform && terraform apply

# Monitor deployment
kubectl get pods -n ai-security-testing
```

---

This comprehensive architecture document provides a complete overview of the AI Security Testing Platform, including all components, data flows, API interactions, and infrastructure considerations. The system is designed for scalability, security, and maintainability while providing an excellent user experience for AI security testing.
