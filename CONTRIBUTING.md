# Contributing to Adversarial Sandbox

Thank you for your interest in contributing to the Adversarial Sandbox project! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ and npm/yarn
- Python 3.11+
- Terraform (for infrastructure changes)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd adversarial-sandbox
   ```

2. **Start local services**
   ```bash
   # Start infrastructure services (Postgres, Redis, etc.)
   docker-compose -f tools/docker-compose.dev.yml up -d
   
   # Install dependencies
   make install-deps
   
   # Start development servers
   make dev
   ```

3. **Run tests**
   ```bash
   make test
   ```

## Code Standards

### Backend (Platform Services)

- **Language**: Python 3.11+
- **Framework**: FastAPI for REST APIs
- **Testing**: pytest with 90%+ coverage requirement
- **Code Style**: Black formatter, isort, flake8
- **Documentation**: All public APIs must have docstrings

### Frontend

- **Framework**: Next.js 14+ with React 18+
- **Styling**: Tailwind CSS with design system
- **Testing**: Jest and React Testing Library
- **Code Style**: ESLint, Prettier
- **Type Safety**: TypeScript strict mode

### Infrastructure

- **IaC**: Terraform for cloud resources
- **Container**: Docker with multi-stage builds
- **Orchestration**: Kubernetes manifests and Helm charts
- **Documentation**: All infrastructure changes require README updates

## Service Development Guidelines

### Service Structure

Each service in `platform/services/` must include:

```
service-name/
├─ src/                    # Source code
├─ tests/                  # Unit and integration tests
├─ Dockerfile             # Container definition
├─ Makefile              # Build and run commands
├─ pyproject.toml        # Python dependencies and metadata
└─ README.md             # Service documentation
```

### API Design

- Use OpenAPI 3.0 specifications
- Implement proper error handling and status codes
- Include request/response validation
- Document all endpoints with examples

### Database Changes

- All schema changes require migrations
- Include rollback procedures
- Update API documentation
- Add integration tests

## Pull Request Process

1. **Fork and Branch**
   - Create a feature branch from `main`
   - Use descriptive branch names: `feature/attack-executor-enhancement`

2. **Development**
   - Write tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass locally

3. **Pull Request**
   - Provide clear description of changes
   - Link to related issues
   - Include screenshots for UI changes
   - Request appropriate reviewers

4. **Review Process**
   - All PRs require at least one approval
   - Address feedback promptly
   - Ensure CI/CD checks pass

## Testing Requirements

### Unit Tests
- Minimum 90% code coverage for backend services
- All critical paths must have tests
- Mock external dependencies

### Integration Tests
- Test service-to-service communication
- Validate database operations
- Test authentication and authorization

### End-to-End Tests
- Critical user workflows
- Cross-browser compatibility
- Performance benchmarks

## Security Considerations

- Never commit secrets or credentials
- Use environment variables for configuration
- Implement proper input validation
- Follow OWASP guidelines for web security
- Regular dependency updates and security scans

## Documentation

### Code Documentation
- All public APIs must have docstrings
- Include usage examples
- Document configuration options

### Architecture Documentation
- Update architecture diagrams for significant changes
- Document design decisions in `docs/`
- Include sequence diagrams for complex workflows

## Release Process

1. **Version Bumping**
   - Use semantic versioning
   - Update CHANGELOG.md
   - Tag releases appropriately

2. **Deployment**
   - Infrastructure changes require staging deployment
   - All services must pass health checks
   - Monitor metrics post-deployment

## Getting Help

- **Documentation**: Check `docs/` directory first
- **Issues**: Use GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Tag maintainers for urgent reviews

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct. By participating, you agree to uphold this code.

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.
