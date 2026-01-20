#!/bin/bash

# Activer l'environnement virtuel
source venv/bin/activate

# Lancer la CLI
python cli/pirate-cli.py "$@"
