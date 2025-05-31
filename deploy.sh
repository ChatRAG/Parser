#!/bin/sh
aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin 698446905433.dkr.ecr.ap-southeast-2.amazonaws.com

docker build -t chatrag/parser .

docker tag chatrag/parser:latest 698446905433.dkr.ecr.ap-southeast-2.amazonaws.com/chatrag/parser:latest

docker push 698446905433.dkr.ecr.ap-southeast-2.amazonaws.com/chatrag/parser:latest

echo "Open Amazon ECR to check out the newly published docker image."

echo "Use this docker URI to create a new Amazon ECS task version, and run it on a cluster."
