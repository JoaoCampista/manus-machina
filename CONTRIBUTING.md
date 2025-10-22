# Contributing to Manus Machina

Thank you for your interest in contributing to Manus Machina! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)

### Suggesting Features

We welcome feature suggestions! Please open an issue with:
- A clear description of the feature
- Use cases and benefits
- Potential implementation approach (optional)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Write tests** for your changes
5. **Run tests**: `pytest tests/`
6. **Commit your changes**: `git commit -m "Add feature: description"`
7. **Push to your fork**: `git push origin feature/your-feature-name`
8. **Open a Pull Request**

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all public functions and classes
- Keep functions focused and modular

### Testing

- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage

### Documentation

- Update README.md if adding new features
- Add docstrings to new code
- Update examples if relevant

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/manus-machina.git
cd manus-machina

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## Questions?

Feel free to open an issue or reach out to the maintainers.

Thank you for contributing! 🎉

