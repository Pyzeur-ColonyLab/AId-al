#!/bin/bash

# 🏛️ Code-du-Travail Legal Assistant Deployment Script
# Optimized for Pyzeur/Code-du-Travail-mistral-finetune on Amazon Linux t3.xlarge

set -e

echo "🏛️ Code-du-Travail Legal Assistant Deployment"
echo "=============================================="
echo "Model: Pyzeur/Code-du-Travail-mistral-finetune"
echo "Instance: Amazon Linux t3.xlarge (4 vCPUs, 16GB RAM)"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_legal() { echo -e "${PURPLE}[LEGAL-BOT]${NC} $1"; }

# Check prerequisites
check_requirements() {
    print_status "Checking requirements for legal assistant deployment..."
    
    # Check if on Amazon Linux
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        if [[ "$NAME" == *"Amazon Linux"* ]]; then
            print_success "Running on Amazon Linux ✓"
        else
            print_warning "This script is optimized for Amazon Linux"
        fi
    fi
    
    # Check available memory (should be ~16GB for t3.xlarge)
    total_mem=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $total_mem -ge 14 ]]; then
        print_success "Sufficient memory detected: ${total_mem}GB ✓"
    else
        print_warning "Expected ~16GB RAM for t3.xlarge, detected: ${total_mem}GB"
    fi
    
    # Check available storage
    available_space=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $available_space -ge 20 ]]; then
        print_success "Sufficient storage: ${available_space}GB available ✓"
    else
        print_error "Need at least 20GB available storage, have: ${available_space}GB"
        exit 1
    fi
}

# Install Docker for Amazon Linux
install_docker() {
    print_status "Installing Docker on Amazon Linux..."
    
    sudo yum update -y
    sudo yum install -y docker
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    
    print_success "Docker installed ✓"
}

# Install Docker Compose
install_docker_compose() {
    print_status "Installing Docker Compose..."
    
    if ! command -v pip3 &> /dev/null; then
        sudo yum install -y python3-pip
    fi
    
    sudo pip3 install docker-compose
    print_success "Docker Compose installed ✓"
}

# Setup optimized configuration for legal bot
setup_legal_bot_config() {
    print_legal "Setting up legal assistant configuration..."
    
    # Create optimized docker-compose override
    cat > docker-compose.legal.yml << 'EOF'
version: '3.8'

services:
  bot:
    container_name: legal_assistant_bot
    deploy:
      resources:
        limits:
          memory: 12G      # Use most available RAM for Mistral 7B
          cpus: '3.5'      # Use most vCPUs
        reservations:
          memory: 6G       # Reserve sufficient base memory
          cpus: '2.0'
    environment:
      - MODEL_NAME=Pyzeur/Code-du-Travail-mistral-finetune
      - MAX_LENGTH=1024
      - TEMPERATURE=0.3   # Conservative for legal accuracy
      - TOP_P=0.85
      - USE_QUANTIZATION=false
      - DEVICE=cpu
      - LOG_LEVEL=INFO
    volumes:
      - ./legal_docs:/app/legal_docs:ro  # Mount legal documents
      - ./legal_templates:/app/templates:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 2m
      timeout: 10s
      retries: 3
      start_period: 5m

  postgres:
    container_name: legal_assistant_db
    environment:
      POSTGRES_DB: legal_aibot_db
    volumes:
      - legal_postgres_data:/var/lib/postgresql/data
      - ./sql/init_legal.sql:/docker-entrypoint-initdb.d/init.sql:ro

volumes:
  legal_postgres_data:
EOF

    print_success "Legal bot configuration created ✓"
}

# Setup legal-specific directories and files
setup_legal_environment() {
    print_legal "Setting up legal assistant environment..."
    
    # Create directories for legal documents
    mkdir -p legal_docs legal_templates sql logs
    
    # Create legal database initialization script
    cat > sql/init_legal.sql << 'EOF'
-- Legal Assistant Database Schema
CREATE TABLE IF NOT EXISTS legal_queries (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    query TEXT NOT NULL,
    response TEXT,
    article_references TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER
);

CREATE TABLE IF NOT EXISTS legal_articles (
    id SERIAL PRIMARY KEY,
    article_code VARCHAR(20) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    last_updated DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS user_sessions (
    user_id BIGINT PRIMARY KEY,
    current_case_context TEXT,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    query_count INTEGER DEFAULT 0
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_legal_queries_user_id ON legal_queries(user_id);
CREATE INDEX IF NOT EXISTS idx_legal_queries_created_at ON legal_queries(created_at);
CREATE INDEX IF NOT EXISTS idx_legal_articles_code ON legal_articles(article_code);
CREATE INDEX IF NOT EXISTS idx_legal_articles_category ON legal_articles(category);

-- Insert some common Code du Travail articles (examples)
INSERT INTO legal_articles (article_code, title, content, category) VALUES
('L1111-1', 'Principe général', 'Le code du travail régit les relations de travail...', 'Généralités'),
('L3121-1', 'Durée légale du travail', 'La durée légale du travail effectif est fixée à trente-cinq heures par semaine...', 'Temps de travail'),
('L1234-1', 'Rupture du contrat', 'La rupture du contrat de travail peut résulter...', 'Contrat de travail')
ON CONFLICT (article_code) DO NOTHING;
EOF

    # Create legal document templates directory structure
    mkdir -p legal_templates/{contracts,letters,forms}
    
    # Create a sample legal template
    cat > legal_templates/contracts/cdi_template.txt << 'EOF'
CONTRAT DE TRAVAIL À DURÉE INDÉTERMINÉE

Entre :
- L'employeur : [NOM_EMPLOYEUR]
- Le salarié : [NOM_SALARIE]

Article 1 - Fonctions
Le salarié est engagé en qualité de [POSTE] et exercera ses fonctions selon les dispositions du Code du Travail.

Article 2 - Durée du travail
La durée hebdomadaire de travail est fixée à 35 heures, conformément à l'article L3121-1 du Code du Travail.

Article 3 - Rémunération
La rémunération mensuelle brute est fixée à [SALAIRE] euros.

[Références légales automatiques basées sur le modèle]
EOF

    # Set proper permissions
    chmod -R 755 legal_docs legal_templates
    
    print_success "Legal environment setup complete ✓"
}

# Configure legal assistant prompts and settings
configure_legal_assistant() {
    print_legal "Configuring legal assistant parameters..."
    
    echo ""
    echo "🏛️ Configuration de l'Assistant Juridique"
    echo "=========================================="
    echo ""
    
    # Telegram Bot Token
    while [[ -z "$telegram_token" ]]; do
        read -p "🤖 Token du Bot Telegram: " telegram_token
        if [[ -z "$telegram_token" ]]; then
            print_error "Le token Telegram est requis"
        fi
    done
    
    # HuggingFace Token (required for your private model)
    while [[ -z "$hf_token" ]]; do
        echo ""
        print_warning "Votre modèle nécessite un token HuggingFace"
        read -p "🤗 Token HuggingFace (requis pour votre modèle): " hf_token
        if [[ -z "$hf_token" ]]; then
            print_error "Le token HuggingFace est requis pour accéder à votre modèle"
        fi
    done
    
    # Admin users for legal bot management
    echo ""
    echo "👑 Utilisateurs administrateurs (IDs Telegram):"
    echo "   - Peuvent changer de modèle"
    echo "   - Accèdent aux statistiques"
    echo "   - Gèrent la base de connaissances juridiques"
    read -p "   IDs admin (séparés par des virgules): " admin_users
    
    # Legal specialization settings
    echo ""
    echo "⚖️ Configuration spécialisée pour le droit du travail:"
    echo "1) Mode strict (citations d'articles obligatoires)"
    echo "2) Mode équilibré (citations recommandées)"
    echo "3) Mode informatif (réponses plus accessibles)"
    read -p "Choisir le mode (1-3): " legal_mode
    
    case $legal_mode in
        1) 
            temperature="0.2"
            citation_mode="strict"
            ;;
        2) 
            temperature="0.3"
            citation_mode="balanced"
            ;;
        3) 
            temperature="0.4"
            citation_mode="informative"
            ;;
        *) 
            temperature="0.3"
            citation_mode="balanced"
            ;;
    esac
    
    # Database password
    echo ""
    read -s -p "🔐 Mot de passe base de données (ou Entrée pour défaut): " db_password
    if [[ -z "$db_password" ]]; then
        db_password="SecureLegalBot2024!"
    fi
    echo ""
    
    # Update .env file with legal assistant configuration
    print_legal "Mise à jour de la configuration..."
    
    cp .env.example .env
    sed -i "s/TELEGRAM_BOT_TOKEN=.*/TELEGRAM_BOT_TOKEN=$telegram_token/" .env
    sed -i "s|MODEL_NAME=.*|MODEL_NAME=Pyzeur/Code-du-Travail-mistral-finetune|" .env
    sed -i "s/HF_TOKEN=.*/HF_TOKEN=$hf_token/" .env
    sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$db_password/" .env
    sed -i "s/TEMPERATURE=.*/TEMPERATURE=$temperature/" .env
    
    if [[ -n "$admin_users" ]]; then
        sed -i "s/ADMIN_USERS=.*/ADMIN_USERS=$admin_users/" .env
    fi
    
    # Add legal-specific configurations
    cat >> .env << EOF

# Legal Assistant Specific Configuration
LEGAL_MODE=$citation_mode
DEFAULT_SYSTEM_PROMPT=Tu es un assistant juridique spécialisé dans le Code du Travail français. Réponds de manière précise et cite les articles pertinents.
ENABLE_ARTICLE_LOOKUP=true
ENABLE_CASE_HISTORY=true
LEGAL_DISCLAIMER=⚖️ Cette réponse est fournie à titre informatif. Consultez un avocat pour des conseils juridiques personnalisés.
MAX_CONTEXT_LENGTH=4096
LOG_LEGAL_QUERIES=true
EOF

    print_success "Configuration de l'assistant juridique terminée ✓"
}

# Deploy the legal assistant
deploy_legal_assistant() {
    print_legal "Déploiement de l'assistant juridique Code du Travail..."
    
    # Create monitoring script for legal bot
    cat > monitor_legal_bot.sh << 'EOF'
#!/bin/bash
echo "🏛️ Legal Assistant Bot Monitoring"
echo "================================"
echo ""
echo "📊 System Resources:"
free -h
echo ""
echo "💾 Disk Usage:"
df -h /
echo ""
echo "🤖 Bot Status:"
docker-compose -f docker-compose.yml -f docker-compose.legal.yml ps
echo ""
echo "📈 Container Resources:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo ""
echo "📋 Recent Legal Queries (last 5):"
docker-compose exec postgres psql -U botuser -d legal_aibot_db -c "SELECT user_id, LEFT(query, 50) as query_preview, article_references, created_at FROM legal_queries ORDER BY created_at DESC LIMIT 5;" 2>/dev/null || echo "Database not accessible"
echo ""
echo "⚖️ Model Status:"
docker-compose logs --tail=3 bot | grep -E "(Model loaded|Error|Legal)" || echo "No recent model logs"
EOF

    chmod +x monitor_legal_bot.sh
    
    # Pull base images
    docker-compose pull postgres redis
    
    # Build and deploy with legal configuration
    docker-compose -f docker-compose.yml -f docker-compose.legal.yml up -d --build
    
    print_success "Assistant juridique déployé avec succès! ✓"
    
    echo ""
    echo "🎉 Déploiement Terminé!"
    echo "======================="
    echo ""
    echo "🏛️ Votre Assistant Juridique Code du Travail est actif avec:"
    echo "📱 Modèle: Pyzeur/Code-du-Travail-mistral-finetune"
    echo "🖥️  Instance: Amazon Linux t3.xlarge"
    echo "💾 Mémoire: 12GB alloués au modèle"
    echo "⚖️  Spécialisation: Droit du travail français"
    echo "🗄️  Base de données: PostgreSQL avec schéma juridique"
    echo ""
    echo "🔧 Commandes utiles:"
    echo "  📊 Statut complet:     ./monitor_legal_bot.sh"
    echo "  📋 Logs du bot:        docker-compose logs -f bot"
    echo "  🔄 Redémarrer:         docker-compose restart bot"
    echo "  🛑 Arrêter:            docker-compose down"
    echo "  📈 Métriques:          docker stats"
    echo ""
    echo "🤖 Commandes du bot Telegram:"
    echo "  /start - Commencer"
    echo "  /chat <question> - Poser une question juridique"
    echo "  /article <code> - Rechercher un article du Code du Travail"
    echo "  /info - Informations sur le modèle"
    echo "  /help - Aide complète"
    echo ""
    echo "⚖️ Disclaimer: Cet assistant fournit des informations juridiques générales."
    echo "   Pour des conseils spécifiques, consultez un avocat qualifié."
    echo ""
}

# Health check for legal assistant
health_check_legal() {
    print_legal "Vérification de l'état de l'assistant juridique..."
    
    sleep 30  # Wait for full startup
    
    # Check containers
    if docker-compose -f docker-compose.yml -f docker-compose.legal.yml ps | grep -q "Up"; then
        print_success "Conteneurs en cours d'exécution ✓"
    else
        print_error "Certains conteneurs ont échoué"
        return 1
    fi
    
    # Check model loading
    if docker-compose logs bot 2>&1 | grep -q "Model.*loaded\|Ready"; then
        print_success "Modèle juridique chargé ✓"
    else
        print_warning "Modèle en cours de chargement..."
    fi
    
    # Check database
    if docker-compose exec -T postgres pg_isready -U botuser -d legal_aibot_db > /dev/null 2>&1; then
        print_success "Base de données juridique active ✓"
    else
        print_warning "Base de données en cours d'initialisation..."
    fi
    
    print_success "Assistant juridique opérationnel!"
}

# Main deployment
main() {
    echo ""
    print_status "Démarrage du déploiement de l'assistant juridique..."
    echo ""
    
    check_requirements
    
    # Install Docker if needed
    if ! command -v docker &> /dev/null; then
        install_docker
        print_warning "Veuillez vous déconnecter et vous reconnecter, puis relancer ce script"
        exit 0
    fi
    
    # Install Docker Compose if needed
    if ! command -v docker-compose &> /dev/null; then
        install_docker_compose
    fi
    
    setup_legal_bot_config
    setup_legal_environment
    configure_legal_assistant
    deploy_legal_assistant
    health_check_legal
    
    echo ""
    read -p "Voulez-vous voir les logs du bot? (y/n): " show_logs
    if [[ "$show_logs" =~ ^[Yy]$ ]]; then
        print_legal "Affichage des logs (Ctrl+C pour quitter)..."
        docker-compose logs -f bot
    fi
}

# Script commands
case "${1:-}" in
    "logs")
        docker-compose logs -f bot
        ;;
    "status")
        ./monitor_legal_bot.sh
        ;;
    "restart")
        print_legal "Redémarrage de l'assistant juridique..."
        docker-compose -f docker-compose.yml -f docker-compose.legal.yml restart bot
        print_success "Assistant redémarré ✓"
        ;;
    "stop")
        print_legal "Arrêt de l'assistant juridique..."
        docker-compose -f docker-compose.yml -f docker-compose.legal.yml down
        print_success "Assistant arrêté ✓"
        ;;
    "update")
        print_legal "Mise à jour de l'assistant..."
        git pull
        docker-compose -f docker-compose.yml -f docker-compose.legal.yml up -d --build
        print_success "Assistant mis à jour ✓"
        ;;
    "monitor")
        ./monitor_legal_bot.sh
        ;;
    "")
        main
        ;;
    *)
        echo "Usage: $0 [logs|status|restart|stop|update|monitor]"
        echo ""
        echo "🏛️ Assistant Juridique Code du Travail"
        echo "====================================="
        echo ""
        echo "Commandes:"
        echo "  logs    - Afficher les logs"
        echo "  status  - Statut et monitoring"
        echo "  restart - Redémarrer l'assistant"
        echo "  stop    - Arrêter l'assistant"
        echo "  update  - Mettre à jour"
        echo "  monitor - Monitoring en temps réel"
        echo ""
        echo "Exécuter sans argument pour un déploiement interactif"
        ;;
esac
