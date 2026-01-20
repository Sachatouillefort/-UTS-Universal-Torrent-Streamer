import requests
from bs4 import BeautifulSoup
import os
import json
import time
import shutil

# Determine Project Base Directory (One level up from this file's future location in core/)
# While in root (before move), os.path.dirname(__file__) is root.
# After move to core/, os.path.dirname(__file__) is core/, so parent is root.
# To make it robust for both situations before/after move:
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(CURRENT_DIR) == "core":
    BASE_DIR = os.path.dirname(CURRENT_DIR)
else:
    BASE_DIR = CURRENT_DIR

# Constants
SEARCH_URL = None  # Will be loaded from config
CONFIG_FILE = os.path.join(BASE_DIR, "data", "config.json")
HISTORY_FILE = os.path.join(BASE_DIR, "data", "history.json")
CACHE_FILE = os.path.join(BASE_DIR, "data", "cache.json")
CACHE_DIR = "/tmp/webtorrent"

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"metadata": {}, "files": {}}
    return {"metadata": {}, "files": {}}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=4)

ALIASES = {
    # --- ANIME & MANGA (Populaire) ---
    "jjk": "jujutsu kaisen",
    "snk": "shingeki no kyojin",
    "aot": "attack on titan",
    "hxh": "hunter x hunter",
    "fma": "fullmetal alchemist",
    "fmab": "fullmetal alchemist brotherhood",
    "kn": "kimetsu no yaiba",
    "ds": "demon slayer",
    "op": "one piece",
    "db": "dragon ball",
    "dbz": "dragon ball z",
    "dbs": "dragon ball super",
    "naruto": "naruto shippuden",
    "boruto": "boruto: naruto next generations",
    "bleach": "bleach: thousand-year blood war",
    "mha": "my hero academia",
    "bnha": "boku no hero academia",
    "csm": "chainsaw man",
    "vinland": "vinland saga",
    "berserk": "berserk",
    "monster": "monster",
    "nana": "nana",
    "pluto": "pluto",
    "blue lock": "blue lock",
    "spy": "spy x family",
    "mob": "mob psycho 100",
    "opm": "one punch man",
    "saiki": "saiki kusuo no psi-nan",
    "gintama": "gintama",
    "cowboy": "cowboy bebop",
    "champloo": "samurai champloo",
    "evangelion": "neon genesis evangelion",
    "eva": "neon genesis evangelion",
    "ghibli": "studio ghibli",
    "akira": "akira",
    "ghost": "ghost in the shell",
    "cyberpunk": "cyberpunk edgerunners",
    "arcane": "arcane",
    "castlevania": "castlevania",
    "dota": "dota dragon's blood",
    "rick": "rick and morty",
    "south": "south park",
    "simpsons": "the simpsons",
    "futurama": "futurama",
    "bojack": "bojack horseman",
    "archer": "archer",
    "invincible": "invincible",
    "boys": "the boys",
    "gen v": "gen v",
    "stranger": "stranger things",
    "witcher": "the witcher",
    "mando": "the mandalorian",
    "loki": "loki",
    "andor": "andor",
    "obiwan": "obi-wan kenobi",
    "ahsoka": "ahsoka",
    "last of us": "the last of us",
    "tlou": "the last of us",
    "house": "house of the dragon",
    "got": "game of thrones",
    "rings": "the rings of power",
    "lotr": "the lord of the rings",
    "foundation": "foundation",
    "silo": "silo",
    "severance": "severance",
    "ted": "ted lasso",
    "bear": "the bear",
    "succession": "succession",
    "bb": "breaking bad",
    "bcs": "better call saul",
    "wire": "the wire",
    "sopranos": "the sopranos",
    "office": "the office",
    "friends": "friends",
    "himym": "how i met your mother",
    "b99": "brooklyn nine-nine",
    "community": "community",
    "parks": "parks and recreation",
    "it crowd": "the it crowd",
    "black mirror": "black mirror",
    "dark": "dark",
    "1899": "1899",
    "mindhunter": "mindhunter",
    "narcos": "narcos",
    "peaky": "peaky blinders",
    "vikings": "vikings",
    "crown": "the crown",
    "queens": "the queen's gambit",
    "squid": "squid game",
    "alice": "alice in borderland",
    "money": "money heist",
    "casa": "la casa de papel",
    "lupin": "lupin"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'serie' in data:
                    return [data]
                return data if isinstance(data, list) else []
        except:
            return []
    return []

def save_history(title, magnet, file_index=None, season=None, episode=None, progress=0, duration=0, cover=None):
    history = load_history()
    
    # Create new entry
    new_entry = {
        "title": title,
        "magnet": magnet,
        "file_index": file_index,
        "season": season,
        "episode": episode,
        "progress": progress,
        "duration": duration,
        "cover": cover,
        "timestamp": time.time()
    }
    
    # Remove existing entry for this title (to move it to top)
    history = [h for h in history if h.get('title', '').lower() != title.lower()]
    
    # Add new entry at the top
    history.insert(0, new_entry)
    
    # Keep last 50 items
    history = history[:50]
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def get_cache_size():
    total_size = 0
    if os.path.exists(CACHE_DIR):
        for dirpath, dirnames, filenames in os.walk(CACHE_DIR):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
    return total_size

def clean_cache():
    if os.path.exists(CACHE_DIR):
        try:
            shutil.rmtree(CACHE_DIR)
            return True, "Cache nettoyé avec succès !"
        except Exception as e:
            return False, f"Erreur lors du nettoyage du cache : {e}"
    else:
        return True, "Le cache est déjà vide."

def get_search_url():
    """Get the search URL from config. Returns None if not configured."""
    config = load_config()
    return config.get('search_url')

def search_tpb(query):
    """Search for torrents using configured search URL."""
    # Check if search URL is configured
    search_base_url = get_search_url()
    if not search_base_url:
        return []  # Return empty list if not configured
    
    # Check cache first
    cache = load_cache()
    if query in cache.get("search", {}):
        return cache["search"][query]

    # Try to use the configured search URL
    # Support for different URL patterns
    try:
        # If URL contains apibay.org, use API format
        if 'apibay' in search_base_url:
            search_url = f"{search_base_url}/q.php?q={query}"
        else:
            # For other sites, try standard search format
            search_url = f"{search_base_url}/search/{query}/0/99/0"
        
        response = requests.get(search_url, timeout=10)
        if response.status_code != 200:
            return []
        
        # Try API response first (apibay format)
        if 'apibay' in search_base_url:
            data = response.json()
            
            # Si l'API ne trouve rien
            if len(data) == 1 and data[0].get('name') == 'No results returned':
                return []

            results = []
            for item in data:
                info_hash = item.get('info_hash')
                name = item.get('name')
                seeders = int(item.get('seeders', 0))
                leechers = item.get('leechers', 0)
                
                if info_hash and seeders > 0:
                    magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={name}&tr=udp://tracker.coppersurfer.tk:6969/announce&tr=udp://tracker.openbittorrent.com:80/announce&tr=udp://open.demonii.com:1337/announce&tr=udp://tracker.leechers-paradise.org:6969&tr=udp://tracker.opentrackr.org:1337/announce"
                    
                    results.append({
                        'title': name,
                        'magnet': magnet,
                        'seeders': seeders,
                        'leechers': leechers
                    })
        else:
            # HTML scraping fallback for other sites
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Generic torrent row parsing (adjust selector based on site)
            torrent_rows = soup.find_all('tr')
            
            for row in torrent_rows:
                try:
                    magnet_link = row.find('a', href=lambda x: x and x.startswith('magnet:'))
                    if not magnet_link:
                        continue
                    
                    title_elem = row.find('a', class_='detLink') or row.find('div', class_='detName')
                    if not title_elem:
                        continue
                    
                    # Extract seeders (usually in second or third td)
                    tds = row.find_all('td')
                    seeders = 0
                    for td in tds:
                        if td.get_text().strip().isdigit():
                            seeders = int(td.get_text().strip())
                            break
                    
                    if seeders > 0:
                        results.append({
                            'title': title_elem.get_text().strip(),
                            'magnet': magnet_link['href'],
                            'seeders': seeders,
                            'leechers': 0
                        })
                except:
                    continue
        
        # Tri par seeders
        results.sort(key=lambda x: x['seeders'], reverse=True)
        
        # Update cache
        if "search" not in cache: cache["search"] = {}
        cache["search"][query] = results
        save_cache(cache)
        
        return results

    except Exception as e:
        print(f"Erreur lors de la recherche : {e}")
        return []

def generate_variations(name, s=None, e=None):
    variations = []
    
    if s is not None:
        # --- RECHERCHE AVEC SAISON ---
        try:
            s_int = int(s)
            if e is not None:
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
    
    return list(set(variations)) # Deduplicate

def get_series_rank(title):
    title_lower = title.lower()
    
    # Priority 0: Complete Series / Integrale
    if "complete" in title_lower or "integrale" in title_lower or "totale" in title_lower or "collection" in title_lower:
        return 0
    
    # Priority 1+: Specific Seasons
    import re
    # S01, S1, Season 1
    match = re.search(r'(?:s|season)[ ._-]?(\d{1,2})', title_lower)
    if match:
        season_num = int(match.group(1))
        return season_num
        
    return 999 

def search_smart(name, season=None, episode=None):
    # 1. Alias Correction (Matches CLI logic)
    name_lower = name.lower().strip()
    if name_lower in ALIASES:
        print(f"Alias detected: '{name}' -> '{ALIASES[name_lower]}'")
        name = ALIASES[name_lower]
        
    # 2. Typos/Fuzzy Correction (Matches CLI logic)
    # Only if it's a short/simple name to avoid correcting intentional weird titles
    # But for now, let's trust correct_query if it's reliable
    corrected = correct_query(name)
    if corrected and corrected.lower() != name_lower:
        print(f"Query corrected: '{name}' -> '{corrected}'")
        name = corrected

    queries = []
    
    if season and episode:
        # Series Logic
        queries = generate_variations(name, season, episode)
    else:
        # Movie Logic
        # 1. "Title Year" (Standard)
        queries.append(name)
        
        # 2. Extract Year and search "Title" and "Title 1080p"
        import re
        # Check if name ends with year: "Avatar 2009"
        match = re.match(r'^(.*?) (\d{4})$', name)
        if match:
            clean_title = match.group(1).strip()
            year = match.group(2)
            
            # Add simple title
            queries.append(clean_title) 
            
            # Add Title + 1080p
            queries.append(f"{clean_title} 1080p")
            
            # Add Title + Year + 1080p (Specific)
            queries.append(f"{clean_title} {year} 1080p")
            
            # Add Title + French (for FR users)
            queries.append(f"{clean_title} French")
            queries.append(f"{clean_title} VFF")

    print(f"Smart Search Queries: {queries}")
    
    all_results = []
    seen_magnets = set()
    
    for q in queries:
        results = search_tpb(q)
        for res in results:
            if res['magnet'] not in seen_magnets:
                # SPAM FILTER: Check if result title actually contains keywords from the query
                # This removes "Zootopia" results when searching "Jujutsu" (keyword stuffing in description)
                # Logic: Result must contain at least ONE meaningful word (len > 2) from the ORIGINAL name
                # We use 'name' (the user query) not 'q' (which might be a variation)
                
                res_title_lower = res['title'].lower()
                query_words = [w.lower() for w in name.split() if len(w) > 2]
                
                # If query is very short/common, skip strict filter? No, spam is bad.
                # If query has no words > 2 chars (e.g. "Up"), careful.
                if not query_words:
                    # Fallback for short titles: simply matching the full string inside
                    match = name.lower() in res_title_lower
                else:
                    # Require at least one keyword match (e.g. "Jujutsu" in "Jujutsu Kaisen")
                    match = any(w in res_title_lower for w in query_words)
                
                if match:
                    seen_magnets.add(res['magnet'])
                    all_results.append(res)
                
    # Sort Logic
    # Helper to calculate result score
    def get_score(result_title):
        score = 0
        name_upper = result_title.upper()
        
        # 1. Year Match Boost (Critical for "Avatar 2009" vs "Avatar Anime")
        # UPDATED: User prefers Seeders over strict Year match. 
        # We remove the massive year boost, but keep the series penalty.
        import re
        year_match = re.match(r'^(.*?) (\d{4})$', name)
        
        # 2. Penalize Series keywords if we have a year (likely a movie)
        # This keeps "Avatar The Last Airbender S01" at the bottom when searching "Avatar"
        if any(x in name_upper for x in [" S0", "SEASON", "COMPLETE", "EPISODE", "INTÉGRALE", "INTEGRALE"]):
                pass
        
        series_keywords = [" S0", "E0", "SEASON ", "EPISODE "]
        if any(k in name_upper for k in series_keywords):
            score -= 500 # Penalize series stuff
        
        # 3. Quality Boost (Small tie-breaker)
        if "1080P" in name_upper: score += 10
        if "4K" in name_upper or "2160P" in name_upper: score += 5
        
        # 4. French Boost (since user is French)
        if "FRENCH" in name_upper or "TRUEFRENCH" in name_upper or "VFF" in name_upper:
            score += 50
            
        return score

    if season is None and episode is None:
        # Sort by Score (Desc), then Seeders (Desc)
        all_results.sort(key=lambda x: (get_score(x['title']), x['seeders']), reverse=True)
    else:
        # Series episode search - just seeders usually fine, or keep logic
        all_results.sort(key=lambda x: x['seeders'], reverse=True)
        
    return all_results

def fetch_metadata(query):
    cache = load_cache()
    if query in cache.get("metadata", {}):
        return cache["metadata"][query]

    try:
        from imdb import Cinemagoer
        from ddgs import DDGS
        import re
        
        # CLEAN THE QUERY
        # Strategy: Truncate at the first sign of "technical" info (Year, Season, Resolution, Codec)
        
        # Normalize separators
        clean_q = re.sub(r'[\.\-\_]', ' ', query)
        
        # List of "break" patterns that signal the end of the title
        break_patterns = [
            r'\b(19|20)\d{2}\b',           # Year (19xx or 20xx)
            r'\bS\d{1,2}',                 # Season (S01)
            r'\bE\d{1,2}',                 # Episode (E01)
            r'\b\d{3,4}p\b',               # Resolution (1080p, 720p)
            r'\b(WEB|HDTV|BluRay|DVDRip)\b', # Source
            r'\b(x264|x265|h264|h265|HEVC)\b', # Codec
            r'\b(MULTI|VOSTFR|FRENCH|TRUEFRENCH)\b' # Language
        ]
        
        # Find the earliest break point
        min_idx = len(clean_q)
        for pattern in break_patterns:
            match = re.search(pattern, clean_q, re.IGNORECASE)
            if match:
                min_idx = min(min_idx, match.start())
        
        # Truncate
        clean_q = clean_q[:min_idx].strip()
        
        # Fallback: if empty (e.g. query started with a year), use original but cleaned
        if not clean_q or len(clean_q) < 2:
             clean_q = re.sub(r'[\.\-\_]', ' ', query)
        
        print(f"Cleaned query: '{query}' -> '{clean_q}'")
        
        print(f"Cleaned query: '{query}' -> '{clean_q}'")
        
        ia = Cinemagoer()
        movie = None
        
        # Search with cleaned query
        results = ia.search_movie(clean_q)
        if results:
            # Fetch full movie object by ID to ensure we get all data (covers etc)
            movie = ia.get_movie(results[0].movieID)
        else:
            # Fallback to DDGS with cleaned query
            with DDGS() as ddgs:
                ddg_results = list(ddgs.text(f"site:imdb.com/title {clean_q}", max_results=1))
                if ddg_results:
                    url = ddg_results[0]['href']
                    match = re.search(r'tt\d+', url)
                    if match:
                        imdb_id = match.group(0)[2:]
                        movie = ia.get_movie(imdb_id)

        if movie:
            try:
                ia.update(movie, info=['main', 'plot'])
            except:
                pass
            
            title = movie.get('title', 'Inconnu')
            year = movie.get('year', '????')
            rating = movie.get('rating', 'N/A')
            
            plot_raw = movie.get('plot', ['Pas de résumé disponible.'])
            if isinstance(plot_raw, list):
                plot = plot_raw[0]
            else:
                plot = str(plot_raw)
                
            genres = movie.get('genres', [])
            
            if '::' in plot:
                plot = plot.split('::')[0]
            
            # Try multiple keys for cover
            cover = movie.get('cover url')
            if not cover:
                cover = movie.get('full-size cover url')
            
            # Fallback to DDG Images if no cover found
            if not cover:
                try:
                    with DDGS() as ddgs:
                        keywords = f"{clean_q} {year} movie poster"
                        imgs = list(ddgs.images(
                            keywords, 
                            region="wt-wt", 
                            safesearch="off", 
                            size="Medium", 
                            type_image="Photo", 
                            layout="Tall",
                            max_results=1
                        ))
                        if imgs:
                            cover = imgs[0]['image']
                except Exception as e:
                    print(f"DDG Image Error: {e}")

            data = {
                'title': title,
                'year': year,
                'rating': rating,
                'plot': plot,
                'genres': genres,
                'cover': cover
            }
            
            # Update cache
            if "metadata" not in cache: cache["metadata"] = {}
            cache["metadata"][query] = data
            save_cache(cache)
            
            return data
    except Exception as e:
        print(f"Erreur métadonnées : {e}")
        # Emergency fallback if IMDb completely fails
        try:
             with DDGS() as ddgs:
                keywords = f"{clean_q} movie poster"
                imgs = list(ddgs.images(keywords, region="wt-wt", size="Medium", type_image="Photo", layout="Tall", max_results=1))
                cover = imgs[0]['image'] if imgs else None
                
                return {
                    'title': clean_q,
                    'year': '????',
                    'rating': 'N/A',
                    'plot': 'Pas de résumé disponible (Erreur IMDb).',
                    'genres': [],
                    'cover': cover
                }
        except:
            pass
        pass
    return None

def download_subtitles(serie_name, season, episode, raw_filename=None, year=None):
    try:
        from subliminal import download_best_subtitles, save_subtitles, region
        from subliminal.video import Video, Episode, Movie
        from babelfish import Language
        
        region.configure('dogpile.cache.memory', replace_existing_backend=True)
        
        if raw_filename:
            video_name = raw_filename
            if not any(video_name.lower().endswith(ext) for ext in ['.mkv', '.mp4', '.avi']):
                video_name += ".mkv"
                
            # Fallback: if serie_name is None, try to guess it from specific raw_filename
            if not serie_name:
                import re
                clean = raw_filename.replace('.', ' ').replace('_', ' ')
                # Match "Name Year" pattern
                match = re.search(r'^([a-zA-Z0-9 ]+?) ((?:19|20)\d{2})', clean)
                if match:
                    serie_name = match.group(1).strip()
                    if not year:
                        try:
                            year = int(match.group(2))
                        except: pass
                else:
                    serie_name = " ".join(clean.split()[:3]) # Very rough fallback
                print(f"Fallback guess: Title='{serie_name}', Year={year}")
        else:
            video_name = f"{serie_name} S{int(season):02d}E{int(episode):02d}.mkv"

        # Explicitly create Video object to avoid parsing errors
        video = None
        if season and episode:
            # It's an episode
            video = Episode(video_name, series=serie_name, season=int(season), episode=int(episode), year=year)
        else:
            # It's a movie
            # We treat serie_name as the movie title here
            video = Movie(video_name, title=serie_name, year=year)
            
        print(f"Searching subtitles for: {video} (Year: {year})")
        
        config = load_config()
        provider_configs = {}
        providers = ['thesubdb', 'tvsubtitles'] # Safe defaults

        if config.get('opensubtitles_user') and config.get('opensubtitles_pass'):
            provider_configs['opensubtitles'] = {
                'username': config['opensubtitles_user'],
                'password': config['opensubtitles_pass']
            }
            provider_configs['opensubtitlescom'] = {
                'username': config['opensubtitles_user'],
                'password': config['opensubtitles_pass']
            }
            providers.extend(['opensubtitles', 'opensubtitlescom'])
            
            import ssl
            if hasattr(ssl, '_create_unverified_context'):
                ssl._create_default_https_context = ssl._create_unverified_context

        best_subtitles = download_best_subtitles(
            [video], 
            {Language('fra'), Language('eng')},
            providers=providers,
            provider_configs=provider_configs
        )
        
        if best_subtitles[video]:
            selected_sub = None
            for sub in best_subtitles[video]:
                if sub.language == Language('fra'):
                    selected_sub = sub
                    break
            
            if not selected_sub:
                selected_sub = best_subtitles[video][0]

            save_subtitles(video, [selected_sub])
            
            base_name = os.path.splitext(video_name)[0]
            srt_path = base_name + f".{selected_sub.language.alpha2}.srt"
            
            # Convert to VTT for browser compatibility
            vtt_path = base_name + f".{selected_sub.language.alpha2}.vtt"
            
            # Check if SRT exists (subliminal might name it differently)
            if not os.path.exists(srt_path):
                # Try finding any SRT
                import glob
                candidates = glob.glob(f"{glob.escape(base_name)}*.srt")
                if candidates:
                    srt_path = candidates[0]
            
            if os.path.exists(srt_path):
                convert_srt_to_vtt(srt_path, vtt_path)
                return vtt_path
                
            return None
            
    except Exception as e:
        print(f"Subtitle error: {e}")
        # Fallback: if filename parsing failed, try searching by query?
        # For now, just return None to avoid crashing
        return None

def convert_srt_to_vtt(srt_path, vtt_path):
    try:
        with open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Basic SRT to VTT conversion
        # 1. Add header
        vtt_content = "WEBVTT\n\n" + content
        
        # 2. Convert timestamps (00:00:00,000 -> 00:00:00.000)
        import re
        vtt_content = re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})', r'\1.\2', vtt_content)
        
        with open(vtt_path, 'w', encoding='utf-8') as f:
            f.write(vtt_content)
            
        print(f"Converted {srt_path} to {vtt_path}")
    except Exception as e:
        print(f"VTT Conversion failed: {e}")

def correct_query(user_input):
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(f"{user_input} tv series imdb", max_results=1))
            if results:
                title = results[0]['title']
                clean_title = title.split('(')[0].split('⭐')[0].split('|')[0].split(' - Wikipedia')[0].strip()
                if clean_title.startswith('"'):
                    parts = clean_title.split('"')
                    if len(parts) >= 3:
                        clean_title = parts[1]
                if clean_title.lower() != user_input.lower():
                    return clean_title
    except Exception:
        pass
    return None

def get_torrent_files(magnet):
    """
    Récupère la liste des fichiers d'un torrent via webtorrent downloadmeta.
    Retourne une liste de dicts: {'index': i, 'name': name, 'size': size}
    """
    cache = load_cache()
    if magnet in cache.get("files", {}):
        return cache["files"][magnet]

    import subprocess
    import bencodepy
    import os
    import shutil
    import requests
    
    # 1. Try to download .torrent from cache (FAST)
    infohash = None
    if "xt=urn:btih:" in magnet:
        try:
            infohash = magnet.split("xt=urn:btih:")[1].split("&")[0].lower()
        except:
            pass
            
    # Dossier temporaire pour le .torrent
    temp_dir = "/tmp/pirate_meta"
    os.makedirs(temp_dir, exist_ok=True)
    torrent_file = None

    if infohash:
        print(f"Trying to fetch .torrent from cache for {infohash}...")
        cache_urls = [
            f"http://btcache.me/torrent/{infohash}",
            f"https://itorrents.org/torrent/{infohash}.torrent",
            f"https://torrage.info/torrent.php?h={infohash}"
        ]
        
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        
        for url in cache_urls:
            try:
                print(f"Checking {url}...")
                response = requests.get(url, timeout=5, headers=headers)
                if response.status_code == 200 and len(response.content) > 0:
                    # Verify it starts with 'd' (bencoded dict)
                    if response.content.startswith(b'd'):
                        torrent_path = os.path.join(temp_dir, f"{infohash}.torrent")
                        with open(torrent_path, "wb") as f:
                            f.write(response.content)
                        torrent_file = torrent_path
                        print(f"Successfully fetched from {url}")
                        break
                    else:
                        print(f"Invalid content from {url} (not bencoded)")
                else:
                    print(f"Failed {url}: Status {response.status_code}")
            except Exception as e:
                print(f"Cache fetch failed for {url}: {e}")
    
    # 2. Fallback to webtorrent (SLOW)
    if not torrent_file:
        # Trouver webtorrent
        webtorrent_cmd = "webtorrent"
        if shutil.which("webtorrent") is None:
            local_bin = os.path.join(BASE_DIR, "setup", "node_modules", ".bin", "webtorrent")
            if os.path.exists(local_bin):
                webtorrent_cmd = local_bin
                
        # Nettoyage préventif
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))
            
        cmd = [webtorrent_cmd, "downloadmeta", magnet, "--out", temp_dir]
        print(f"Fetching metadata via WebTorrent (fallback): {cmd}")
        
        try:
            subprocess.run(cmd, check=True, timeout=60, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Trouver le fichier .torrent généré
            for f in os.listdir(temp_dir):
                if f.endswith(".torrent"):
                    torrent_file = os.path.join(temp_dir, f)
                    break
        except Exception as e:
            print(f"WebTorrent fallback failed: {e}")

    if not torrent_file:
        return []
        
    try:
        # Parser le fichier
        metadata = bencodepy.decode_from_file(torrent_file)
        info = metadata[b'info']
        
        files = []
        if b'files' in info:
            for i, f in enumerate(info[b'files']):
                path = [p.decode('utf-8') for p in f[b'path']]
                name = os.path.join(*path)
                size = f[b'length']
                files.append({'index': i, 'name': name, 'size': size})
        else:
            name = info[b'name'].decode('utf-8')
            size = info[b'length']
            files.append({'index': 0, 'name': name, 'size': size})
            
        # Update cache
        if "files" not in cache: cache["files"] = {}
        cache["files"][magnet] = files
        save_cache(cache)

        return files

    except Exception as e:
        print(f"Error parsing files: {e}")
        return []

# TMDB Integration
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_BASE = "https://image.tmdb.org/t/p/original"

def get_tmdb_key():
    config = load_config()
    return config.get("tmdb_api_key")

def normalize_tmdb_item(item, media_type=None):
    # Determine type
    m_type = media_type or item.get('media_type', 'movie')
    
    # Title
    title = item.get('title') or item.get('name') or "Inconnu"
    
    # Year
    date = item.get('release_date') or item.get('first_air_date')
    year = date.split('-')[0] if date else "????"
    
    # Cover
    poster_path = item.get('poster_path')
    cover = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else None
    
    # Backdrop (for hero)
    backdrop_path = item.get('backdrop_path')
    backdrop = f"{TMDB_BACKDROP_BASE}{backdrop_path}" if backdrop_path else None

    return {
        'id': item.get('id'),
        'tmdb_id': item.get('id'),
        'title': title,
        'original_title': item.get('original_title') or item.get('original_name'),
        'original_language': item.get('original_language'),
        'year': year,
        'cover': cover,
        'backdrop': backdrop,
        'plot': item.get('overview', ''),
        'rating': item.get('vote_average', 'N/A'),
        'type': m_type,
        # Flag to indicate this is a metadata-only item, not a torrent yet
        'is_tmdb': True
    }

def fetch_tmdb_trending():
    key = get_tmdb_key()
    if not key: return []
    
    try:
        url = f"{TMDB_BASE_URL}/trending/all/week?api_key={key}&language=fr-FR"
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            return [normalize_tmdb_item(item) for item in data['results']]
    except Exception as e:
        print(f"TMDB Error: {e}")
    return []

def fetch_tmdb_popular_movies():
    key = get_tmdb_key()
    if not key: return []
    try:
        url = f"{TMDB_BASE_URL}/movie/popular?api_key={key}&language=fr-FR"
        resp = requests.get(url)
        if resp.status_code == 200:
            return [normalize_tmdb_item(item, 'movie') for item in resp.json()['results']]
    except Exception as e:
        print(f"TMDB Error: {e}")
    return []

def fetch_tmdb_popular_series():
    key = get_tmdb_key()
    if not key: return []
    try:
        url = f"{TMDB_BASE_URL}/tv/popular?api_key={key}&language=fr-FR"
        resp = requests.get(url)
        if resp.status_code == 200:
            return [normalize_tmdb_item(item, 'tv') for item in resp.json()['results']]
    except Exception as e:
        print(f"TMDB Error: {e}")
    return []

def fetch_tmdb_anime():
    # Anime is usually genre 16 (Animation) + origin_country JP
    key = get_tmdb_key()
    if not key: return []
    try:
        url = f"{TMDB_BASE_URL}/discover/tv?api_key={key}&language=fr-FR&with_genres=16&with_original_language=ja&sort_by=popularity.desc"
        resp = requests.get(url)
        if resp.status_code == 200:
            return [normalize_tmdb_item(item, 'tv') for item in resp.json()['results']]
    except Exception as e:
        print(f"TMDB Error: {e}")
    return []

def fetch_tmdb_documentaries():
    # Genre 99
    key = get_tmdb_key()
    if not key: return []
    try:
        url = f"{TMDB_BASE_URL}/discover/movie?api_key={key}&language=fr-FR&with_genres=99&sort_by=popularity.desc"
        resp = requests.get(url)
        if resp.status_code == 200:
            return [normalize_tmdb_item(item, 'movie') for item in resp.json()['results']]
    except Exception as e:
        print(f"TMDB Error: {e}")
    return []

def fetch_tmdb_search(query):
    key = get_tmdb_key()
    if not key: return []
    try:
        url = f"{TMDB_BASE_URL}/search/multi?api_key={key}&language=fr-FR&query={query}"
        resp = requests.get(url)
        if resp.status_code == 200:
            return [normalize_tmdb_item(item) for item in resp.json()['results']]
    except Exception as e:
        print(f"TMDB Error: {e}")
    return []
