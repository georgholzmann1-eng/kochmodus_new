import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# 1. URL Extraktion (wie besprochen)
def extract_url(text):
    urls = re.findall(r'(https?://\S+)', text)
    return urls[0] if urls else text

# 2. Den richtigen Inhalt finden
def scrape_yazio(url):
    headers = {
        # Wir geben uns als sehr alter Browser aus, um App-Redirects zu vermeiden
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        session = requests.Session()
        # 1. Den Kurzlink aufrufen
        response = session.get(url, headers=headers, allow_redirects=True)
        
        # 2. Falls wir im App-Store gelandet sind, versuchen wir die URL zu manipulieren
        # YAZIO Applinks führen oft zu einer URL, die die Rezept-ID enthält.
        final_url = response.url
        st.write(f"DEBUG: Ziel-URL ist {final_url}") # Nur zum Testen

        if "apple.com" in final_url or "google.com" in final_url:
             return "Fehler: YAZIO erzwingt App-Download. Dieses Rezept ist leider nicht öffentlich im Web einsehbar.", [], []

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # NEU: Wir suchen sehr breit nach Zutaten, da YAZIO unterschiedliche Layouts nutzt
        ingredients = []
        # Suche nach allen Elementen, die Mengenangaben enthalten (Zahlen + Einheiten)
        for item in soup.find_all(['li', 'div'], class_=re.compile(r'ingredient|Zutat', re.I)):
            text = item.get_text(strip=True)
            if text:
                ingredients.append(text)
        
        # Schritte finden
        steps = []
        for step in soup.find_all(['li', 'div'], class_=re.compile(r'step|instruction|Zubereitung', re.I)):
            text = step.get_text(strip=True)
            # Nur lange Texte sind echte Anleitungsschritte
            if len(text) > 10:
                steps.append(text)
        
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Dein Rezept"
        
        return title, ingredients, steps

    except Exception as e:
        return f"Fehler beim Laden: {e}", [], []

# --- UI LOGIK ---
query_params = st.query_params
raw_input = query_params.get("url", "")
clean_url = extract_url(raw_input)

url = st.text_input("YAZIO Link:", value=clean_url)

if url:
    with st.spinner('Rezept wird analysiert...'):
        title, ingredients, steps = scrape_yazio(url)
    
    if ingredients:
        st.header(title)
        
        # Sidebar für Zutaten (Immer sichtbar)
        with st.sidebar:
            st.header("🛒 Zutaten")
            for ing in ingredients:
                st.write(f"✅ {ing}")
        
        # Story-Modus für Schritte
        if steps:
            if 'step' not in st.session_state:
                st.session_state.step = 0
            
            curr = st.session_state.step
            
            # Progress-Balken
            st.progress((curr + 1) / len(steps))
            
            # Große Anzeige für den aktuellen Schritt
            st.subheader(f"Schritt {curr + 1} von {len(steps)}")
            st.markdown(f"### {steps[curr]}")
            
            # Riesige Buttons für nasse Finger
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬅️ ZURÜCK", use_container_width=True) and curr > 0:
                    st.session_state.step -= 1
                    st.rerun()
            with col2:
                if st.button("WEITER ➡️", use_container_width=True) and curr < len(steps) - 1:
                    st.session_state.step += 1
                    st.rerun()
    else:
        st.warning("Keine Zutaten gefunden. Möglicherweise ist das Rezept hinter einem Login geschützt oder die URL wird blockiert.")
