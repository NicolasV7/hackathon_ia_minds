#!/bin/bash
# Quick verification script for Dokploy deployment
# Run this after deployment to verify everything is working

echo "🔍 Verifying UPTC EcoEnergy Deployment..."
echo "=========================================="

# Check if services are running
echo ""
echo "📦 Checking Docker Services..."
docker-compose -f docker-compose.dokploy.yml ps

# Check database
echo ""
echo "🗄️  Checking Database..."
docker-compose -f docker-compose.dokploy.yml exec -T database pg_isready -U uptc_user -d uptc_energy
if [ $? -eq 0 ]; then
    echo "✅ Database is ready"
else
    echo "❌ Database is not ready"
fi

# Check backend health
echo ""
echo "⚡ Checking Backend Health..."
curl -f http://localhost:8000/health 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not responding"
fi

# Check frontend
echo ""
echo "🌐 Checking Frontend..."
curl -f http://localhost:3000 2>/dev/null >/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Frontend is responding"
else
    echo "❌ Frontend is not responding"
fi

# Check data count
echo ""
echo "📊 Checking Data..."
docker-compose -f docker-compose.dokploy.yml exec -T database psql -U uptc_user -d uptc_energy -c "SELECT COUNT(*) as total_records FROM consumption_records;" 2>/dev/null

echo ""
echo "=========================================="
echo "✅ Verification Complete!"
echo ""
echo "📱 Access Points:"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo "   API:      http://localhost:8000/api/v1"
echo "=========================================="
