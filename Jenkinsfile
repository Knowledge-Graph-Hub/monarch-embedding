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
        // Very first: pause for a minute to give a chance to
        // cancel and clean the workspace before use.
        stage('Ready and clean') {
            steps {
                // Give us a minute to cancel if we want.
                sleep time: 1, unit: 'MINUTES'
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
            when { anyOf { branch 'master' } }
            steps {
                dir('./ansible') {
                    withCredentials([file(credentialsId: 'ansible-bbop-local-slave', variable: 'DEPLOY_LOCAL_IDENTITY')]) {
                        echo 'Trying to start up instance...'
                            // sh 'ansible-playbook update-kg-hub-endpoint.yaml --inventory=hosts.local-rdf-endpoint --private-key="$DEPLOY_LOCAL_IDENTITY" -e target_user=bbop --extra-vars="endpoint=internal"'
                            //
                            // keep trying to start the instance until success
                            //
                            sh '''#!/bin/bash
                                  echo "In bash script..."
                                  VM=graph-embedding-2-vm
                                  ZONE=us-central1-c
                                  STATUS=$(gcloud compute instances describe $VM --zone=$ZONE --format="yaml(status)")

                                  n=0
                                  until [ "$n" -ge 10 ]
                                  do
                                       echo "instance $VM $STATUS; trying to start instance..."
                                       gcloud compute instances start $VM --zone=$ZONE
                                       STATUS=$(gcloud compute instances describe $VM --zone=$ZONE --format="yaml(status)")

                                       [ "$STATUS" != "status: TERMINATED" ] && break
                                       n=$((n+1))
                                       sleep 30
                                  done
                                  gcloud compute instances describe $VM --zone=$ZONE --format="yaml(status)"
                            '''
                    }
                }

            }
        }

    }
}
