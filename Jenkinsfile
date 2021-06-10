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
        GCLOUD_PROJECT = 'test-project-covid-19-277821'
        VM='graph-embedding-2-vm'
        ZONE='us-central1-c'
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
                    withCredentials([file(credentialsId: 'GCLOUD_CRED_JSON', variable: 'GCLOUD_CRED_JSON')]) {
                        echo 'Trying to start up instance...'
                            // keep trying to start the instance until success
                            //
                            sh '''#!/bin/bash
                                  gcloud auth activate-service-account --key-file=$GCLOUD_CRED_JSON --project $GCLOUD_PROJECT

                                  STATUS=$(gcloud compute instances describe $VM --zone=$ZONE --format="yaml(status)")

                                  n=0
                                  until [ "$n" -ge 10 ]
                                  do
                                       echo "instance $VM $STATUS; trying to start instance..."
                                       gcloud compute instances start $VM --zone=$ZONE
                                       STATUS=$(gcloud compute instances describe $VM --zone=$ZONE --format="yaml(status)")

                                       [ "$STATUS" != "status: TERMINATED" ] && break
                                       n=$((n+1))
                                       echo "no dice - sleeping for 30 s"
                                       sleep 30
                                  done
                                  gcloud compute instances describe $VM --zone=$ZONE --format="yaml(status)"
                            '''
                    }
                }

            }
        }


        stage('Stop Gcloud instance') {
            when { anyOf { branch 'main' } }
            steps {
                dir('./ansible') {
                    withCredentials([file(credentialsId: 'GCLOUD_CRED_JSON', variable: 'GCLOUD_CRED_JSON')]) {
                        echo 'Trying to stop instance...'
                            // keep trying to start the instance until success
                            //
                            sh '''#!/bin/bash
                                  gcloud auth activate-service-account --key-file=$GCLOUD_CRED_JSON --project $GCLOUD_PROJECT

                                  STATUS=$(gcloud compute instances describe $VM --zone=$ZONE --format="yaml(status)")

                                  n=0
                                  until [ "$n" -ge 10 ]
                                  do
                                       echo "instance $VM $STATUS; trying to start instance..."
                                       gcloud compute instances stop $VM --zone=$ZONE
                                       STATUS=$(gcloud compute instances describe $VM --zone=$ZONE --format="yaml(status)")

                                       [ "$STATUS" == "status: TERMINATED" ] && break
                                       n=$((n+1))
                                       echo "no dice - sleeping for 30 s"
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
