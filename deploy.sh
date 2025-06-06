#!/bin/bash

# 🚀 AId-al Universal AI Bot Deployment Script
# This script automates the deployment of the Universal AI Telegram Bot

set -e  # Exit on error

echo "🤖 AId-al Universal AI Bot Deployment"
echo "====================================="

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

# Function to install Docker
install_docker() {
    print_status "Installing Docker..."
    
    # Update package index
    sudo apt-get update
    
    # Install dependencies
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Set up stable repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    print_success "Docker installed successfully"
}

# Function to install Docker Compose
install_docker_compose() {
    print_status "Installing Docker Compose..."
    
    # Install docker-compose
    sudo apt-get install -y docker-compose
    
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

# Function to prompt for configuration
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
    
    # Model Name
    echo ""
    echo "🎯 Choose a model or enter custom model name:"
    echo "1) Pyzeur/Code-du-Travail-mistral-finetune (Your fine-tuned model)"
    echo "2) microsoft/DialoGPT-medium (General chat)"
    echo "3) gpt2 (Text generation)"
    echo "4) distilbert-base-cased-distilled-squad (Question answering)"
    echo "5) Custom model name"
    echo ""
    
    read -p "Choose option (1-5): " model_choice
    
    case $model_choice in
        1) model_name="Pyzeur/Code-du-Travail-mistral-finetune" ;;
        2) model_name="microsoft/DialoGPT-medium" ;;
        3) model_name="gpt2" ;;
        4) model_name="distilbert-base-cased-distilled-squad" ;;
        5) 
            read -p "Enter custom model name: " custom_model
            model_name="$custom_model"
            ;;
        *) 
            print_warning "Invalid choice, using default model"
            model_name="microsoft/DialoGPT-medium"
            ;;
    esac
    
    # HuggingFace Token (optional)
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
    
    # Update .env file with user inputs
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

# Function to build and deploy
deploy_bot() {
    print_status "Building and deploying the bot..."
    
    # Create necessary directories
    mkdir -p models/saved_models data
    
    # Build and start containers
    docker-compose up -d --build
    
    print_success "Bot deployed successfully!"
    
    echo ""
    echo "🎉 Deployment Complete!"
    echo "====================="
    echo ""
    echo "Your Universal AI Bot is now running with:"
    echo "📱 Model: $model_name"
    echo "🤖 Telegram Bot: Active"
    echo "🗄️  Database: PostgreSQL"
    echo "⚡ Cache: Redis"
    echo ""
    echo "Useful commands:"
    echo "  📊 Check status:    docker-compose ps"
    echo "  📋 View logs:       docker-compose logs -f bot"
    echo "  🔄 Restart bot:     docker-compose restart bot"
    echo "  🛑 Stop all:        docker-compose down"
    echo ""
    echo "Bot commands in Telegram:"
    echo "  /start - Get started"
    echo "  /chat <message> - Chat with AI"
    echo "  /info - Model information"
    echo "  /switch <model> - Switch models (admin)"
    echo ""
}

# Function to show logs
show_logs() {
    print_status "Showing bot logs (Press Ctrl+C to exit)..."
    docker-compose logs -f bot
}

# Main deployment function
main() {
    echo ""
    print_status "Starting deployment process..."
    echo ""
    
    # Check system requirements
    print_status "Checking system requirements..."
    
    if ! command_exists docker; then
        print_warning "Docker not found, installing..."
        install_docker
        print_warning "Please log out and log back in for Docker permissions to take effect"
        print_warning "Then run this script again"
        exit 0
    else
        print_success "Docker is installed"
    fi
    
    if ! command_exists docker-compose; then
        install_docker_compose
    else
        print_success "Docker Compose is installed"
    fi
    
    # Setup environment
    setup_environment
    
    # Configure bot
    configure_bot
    
    # Deploy
    deploy_bot
    
    # Ask if user wants to see logs
    echo ""
    read -p "Would you like to view the bot logs? (y/n): " show_logs_choice
    if [[ "$show_logs_choice" =~ ^[Yy]$ ]]; then
        show_logs
    fi
}

# Script options
case "${1:-}" in
    "logs")
        show_logs
        ;;
    "status")
        print_status "Bot status:"
        docker-compose ps
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
    "")
        main
        ;;
    *)
        echo "Usage: $0 [logs|status|restart|stop|update]"
        echo ""
        echo "Commands:"
        echo "  logs    - Show bot logs"
        echo "  status  - Show service status"
        echo "  restart - Restart the bot"
        echo "  stop    - Stop all services"
        echo "  update  - Update and rebuild bot"
        echo ""
        echo "Run without arguments for interactive deployment"
        ;;
esac
