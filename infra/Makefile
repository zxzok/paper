PROJECT_NAME=manuweaver

build-backend:
docker build -f infra/Dockerfile -t $(PROJECT_NAME)-backend .

build-frontend:
docker build -f infra/Dockerfile.frontend -t $(PROJECT_NAME)-frontend .

up:
docker compose up --build

down:
docker compose down
