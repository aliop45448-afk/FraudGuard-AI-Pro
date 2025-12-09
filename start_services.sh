#!/bin/bash

echo "🚀 Starting FraudGuard AI Pro Services..."
echo ""

# Create logs directory
mkdir -p logs

# Function to start a service
start_service() {
    local service_name=$1
    local port=$2
    local script=$3
    
    echo "Starting $service_name on port $port..."
    cd "/tmp/FraudGuard-AI-Pro/services/$service_name"
    python3 "$script" > "../../logs/${service_name}.log" 2>&1 &
    echo $! > "../../logs/${service_name}.pid"
    sleep 2
}

# Start all services
start_service "api-gateway" "5000" "gateway.py"
start_service "auth-service" "5001" "app.py"
start_service "monitoring-service" "5002" "dashboard_service.py"
start_service "inference-service" "5003" "app.py"
start_service "api-service" "5004" "api_service.py"
start_service "security-service" "5005" "security_compliance.py"
start_service "reports-service" "5006" "reports_analytics.py"
start_service "ai-assistant-service" "5007" "ai_assistant.py"
start_service "integrations-service" "5008" "integrations.py"

echo ""
echo "✅ All services started!"
echo ""
echo "Service Status:"
echo "  - API Gateway: http://localhost:5000"
echo "  - Auth Service: http://localhost:5001"
echo "  - Monitoring Service: http://localhost:5002"
echo "  - Inference Service: http://localhost:5003"
echo "  - API Service: http://localhost:5004"
echo "  - Security Service: http://localhost:5005"
echo "  - Reports Service: http://localhost:5006"
echo "  - AI Assistant: http://localhost:5007"
echo "  - Integrations Service: http://localhost:5008"
echo ""
echo "Logs available in: logs/ directory"
