# 🔐 Streamlit Secrets Setup Guide

## Problema rezolvată
Aplicația ta folosește acum o funcție care verifică **automat** unde rulează:
- Pe **Streamlit Cloud** → citește din `st.secrets`
- **Local** → citește din fișierul `.env`

## Cum să configurezi secretele în Streamlit Cloud

### Pasul 1: Accesează Dashboard-ul Streamlit
1. Mergi la [share.streamlit.io](https://share.streamlit.io)
2. Loghează-te cu contul tău
3. Găsește aplicația ta în listă

### Pasul 2: Configurează Secrets
1. Click pe aplicația ta
2. Click pe **⚙️ Settings** (din meniul din dreapta sus)
3. Click pe **🔐 Secrets**

### Pasul 3: Adaugă GEMINI_API_KEY
În editorul de secrets, adaugă:

```toml
GEMINI_API_KEY = "your_actual_api_key_here"
```

**Important:** 
- Fără ghilimele în jurul valorii în unele cazuri (Streamlit acceptă ambele formate)
- Dacă ai alte variabile, le poți adăuga aici:

```toml
GEMINI_API_KEY = "your_actual_api_key_here"
GEMINI_MODEL = "gemini-2.0-flash"
```

### Pasul 4: Salvează și Redeployează
1. Click pe **Save**
2. Aplicația se va reporni automat
3. API Key-ul va fi disponibil acum prin `st.secrets`

## Verificare locală
Pentru a testa local, asigură-te că ai fișierul `.env` în rădăcina proiectului:

```env
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

## Structura fișierului `.gitignore`
Verifică că ai aceste linii în `.gitignore`:

```
.env
.streamlit/secrets.toml
__pycache__/
*.pyc
```

## Cum funcționează acum codul

Funcția `get_env_var()` din `config.py`:
1. **Verifică dacă Streamlit este disponibil** (doar pe Cloud)
2. **Încearcă să citească din `st.secrets`** mai întâi
3. **Dacă nu găsește**, citește din `.env` (local development)

```python
def get_env_var(key, default=None):
    if _streamlit_available:
        try:
            if hasattr(st, 'secrets') and key in st.secrets:
                return st.secrets[key]
        except Exception:
            pass
    return os.getenv(key, default)
```

## Troubleshooting

### Eroare: "GEMINI_API_KEY not set"
✅ **Soluție:** Verifică că ai salvat secretul în Streamlit Cloud și că numele este exact `GEMINI_API_KEY`

### Funcționează local dar nu pe Cloud
✅ **Soluție:** 
1. Verifică că ai adăugat secretul în Settings → Secrets
2. Redeploy aplicația (uneori e nevoie de reboot manual)
3. Verifică logs-urile pentru alte erori

### API Key invalid
✅ **Soluție:** Verifică că API Key-ul de la Google Gemini este valid și activ

## Link-uri utile
- [Streamlit Secrets Documentation](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Google AI Studio - Get API Key](https://makersuite.google.com/app/apikey)

