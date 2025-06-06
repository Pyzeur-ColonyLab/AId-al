#!/bin/bash

# 💬 Simple AI Chatbot Deployment Script
# Lightweight deployment without database - just pure chatbot functionality
# Works with any HuggingFace model on Amazon Linux

set -e

echo "💬 Simple AI Chatbot Deployment"
echo "==============================="
echo "Lightweight setup - No database required"
echo "Perfect for quick testing and simple chatbots"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_chatbot() { echo -e "${CYAN}[CHATBOT]${NC} $1"; }

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check available memory
    total_mem=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $total_mem -ge 3 ]]; then
        print_success "Memory: ${total_mem}GB available ✓"
    else
        print_warning "Low memory detected: ${total_mem}GB"
        echo "Consider using smaller models like gpt2 or DistilBERT"
    fi
    
    # Check available storage
    available_space=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $available_space -ge 10 ]]; then
        print_success "Storage: ${available_space}GB available ✓"
    else
        print_error "Need at least 10GB available storage"
        exit 1
    fi
}

# Install Docker for Amazon Linux
install_docker() {
    print_status "Installing Docker..."
    
    # Detect OS
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        if [[ "$NAME" == *"Amazon Linux"* ]]; then
            # Amazon Linux
            sudo yum update -y
            sudo yum install -y docker
        elif [[ "$NAME" == *"Ubuntu"* ]] || [[ "$NAME" == *"Debian"* ]]; then
            # Ubuntu/Debian
            sudo apt update
            sudo apt install -y docker.io
        else
            print_error "Unsupported OS. Please install Docker manually."
            exit 1
        fi
    fi
    
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    
    print_success "Docker installed ✓"
}

# Install Docker Compose
install_docker_compose() {
    print_status "Installing Docker Compose..."
    
    if command -v pip3 &> /dev/null; then
        sudo pip3 install docker-compose
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3-pip
        sudo pip3 install docker-compose
    elif command -v apt &> /dev/null; then
        sudo apt install -y docker-compose
    else
        print_error "Cannot install Docker Compose. Please install manually."
        exit 1
    fi
    
    print_success "Docker Compose installed ✓"
}

# Create simple chatbot configuration
setup_simple_chatbot() {
    print_chatbot "Setting up simple chatbot configuration..."
    
    # Create minimal docker-compose for chatbot only
    cat > docker-compose.simple.yml << 'EOF'
version: '3.8'

services:
  chatbot:
    build: .
    container_name: simple_ai_chatbot
    env_file:
      - .env
    environment:
      - SIMPLE_MODE=true
      - USE_DATABASE=false
      - USE_REDIS=false
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
      - huggingface_cache:/tmp/huggingface
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 1G

volumes:
  huggingface_cache:
EOF

    print_success "Simple chatbot configuration created ✓"
}

# Create minimal Dockerfile for chatbot
create_simple_dockerfile() {
    print_chatbot "Creating optimized Dockerfile..."
    
    # Backup original Dockerfile if it exists
    if [[ -f Dockerfile ]]; then
        cp Dockerfile Dockerfile.backup
    fi
    
    cat > Dockerfile.simple << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for simple mode
RUN pip install --no-cache-dir \
    python-telegram-bot==20.3 \
    transformers==4.30.0 \
    torch==2.0.0 \
    accelerate==0.20.0

# Copy application code
COPY . .

# Create directories
RUN mkdir -p models logs

# Expose port (optional)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the bot
CMD ["python", "app.py"]
EOF

    print_success "Simple Dockerfile created ✓"
}

# Configure the chatbot
configure_simple_chatbot() {
    print_chatbot "Configuring your AI chatbot..."
    
    echo ""
    echo "💬 Simple Chatbot Configuration"
    echo "==============================="
    echo ""
    
    # Telegram Bot Token
    while [[ -z "$telegram_token" ]]; do
        read -p "🤖 Telegram Bot Token: " telegram_token
        if [[ -z "$telegram_token" ]]; then
            print_error "Telegram Bot Token is required"
        fi
    done
    
    # Model selection for simple setup
    echo ""
    echo "🎯 Choose your AI model:"
    echo "1) gpt2 (Fast, lightweight - 124MB)"
    echo "2) microsoft/DialoGPT-small (Good chat - 117MB)"
    echo "3) microsoft/DialoGPT-medium (Better chat - 345MB)"
    echo "4) distilgpt2 (Very fast - 82MB)"
    echo "5) Pyzeur/Code-du-Travail-mistral-finetune (Legal assistant - 7GB)"
    echo "6) Custom model name"
    echo ""
    
    read -p "Choose option (1-6): " model_choice
    
    case $model_choice in
        1) 
            model_name="gpt2"
            memory_limit="2G"
            ;;
        2) 
            model_name="microsoft/DialoGPT-small"
            memory_limit="2G"
            ;;
        3) 
            model_name="microsoft/DialoGPT-medium" 
            memory_limit="3G"
            ;;
        4) 
            model_name="distilgpt2"
            memory_limit="1G"
            ;;
        5) 
            model_name="Pyzeur/Code-du-Travail-mistral-finetune"
            memory_limit="8G"
            echo ""
            print_warning "This model requires a HuggingFace token and significant memory"
            read -p "🤗 HuggingFace Token: " hf_token
            ;;
        6) 
            read -p "Enter custom model name: " custom_model
            model_name="$custom_model"
            memory_limit="4G"
            read -p "🤗 HuggingFace Token (if needed): " hf_token
            ;;
        *) 
            print_warning "Invalid choice, using default model"
            model_name="gpt2"
            memory_limit="2G"
            ;;
    esac
    
    # Optional settings
    echo ""
    echo "⚙️ Optional Settings:"
    read -p "🌡️  Temperature (0.1-1.0, default 0.7): " temperature
    temperature=${temperature:-0.7}
    
    read -p "📏 Max response length (default 100): " max_length
    max_length=${max_length:-100}
    
    read -p "👑 Admin user ID (optional): " admin_user
    
    # Create simple .env file
    print_chatbot "Creating configuration file..."
    
    cat > .env.simple << EOF
# Simple Chatbot Configuration
TELEGRAM_BOT_TOKEN=$telegram_token
MODEL_NAME=$model_name
HF_TOKEN=${hf_token:-}

# Simple mode settings
SIMPLE_MODE=true
USE_DATABASE=false
USE_REDIS=false

# Model parameters
TEMPERATURE=$temperature
MAX_LENGTH=$max_length
DEVICE=cpu
USE_QUANTIZATION=false

# Optional admin
ADMIN_USERS=${admin_user:-}

# Logging
LOG_LEVEL=INFO
ENABLE_CONVERSATION_LOGGING=false

# Performance
BATCH_SIZE=1
MAX_WORKERS=2

# Memory limit for docker
MEMORY_LIMIT=$memory_limit
EOF

    cp .env.simple .env
    
    print_success "Configuration complete ✓"
}

# Deploy the simple chatbot
deploy_simple_chatbot() {
    print_chatbot "Deploying your AI chatbot..."
    
    # Create logs directory
    mkdir -p logs models
    
    # Update docker-compose with memory limit
    if [[ -n "$memory_limit" ]]; then
        sed -i "s/memory: 4G/memory: $memory_limit/" docker-compose.simple.yml
    fi
    
    # Use simple Dockerfile
    if [[ -f Dockerfile.simple ]]; then
        cp Dockerfile.simple Dockerfile
    fi
    
    # Create simple monitoring script
    cat > monitor_simple.sh << 'EOF'
#!/bin/bash
echo "💬 Simple Chatbot Monitoring"
echo "============================"
echo ""
echo "📊 System Resources:"
free -h
echo ""
echo "🤖 Chatbot Status:"
docker-compose -f docker-compose.simple.yml ps
echo ""
echo "📈 Container Resources:"
docker stats --no-stream simple_ai_chatbot 2>/dev/null || echo "Chatbot not running"
echo ""
echo "📋 Recent Logs:"
docker-compose -f docker-compose.simple.yml logs --tail=5 chatbot 2>/dev/null || echo "No logs available"
EOF

    chmod +x monitor_simple.sh
    
    print_status "Building and starting chatbot..."
    
    # Build and start
    docker-compose -f docker-compose.simple.yml up -d --build
    
    print_success "🎉 Simple AI Chatbot deployed successfully!"
    
    echo ""
    echo "💬 Your AI Chatbot is Ready!"
    echo "============================"
    echo ""
    echo "🤖 Model: $model_name"
    echo "🧠 Memory: $memory_limit allocated"
    echo "🌡️  Temperature: $temperature"
    echo "📏 Max length: $max_length tokens"
    echo "📱 Telegram: Active"
    echo ""
    echo "🔧 Management Commands:"
    echo "  📊 Status:     ./monitor_simple.sh"
    echo "  📋 Logs:       docker-compose -f docker-compose.simple.yml logs -f chatbot"
    echo "  🔄 Restart:    docker-compose -f docker-compose.simple.yml restart"
    echo "  🛑 Stop:       docker-compose -f docker-compose.simple.yml down"
    echo ""
    echo "🤖 Bot Commands:"
    echo "  /start - Start chatting"
    echo "  /chat <message> - Chat with AI"
    echo "  /info - Bot information"
    echo ""
    echo "💡 Example: /chat Hello, how are you?"
    echo ""
}

# Simple health check
health_check_simple() {
    print_chatbot "Checking chatbot health..."
    
    sleep 15  # Wait for startup
    
    if docker-compose -f docker-compose.simple.yml ps | grep -q "Up"; then
        print_success "Chatbot is running ✓"
    else
        print_error "Chatbot failed to start"
        echo "Check logs with: docker-compose -f docker-compose.simple.yml logs chatbot"
        return 1
    fi
    
    # Check if model loaded
    if docker-compose -f docker-compose.simple.yml logs chatbot | grep -q "Model loaded\|Bot started\|Ready"; then
        print_success "AI model loaded successfully ✓"
    else
        print_warning "Model still loading... This may take a few minutes"
    fi
    
    print_success "✨ Your AI chatbot is ready to chat!"
}

# Main deployment function
main() {
    echo ""
    print_status "Starting simple chatbot deployment..."
    echo ""
    
    check_requirements
    
    # Install Docker if needed
    if ! command -v docker &> /dev/null; then
        install_docker
        print_warning "Please log out and log back in, then run this script again"
        exit 0
    fi
    
    # Install Docker Compose if needed
    if ! command -v docker-compose &> /dev/null; then
        install_docker_compose
    fi
    
    setup_simple_chatbot
    create_simple_dockerfile
    configure_simple_chatbot
    deploy_simple_chatbot
    health_check_simple
    
    echo ""
    read -p "Would you like to view the chatbot logs? (y/n): " show_logs
    if [[ "$show_logs" =~ ^[Yy]$ ]]; then
        print_chatbot "Showing logs (Ctrl+C to exit)..."
        docker-compose -f docker-compose.simple.yml logs -f chatbot
    fi
}

# Script management commands
case "${1:-}" in
    "logs")
        docker-compose -f docker-compose.simple.yml logs -f chatbot
        ;;
    "status")
        ./monitor_simple.sh
        ;;
    "restart")
        print_chatbot "Restarting chatbot..."
        docker-compose -f docker-compose.simple.yml restart
        print_success "Chatbot restarted ✓"
        ;;
    "stop")
        print_chatbot "Stopping chatbot..."
        docker-compose -f docker-compose.simple.yml down
        print_success "Chatbot stopped ✓"
        ;;
    "start")
        print_chatbot "Starting chatbot..."
        docker-compose -f docker-compose.simple.yml up -d
        print_success "Chatbot started ✓"
        ;;
    "update")
        print_chatbot "Updating chatbot..."
        git pull
        docker-compose -f docker-compose.simple.yml up -d --build
        print_success "Chatbot updated ✓"
        ;;
    "monitor")
        ./monitor_simple.sh
        ;;
    "clean")
        print_chatbot "Cleaning up..."
        docker-compose -f docker-compose.simple.yml down -v
        docker system prune -f
        print_success "Cleanup complete ✓"
        ;;
    "")
        main
        ;;
    *)
        echo "Usage: $0 [logs|status|restart|stop|start|update|monitor|clean]"
        echo ""
        echo "💬 Simple AI Chatbot Management"
        echo "==============================="
        echo ""
        echo "Commands:"
        echo "  logs    - Show chatbot logs"
        echo "  status  - Show status and monitoring"
        echo "  restart - Restart the chatbot"
        echo "  stop    - Stop the chatbot"
        echo "  start   - Start the chatbot"
        echo "  update  - Update and rebuild"
        echo "  monitor - Show system monitoring"
        echo "  clean   - Clean up everything"
        echo ""
        echo "Run without arguments for interactive setup"
        ;;
esac
