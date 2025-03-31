# CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment.

## Workflows

### Main CI/CD Pipeline

The main pipeline (`ci-cd.yml`) runs on every push to the main branch and on pull requests. It includes:

1. **Testing**: Runs the test suite with pytest across multiple Python versions
2. **Linting**: Checks code quality with flake8, black, and isort
3. **Building**: Creates distribution packages
4. **Publishing**: Publishes to PyPI when a new version tag is pushed

### Documentation

The documentation workflow (`docs.yml`) builds and deploys the project documentation to GitHub Pages whenever changes are made to documentation files or Python code.

### Regression Testing

The regression testing workflow (`regression.yml`) runs a comprehensive test suite weekly and can be triggered manually. This ensures the tool works correctly with various configurations and simulators.

## Setting Up Secrets

For the publishing step to work, you need to set up the following secrets in your GitHub repository:

1. `PYPI_USERNAME`: Your PyPI username
2. `PYPI_PASSWORD`: Your PyPI password or token

To add these secrets:
1. Go to your GitHub repository
2. Click on "Settings"
3. Click on "Secrets and variables" > "Actions"
4. Click "New repository secret"
5. Add each secret with its appropriate value 