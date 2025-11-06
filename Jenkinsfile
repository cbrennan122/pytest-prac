pipeline {
  agent {
    docker {
      image 'python:3.11-slim'
      args '-u 0:0' // run as root to apt-get if needed
    }
  }

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '20'))
    disableConcurrentBuilds()
  }

  parameters {
    booleanParam(name: 'RUN_SLOW_TESTS', defaultValue: false, description: 'Include slow tests')
  }

  environment {
    PY_COLORS = '1'
    REPORT_DIR = 'reports'
  }

  stages {
    stage('Checkout') {
      steps { 
        deleteDir()
        checkout([$class: 'GitSCM',
        branches: [[name: '*/main']],
        userRemoteConfigs: [[url: 'https://github.com/cbrennan122/pytest-prac.git']],
        extensions: [[$class: 'CloneOption', noTags: true, shallow: false, depth: 0]]
        ])
       }
    }

    stage('System deps (fast)') {
      steps {
        ansiColor('xterm') {
          sh '''
            set -euxo pipefail
            apt-get update -y
            apt-get install -y --no-install-recommends git
            rm -rf /var/lib/apt/lists/*
          '''
        }
      }
    }

    stage('Setup venv & deps') {
      steps {
        ansiColor('xterm') {
          sh '''
            set -euxo pipefail
            python -m venv .venv
            . .venv/bin/activate
            python -m pip install --upgrade pip wheel
            if [ -f requirements-dev.txt ]; then
              pip install -r requirements-dev.txt
            fi
          '''
        }
      }
    }

    stage('Test') {
      steps {
        retry(1) {
          ansiColor('xterm') {
            sh '''
              set -euxo pipefail
              . .venv/bin/activate
              mkdir -p "$REPORT_DIR"

              EXTRA_ARGS=""
              if [ "${RUN_SLOW_TESTS}" = "true" ]; then
                EXTRA_ARGS="-m slow"
              fi

              # Your runner should write reports/junit.xml and reports/report.html
              python tools/ci_run.py --report-dir "$REPORT_DIR" --extra -vv ${EXTRA_ARGS}
            '''
          }
        }
      }
      post {
        always {
          junit allowEmptyResults: true, testResults: 'reports/junit.xml'
          publishHTML(target: [
            allowMissing: true,
            keepAll: true,
            alwaysLinkToLastBuild: true,
            reportDir: 'reports',
            reportFiles: 'report.html',
            reportName: 'Pytest HTML Report'
          ])
          archiveArtifacts artifacts: 'reports/**', fingerprint: true, onlyIfSuccessful: false
        }
      }
    }
  }

  post {
    success { echo "✅ Pipeline succeeded on ${env.BRANCH_NAME}" }
    unstable { echo "⚠️ Pipeline unstable" }
    failure { echo "❌ Pipeline failed" }
    always  { echo "Finished: ${currentBuild.currentResult}" }
  }
}
