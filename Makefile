.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo "Targets:"
	@echo "  build - Build the Docker image"
	@echo "  run - Run the Docker container"
	@echo "  stop - Stop and remove the Docker container"
	@echo "  logs - View the logs of the Docker container"
	@echo "  remove - Remove the Docker image"
.PHONY: build run stop logs remove

build:
	docker build -t notifications .

run_d:
	docker run -d --name notifications -p 8080:8080 notifications

run:
	docker run --name notifications -p 8080:8080 notifications

stop:
	docker stop notifications || true && docker rm notifications || true

logs:
	docker logs -f notifications

remove:
	docker rmi notifications || true

