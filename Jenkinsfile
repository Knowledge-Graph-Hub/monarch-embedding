pipeline {
    agent any

    //     triggers{
    //         cron('H H 1 1-12 *')
    //     }

    environment {
        BUILDSTARTDATE = sh(script: "echo `date +%Y%m%d`", returnStdout: true).trim()
        S3PROJECTDIR = 'monarch-embedding' // no trailing slash

        // Distribution ID for the AWS CloudFront for this bucket
        // used solely for invalidations
        AWS_CLOUDFRONT_DISTRIBUTION_ID = 'EUVSWXZQBXCFP'
    }

    options {
        timestamps()
    }
    stages {
        // Very first: pause for a short time to give a chance to
        // cancel and clean the workspace before use.
        stage('Ready and clean') {
            steps {
                // Give us a moment to cancel if we want.
                sleep time: 30, unit: 'SECONDS'
                cleanWs()
            }
        }

        stage('Initialize') {
            steps {
                // Start preparing environment.
                parallel(
                        "Report": {
                            sh 'env > env.txt'
                            sh 'echo $BRANCH_NAME > branch.txt'
                            sh 'echo "$BRANCH_NAME"'
                            sh 'cat env.txt'
                            sh 'cat branch.txt'
                            sh "echo $BUILDSTARTDATE > dow.txt"
                            sh "echo $BUILDSTARTDATE"
                        })
            }
        }

        stage('Spin up Gcloud instance') {
            when { anyOf { branch 'main' } }
            steps {
                dir('./ansible') {
                    # CLOUDSDK_ACTIVE_CONFIG_NAME is automatically used by gcloud cli (I think)
                    withCredentials([file(credentialsId: 'GCLOUD_CRED_JSON', variable: 'CLOUDSDK_ACTIVE_CONFIG_NAME')]) {
                        echo 'Trying to start up instance...'
                            // sh 'ansible-playbook update-kg-hub-endpoint.yaml --inventory=hosts.local-rdf-endpoint --private-key="$DEPLOY_LOCAL_IDENTITY" -e target_user=bbop --extra-vars="endpoint=internal"'
                            //
                            // keep trying to start the instance until success
                            //
                            sh '''#!/bin/bash
                                  echo "In bash script..."
                                  VM=graph-embedding-2-vm
                                  ZONE=us-central1-c

                                  echo "env:"
                                  env

                                  echo "Testing for environmental variable CLOUDSDK_ACTIVE_CONFIG_NAME:"
                                  echo $CLOUDSDK_ACTIVE_CONFIG_NAME

                                  STATUS=$(gcloud --configuration=$CLOUDSDK_ACTIVE_CONFIG_NAME compute instances describe $VM --zone=$ZONE --format="yaml(status)")

                                  n=0
                                  until [ "$n" -ge 10 ]
                                  do
                                       echo "instance $VM $STATUS; trying to start instance..."
                                       gcloud compute instances start $VM --zone=$ZONE
                                       STATUS=$(gcloud --configuration=$CLOUDSDK_ACTIVE_CONFIG_NAME compute instances describe $VM --zone=$ZONE --format="yaml(status)")

                                       [ "$STATUS" != "status: TERMINATED" ] && break
                                       n=$((n+1))
                                       echo "no dice - sleeping for 30 s"
                                       sleep 30
                                  done
                                  gcloud --configuration=$CLOUDSDK_ACTIVE_CONFIG_NAME compute instances describe $VM --zone=$ZONE --format="yaml(status)"
                            '''
                    }
                }

            }
        }

    }
}
