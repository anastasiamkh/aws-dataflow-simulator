setup:
	aws configure
	cdk bootstrap aws://${AWS_ACCOUNT_ID}/eu-central-1
	poetry install

install:
	poetry install

lint:
	poetry run black . &&\
	poetry run ruff format

docker-build:
	docker build --platform linux/amd64 -t csv-to-kinesis .

docker-push:
	aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com &&\
	docker tag csv-to-kinesis:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/csv-to-kinesis-repo:latest &&\
	docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/csv-to-kinesis-repo:latest
