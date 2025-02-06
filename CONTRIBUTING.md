# Contributing to SmartDoc AI

Thank you for your interest in contributing to SmartDoc AI! This document provides guidelines and workflows for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Documentation](#documentation)
- [Testing](#testing)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Maintain professionalism in communications
- Report unacceptable behavior to project maintainers

## Development Setup

1. Fork the repository
2. Clone your fork locally
3. Setup development environment:

**Backend:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
1. `cd frontend`
2. `npm install`

## Making Changes

1. Create a new branch:
`git checkout -b feature/your-feature-name`

2. Make your changes
3. Test thoroughly
4. Commit with clear messages:
   - Use present tense ("Add feature" not "Added feature")
   - Reference issues/PRs where appropriate
   
## Pull Request Process

1. Update documentation reflecting changes
2. Add tests for new features
3. Ensure all tests pass
4. Update `CHANGELOG.md`
5. Submit PR with detailed description
6. Address review feedback

## Coding Standards

### Python (Backend)
- Follow PEP 8
- Type hints required
- Docstrings for all functions
- Max line length: 88 characters
- Sort imports with isort

### TypeScript/JavaScript (Frontend)
- Use TypeScript where possible
- Follow Prettier configuration
- ESLint compliance required
- Component-based architecture
- Props interface definitions

## Documentation

- Update README.md for user-facing changes
- Document API changes in OpenAPI spec
- Add JSDoc for frontend utilities
- Include examples for new features

## Testing

### Backend Tests
- Unit tests required for new features
- Integration tests for API endpoints
- Minimum 80% coverage
- Run tests:
`python -m pytest`

### Frontend Tests
- Component tests with React Testing Library
- E2E tests for critical paths
- Run tests:
`npm test`

## Version Control

- One feature per branch
- Rebase before PR
- Clean commit history
- No merge commits

## Core Areas for Contribution

1. **AI Model Improvements**
   - Model optimization
   - Alternative model support
   - Performance enhancements

2. **Frontend Development**
   - UI/UX improvements
   - Accessibility features
   - Mobile responsiveness

3. **Backend Enhancements**
   - API optimization
   - Database integration
   - Caching improvements

4. **Documentation**
   - User guides
   - API documentation
   - Setup tutorials

5. **Testing**
   - Test coverage
   - Performance testing
   - Security testing

## Recognition

Contributors will be added to `CONTRIBUTORS.md` with:
- Name/GitHub username
- Contributions summary
- Date of first contribution

## Questions?

Open an issue for:
- Feature proposals
- Bug reports
- Documentation improvements
- General questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License. See [LICENSE](LICENSE) for details.