import streamlit as st
import requests
from bs4 import BeautifulSoup
import re  # Wir brauchen "re" für Regular Expressions (Mustererkennung)

# 1. Funktion, um die URL aus dem YAZIO-Text zu extrahieren
def extract_url(text):
    if not text:
        return ""
    # Sucht nach allem, was mit http oder https beginnt
    urls = re.findall(r'(https?://\S+)', text)
    return urls[0] if urls else text

# 2. Link aus der Browser-Zeile holen (von HTTP Shortcuts)
query_params = st.query_params
raw_input = query_params.get("url", "")

# 3. Den Text filtern: Nur die URL behalten
clean_url = extract_url(raw_input)

# 4. Das Eingabefeld mit der sauberen URL füllen
url = st.text_input("YAZIO Rezept-Link:", value=clean_url)

if url:
    try:
        # Daten von YAZIO holen
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraktion (Beispielhafte Selektoren, müssen ggf. angepasst werden)
        title = soup.find('h1').text
        ingredients = [li.text for li in soup.find_all('div', class_='rezept-zutat')]
        steps = [step.text for step in soup.find_all('div', class_='rezept-zubereitung-schritt')]

        st.header(title)
        
        # Sidebar für Zutaten (immer sichtbar)
        with st.sidebar:
            st.header("🛒 Zutaten")
            for ing in ingredients:
                st.write(f"- {ing}")

        # Story-Modus (Step-by-Step)
        if steps:
            if 'step_index' not in st.session_state:
                st.session_state.step_index = 0

            step_count = len(steps)
            current_step = st.session_state.step_index
            
            # Progress Bar wie bei Stories
            progress = (current_step + 1) / step_count
            st.progress(progress)
            
            st.subheader(f"Schritt {current_step + 1} von {step_count}")
            st.info(steps[current_step])

            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬅️ Zurück") and current_step > 0:
                    st.session_state.step_index -= 1
                    st.rerun()
            with col2:
                if st.button("Weiter ➡️") and current_step < step_count - 1:
                    st.session_state.step_index += 1
                    st.rerun()
        
    except Exception as e:
        st.error("Rezept konnte nicht geladen werden. Prüfe den Link!")
