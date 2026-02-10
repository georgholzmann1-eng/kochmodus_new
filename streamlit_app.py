import streamlit as st
import requests
from bs4 import BeautifulSoup

# Verhindert, dass das Display ausgeht (simuliert durch JavaScript)
st.components.v1.html(
    "<script>navigator.wakeLock.request('screen');</script>",
    height=0,
)

#import streamlit as st

# Extrahiere den Link aus der URL (z.B. ...app/?url=https://yazio...)
url_params = st.query_params
received_url = url_params.get("url", "")

# Falls ein Link empfangen wurde, setze ihn als Standardwert
url = st.text_input("YAZIO Rezept-Link:", value=received_url)

st.title("👨‍🍳 Mein Koch-Modus")

# Link Input (wird über die "Teilen"-Funktion übergeben)
#url = st.text_input("YAZIO Rezept-Link hier einfügen:", placeholder="https://www.yazio.com/de/rezepte/...")

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
