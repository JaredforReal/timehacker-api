#!/bin/bash

# 服务器部署脚本
echo "🚀 Starting TimeHacker API Deployment..."

# 检查环境变量
if [ ! -f .env ]; then
    echo "❌ .env file not found! Please copy .env.example to .env and configure it."
    exit 1
fi

echo "1. Building Docker image..."
docker-compose build --no-cache

echo "2. Running code quality checks..."
./scripts/check_quality.sh || {
    echo "❌ Code quality checks failed. Please fix issues before deployment."
    exit 1
}

echo "3. Running tests..."
docker-compose run --rm api pytest tests/ || {
    echo "❌ Tests failed. Please fix issues before deployment."
    exit 1
}

echo "4. Starting services..."
docker-compose up -d

echo "5. Waiting for services to be ready..."
sleep 30

echo "6. Health check..."
curl -f http://localhost:8000/ || {
    echo "❌ Health check failed!"
    docker-compose logs api
    exit 1
}

echo "✅ Deployment completed successfully!"
echo "📍 API is running at: http://localhost:8000"
echo "📊 API documentation: http://localhost:8000/docs"

echo "📋 Next steps:"
echo "1. Configure SSL certificates in the ssl/ directory"
echo "2. Update nginx.conf with your domain name"
echo "3. Set up your DNS to point to this server"
echo "4. Configure firewall rules"
