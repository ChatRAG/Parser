#!/bin/sh
aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin 698446905433.dkr.ecr.ap-southeast-2.amazonaws.com

docker build -t chatrag/parser .

docker tag chatrag/parser:latest 698446905433.dkr.ecr.ap-southeast-2.amazonaws.com/chatrag/parser:latest

docker push 698446905433.dkr.ecr.ap-southeast-2.amazonaws.com/chatrag/parser:latest

#aws ecs register-task-definition --cli-input-json file://task-definition.json
