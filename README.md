# ACEEST Fitness DevOps

A foundational Flask web application for fitness and gym management, with automated testing, code-quality checks, Docker support, GitHub Actions CI, and Jenkins CI.

## Project Overview

This project provides fitness and gym-management services through a Flask application.

### Application Features

- Calorie calculation
- BMI calculation
- Membership management
- Weekly progress tracking
- Workout logging
- Fitness program generation
- Health check endpoint

## Project Structure

```text
aceest-fitness-devops/
├── .github/
│   └── workflows/
│       └── main.yml
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   └── test_fitness.py
├── .flake8
├── .gitignore
├── app.py
├── Dockerfile
├── Jenkinsfile
├── fitness.py
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Run the Application Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Flask application:

```bash
python app.py
```

Open:

```text
http://localhost:5000
```

Health check:

```text
http://localhost:5000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## Run Tests

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run Pytest:

```bash
pytest
```

Run Flake8:

```bash
flake8 .
```

## Docker

Build the Docker image:

```bash
docker build -t aceest-fitness .
```

Run the container:

```bash
docker run -d -p 5000:5000 --name aceest-fitness-container aceest-fitness
```

Check the running container:

```bash
docker ps
```

Test the application:

```text
http://localhost:5000/health
```

The Docker image uses Python 3.11, installs dependencies from `requirements.txt`, and runs the application using Gunicorn with one worker.

## GitHub Actions

The workflow is located at:

```text
.github/workflows/main.yml
```

The workflow:

1. Checks out the source code.
2. Sets up Python 3.11.
3. Installs development dependencies.
4. Runs Pytest.
5. Runs Flake8.
6. Builds the Docker image.

It runs for pushes to `main` and feature branches, and for pull requests targeting `main`.

## Jenkins

The Jenkins pipeline is defined in:

```text
Jenkinsfile
```

The pipeline:

1. Checks out the source code.
2. Installs Python dependencies.
3. Runs Pytest.
4. Runs Flake8.
5. Builds the Docker image.

Jenkins requires Python and Docker access on the Jenkins build agent.

## Git Branching Strategy

Feature-based branches are used:

```text
main
 ├── feature/flask-app
 ├── feature/docker
 ├── feature/github-actions
 ├── feature/jenkins
 └── feature/documentation
```

Changes are developed in feature branches and merged into `main` through Pull Requests.

## Development Workflow

```text
Develop feature
      ↓
Create feature branch
      ↓
Commit changes
      ↓
Push branch to GitHub
      ↓
Create Pull Request
      ↓
Run CI checks
      ↓
Merge into main
```

## License

This project is created for the ACEEST Fitness DevOps assignment.
