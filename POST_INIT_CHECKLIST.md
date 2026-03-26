# Post-Initialization Checklist

This checklist guides you through the manual steps needed after running `make init NAME=your-project` to customize your new project.

## 🎯 Overview

The `make init` command automates the following:
- ✅ Renames the module directory from `example_module` to your project name (hyphenated names are normalized: my-project → my_project)
- ✅ Updates `pyproject.toml` with your project name
- ✅ Updates all Python imports to use the new module name
- ✅ Updates CI workflow to use the new module name
- ✅ Removes `main.py` (template uses a library package structure)

However, some items require manual attention to ensure your project is properly configured.

## 📋 Documentation Updates

### README.md
- [ ] **Update project title and description**
  - Change "Python Starter Template" to your project name
  - Update the description to reflect what your project does
  - Add your project's specific features

- [ ] **Replace `[[MODULE_NAME]]` references**
  - Search for all instances of `[[MODULE_NAME]]`
  - Replace with your actual module name (e.g., project name `my-project` becomes module directory `my_project`)

- [ ] **Update CI badge URLs**
  - Replace `YOUR_USERNAME` with your GitHub username
  - Replace `YOUR_REPO` with your repository name
  - Example: `https://github.com/johndoe/my-awesome-project/workflows/CI/badge.svg`

- [ ] **Update features list**
  - Remove or add features based on your project's capabilities
  - Add specific libraries or frameworks your project uses

- [ ] **Add usage examples**
  - Replace template examples with your actual usage
  - Add code snippets showing how to use your project

- [ ] **Remove the warning banner**
  - Delete the `⚠️ TEMPLATE FILE` banner at the top
  - Remove the "📝 Post-Initialization Checklist" section

### AGENTS.md
- [ ] **Review and customize patterns**
  - Update module organization to match your structure
  - Add project-specific commands or workflows
  - Remove git worktrees section if not using that workflow
  - Update coverage commands to use your module name

- [ ] **Remove the warning banner**
  - Delete the `⚠️ TEMPLATE FILE` banner at the top

## ⚙️ Configuration Updates

### pyproject.toml
- [ ] **Update project metadata**
  ```toml
  name = "your-project-name"
  description = "Your project description"
  authors = [{ name = "Your Name", email = "your.email@example.com" }]
  ```

- [ ] **Review dependencies**
  - Remove unused template dependencies
  - Add your project's specific dependencies
  - Update dev dependencies as needed

- [ ] **Update coverage configuration**
  - Ensure `[[MODULE_NAME]]` is replaced with your actual module name
  - Adjust coverage threshold if needed (default: 96%)

### .github/workflows/ci.yml
- [ ] **Review CI workflow**
  - The workflow is automatically updated by `make init`
  - Verify module name is correct in coverage commands
  - Add additional jobs if needed (e.g., deployment, integration tests)

## 🧹 Code Cleanup

### Module Structure
- [ ] **Review your module directory**
  - Remove or modify `core.py` based on your needs
  - Add new modules as needed
  - Update `__init__.py` with your public API

- [ ] **Update test files**
  - Rename `test_example.py` to match your modules
  - Remove template tests if not applicable
  - Add tests for your actual functionality

### main.py (if needed)
- [ ] **Decide if you need an entrypoint**
  - If creating a library: Keep removed (default behavior)
  - If creating an application: Create `main.py` with your entry point
  - Update `pyproject.toml` to include `[project.scripts]` if needed

## 🧪 Testing Updates

- [ ] **Update test configuration**
  - Ensure `[[MODULE_NAME]]` is replaced in `pyproject.toml`
  - Update coverage source paths if needed
  - Add test-specific fixtures in `conftest.py`

- [ ] **Run tests**
  ```bash
  pytest
  ```
  - Ensure all tests pass
  - Check coverage meets the 96% threshold

## 🚀 CI/CD Updates

- [ ] **Test CI workflow**
  - Push your changes to GitHub
  - Verify the CI workflow runs successfully
  - Check that coverage reports are generated correctly

- [ ] **Set up Codecov** (optional)
  - If using Codecov, add your repository token to GitHub secrets
  - Update `CODECOV_TOKEN` in repository settings

## 📄 License

- [ ] **Review license**
  - Template uses MIT License
  - Update LICENSE file if you need a different license
  - Update `license = "MIT"` in `pyproject.toml` if changed

## 🗑️ Remove Unnecessary Files

- [ ] **Remove template documentation**
  - Delete `POST_INIT_CHECKLIST.md` after completing all steps
  - Delete `TEMPLATE_GUIDE.md` (if you no longer need it)
  - Consider creating your own contributing guide

## ✅ Final Verification

- [ ] **Run all checks**
  ```bash
  make lint
  make pytest
  ```
  - Ensure linting passes
  - Ensure tests pass with adequate coverage

- [ ] **Test your project**
  - Install your package: `pip install -e .`
  - Test your public API
  - Verify documentation is clear and accurate

- [ ] **Commit your changes**
  ```bash
  git add .
  git commit -m "chore: customize project after initialization"
  ```

## 🎉 You're Done!

Your project is now fully configured and ready for development. Remember to:

- Keep documentation updated as you add features
- Maintain test coverage above 96%
- Follow the coding patterns defined in AGENTS.md
- Use conventional commits for your commit messages

For questions or issues, refer to the project documentation or create an issue in your repository.
