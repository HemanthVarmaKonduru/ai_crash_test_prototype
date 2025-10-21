# Adversarial Sandbox

Enterprise-grade LLM security testing platform for comprehensive adversarial attack simulation and evaluation.

## Architecture Overview

This repository contains a microservices-based platform for testing Large Language Models against sophisticated adversarial attacks. The system is designed for enterprise security teams to identify vulnerabilities, assess model robustness, and implement defensive measures.

### Key Features

- **Multi-Modal Attack Testing**: Prompt injection, jailbreak detection, data extraction, and adversarial robustness testing
- **Scalable Architecture**: Microservices-based design with horizontal scaling capabilities
- **Real-time Monitoring**: Live dashboards and metrics aggregation
- **Enterprise Security**: RBAC, SSO integration, audit trails, and compliance reporting

## Repository Structure

```
adversarial-sandbox/
├─ docs/                          # Product docs, architecture, runbooks
├─ infra/                          # IaC: terraform / k8s manifests / helm charts
├─ platform/                       # Backend monorepo (services, libs)
│  ├─ services/                    # Microservices
│  └─ libs/                        # Shared libraries
├─ frontend/                       # Next.js / React app (dashboard + marketing)
├─ tools/                          # Developer tooling, scripts (local dev)
└─ .github/                        # CI workflows, issue/pr templates
```

## Quick Start

1. **Prerequisites**: Docker, Node.js 18+, Python 3.11+
2. **Local Development**: See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions
3. **Infrastructure**: Deploy using Terraform configurations in `infra/`
4. **Documentation**: Comprehensive guides available in `docs/`

## Services

- **API Gateway**: Single entrypoint with auth, rate limiting, and request validation
- **Auth Service**: OAuth2, SSO integration, user/team management
- **Job Orchestrator**: Job lifecycle management and queue coordination
- **Attack Executor**: Stateless workers for running attack modules
- **Evaluator Agent**: LLM-based evaluation and rule-based checks
- **Insight Agent**: Automated insight generation and summarization
- **Metrics Aggregator**: Time-series data storage and dashboard APIs

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
