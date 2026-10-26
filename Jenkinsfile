// Optional alternative CI, not an additional required pipeline.
// Dedicated Linux agent needs Python 3.12, Docker, Terraform 1.9.x and registry access.
pipeline {
  agent { label 'docker' }
  options { timestamps(); timeout(time: 20, unit: 'MINUTES'); disableConcurrentBuilds() }
  stages {
    stage('Test') {
      steps { sh "python3 -m unittest discover -s app -p 'test_*.py' -v" }
    }
    stage('Terraform validate') {
      steps { dir('infra/terraform') { sh 'terraform fmt -check && terraform init -backend=false -input=false && terraform validate' } }
    }
    stage('Build') {
      steps { sh 'docker build --pull --build-arg APP_VERSION="$GIT_COMMIT" -t release-status:jenkins-$BUILD_NUMBER .' }
    }
    stage('Security') {
      steps {
        sh 'docker run --rm -v "$WORKSPACE:/src:ro" aquasec/trivy:0.65.0 fs --scanners misconfig,secret --severity HIGH,CRITICAL --exit-code 1 /src'
        sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:0.65.0 image --severity HIGH,CRITICAL --exit-code 1 release-status:jenkins-$BUILD_NUMBER'
      }
    }
  }
  post { always { sh 'docker image rm release-status:jenkins-$BUILD_NUMBER || true' } }
}
