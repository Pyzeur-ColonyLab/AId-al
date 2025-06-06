# 🤖 AId-al - Universal AI Telegram Bot

A flexible Telegram bot that can work with **any HuggingFace model** - from chat models to classification, Q&A, and text generation. Simply change the model name in configuration and deploy!

## ✨ Features

### 🔄 **Universal Model Support**
- **Plug any HuggingFace model** - GPT, BERT, T5, Mistral, Llama, your custom models
- **Automatic task detection** - text generation, classification, Q&A, chat
- **Smart prompt formatting** - automatically formats prompts for different model types
- **GPU/CPU optimization** - supports quantization and efficient memory usage

### 🎯 **Easy Model Switching**
- Change models via environment variables
- Switch models on-the-fly with admin commands
- Support for private models with HuggingFace tokens
- Model recommendations by use case

### 🚀 **Production Ready**
- Docker containerization
- PostgreSQL database integration
- Redis caching support
- Comprehensive logging and monitoring

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/Pyzeur-ColonyLab/AId-al.git
cd AId-al
cp .env.example .env
```

### 2. Configure Your Model
Edit `.env` file:
```bash
# Use ANY HuggingFace model!
MODEL_NAME=Pyzeur/Code-du-Travail-mistral-finetune  # Your model
# MODEL_NAME=microsoft/DialoGPT-medium               # Chat model
# MODEL_NAME=gpt2                                    # Generation model
# MODEL_NAME=distilbert-base-cased-distilled-squad   # Q&A model

TELEGRAM_BOT_TOKEN=your_bot_token_here
HF_TOKEN=your_huggingface_token  # For private models
```

### 3. Deploy on AWS (or any server)
```bash
# Install Docker and Docker Compose
sudo apt update
sudo apt install docker.io docker-compose

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f bot
```

## 🎯 Supported Model Types

### **Chat & Generation Models**
```bash
MODEL_NAME=microsoft/DialoGPT-medium      # General chat
MODEL_NAME=gpt2-medium                    # Text generation  
MODEL_NAME=mistralai/Mistral-7B-Instruct # Instruction following
MODEL_NAME=microsoft/phi-2                # Small but powerful
MODEL_NAME=google/gemma-2b-it            # Google's model
```

### **Classification Models**
```bash
MODEL_NAME=cardiffnlp/twitter-roberta-base-sentiment-latest  # Sentiment
MODEL_NAME=distilbert-base-uncased-finetuned-sst-2-english  # Binary sentiment
```

### **Question Answering**
```bash
MODEL_NAME=distilbert-base-cased-distilled-squad  # SQuAD QA
MODEL_NAME=deepset/roberta-base-squad2             # SQuAD 2.0
```

### **Your Custom Models**
```bash
MODEL_NAME=your_username/your-fine-tuned-model
HF_TOKEN=your_hf_token  # If private
```

## 🤖 Bot Commands

### **AI Interaction**
- `/chat <message>` - Chat with the AI model
- `/ask <question>` - Ask specific questions
- `/info` - Get current model information
- `/models` - List popular models by category

### **Model Management (Admin)**
- `/switch <model_name>` - Switch to different model on-the-fly

### **Resource Management**
- `/url <n>` - Get saved URL resource
- `/contract <n>` - Get smart contract address
- `/add_url <n> <url>` - Add URL resource
- `/add_contract <n> <address>` - Add smart contract

## 🔧 Configuration Options

### **Model Settings**
```bash
MODEL_NAME=your_model_name        # Any HuggingFace model
MODEL_TYPE=universal              # universal, transformer, auto
MAX_LENGTH=512                    # Max response length
USE_QUANTIZATION=false           # Enable for large models on limited GPU
DEVICE=auto                      # auto, cpu, cuda
```

### **Generation Parameters**
```bash
TEMPERATURE=0.7                  # Creativity (0.0-1.0)
TOP_P=0.9                       # Nucleus sampling
TOP_K=50                        # Top-k sampling
REPETITION_PENALTY=1.1          # Avoid repetition
DO_SAMPLE=true                  # Enable sampling
```

### **Security**
```bash
ALLOWED_USERS=123456789,987654321  # Comma-separated user IDs
ADMIN_USERS=123456789              # Admin user IDs for model switching
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram Bot  │◄──►│  Universal Model │◄──►│  HuggingFace    │
│                 │    │     Handler      │    │     Models      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │      Redis       │    │   File Storage  │
│   (Resources)   │    │    (Caching)     │    │   (Models)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📦 AWS Deployment Guide

### **EC2 Instance Requirements**
- **t3.medium** (minimum) - for small models like DialoGPT-medium
- **t3.large** - for models like GPT-2 medium
- **g4dn.xlarge** - for large models with GPU acceleration
- **Storage**: 20GB+ EBS volume

### **Step-by-Step AWS Deployment**

1. **Launch EC2 Instance**
```bash
# Connect to your instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y
```

2. **Install Docker**
```bash
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker ubuntu
sudo systemctl enable docker
sudo systemctl start docker
```

3. **Clone and Configure**
```bash
git clone https://github.com/Pyzeur-ColonyLab/AId-al.git
cd AId-al
cp .env.example .env
nano .env  # Edit with your configuration
```

4. **Deploy**
```bash
# Build and start
docker-compose up -d

# Monitor logs
docker-compose logs -f bot

# Check status
docker-compose ps
```

### **GPU Support (Optional)**
For large models, use GPU-enabled instance:
```bash
# Install NVIDIA Docker support
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Update docker-compose.yml to use GPU
# Add under bot service:
# deploy:
#   resources:
#     reservations:
#       devices:
#         - driver: nvidia
#           count: 1
#           capabilities: [gpu]
```

## 🔄 Switching Models

### **Via Environment (Restart Required)**
```bash
# Edit .env file
MODEL_NAME=new_model_name

# Restart container
docker-compose restart bot
```

### **Via Bot Command (Real-time)**
```bash
# In Telegram (admin only)
/switch microsoft/DialoGPT-large
/switch gpt2-medium
/switch your_username/your-custom-model
```

## 💡 Example Use Cases

### **1. Legal Assistant (Your Model)**
```bash
MODEL_NAME=Pyzeur/Code-du-Travail-mistral-finetune
TEMPERATURE=0.3  # More focused responses
```
**Usage**: `/ask Quelle est la durée légale du travail en France?`

### **2. General Chat Bot**
```bash
MODEL_NAME=microsoft/DialoGPT-medium
TEMPERATURE=0.7  # Balanced creativity
```
**Usage**: `/chat How are you today?`

### **3. Sentiment Analysis**
```bash
MODEL_NAME=cardiffnlp/twitter-roberta-base-sentiment-latest
```
**Usage**: `/chat I love this product!` → Returns sentiment classification

### **4. Question Answering**
```bash
MODEL_NAME=distilbert-base-cased-distilled-squad
```
**Usage**: `/ask What is machine learning?` → Extracts answer from context

## 🔍 Monitoring & Troubleshooting

### **Check Bot Status**
```bash
# View logs
docker-compose logs -f bot

# Check container status
docker-compose ps

# Resource usage
docker stats
```

### **Common Issues**

**Model Loading Fails**
```bash
# Check if model exists on HuggingFace
# Verify HF_TOKEN for private models
# Ensure sufficient memory/disk space
```

**Out of Memory**
```bash
# Enable quantization
USE_QUANTIZATION=true

# Reduce max length
MAX_LENGTH=256

# Use smaller model
MODEL_NAME=gpt2  # Instead of gpt2-large
```

**Bot Not Responding**
```bash
# Check Telegram token
echo $TELEGRAM_BOT_TOKEN

# Verify network connectivity
curl -s https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📝 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [HuggingFace](https://huggingface.co/) for the amazing transformers library
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for Telegram integration
- Community contributors and model creators

---

**Made with ❤️ for the AI community**

*Deploy any HuggingFace model as a Telegram bot in minutes!*
