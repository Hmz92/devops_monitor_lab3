# DevOps Monitor

FastAPI backend + Streamlit dashboard pour suivre les métriques système et une liste de serveurs.

## Install

```bash
cd devops-monitor
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Run

### Backend

```bash
uvicorn api.main:app --reload --port 8000
```
- Swagger UI : [http://localhost:8000/docs](http://localhost:8000/docs)
- Métriques JSON : [http://localhost:8000/metrics](http://localhost:8000/metrics)

### Dashboard (autre terminal)

```bash
streamlit run dashboard/app.py
```
- Interface accessible sur [http://localhost:8501](http://localhost:8501)

> [!NOTE]
> La clé API par défaut est `demo-key`.
> Pour la changer :
> - **Windows** : `set API_KEY=ma-cle` avant de lancer uvicorn.
> - **Linux/macOS** : `export API_KEY=ma-cle` avant de lancer uvicorn.

---

## Endpoints

- **`GET /health`** - Vérification de l'état de l'API
- **`GET /metrics`** - Métriques système actuelles (CPU, RAM, Disque)
- **`WS /ws/metrics`** - Flux WebSocket temps réel pour les métriques
- **`POST /servers`** - Enregistrer un nouveau serveur *(Nécessite la clé API dans le header `X-API-Key`)*
- **`GET /servers`** - Lister les serveurs enregistrés *(Supporte le filtre `?status=UP`)*
- **`GET /servers/{id}`** - Récupérer les détails d'un serveur spécifique
- **`DELETE /servers/{id}`** - Supprimer un serveur *(Nécessite la clé API dans le header `X-API-Key`)*
- **`POST /servers/{id}/check`** - Déclencher une vérification de santé immédiate

---

## Tests

Exécutez la suite de tests automatisée avec `pytest` :

```bash
# Lancer les tests unitaires et d'intégration
pytest tests/ -v

# Lancer avec le rapport de couverture
pytest --cov=api
```
