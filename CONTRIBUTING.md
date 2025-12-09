# Contributing to SyteScan Progress Analyzer

Thank you for considering contributing to SyteScan! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/sytescan.git
   cd sytescan
   ```
3. **Set up development environment** (see [DEV-SETUP.md](DEV-SETUP.md))

## Development Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions/modifications

### Making Changes

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our coding standards

3. Write/update tests for your changes

4. Run the test suite:
   ```bash
   # Frontend tests
   npm test
   
   # Backend tests
   cd backend && pytest
   ```

5. Run linting:
   ```bash
   # Frontend
   npm run lint
   
   # Backend
   cd backend && flake8 app/
   ```

6. Commit your changes with clear commit messages:
   ```bash
   git commit -m "feat: add new detection algorithm"
   ```

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code changes that neither fix bugs nor add features
- `test:` - Adding or modifying tests
- `chore:` - Maintenance tasks

### Pull Request Process

1. Update documentation if needed
2. Ensure all tests pass
3. Update the CHANGELOG.md if applicable
4. Submit a pull request with:
   - Clear title describing the change
   - Description of what and why
   - Link to any related issues

## Coding Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints where possible
- Document functions with docstrings
- Maximum line length: 88 characters (Black default)

### TypeScript/JavaScript (Frontend)

- Use TypeScript for all new code
- Follow ESLint configuration
- Use functional components with hooks
- Document complex logic with comments

## Testing Guidelines

- Write unit tests for new functionality
- Maintain >80% code coverage where practical
- Include integration tests for API endpoints
- Test edge cases and error handling

## Questions?

If you have questions, please:
1. Check existing documentation
2. Search existing issues
3. Open a new issue with the `question` label

Thank you for contributing! 🎉
