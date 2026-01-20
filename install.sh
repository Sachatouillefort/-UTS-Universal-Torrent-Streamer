#!/bin/bash

echo "🏴‍☠️ Installation de Pirate CLI"
echo ""

# Vérifier si Python 3 est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

echo "✅ Python 3 détecté"

# Vérifier si npm est installé
if ! command -v npm &> /dev/null; then
    echo "❌ npm n'est pas installé. Veuillez installer Node.js et npm d'abord."
    echo "   Téléchargez depuis: https://nodejs.org/"
    exit 1
fi

echo "✅ npm détecté"

# Créer un environnement virtuel
echo ""
echo "📦 Création de l'environnement virtuel Python..."
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances Python
echo ""
echo "📦 Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Installer webtorrent-cli localement
echo ""
echo "📦 Installation de webtorrent-cli..."
npm install

echo ""
echo "✅ Installation terminée !"
echo ""
echo "Pour utiliser Pirate CLI :"
echo "  1. Activez l'environnement virtuel : source venv/bin/activate"
echo "  2. Lancez la CLI : python cli/pirate-cli.py"
echo ""
echo "Ou utilisez le script de lancement : ./run.sh"
