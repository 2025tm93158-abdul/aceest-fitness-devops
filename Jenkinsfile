pipeline {
    agent any

    options {
        skipDefaultCheckout()
        disableConcurrentBuilds()
    }

    triggers {
        pollSCM('H/5 * * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/python -m pip install -r requirements-dev.txt pytest-cov
                '''
            }
        }

        stage('Pytest and Coverage') {
            steps {
                sh '''
                    mkdir -p reports
                    .venv/bin/python -m pytest --junitxml=reports/pytest.xml --cov=app --cov=fitness --cov-report=xml:reports/coverage.xml
                '''
            }
        }

        stage('Flake8') {
            steps {
                sh '.venv/bin/python -m flake8 .'
            }
        }

        stage('SonarQube Quality Gate') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_AUTH_TOKEN')]) {
                    sh '''
                        set +x
                        export SONARQUBE_SCANNER_PARAMS="$(printf '{"sonar.login":"%s"}' "$SONAR_AUTH_TOKEN")"
                        /opt/sonar-scanner-5.0.2.4997-linux/bin/sonar-scanner \
                            -Dsonar.host.url=http://localhost:9000 \
                            -Dsonar.projectKey=aceest-fitness \
                            -Dsonar.sources=app.py,fitness.py \
                            -Dsonar.tests=tests \
                            -Dsonar.python.version=3.9 \
                            -Dsonar.python.coverage.reportPaths=reports/coverage.xml \
                            -Dsonar.qualitygate.wait=true \
                            -Dsonar.qualitygate.timeout=180
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t aceest-fitness:ci .'
            }
        }

        stage('Test Inside Docker') {
            steps {
                sh '''
                    docker run --rm aceest-fitness:ci sh -c 'python -m pip install --no-cache-dir pytest && python -m pytest'
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    sh '''
                        set +x
                        DOCKER_CONFIG="$(mktemp -d)"
                        export DOCKER_CONFIG
                        trap 'rm -rf -- "$DOCKER_CONFIG"' EXIT

                        printf '%s' "$DOCKERHUB_TOKEN" | docker login --username "$DOCKERHUB_USER" --password-stdin
                        IMAGE="2025tm93158/aceest-fitness:vm-$(git rev-parse --short=12 HEAD)"
                        docker tag aceest-fitness:ci "$IMAGE"
                        docker push "$IMAGE"
                        echo "Published $IMAGE"
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/*.xml', allowEmptyArchive: true
        }
    }
}
