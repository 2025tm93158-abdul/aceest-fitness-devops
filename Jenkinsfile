
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                    python -m venv .venv
                    .venv\\Scripts\\python.exe -m pip install --upgrade pip
                    .venv\\Scripts\\python.exe -m pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                bat '.venv\\Scripts\\python.exe -m pytest'
            }
        }

        stage('Code Quality') {
            steps {
                bat '.venv\\Scripts\\python.exe -m flake8 .'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '"C:\\Users\\abdul\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" build -t aceest-fitness .'
            }
        }
    }

    post {
        always {
            echo 'Jenkins pipeline completed.'
        }
    }
}
