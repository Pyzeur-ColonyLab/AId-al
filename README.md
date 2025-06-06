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

### 🏛️ **Legal Assistant Specialization**
- **Optimized for Code-du-Travail** - Specialized for French labor law
- **Article citation support** - Automatic legal article references
- **Legal document templates** - Pre-built contract and letter templates
- **Case history tracking** - Context-aware legal conversations

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

### 3. Deploy Options

#### **🐧 Standard Deployment (Ubuntu/Debian)**
```bash
# Install Docker and Docker Compose
sudo apt update
sudo apt install docker.io docker-compose

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f bot
```

#### **🔥 Amazon Linux Deployment (EC2 Optimized)**
```bash
# Use the optimized Amazon Linux deployment script
chmod +x deploy_amazon_linux.sh
./deploy_amazon_linux.sh
```

#### **⚖️ Legal Assistant Deployment (Specialized)**
```bash
# For Code-du-Travail legal assistant with specialized features
chmod +x deploy_legal_assistant.sh
./deploy_legal_assistant.sh
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

### **Legal & Specialized Models**
```bash
MODEL_NAME=Pyzeur/Code-du-Travail-mistral-finetune  # French labor law
MODEL_NAME=your_username/your-fine-tuned-model     # Your custom models
HF_TOKEN=your_hf_token  # If private
```

## 🤖 Bot Commands

### **AI Interaction**
- `/chat <message>` - Chat with the AI model
- `/ask <question>` - Ask specific questions
- `/info` - Get current model information
- `/models` - List popular models by category

### **Legal Assistant Commands (when using legal deployment)**
- `/article <code>` - Look up specific Code du Travail articles
- `/template <type>` - Get legal document templates
- `/search <term>` - Search legal knowledge base
- `/history` - View conversation context

### **Model Management (Admin)**
- `/switch <model_name>` - Switch to different model on-the-fly
- `/stats` - View usage statistics (legal deployment)
- `/export` - Export legal query data (legal deployment)

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

### **Legal Assistant Settings** (using `.env.legal.example`)
```bash
LEGAL_MODE=balanced              # strict, balanced, informative
ENABLE_ARTICLE_LOOKUP=true       # Enable article lookup
ENABLE_CASE_HISTORY=true         # Remember conversation context
LEGAL_DISCLAIMER=true            # Add legal disclaimers
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

#### **For General Models**
- **t3.medium** (minimum) - for small models like DialoGPT-medium
- **t3.large** - for models like GPT-2 medium
- **t3.xlarge** - for Mistral 7B models (recommended for legal assistant)
- **g4dn.xlarge** - for large models with GPU acceleration

#### **For Legal Assistant (Code-du-Travail)**
- **t3.xlarge** (recommended) - 4 vCPUs, 16GB RAM
- **Storage**: 30GB+ GP3 volume
- **OS**: Amazon Linux 2023 (optimized)

### **Amazon Linux Deployment (t3.xlarge)**

1. **Launch EC2 Instance**
```bash
# Connect to your instance
ssh -i your-key.pem ec2-user@your-ec2-ip

# Clone repository
git clone https://github.com/Pyzeur-ColonyLab/AId-al.git
cd AId-al
```

2. **Deploy with Optimized Script**
```bash
# For general models on Amazon Linux
chmod +x deploy_amazon_linux.sh
./deploy_amazon_linux.sh

# OR for specialized legal assistant
chmod +x deploy_legal_assistant.sh
./deploy_legal_assistant.sh
```

The scripts will automatically:
- Install Docker and Docker Compose for Amazon Linux
- Optimize memory allocation for t3.xlarge
- Configure legal-specific database schema (legal deployment)
- Set up monitoring and health checks

### **Ubuntu/Debian Deployment**

1. **Install Docker**
```bash
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker ubuntu
sudo systemctl enable docker
sudo systemctl start docker
```

2. **Clone and Configure**
```bash
git clone https://github.com/Pyzeur-ColonyLab/AId-al.git
cd AId-al
cp .env.example .env
nano .env  # Edit with your configuration
```

3. **Deploy**
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

### **1. Legal Assistant (Code-du-Travail)**
```bash
MODEL_NAME=Pyzeur/Code-du-Travail-mistral-finetune
TEMPERATURE=0.3  # More focused responses
```
**Usage**: 
- `/ask Quelle est la durée légale du travail en France?`
- `/article L3121-1` - Look up specific article
- `/template contrat` - Get contract template

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

# Legal assistant monitoring (if deployed)
./monitor_legal_bot.sh
```

### **Management Commands**
```bash
# Amazon Linux deployment
./deploy_amazon_linux.sh status    # Check status
./deploy_amazon_linux.sh logs      # View logs
./deploy_amazon_linux.sh restart   # Restart bot
./deploy_amazon_linux.sh monitor   # Monitor resources

# Legal assistant deployment
./deploy_legal_assistant.sh status  # Check status with legal metrics
./deploy_legal_assistant.sh monitor # Legal-specific monitoring
```

### **Common Issues**

**Model Loading Fails**
```bash
# Check if model exists on HuggingFace
# Verify HF_TOKEN for private models
# Ensure sufficient memory/disk space
```

**Out of Memory (especially for Mistral 7B)**
```bash
# Enable quantization (if needed)
USE_QUANTIZATION=true

# Reduce max length
MAX_LENGTH=512

# For legal assistant on t3.xlarge, memory should be sufficient
# Check with: free -h
```

**Bot Not Responding**
```bash
# Check Telegram token
echo $TELEGRAM_BOT_TOKEN

# Verify network connectivity
curl -s https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe
```

## 📊 Legal Assistant Features

### **Database Schema**
The legal assistant deployment includes specialized tables:
- `legal_queries` - Track all legal questions and responses
- `legal_articles` - Code du Travail articles database
- `user_sessions` - Conversation context and case history

### **Legal Document Templates**
Pre-built templates for:
- CDI (Contrat à Durée Indéterminée)
- CDD (Contrat à Durée Déterminée)
- Resignation letters
- Legal notices

### **Article Lookup System**
- Search by article code (e.g., L3121-1)
- Category-based browsing
- Cross-reference suggestions

## 🚀 Performance Optimizations

### **For t3.xlarge Instances**
- **Memory allocation**: 12GB for Mistral 7B models
- **CPU optimization**: Uses 3.5 of 4 vCPUs
- **Caching**: Optimized Redis configuration
- **Model loading**: Efficient HuggingFace cache management

### **Legal Assistant Optimizations**
- **Conservative temperature** (0.3) for legal accuracy
- **Extended context** (4096 tokens) for legal documents
- **Specialized prompts** for Code du Travail expertise
- **Citation mode** for article references

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
- Special thanks for the Code-du-Travail model fine-tuning

---

**Made with ❤️ for the AI community**

*Deploy any HuggingFace model as a Telegram bot in minutes!*

### 🏛️ Legal Disclaimer

The legal assistant functionality provides general information about French labor law (Code du Travail) and should not be considered as professional legal advice. For specific legal matters, please consult with a qualified attorney.
