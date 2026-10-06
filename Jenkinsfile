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
                bat 'C:\\Users\\abdul\\AppData\\Local\\Programs\\Python\\Python314\\python.exe -m pip install --upgrade pip'
		bat 'C:\\Users\\abdul\\AppData\\Local\\Programs\\Python\\Python314\\python.exe -m pip install -r requirements-dev.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'C:\\Users\\abdul\\AppData\\Local\\Programs\\Python\\Python314\\python.exe -m pytest'
            }
        }

        stage('Code Quality') {
            steps {
                bat 'C:\\Users\\abdul\\AppData\\Local\\Programs\\Python\\Python314\\python.exe -m flake8 .'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t aceest-fitness .'
            }
        }
    }

    post {
        always {
            echo 'Jenkins pipeline completed.'
        }
    }
}
