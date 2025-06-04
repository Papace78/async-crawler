# Async Crawler

## Description
Un crawler Python asynchrone (réalisé en pair-programming) pour collecter, transformer et enrichir des métadonnées vidéo depuis une API tierce avec callbacks pour gerer l’arrêt du crawl.


## Technologies
- **Python 3.11**  
- **Asyncio** & **httpx.AsyncClient** (concurrence, 50 requêtes simultanées)  
- **Tenacity** (retry exponentiel)  
- **Rich.progress.track** (barre de progression)  
- **Pendulum** (gestion des dates/UTC)  
- **Pytest** (tests unitaires)  
- **Poetry** (packaging, CLI)  
- **Docker** (multi-étapes)  
- **MongoDB** (stockage final, géré par pair-programming)  
