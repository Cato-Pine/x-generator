# Contributing to {{PROJECT_NAME}}

Thank you for your interest in contributing! This guide will help you get started.

## Code of Conduct

Please be respectful and constructive in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/{{project-name}}.git
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Make your changes
5. Run tests and linting:
   ```bash
   {{package_manager}} run test
   {{package_manager}} run lint
   ```
6. Commit your changes (see commit guidelines below)
7. Push to your fork and submit a Pull Request

## Commit Message Guidelines

We follow conventional commits:

```
type(scope): description

[optional body]
[optional footer]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code restructuring, no feature change
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat(auth): add password reset functionality
fix(api): handle timeout errors gracefully
docs(readme): update installation instructions
```

## Pull Request Process

1. **Title**: Use the same format as commit messages
2. **Description**: Explain what and why, not how
3. **Tests**: Include tests for new functionality
4. **Documentation**: Update docs if needed
5. **Size**: Keep PRs focused and reasonably sized

## Development Workflow

### Branching Strategy
- `main` - Production-ready code
- `develop` - Integration branch (if used)
- `feature/*` - New features
- `fix/*` - Bug fixes

### Before Submitting
- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New code has test coverage
- [ ] Documentation updated if needed
- [ ] No console.logs or debug code
- [ ] No secrets or credentials committed

## Reporting Issues

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, version, etc.)
- Screenshots if applicable

## Questions?

Open an issue with the `question` label or reach out to the maintainers.
