#!/bin/bash
set -e

echo "🚀 Setting up Design & Bug Tracker..."

# Backend setup
echo "📦 Installing backend dependencies..."
cd backend
pip install -q -r requirements.txt
cp .env.example .env 2>/dev/null || true
cd ..

# Frontend setup
echo "📦 Installing frontend dependencies..."
cd frontend
npm install -q
cd ..

echo "✅ Setup complete!"
echo ""
echo "To run the app:"
echo "  Terminal 1: cd backend && python main.py"
echo "  Terminal 2: cd frontend && npm run dev"
echo ""
echo "Then open: http://localhost:5173"
