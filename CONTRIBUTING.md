# Contributing to Detector Mapping Visualizer

Thank you for your interest in contributing to the Detector Mapping Visualizer! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/alicefittoolkit/DetectorMappingVisualizer.git
   cd DetectorMappingVisualizer
   ```
3. **Set up the development environment**:
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/` for new features
- `bugfix/` for bug fixes
- `docs/` for documentation updates
- `refactor/` for code refactoring

### 2. Make Your Changes

- Write clear, concise code
- Follow PEP 8 style guidelines (enforced by Black and Flake8)
- Add docstrings to functions and classes
- Update documentation if needed

### 3. Write Tests

- Add tests for new features in the `tests/` directory
- Ensure all tests pass: `pytest`
- Aim for high test coverage
- Tests should mirror the structure of the main package

### 4. Run Quality Checks

Pre-commit hooks will run automatically, but you can also run them manually:

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run specific checks
black detectormappingvisualizer tests
flake8 detectormappingvisualizer
mypy detectormappingvisualizer
pytest
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add new visualization feature"
```

Use conventional commit messages:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for adding tests
- `refactor:` for code refactoring
- `style:` for formatting changes
- `chore:` for maintenance tasks

**Important**: Pre-commit hooks will run automatically before each commit. If they fail, fix the issues and commit again.

### 6. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- A clear title and description
- Reference to any related issues
- Screenshots if applicable

## Testing Guidelines

### Writing Tests

- Place tests in `tests/` directory
- Test file names should start with `test_`
- Test function names should start with `test_`
- Use descriptive test names that explain what is being tested

Example:
```python
def test_main_runs_without_error():
    """Test that main() runs without raising an exception."""
    main()
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=detectormappingvisualizer

# Run specific test file
pytest tests/test_main.py

# Run specific test
pytest tests/test_main.py::TestMain::test_main_runs_without_error
```

## Code Style

This project uses several tools to maintain code quality:

- **Black**: Automatic code formatting (line length: 100)
- **Flake8**: Linting and style checking
- **MyPy**: Static type checking
- **Pytest**: Testing framework

All these tools are configured in `pyproject.toml` and run via pre-commit hooks.

## Documentation

- Update `README.md` for user-facing changes
- Add docstrings to new functions and classes
- Use Google-style docstrings
- Update examples if the API changes

Example docstring:
```python
def process_data(data: dict, threshold: float = 0.5) -> list:
    """
    Process detector data and filter by threshold.
    
    Args:
        data: Dictionary containing detector measurements
        threshold: Minimum value for filtering (default: 0.5)
    
    Returns:
        List of processed data points above threshold
        
    Raises:
        ValueError: If data is empty or invalid
    """
    pass
```

## Pull Request Process

1. **Ensure all tests pass** and pre-commit hooks succeed
2. **Update documentation** if needed
3. **Add a clear PR description** explaining:
   - What changes were made
   - Why the changes were necessary
   - How the changes were tested
4. **Link related issues** using keywords (e.g., "Fixes #123")
5. **Wait for review** and address any feedback
6. **Squash commits** if requested before merging

## Release Process

Releases are automated via GitHub Actions:

1. Version bumping is handled automatically by a bot
2. When a version tag is pushed (e.g., `v0.2.0`), the release workflow:
   - Runs all tests
   - Builds the package
   - Creates a GitHub release
   - (Optionally) Publishes to PyPI

## Questions or Issues?

- **Bug reports**: Open an issue with the "bug" label
- **Feature requests**: Open an issue with the "enhancement" label
- **Questions**: Open a discussion on GitHub

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the Detector Mapping Visualizer! 🎉

