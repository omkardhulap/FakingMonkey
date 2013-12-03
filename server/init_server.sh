#!/bin/bash
ssh -i /home/kinjyen/.ssh/awskey_djmailhot.pem $AWS_MICRO 'bash -s' < setup_server.sh
