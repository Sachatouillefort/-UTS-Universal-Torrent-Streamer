# Pirate CLI

Une CLI Python pour rechercher et gérer des torrents avec des fonctionnalités avancées.

## ⚠️ Avertissement Légal

**Cet outil est fourni à des fins éducatives et pour accéder à du contenu libre de droits uniquement.**

- L'auteur ne cautionne ni n'encourage le piratage de contenu protégé par des droits d'auteur
- Cet outil peut être utilisé pour accéder à des contenus légaux distribués via BitTorrent (distributions Linux, films du domaine public, musique sous licence Creative Commons, etc.)
- L'utilisateur est seul responsable de l'usage qu'il fait de cet outil
- Le téléchargement de contenu protégé par des droits d'auteur sans autorisation est illégal dans la plupart des pays

**EN UTILISANT CET OUTIL, VOUS ACCEPTEZ CES CONDITIONS.**

## Fonctionnalités

- 🔍 Recherche de torrents sur The Pirate Bay
- 📊 Métadonnées IMDb intégrées
- 📝 Téléchargement automatique de sous-titres
- 📚 Historique des téléchargements
- ⚙️ Configuration OpenSubtitles
- 🎨 Interface CLI interactive avec Rich
- 🎬 Streaming avec MPV, Chromecast, AirPlay ou DLNA

## Prérequis

- **Python 3.8+**
- **Node.js et npm** (pour webtorrent-cli)
- **MPV** (lecteur vidéo - optionnel mais recommandé)

### Installation de MPV

**macOS:**
```bash
brew install mpv
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install mpv
```

**Windows:**
Téléchargez depuis [mpv.io](https://mpv.io/installation/)

## Installation rapide

```bash
# Cloner le repo
git clone <votre-repo-url>
cd pirate-cli-standalone

# Lancer l'installation automatique
./install.sh
```

## Installation manuelle

```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances Python
pip install -r requirements.txt

# Installer webtorrent-cli
npm install -g webtorrent-cli
```

## Utilisation

### Lancement rapide
```bash
./run.sh
```

### Lancement manuel
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer la CLI
python cli/pirate-cli.py
```

### Modes disponibles

**Mode Guidé (Séries):**
- Format SxxExx automatique
- Gestion des alias (jjk → jujutsu kaisen)
- Historique avec reprise automatique
- Métadonnées IMDb

**Mode Libre (Films, Anime, etc.):**
- Recherche personnalisée
- Téléchargement de sous-titres

### Exemples

```bash
# Interface interactive
./run.sh

# Recherche directe
python cli/pirate-cli.py "breaking bad s01e01"
```

## Configuration

### OpenSubtitles

Pour télécharger les sous-titres, configurez votre compte OpenSubtitles :
1. Lancez la CLI
2. Sélectionnez "Configuration (OpenSubtitles)"
3. Entrez vos identifiants

### Fichiers de données

- `data/config.json` - Configuration (compte OpenSubtitles)
- `data/history.json` - Historique de visionnage
- `data/cache.json` - Cache des métadonnées

## Résolution de problèmes

### "webtorrent-cli n'est pas trouvé"
```bash
npm install -g webtorrent-cli
```

### "mpv n'est pas trouvé"
Installez MPV (voir section Prérequis)

### Les sous-titres ne se chargent pas
1. Vérifiez votre configuration OpenSubtitles
2. Assurez-vous que l'épisode/saison sont corrects

### Problèmes de Casting (Chromecast/AirPlay)
- Les fichiers MKV, HEVC/x265, DTS peuvent ne pas fonctionner
- Préférez des fichiers MP4 avec codec H.264

## Dépendances

- `requests` - Requêtes HTTP
- `beautifulsoup4` - Parsing HTML
- `rich` - Interface CLI améliorée
- `questionary` - Prompts interactifs
- `subliminal` - Téléchargement de sous-titres
- `cinemagoer` - Métadonnées IMDb
- `webtorrent-cli` - Streaming torrent

Voir `requirements.txt` pour la liste complète.

## ⚖️ Clause de Non-Responsabilité

Ce logiciel est fourni "tel quel", sans garantie d'aucune sorte. L'auteur décline toute responsabilité quant à l'utilisation qui en est faite. Les utilisateurs sont responsables de respecter les lois applicables dans leur juridiction concernant les droits d'auteur et la propriété intellectuelle.

## Usages Légaux Suggérés

- Téléchargement de distributions Linux (Ubuntu, Fedora, Arch Linux, etc.)
- Accès à des films du domaine public
- Téléchargement de musique sous licence Creative Commons
- Contenu éducatif libre de droits
- Tout contenu dont vous possédez les droits ou qui est distribué légalement via BitTorrent

## Licence

ISC - Le code source est sous licence ISC. Cela ne vous donne pas le droit d'utiliser cet outil pour des activités illégales.
