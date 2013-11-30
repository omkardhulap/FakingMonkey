#!/bin/bash
scp -i ~/.ssh/awskey_djmailhot.pem memstats.php $AWS_MICRO:
scp -i ~/.ssh/awskey_djmailhot.pem memcache.php $AWS_MICRO:

ssh -i ~/.ssh/awskey_djmailhot.pem $AWS_MICRO 'bash -s' < setup_server.sh
