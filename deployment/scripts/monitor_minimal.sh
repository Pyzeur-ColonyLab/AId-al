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
