pipeline {
  agent any

  options {
    timestamps()
    ansiColor('xterm')
    buildDiscarder(logRotator(numToKeepStr: '20'))
    disableConcurrentBuilds()
  }

  parameters {
    booleanParam(name: 'RUN_SLOW_TESTS', defaultValue: false, description: 'Include slow tests')
  }

  environment {
    PY_COLORS = '1'
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
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
        // Retry the test stage once if it’s flaky
        retry(1) {
          sh """
            . .venv/bin/activate
            EXTRA_ARGS=''
            if [ "${RUN_SLOW_TESTS}" = "true" ]; then EXTRA_ARGS='-m slow'; fi
            python tools/ci_run.py --report-dir reports --extra -vv \$EXTRA_ARGS
          """
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
