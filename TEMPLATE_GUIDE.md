# Python Starter Template Guide

This guide explains the purpose of this template and how to use it to start a new Python project.

## 🎯 What This Template Provides

The Python Starter Template is a **modern, opinionated starting point** for Python 3.13 projects. It includes:

- **Best Practices**: Preconfigured tooling and code quality standards
- **Fast Development**: uv for lightning-fast dependency management
- **High Quality**: 96% minimum test coverage with automated checks
- **CI/CD Ready**: GitHub Actions workflow for continuous integration
- **Type Safety**: Full type hints with pyright static analysis
- **Clean Code**: Automated linting and formatting with ruff

### Key Features

| Feature | Tool | Purpose |
|---------|------|---------|
| Package Manager | **uv** | Fast dependency management and virtual environments |
| Testing | **pytest** | Test runner with coverage reporting |
| Linting | **ruff** | Fast Python linter and formatter |
| Type Checking | **pyright** | Static type analysis |
| CI/CD | **GitHub Actions** | Automated testing on push/PR |
| Pre-commit Hooks | **Custom** | Enforce code quality before commits |

## 🚀 How to Use This Template

### Step 1: Create a New Repository

1. **Clone this template**:
   ```bash
   git clone https://github.com/JoshCLWren/python-starter-template.git your-project-name
   cd your-project-name
   ```

2. **Initialize your project**:
   ```bash
   make init NAME=your-project-name
   ```

   This command automates:
   - Renaming the module from `example_module` to your package directory/module name (hyphenated project names are normalized: my-project → my_project)
   - Updating `pyproject.toml` with your project name
   - Updating all Python imports to use the new module name
   - Updating CI workflow configuration
   - Removing the template's `main.py` (library package structure)

### Step 2: Install Dependencies

```bash
uv sync --group dev
```

This creates a virtual environment and installs all dependencies.

### Step 3: Activate Virtual Environment

```bash
source .venv/bin/activate
```

Do this once per terminal session.

### Step 4: Customize Your Project

**IMPORTANT**: The template includes placeholder text that needs manual updates. See **POST_INIT_CHECKLIST.md** for a complete guide.

Key items to update:
- ✏️ README.md - Project title, description, features, usage examples
- ✏️ AGENTS.md - Project-specific patterns and workflows
- ✏️ CI badge URLs - Replace `YOUR_USERNAME` and `YOUR_REPO`
- ✏️ Module name references - Replace `[[MODULE_NAME]]` with your actual module name

### Step 5: Verify Everything Works

```bash
# Run tests
pytest

# Run linting
make lint

# Run your application (if this is an application with an entrypoint)
# If you initialized a library/package (no main.py), skip this step
python main.py
```

## 🤖 What Gets Automated vs Manual

### ✅ Automated by `make init`

The `make init` command handles the mechanical renaming:

| Task | Description |
|------|-------------|
| Module renaming | Renames `example_module/` to your project name |
| Package config | Updates `name` in `pyproject.toml` |
| Import updates | Updates all `from example_module` and `import example_module` statements |
| CI workflow | Updates coverage paths in `.github/workflows/ci.yml` |
| Main cleanup | Removes `main.py` (library package structure) |

### 📝 Manual Updates Required

Some items require human judgment and can't be automated:

| Item | Why Manual? |
|------|-------------|
| Project description | Only you know what your project does |
| Features list | Every project has different features |
| Usage examples | Specific to your project's API |
| CI badge URLs | Requires your GitHub username and repo name |
| License choice | Legal decision varies by project |
| Documentation | Project-specific concepts and patterns |

## 📚 Template Structure

```text
python-starter-template/
├── [[MODULE_NAME]]/          # Your main package (renamed on init)
│   ├── __init__.py
│   └── core.py              # Example module (customize or remove)
├── tests/                    # Test suite
│   ├── conftest.py          # pytest fixtures
│   └── test_example.py      # Example tests (customize)
├── .github/
│   ├── actions/setup/        # CI setup action (installs uv, Python, etc.)
│   └── workflows/ci.yml     # CI pipeline (lint + tests)
├── scripts/
│   └── lint.sh              # Linting script (ruff + pyright)
├── .githooks/
│   └── pre-commit           # Pre-commit hook (blocks bad commits)
├── main.py                  # Application entrypoint (removed on init)
├── pyproject.toml          # Project configuration
├── uv.lock                 # Dependency lockfile
├── Makefile                # Convenience commands
├── README.md               # Project documentation (UPDATE THIS!)
├── AGENTS.md               # AI agent guidelines (UPDATE THIS!)
├── POST_INIT_CHECKLIST.md  # Post-init checklist (follow this!)
└── TEMPLATE_GUIDE.md       # This file
```

## 🔧 Development Workflow

### Daily Development

After initialization, your typical workflow is:

```bash
# Activate venv (once per session)
source .venv/bin/activate

# Make changes to your code
# ...

# Run tests
pytest

# Run linting
make lint

# Commit (pre-commit hook will run linting)
git add .
git commit -m "feat: add new feature"
```

### Key Commands

| Command | Description |
|---------|-------------|
| `make lint` | Run ruff + pyright checks |
| `make pytest` | Run test suite |
| `make sync` | Install/update dependencies |
| `pytest` | Run tests directly |
| `ruff format .` | Format code |
| `pyright .` | Run type checker |

## 🎓 Best Practices for Starting a New Project

### 1. Start Simple

- Begin with minimal functionality
- Add features incrementally
- Keep test coverage high from the start

### 2. Follow the Patterns

- Use type hints everywhere
- Write tests before or with code (TDD)
- Keep functions small and focused
- Use descriptive names (no abbreviations)

### 3. Leverage the Tooling

- Let ruff format your code automatically
- Use pyright to catch type errors early
- Run tests frequently while developing
- Trust the pre-commit hook to catch issues

### 4. Document as You Go

- Update README.md when adding features
- Add docstrings to public functions
- Keep AGENTS.md current with your project's patterns

### 5. Commit Often

- Use conventional commits (`feat:`, `fix:`, `docs:`, etc.)
- Keep commits small and focused
- Let the pre-commit hook enforce quality

## 🆘 Common Issues

### Issue: Tests fail after init

**Solution**: Make sure you've replaced all `[[MODULE_NAME]]` references in `pyproject.toml` with your actual module name.

### Issue: CI fails on GitHub

**Solution**: Update the CI badge URL in README.md to use your username and repo.

### Issue: Can't import my module

**Solution**: Make sure you've activated the virtual environment: `source .venv/bin/activate`

### Issue: Pre-commit hook blocking commits

**Solution**: This is intentional! Fix the linting/type errors before committing. Run `make lint` to see what's wrong.

## 📖 Additional Resources

- [uv Documentation](https://docs.astral.sh/uv/) - Fast Python package manager
- [pytest Documentation](https://docs.pytest.org/) - Testing framework
- [ruff Documentation](https://docs.astral.sh/ruff/) - Linter and formatter
- [pyright Documentation](https://microsoft.github.io/pyright/) - Type checker
- [Conventional Commits](https://www.conventionalcommits.org/) - Commit message standard

## 🤝 Contributing to the Template

If you find issues with the template or have suggestions for improvements:

1. Check existing issues at https://github.com/JoshCLWren/python-starter-template/issues
2. Create a new issue with details
3. Consider submitting a pull request with your improvements

## 📄 License

This template is released under the MIT License. Feel free to use it for your own projects.

## 🙏 Acknowledgments

Created by Josh Wren as a starting point for modern Python projects.

---

**Happy coding! 🎉**

Remember to follow the **POST_INIT_CHECKLIST.md** after running `make init` to customize your project properly.
