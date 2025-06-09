#!/bin/bash

# 💬 Simple AI Chatbot Deployment Script (Fixed)
# Lightweight deployment without database - just pure chatbot functionality
# Uses existing configuration structure to avoid Pydantic validation errors

set -e

echo "💬 Simple AI Chatbot Deployment (Fixed)"
echo "======================================="
echo "Lightweight setup - No database required"
echo "Compatible with existing settings structure"
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

# Quick fix function
quick_fix() {
    print_status "Applying quick fix for existing deployment..."
    
    # Stop the container
    docker-compose -f docker-compose.simple.yml down 2>/dev/null || true
    
    # Create a clean .env using only supported variables
    cat > .env << 'EOF'
# Basic Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_token_here
MODEL_NAME=gpt2
HF_TOKEN=

# Model Parameters
TEMPERATURE=0.7
MAX_LENGTH=100
DEVICE=cpu
USE_QUANTIZATION=false
BATCH_SIZE=1

# Database (required by settings but can point to dummy)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dummy_db
DB_USER=dummy_user
DB_PASSWORD=dummy_pass

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379

# Application
DEBUG=false
LOG_LEVEL=INFO
MAX_WORKERS=2

# Optional
ADMIN_USERS=
ALLOWED_USERS=
EOF

    # Use minimal docker-compose that works with current structure
    cat > docker-compose.minimal.yml << 'EOF'
version: '3.8'

services:
  simple_bot:
    build: .
    container_name: simple_ai_chatbot
    env_file:
      - .env
    volumes:
      - ./models:/app/models
      - huggingface_cache:/tmp/huggingface
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 512M

volumes:
  huggingface_cache:
EOF

    print_success "Quick fix applied ✓"
}

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check available memory
    total_mem=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $total_mem -ge 3 ]]; then
        print_success "Memory: ${total_mem}GB available ✓"
    else
        print_warning "Low memory detected: ${total_mem}GB"
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
    
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        if [[ "$NAME" == *"Amazon Linux"* ]]; then
            sudo yum update -y
            sudo yum install -y docker
        elif [[ "$NAME" == *"Ubuntu"* ]] || [[ "$NAME" == *"Debian"* ]]; then
            sudo apt update
            sudo apt install -y docker.io
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
    fi
    
    print_success "Docker Compose installed ✓"
}

# Configure the simple chatbot
configure_simple_chatbot() {
    print_chatbot "Configuring your simple AI chatbot..."
    
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
    
    # Simple model selection
    echo ""
    echo "🎯 Choose your AI model:"
    echo "1) gpt2 (Lightweight - 124MB)"
    echo "2) microsoft/DialoGPT-small (Good chat - 117MB)"
    echo "3) microsoft/DialoGPT-medium (Better chat - 345MB)"
    echo "4) distilgpt2 (Very fast - 82MB)"
    echo "5) Pyzeur/Code-du-Travail-mistral-finetune (Legal assistant)"
    echo "6) Custom model"
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
            read -p "🤗 HuggingFace Token: " hf_token
            ;;
        6) 
            read -p "Enter model name: " model_name
            memory_limit="4G"
            read -p "🤗 HuggingFace Token (if needed): " hf_token
            ;;
        *) 
            model_name="gpt2"
            memory_limit="2G"
            ;;
    esac
    
    # Optional settings
    echo ""
    read -p "🌡️  Temperature (0.1-1.0, default 0.7): " temperature
    temperature=${temperature:-0.7}
    
    read -p "📏 Max response length (default 100): " max_length
    max_length=${max_length:-100}
    
    read -p "👑 Admin user ID (optional): " admin_user
    
    # Create simple .env file with only supported variables
    print_chatbot "Creating configuration..."
    
    cat > .env << EOF
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=$telegram_token

# Model Configuration
MODEL_NAME=$model_name
HF_TOKEN=${hf_token:-}

# Model Parameters
TEMPERATURE=$temperature
MAX_LENGTH=$max_length
DEVICE=cpu
USE_QUANTIZATION=false
BATCH_SIZE=1

# Required Database Settings (dummy values for simple mode)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dummy_db
DB_USER=dummy_user
DB_PASSWORD=dummy_pass

# Optional Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
MAX_WORKERS=2

# User Management
ADMIN_USERS=${admin_user:-}
ALLOWED_USERS=

# Feature Flags (disable complex features)
ENABLE_URL_RESOURCES=false
ENABLE_SMART_CONTRACTS=false
ENABLE_METRICS=false
EOF

    print_success "Configuration complete ✓"
}

# Create minimal docker compose
create_minimal_compose() {
    print_chatbot "Creating minimal Docker configuration..."
    
    cat > docker-compose.minimal.yml << EOF
version: '3.8'

services:
  simple_bot:
    build: .
    container_name: simple_ai_chatbot
    env_file:
      - .env
    volumes:
      - ./models:/app/models
      - huggingface_cache:/tmp/huggingface
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: $memory_limit
        reservations:
          memory: 512M

volumes:
  huggingface_cache:
EOF

    print_success "Minimal configuration created ✓"
}

# Deploy the simple chatbot
deploy_simple_chatbot() {
    print_chatbot "Deploying simple AI chatbot..."
    
    mkdir -p models logs
    
    # Create monitoring script
    cat > monitor_minimal.sh << 'EOF'
#!/bin/bash
echo "💬 Simple Chatbot Monitoring"
echo "============================"
echo ""
echo "📊 System Resources:"
free -h
echo ""
echo "🤖 Bot Status:"
docker-compose -f docker-compose.minimal.yml ps
echo ""
echo "📈 Memory Usage:"
docker stats --no-stream simple_ai_chatbot 2>/dev/null || echo "Bot not running"
echo ""
echo "📋 Recent Logs:"
docker-compose -f docker-compose.minimal.yml logs --tail=10 simple_bot 2>/dev/null || echo "No logs yet"
EOF

    chmod +x monitor_minimal.sh
    
    print_status "Building and starting chatbot..."
    
    # Build and start with minimal compose
    docker-compose -f docker-compose.minimal.yml up -d --build
    
    print_success "🎉 Simple AI Chatbot deployed!"
    
    echo ""
    echo "💬 Your Simple AI Chatbot is Ready!"
    echo "==================================="
    echo ""
    echo "🤖 Model: $model_name"
    echo "🧠 Memory: $memory_limit allocated"
    echo "🌡️  Temperature: $temperature"
    echo "📏 Max length: $max_length tokens"
    echo ""
    echo "🔧 Management Commands:"
    echo "  📊 Status:     ./monitor_minimal.sh"
    echo "  📋 Logs:       docker-compose -f docker-compose.minimal.yml logs -f"
    echo "  🔄 Restart:    docker-compose -f docker-compose.minimal.yml restart"
    echo "  🛑 Stop:       docker-compose -f docker-compose.minimal.yml down"
    echo ""
    echo "🤖 Try these commands in Telegram:"
    echo "  /start"
    echo "  /chat Hello, how are you?"
    echo "  /info"
    echo ""
}

# Health check
health_check_simple() {
    print_chatbot "Checking chatbot health..."
    
    sleep 15
    
    if docker-compose -f docker-compose.minimal.yml ps | grep -q "Up"; then
        print_success "Chatbot is running ✓"
        
        # Check logs for successful startup
        if docker-compose -f docker-compose.minimal.yml logs simple_bot | grep -q "Bot started\|Model loaded\|telegram"; then
            print_success "Bot appears to be working ✓"
        else
            print_warning "Bot may still be initializing..."
        fi
    else
        print_error "Chatbot failed to start"
        echo "Check logs: docker-compose -f docker-compose.minimal.yml logs simple_bot"
        return 1
    fi
}

# Main function
main() {
    echo ""
    print_status "Starting simple chatbot deployment..."
    echo ""
    
    check_requirements
    
    if ! command -v docker &> /dev/null; then
        install_docker
        print_warning "Please log out and log back in, then run this script again"
        exit 0
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        install_docker_compose
    fi
    
    configure_simple_chatbot
    create_minimal_compose
    deploy_simple_chatbot
    health_check_simple
    
    echo ""
    read -p "View chatbot logs? (y/n): " show_logs
    if [[ "$show_logs" =~ ^[Yy]$ ]]; then
        docker-compose -f docker-compose.minimal.yml logs -f simple_bot
    fi
}

# Script commands
case "${1:-}" in
    "fix")
        quick_fix
        print_success "Applied quick fix. Now run: docker-compose -f docker-compose.minimal.yml up -d --build"
        ;;
    "logs")
        docker-compose -f docker-compose.minimal.yml logs -f simple_bot
        ;;
    "status")
        ./monitor_minimal.sh 2>/dev/null || echo "Run the script first to create monitoring"
        ;;
    "restart")
        docker-compose -f docker-compose.minimal.yml restart
        ;;
    "stop")
        docker-compose -f docker-compose.minimal.yml down
        ;;
    "start")
        docker-compose -f docker-compose.minimal.yml up -d
        ;;
    "clean")
        docker-compose -f docker-compose.minimal.yml down -v
        docker system prune -f
        ;;
    "")
        main
        ;;
    *)
        echo "Usage: $0 [fix|logs|status|restart|stop|start|clean]"
        echo ""
        echo "💬 Simple Chatbot Commands:"
        echo "  fix     - Quick fix for existing issues"
        echo "  logs    - Show logs"
        echo "  status  - Show status"
        echo "  restart - Restart bot"
        echo "  stop    - Stop bot"
        echo "  start   - Start bot"
        echo "  clean   - Clean everything"
        ;;
esac
