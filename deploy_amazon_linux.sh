#!/bin/bash

# 🚀 AId-al Universal AI Bot Deployment Script for Amazon Linux
# Optimized for t3.xlarge EC2 instance with Amazon Linux

set -e  # Exit on error

echo "🤖 AId-al Universal AI Bot Deployment (Amazon Linux)"
echo "===================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "Don't run this script as root"
   exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Docker on Amazon Linux
install_docker_amazon_linux() {
    print_status "Installing Docker on Amazon Linux..."
    
    # Update system
    sudo yum update -y
    
    # Install Docker
    sudo yum install -y docker
    
    # Start Docker service
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    print_success "Docker installed successfully"
    print_warning "You may need to log out and log back in for Docker permissions to take effect"
}

# Function to install Docker Compose on Amazon Linux
install_docker_compose_amazon_linux() {
    print_status "Installing Docker Compose on Amazon Linux..."
    
    # Install pip if not present
    if ! command_exists pip3; then
        sudo yum install -y python3-pip
    fi
    
    # Install docker-compose via pip
    sudo pip3 install docker-compose
    
    print_success "Docker Compose installed successfully"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    if [[ ! -f .env ]]; then
        if [[ -f .env.example ]]; then
            cp .env.example .env
            print_success "Created .env file from template"
        else
            print_error ".env.example file not found"
            exit 1
        fi
    else
        print_warning ".env file already exists, skipping..."
    fi
}

# Function to optimize for t3.xlarge
optimize_for_instance() {
    print_status "Optimizing configuration for t3.xlarge instance..."
    
    # Create optimized docker-compose override for t3.xlarge
    cat > docker-compose.override.yml << 'EOF'
version: '3.8'

services:
  bot:
    deploy:
      resources:
        limits:
          memory: 12G  # Use more RAM available on t3.xlarge
          cpus: '3.5'  # Use most of the 4 vCPUs
        reservations:
          memory: 4G
          cpus: '1.0'
    environment:
      - MAX_LENGTH=512
      - USE_QUANTIZATION=false  # t3.xlarge has enough RAM
      - DEVICE=cpu
      - TEMPERATURE=0.7
      - TOP_P=0.9
      - TOP_K=50
EOF
    
    print_success "Created optimized configuration for t3.xlarge"
}

# Function to configure bot interactively
configure_bot() {
    print_status "Configuring bot settings..."
    
    echo ""
    echo "Please provide the following information:"
    echo ""
    
    # Telegram Bot Token
    while [[ -z "$telegram_token" ]]; do
        read -p "🤖 Telegram Bot Token: " telegram_token
        if [[ -z "$telegram_token" ]]; then
            print_error "Telegram Bot Token is required"
        fi
    done
    
    # Model selection optimized for t3.xlarge
    echo ""
    echo "🎯 Choose a model (optimized for t3.xlarge):"
    echo "1) microsoft/DialoGPT-medium (General chat - Recommended)"
    echo "2) gpt2 (Fast text generation)"
    echo "3) distilbert-base-cased-distilled-squad (Q&A)"
    echo "4) microsoft/DialoGPT-large (Larger chat model)"
    echo "5) Pyzeur/Code-du-Travail-mistral-finetune (Legal assistant)"
    echo "6) Custom model name"
    echo ""
    
    read -p "Choose option (1-6): " model_choice
    
    case $model_choice in
        1) model_name="microsoft/DialoGPT-medium" ;;
        2) model_name="gpt2" ;;
        3) model_name="distilbert-base-cased-distilled-squad" ;;
        4) model_name="microsoft/DialoGPT-large" ;;
        5) model_name="Pyzeur/Code-du-Travail-mistral-finetune" ;;
        6) 
            read -p "Enter custom model name: " custom_model
            model_name="$custom_model"
            ;;
        *) 
            print_warning "Invalid choice, using recommended model"
            model_name="microsoft/DialoGPT-medium"
            ;;
    esac
    
    # HuggingFace Token
    echo ""
    read -p "🤗 HuggingFace Token (optional, for private models): " hf_token
    
    # Database Password
    echo ""
    read -s -p "🔐 Database Password (or press Enter for default): " db_password
    if [[ -z "$db_password" ]]; then
        db_password="securepassword123"
    fi
    echo ""
    
    # Admin Users
    echo ""
    read -p "👑 Admin User IDs (comma-separated Telegram user IDs, optional): " admin_users
    
    # Update .env file
    print_status "Updating configuration file..."
    
    sed -i "s/TELEGRAM_BOT_TOKEN=.*/TELEGRAM_BOT_TOKEN=$telegram_token/" .env
    sed -i "s|MODEL_NAME=.*|MODEL_NAME=$model_name|" .env
    sed -i "s/HF_TOKEN=.*/HF_TOKEN=$hf_token/" .env
    sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$db_password/" .env
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql://botuser:$db_password@postgres:5432/aibot_db|" .env
    
    if [[ -n "$admin_users" ]]; then
        sed -i "s/ADMIN_USERS=.*/ADMIN_USERS=$admin_users/" .env
    fi
    
    print_success "Configuration updated"
}

# Function to setup system monitoring
setup_monitoring() {
    print_status "Setting up system monitoring..."
    
    # Install htop for better monitoring
    sudo yum install -y htop
    
    # Create monitoring script
    cat > monitor.sh << 'EOF'
#!/bin/bash
echo "=== System Resources ==="
echo "Memory Usage:"
free -h
echo ""
echo "Disk Usage:"
df -h
echo ""
echo "Docker Container Status:"
docker-compose ps
echo ""
echo "Container Resource Usage:"
docker stats --no-stream
EOF
    
    chmod +x monitor.sh
    print_success "Monitoring tools installed"
}

# Function to deploy the bot
deploy_bot() {
    print_status "Building and deploying the bot..."
    
    # Create necessary directories
    mkdir -p models/saved_models data
    
    # Set appropriate permissions
    sudo chown -R $USER:$USER models data
    
    # Pull latest images first
    docker-compose pull postgres redis
    
    # Build and start containers
    docker-compose up -d --build
    
    print_success "Bot deployed successfully!"
    
    echo ""
    echo "🎉 Deployment Complete on Amazon Linux!"
    echo "======================================"
    echo ""
    echo "Your Universal AI Bot is now running with:"
    echo "📱 Model: $model_name"
    echo "🖥️  Instance: t3.xlarge (4 vCPUs, 16GB RAM)"
    echo "💾 Storage: 30GB GP3"
    echo "🤖 Telegram Bot: Active"
    echo "🗄️  Database: PostgreSQL"
    echo "⚡ Cache: Redis"
    echo ""
    echo "Useful commands:"
    echo "  📊 Check status:        docker-compose ps"
    echo "  📋 View logs:           docker-compose logs -f bot"
    echo "  🔄 Restart bot:         docker-compose restart bot"
    echo "  🛑 Stop all:            docker-compose down"
    echo "  📈 Monitor resources:   ./monitor.sh"
    echo "  📊 System monitor:      htop"
    echo ""
    echo "Bot commands in Telegram:"
    echo "  /start - Get started"
    echo "  /chat <message> - Chat with AI"
    echo "  /info - Model information"
    echo "  /switch <model> - Switch models (admin)"
    echo ""
}

# Function to check deployment health
health_check() {
    print_status "Performing health check..."
    
    sleep 10  # Wait for containers to fully start
    
    # Check if containers are running
    if docker-compose ps | grep -q "Up"; then
        print_success "Containers are running"
    else
        print_error "Some containers failed to start"
        docker-compose logs
        return 1
    fi
    
    # Check bot logs for errors
    if docker-compose logs bot 2>&1 | grep -q "ERROR\|Exception\|Failed"; then
        print_warning "Bot logs contain errors, check with: docker-compose logs bot"
    else
        print_success "Bot appears to be running without errors"
    fi
}

# Main deployment function
main() {
    echo ""
    print_status "Starting deployment process for Amazon Linux..."
    echo ""
    
    # Check system requirements
    print_status "Checking system requirements..."
    
    # Check if we're on Amazon Linux
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        if [[ "$NAME" != *"Amazon Linux"* ]]; then
            print_warning "This script is optimized for Amazon Linux"
        fi
    fi
    
    # Install Docker if not present
    if ! command_exists docker; then
        install_docker_amazon_linux
        print_warning "Please log out and log back in, then run this script again"
        exit 0
    else
        print_success "Docker is installed"
    fi
    
    # Install Docker Compose if not present
    if ! command_exists docker-compose; then
        install_docker_compose_amazon_linux
    else
        print_success "Docker Compose is installed"
    fi
    
    # Setup environment
    setup_environment
    
    # Optimize for t3.xlarge
    optimize_for_instance
    
    # Configure bot
    configure_bot
    
    # Setup monitoring
    setup_monitoring
    
    # Deploy
    deploy_bot
    
    # Health check
    health_check
    
    # Ask if user wants to see logs
    echo ""
    read -p "Would you like to view the bot logs? (y/n): " show_logs_choice
    if [[ "$show_logs_choice" =~ ^[Yy]$ ]]; then
        print_status "Showing bot logs (Press Ctrl+C to exit)..."
        docker-compose logs -f bot
    fi
}

# Script options for management
case "${1:-}" in
    "logs")
        docker-compose logs -f bot
        ;;
    "status")
        print_status "Bot status:"
        docker-compose ps
        echo ""
        ./monitor.sh
        ;;
    "restart")
        print_status "Restarting bot..."
        docker-compose restart bot
        print_success "Bot restarted"
        ;;
    "stop")
        print_status "Stopping all services..."
        docker-compose down
        print_success "All services stopped"
        ;;
    "update")
        print_status "Updating bot..."
        git pull
        docker-compose up -d --build
        print_success "Bot updated"
        ;;
    "monitor")
        ./monitor.sh
        ;;
    "")
        main
        ;;
    *)
        echo "Usage: $0 [logs|status|restart|stop|update|monitor]"
        echo ""
        echo "Commands:"
        echo "  logs    - Show bot logs"
        echo "  status  - Show service status and resources"
        echo "  restart - Restart the bot"
        echo "  stop    - Stop all services"
        echo "  update  - Update and rebuild bot"
        echo "  monitor - Show system monitoring"
        echo ""
        echo "Run without arguments for interactive deployment"
        ;;
esac
