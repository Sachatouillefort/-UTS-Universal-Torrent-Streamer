import requests
from bs4 import BeautifulSoup
import sys
import subprocess
import os
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import questionary
import time

import json

console = Console()

import requests
from bs4 import BeautifulSoup
import sys
import subprocess
import os
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel
from rich.text import Text
import questionary
import time
import json

# Add core to sys.path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../core')))

# Import core logic
from pirate_core import (
    load_config, save_config, load_history, save_history,
    get_cache_size, clean_cache, search_tpb, download_subtitles,
    fetch_metadata, correct_query, ALIASES
)

console = Console()

def configure():
    console.print("\n[bold cyan]Configuration[/bold cyan]")
    
    config = load_config()
    
    # Search URL configuration
    current_url = config.get('search_url', '')
    console.print("\n[bold yellow]1. Source de recherche torrent[/bold yellow]")
    console.print("Vous devez configurer l'URL de votre source de recherche torrent.")
    console.print("[dim]Exemples: https://apibay.org (API), ou tout autre site de votre choix[/dim]")
    
    if current_url:
        console.print(f"URL actuelle : [bold green]{current_url}[/bold green]")
        if questionary.confirm("Voulez-vous modifier l'URL de recherche ?", default=False).ask():
            search_url = questionary.text("URL de la source de recherche :", default=current_url).ask()
            if search_url:
                config['search_url'] = search_url.rstrip('/')
                save_config(config)
                console.print("[green]URL de recherche mise à jour ![/green]")
    else:
        console.print("[bold red]⚠️  Aucune source configurée - La recherche ne fonctionnera pas ![/bold red]")
        search_url = questionary.text("URL de la source de recherche :").ask()
        if search_url:
            config['search_url'] = search_url.rstrip('/')
            save_config(config)
            console.print("[green]URL de recherche configurée ![/green]")
        else:
            console.print("[yellow]Configuration annulée.[/yellow]")
            return
    
    # OpenSubtitles configuration
    console.print("\n[bold yellow]2. OpenSubtitles (optionnel)[/bold yellow]")
    console.print("Un compte OpenSubtitles.com est nécessaire pour télécharger les sous-titres via l'API.")
    
    current_user = config.get('opensubtitles_user', '')
    
    if current_user:
        console.print(f"Compte actuel : [bold green]{current_user}[/bold green]")
        if not questionary.confirm("Voulez-vous modifier la configuration OpenSubtitles ?", default=False).ask():
            return
    else:
        if not questionary.confirm("Voulez-vous configurer OpenSubtitles ?", default=False).ask():
            return

    username = questionary.text("Nom d'utilisateur OpenSubtitles :", default=current_user).ask()
    password = questionary.password("Mot de passe OpenSubtitles :").ask()
    
    if username and password:
        config['opensubtitles_user'] = username
        config['opensubtitles_pass'] = password
        save_config(config)
        console.print("[green]Configuration OpenSubtitles sauvegardée ![/green]")
    else:
        console.print("[yellow]Configuration OpenSubtitles annulée.[/yellow]")

def display_metadata(query):
    data = fetch_metadata(query)
    if data:
        text = Text()
        text.append(f"{data['title']} ({data['year']})\n", style="bold cyan")
        if data['rating'] and data['rating'] != 'N/A':
            text.append(f"⭐ {data['rating']}/10 | {', '.join(data['genres'])}\n\n", style="yellow")
        else:
            text.append(f"{', '.join(data['genres'])}\n\n", style="yellow")
        text.append(data['plot'], style="white")
        
        console.print(Panel(text, title="Infos IMDb", border_style="cyan"))
        return True
    else:
        console.print("[dim]Aucune info IMDb trouvée.[/dim]")
        return False

def select_torrent(torrents):
    if not torrents:
        console.print("[red]Aucun torrent trouvé.[/red]")
        return None

    choices = []
    for t in torrents:
        # Format: [Seeders] Title
        label = f"[{t['seeders']} seeds] {t['title']}"
        choices.append(questionary.Choice(label, value=t))
    
    choices.append(questionary.Choice("Annuler", value=None))

    selected = questionary.select(
        "Sélectionne un torrent :",
        choices=choices
    ).ask()
    
    return selected

def stream_torrent(magnet, subtitle_path=None, cast_target=None):
    console.print("\n[*] Lancement du streaming... (Cela peut prendre quelques secondes pour trouver des pairs)", style="green")
    if not cast_target:
        console.print("[*] Appuie sur 'q' dans le lecteur pour quitter.", style="green")
    
    if subtitle_path and not cast_target:
        console.print("[bold yellow][TIP] Sous-titres décalés ? Utilise 'z' et 'x' pour ajuster le délai dans MPV.[/bold yellow]")
    
    console.print("[*] Ctrl+C pour arrêter le téléchargement et revenir au menu.", style="yellow")
    
    webtorrent_cmd = "webtorrent"
    
    from shutil import which
    if which("webtorrent") is None:
        local_bin = os.path.join(os.getcwd(), "node_modules", ".bin", "webtorrent")
        if os.path.exists(local_bin):
            webtorrent_cmd = local_bin
        else:
            console.print("[bold red]Erreur: webtorrent-cli n'est pas trouvé.[/bold red]")
            console.print("Installe-le avec : npm install webtorrent-cli")
            return

    cmd = [webtorrent_cmd, magnet, "--no-quit", "--interactive-select"]
    
    if cast_target == "chromecast":
        cmd.append("--chromecast")
    elif cast_target == "airplay":
        cmd.append("--airplay")
    elif cast_target == "dlna":
        cmd.append("--dlna")
    else:
        cmd.append("--mpv")
    
    if subtitle_path:
        console.print(f"[*] Chargement des sous-titres : {subtitle_path}", style="cyan")
        if cast_target:
            # Pour le cast, on utilise --subtitles (si supporté par webtorrent pour le target)
            cmd.append(f"--subtitles={subtitle_path}")
        else:
            # Pour mpv local
            cmd.append(f"--player-args=--sub-file='{subtitle_path}'")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        console.print("\n[yellow]Arrêt du streaming demandé par l'utilisateur.[/yellow]")
    except FileNotFoundError:
        console.print("[bold red]Erreur: webtorrent-cli n'est pas installé ou n'est pas dans le PATH.[/bold red]")
        console.print("Installe-le avec : npm install -g webtorrent-cli")

if __name__ == "__main__":
    console.print("[bold yellow]🔍 TORRENT SEARCH CLI 🔍[/bold yellow]", justify="center")
    
    # Check if search URL is configured
    from pirate_core import get_search_url
    if not get_search_url():
        console.print("\n[bold red]⚠️  ATTENTION : Aucune source de recherche configurée ![/bold red]")
        console.print("[yellow]Vous devez configurer une source de recherche avant de pouvoir utiliser cet outil.[/yellow]")
        console.print("[dim]Allez dans Configuration pour définir l'URL de votre source de recherche.[/dim]\n")
    
    while True:
        subtitle_file = None # Reset subtitle file
        serie_input = None
        saison = None
        episode = None
        
        if len(sys.argv) < 2:
            # Vérification de la configuration existante
            config = load_config()
            
            # Check search URL status
            search_url_status = "✓ Configurée" if config.get('search_url') else "✗ Non configurée"
            opensubtitles_status = f"✓ {config['opensubtitles_user']}" if config.get('opensubtitles_user') else "✗ Non configuré"
            
            config_label = f"Configuration (Source: {search_url_status} | Sous-titres: {opensubtitles_status})"

            # Vérification de l'historique pour le label
            history = load_history()
            history_label = "Historique"
            if history:
                history_label += f" ({len(history)} items)"

            # Calcul de la taille du cache
            cache_size = get_cache_size()
            cache_size_gb = cache_size / (1024 * 1024 * 1024)
            cache_label = f"Gestion du Cache ({cache_size_gb:.2f} GB)"

            choices = [
                questionary.Choice("Recherche Guidée (Série SxxExx)", "guided"),
                questionary.Choice("Recherche Libre (Film, Anime, etc.)", "manual"),
                questionary.Choice(history_label, "history"),
                questionary.Choice(cache_label, "cache"),
                questionary.Choice(config_label, "config"),
                questionary.Choice("Quitter", "quit")
            ]

            mode = questionary.select(
                "Mode de recherche :",
                choices=choices
            ).ask()
            
            if mode == "quit" or mode is None:
                console.print("[yellow]Bye ![/yellow]")
                sys.exit()
            
            if mode == "config":
                configure()
                continue

            if mode == "cache":
                if questionary.confirm(f"Voulez-vous supprimer tout le contenu du cache ({cache_size_gb:.2f} GB) ?", default=False).ask():
                    success, msg = clean_cache()
                    if success:
                        console.print(f"[green]{msg}[/green]")
                    else:
                        console.print(f"[red]{msg}[/red]")
                continue

            if mode == "history":
                if not history:
                    console.print("[yellow]Historique vide.[/yellow]")
                    continue
                
                history_choices = []
                for h in history:
                    try:
                        next_ep = int(h['episode']) + 1
                        label = f"{h['serie']} S{h['season']}E{next_ep:02d} (Dernier vu: E{h['episode']})"
                        history_choices.append(questionary.Choice(label, value=h))
                    except ValueError:
                        pass
                
                history_choices.append(questionary.Choice("Retour", "back"))
                
                selected_history = questionary.select(
                    "Reprendre une série :",
                    choices=history_choices
                ).ask()
                
                if selected_history == "back" or not selected_history:
                    continue
                
                # On charge les infos et on passe en mode guided
                mode = "guided"
                serie_input = selected_history['serie']
                saison = selected_history['season']
                episode = str(int(selected_history['episode']) + 1)
                console.print(f"[bold cyan]Reprise de {serie_input} S{saison}E{episode}...[/bold cyan]")

            if mode == "guided":
                
                if not 'serie_input' in locals() or not serie_input: # Si pas défini par le resume
                    serie_input = questionary.text("Nom de la série :").ask()
                
                # 1. Vérification des alias AVANT la correction auto
                alias_found = False
                full_name = ALIASES.get(serie_input.lower())
                if full_name:
                    console.print(f"[dim]Alias détecté : '{serie_input}' -> '{full_name}'[/dim]")
                    serie_input = full_name
                    alias_found = True

                # 2. Correction automatique (seulement si pas d'alias trouvé)
                if not alias_found:
                    corrected_serie = correct_query(serie_input)
                    if corrected_serie: # Check if corrected_serie is not None
                        if questionary.confirm(f"Tu as écrit '{serie_input}', voulais-tu dire '{corrected_serie}' ?", default=True).ask():
                            serie_input = corrected_serie

                # Affichage des métadonnées
                console.print("[dim]Recherche des infos...[/dim]")
                display_metadata(serie_input)

                if not 'saison' in locals() or not saison:
                    saison = questionary.text("Saison (Laisser vide pour tout) :").ask()
                
                if not 'episode' in locals() or not episode:
                    episode = questionary.text("Épisode (Laisser vide pour la saison complète) :").ask()
                
                queries = []
                
                # Fonction pour générer les variantes de recherche
                def generate_variations(name, s, e):
                    variations = []
                    
                    if s and s.strip():
                        # --- RECHERCHE AVEC SAISON ---
                        try:
                            s_int = int(s)
                            if e and e.strip():
                                # --- RECHERCHE ÉPISODE SPÉCIFIQUE ---
                                try:
                                    e_int = int(e)
                                    # 1. Standard: S01E01
                                    variations.append(f"{name} S{s_int:02d}E{e_int:02d}")
                                    # 2. Lowercase: s01e01
                                    variations.append(f"{name} s{s_int:02d}e{e_int:02d}")
                                    # 3. Old school: 1x01
                                    variations.append(f"{name} {s_int}x{e_int:02d}")
                                    # 4. Episode only (si Saison 1): Name 01, Name Episode 01
                                    if s_int == 1:
                                        variations.append(f"{name} {e_int:02d}")
                                        variations.append(f"{name} Episode {e_int:02d}")
                                        variations.append(f"{name} E{e_int:02d}")
                                except ValueError:
                                    pass
                            else:
                                # --- RECHERCHE SAISON COMPLÈTE (BATCH) ---
                                # 1. Standard: S01
                                variations.append(f"{name} S{s_int:02d}")
                                # 2. Season X
                                variations.append(f"{name} Season {s_int}")
                                # 3. Complete
                                variations.append(f"{name} Complete")
                                # 4. Batch
                                variations.append(f"{name} Batch")
                                # 5. Juste le nom (pour trouver les packs mal nommés)
                                variations.append(name)
                        except ValueError:
                            pass
                    else:
                        # --- RECHERCHE SÉRIE COMPLÈTE (SANS SAISON) ---
                        variations.append(f"{name} Complete")
                        variations.append(f"{name} Batch")
                        variations.append(f"{name} Collection")
                        variations.append(name)
                    
                    return variations

                try:
                    # Recherche avec le terme exact (qui est maintenant le nom complet si alias trouvé)
                    queries.extend(generate_variations(serie_input, saison, episode))
                    
                except ValueError:
                    console.print("[bold red]Erreur : La saison doit être un nombre.[/bold red]")
                    continue # Retour au menu
                    
                # Choix de la qualité
                quality_choice = questionary.select(
                    "Quelle qualité préfères-tu ?",
                    choices=[
                        questionary.Choice("Tout (Peu importe)", "all"),
                        questionary.Choice("4K / 2160p", "4k"),
                        questionary.Choice("1080p", "1080p"),
                        questionary.Choice("720p", "720p"),
                        questionary.Choice("SD (Non-HD)", "sd")
                    ]
                ).ask()

                # On lance les recherches
                all_results = []
                seen_magnets = set()
                
                # Check if search URL is configured
                if not get_search_url():
                    console.print("[bold red]Erreur: Aucune source de recherche configurée ![/bold red]")
                    console.print("[yellow]Allez dans Configuration pour définir l'URL de votre source de recherche.[/yellow]")
                    continue
                
                for q in queries:
                    results = search_tpb(q)
                    for res in results:
                        if res['magnet'] not in seen_magnets:
                            all_results.append(res)
                            seen_magnets.add(res['magnet'])
                
                # Filtrage par qualité
                if quality_choice != "all":
                    filtered_results = []
                    for res in all_results:
                        title_lower = res['title'].lower()
                        if quality_choice == "4k":
                            if any(x in title_lower for x in ['2160p', '4k', 'uhd']):
                                filtered_results.append(res)
                        elif quality_choice == "1080p":
                            if '1080p' in title_lower:
                                filtered_results.append(res)
                        elif quality_choice == "720p":
                            if '720p' in title_lower:
                                filtered_results.append(res)
                        elif quality_choice == "sd":
                            if not any(x in title_lower for x in ['2160p', '4k', 'uhd', '1080p', '720p']):
                                filtered_results.append(res)
                    
                    if filtered_results:
                        all_results = filtered_results
                    else:
                        console.print(f"[yellow]Aucun résultat trouvé pour la qualité {quality_choice}. Affichage de tous les résultats.[/yellow]")

                # Tri final combiné
                all_results.sort(key=lambda x: x['seeders'], reverse=True)
                torrents = all_results
                
            else:
                query = questionary.text("Que veux-tu regarder ? :").ask()
                if not query:
                    continue
                torrents = search_tpb(query)
        else:
            query = " ".join(sys.argv[1:])
            torrents = search_tpb(query)
            # If arguments are provided, we don't want to loop back to the main menu
            # after the first search. So, we break the main loop after processing.
            # This means the post-stream menu won't be available for command-line searches.
            # If we want it, we'd need to refactor how sys.argv is handled.
            # For now, let's assume command-line args are for a single run.
            
        selected = select_torrent(torrents)
        
        if not selected: # User cancelled selection or no results
            if len(sys.argv) >= 2: # If started with args, exit
                sys.exit()
            else: # If interactive, go back to main menu
                continue
        
        console.print(f"\n[bold green]Tu as choisi : {selected['title']}[/bold green]")
        
        # Choix du lecteur (Casting) - Déplacé avant les sous-titres
        cast_choice = questionary.select(
            "Sur quel appareil lire ?",
            choices=[
                questionary.Choice("Local (MPV)", None),
                questionary.Choice("Chromecast", "chromecast"),
                questionary.Choice("AirPlay (Apple TV)", "airplay"),
                questionary.Choice("DLNA", "dlna")
            ]
        ).ask()

        # Avertissement de compatibilité
        if cast_choice in ['airplay', 'chromecast']:
            title_lower = selected['title'].lower()
            is_risky = False
            reasons = []
            
            if 'mkv' in title_lower:
                is_risky = True
                reasons.append("MKV")
            if 'avi' in title_lower:
                is_risky = True
                reasons.append("AVI")
            if 'dts' in title_lower:
                is_risky = True
                reasons.append("DTS Audio")
            if 'x265' in title_lower or 'hevc' in title_lower:
                is_risky = True
                reasons.append("H.265/HEVC")
                
            if is_risky:
                console.print(f"\n[bold yellow]⚠️  Attention : Ce fichier contient des formats ({', '.join(reasons)}) qui posent souvent problème avec le Casting.[/bold yellow]")
                console.print("[yellow]Si ça ne marche pas, essayez un fichier MP4/x264 ou utilisez le lecteur Local.[/yellow]\n")
                if not questionary.confirm("Essayer quand même ?", default=True).ask():
                    continue
        
        # --- Proposition des sous-titres D'ABORD ---
        want_subs = False
        if mode == "guided" or mode == "manual":
            want_subs = questionary.confirm("Voulez-vous télécharger les sous-titres ?").ask()
        
        # --- Complément d'infos (Mode Guidé) SI sous-titres demandés ---
        if want_subs and mode == "guided":
            # Si on a sélectionné un pack (saison ou série complète) et qu'on n'a pas précisé d'épisode
            if not episode:
                console.print("\n[bold yellow]Pour télécharger les sous-titres, j'ai besoin de savoir quel épisode tu vas regarder.[/bold yellow]")
                ep_input = questionary.text("Numéro de l'épisode (ex: 1) :").ask()
                if ep_input:
                    episode = ep_input
                else:
                    want_subs = False  # Pas d'épisode = pas de sous-titres
            
            # Si la saison n'était pas précisée non plus (Série complète), on la demande
            if want_subs and not saison:
                s_input = questionary.text("Numéro de la saison (ex: 1) :").ask()
                if s_input:
                    saison = s_input
                else:
                    want_subs = False  # Pas de saison = pas de sous-titres
        
        # Téléchargement des sous-titres si demandé
        if want_subs:
            if mode == "guided" and saison and episode:
                # IMPORTANT: serie_input contient maintenant le nom complet (ex: "jujutsu kaisen")
                # grâce à la correction d'alias faite plus haut.
                subtitle_file = download_subtitles(serie_input, saison, episode)
            elif mode == "manual":
                # Mode manuel : on utilise le titre du torrent
                subtitle_file = download_subtitles(None, None, None, raw_filename=selected['title'])
        
        # Sauvegarde de l'historique (si on a les infos)
        if mode == "guided" and saison and episode:
            save_history(serie_input, saison, episode)

        # Boucle de lecture pour ce torrent
        while True:
            stream_torrent(selected['magnet'], subtitle_path=subtitle_file, cast_target=cast_choice)
            
            # Menu après lecture (ou arrêt)
            action = questionary.select(
                "Que faire maintenant ?",
                choices=[
                    questionary.Choice("Relancer ce torrent (choisir un autre fichier)", "retry"),
                    questionary.Choice("Nouvelle recherche", "new"),
                    questionary.Choice("Quitter", "quit")
                ]
            ).ask()
            
            if action == "retry":
                # Si on est en mode guidé, on propose de changer d'épisode pour les sous-titres
                if mode == "guided":
                    if questionary.confirm("Changer d'épisode pour les sous-titres ?", default=False).ask():
                        # Nettoyage de l'ancien sous-titre
                        if subtitle_file and os.path.exists(subtitle_file):
                            try:
                                os.remove(subtitle_file)
                                console.print(f"[dim]Ancien sous-titre supprimé[/dim]")
                            except OSError:
                                pass
                        
                        # Demande du nouvel épisode
                        new_ep = questionary.text("Nouvel épisode (ex: 2) :").ask()
                        if new_ep:
                            episode = new_ep
                            # On garde la même série et saison
                            subtitle_file = download_subtitles(serie_input, saison, episode)
                            # Mise à jour de l'historique
                            save_history(serie_input, saison, episode)
                continue
            elif action == "new":
                # Nettoyage du sous-titre
                if subtitle_file and os.path.exists(subtitle_file):
                    try:
                        os.remove(subtitle_file)
                        console.print(f"[dim]Sous-titre supprimé : {os.path.basename(subtitle_file)}[/dim]")
                    except OSError:
                        pass
                break # Sort de la boucle de lecture, retourne au menu principal
            else:
                # Nettoyage du sous-titre
                if subtitle_file and os.path.exists(subtitle_file):
                    try:
                        os.remove(subtitle_file)
                        console.print(f"[dim]Sous-titre supprimé : {os.path.basename(subtitle_file)}[/dim]")
                    except OSError:
                        pass
                console.print("[yellow]Bye ![/yellow]")
                sys.exit()
        
        # If the script was called with command-line arguments, exit after the first stream.
        # Otherwise, continue the main loop for interactive mode.
        if len(sys.argv) >= 2:
            if subtitle_file and os.path.exists(subtitle_file):
                try:
                    os.remove(subtitle_file)
                except OSError:
                    pass
            sys.exit()
