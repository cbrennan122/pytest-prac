pipeline {
    agent any
    options {
        timestamps()
        ansiColor('xterm')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }
    tools {
        python 'python3'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Setup venv & deps') {
            steps {
                sh '''
                    python -m venv .venv
                    . .venv/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements-dev.txt
                '''
            }
        }
        stage('Test') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python tools/ci_run.py --report-dir reports --extra -vv
                '''
            }
        }
        post {
            always {
                junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                archiveArtifacts artifacts: 'reports/**', fingerprint: true, onlyIfSuccessful: false
            }
        }
        post {
            always {echo "Build Finished: ${currentBuild.currentResult}" }
        }
    }
}