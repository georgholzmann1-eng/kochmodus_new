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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, allow_redirects=True)
        # Falls es ein App-Link ist, nehmen wir die finale URL nach den Umleitungen
        final_url = response.url
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Titel finden
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Rezept"
        
        # Zutaten finden (YAZIO nutzt oft spezifische Klassen oder Data-Attribute)
        # Wir suchen nach Texten in Containern, die typischerweise Zutaten enthalten
        ingredients = []
        ing_elements = soup.select('div[class*="ingredient"], li[class*="ingredient"], .recipe-ingredients-list-item')
        for el in ing_elements:
            ingredients.append(el.get_text(strip=True))
            
        # Schritte finden
        steps = []
        step_elements = soup.select('div[class*="instruction"], .recipe-steps-list-item, div[class*="step"]')
        for el in step_elements:
            text = el.get_text(strip=True)
            if text and len(text) > 5: # Ignoriere kurze Zahlen oder Fragmente
                steps.append(text)
        
        return title, ingredients, steps
    except Exception as e:
        return f"Fehler: {e}", [], []

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
