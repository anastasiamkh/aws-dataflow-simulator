setup:
	aws configure
	cdk bootstrap aws://${AWS_ACCOUNT_ID}/eu-central-1
	poetry install

install:
	poetry install

lint:
	poetry run black . &&\
	poetry run ruff format

unit-tests:
	poetry run pytest tests/

docker-build:
	docker buildx build --platform=linux/amd64 -t csv-to-kinesis-image .

docker-start:
	docker run -d -p 80:80 --platform=linux/amd64 \
	-e AWS_ACCESS_KEY_ID \
	-e AWS_DEFAULT_REGION \
	-e AWS_SECRET_ACCESS_KEY \
	csv-to-kinesis-image csv-to-kinesis-container

docker-cleanup:
	docker stop $(docker ps -q) &&\
	docker rm -f $(docker ps -a -q) &&\
	docker rmi -f $(docker images -q)

docker-ssh:
	docker run -i -t \
	-e PYTHONPATH=/app \
	-e AWS_ACCESS_KEY_ID \
	-e AWS_DEFAULT_REGION \
	-e AWS_SECRET_ACCESS_KEY \
	csv-to-kinesis-image /bin/bash

docker-push:
	aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com &&\
	docker tag csv-to-kinesis:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/csv-to-kinesis-repo:latest &&\
	docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/csv-to-kinesis-repo:latest
