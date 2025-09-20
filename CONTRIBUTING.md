# Contributing to ManuWeaver

Thank you for your interest in improving ManuWeaver. The project welcomes contributions across backend, frontend, infrastructure, and documentation.

## Development Workflow

1. Fork the repository and create a feature branch.
2. Install dependencies using `make setup` or via Poetry/PNPM directly.
3. Run `make fmt` and `make lint` to ensure coding standards.
4. Add unit and integration tests for new functionality.
5. Update documentation when behaviour changes.
6. Submit a pull request describing the change and validation steps.

## Code Style

- Backend Python code follows `ruff`/`black` formatting with type hints.
- Frontend TypeScript uses ESLint + Prettier defaults from Next.js.
- Avoid hard coding secrets; rely on environment variables defined in `.env.example`.

## Testing

- Run `make test` to execute Python unit tests and Playwright smoke checks.
- When adding integrations that call external APIs, record cassettes via VCR.
- Ensure docker-compose deployment succeeds locally before submitting infrastructure changes.

## Security

- Validate all external input, particularly uploaded manuscripts and template archives.
- When integrating new reference providers, enforce DOI or authoritative identifiers to avoid fabricated citations.

## Academic Responsibility

While ManuWeaver automates citation suggestions, authors remain responsible for verifying every reference and ensuring compliance with journal ethics.
