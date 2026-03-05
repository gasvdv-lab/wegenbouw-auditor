import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# --- CONFIGURATIE ---
BEDRIJFS_WACHTWOORD = "Wegenbouw2026" 

st.set_page_config(page_title="Wegenbouw Auditor v2", layout="wide")

def extract_text_from_pdf(uploaded_files):
    """Haalt tekst uit PDF's om tokens te besparen."""
    combined_text = ""
    for file in uploaded_files:
        reader = PdfReader(file)
        for page in reader.pages:
            combined_text += page.extract_text() + "\n"
    return combined_text

if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.title("Beveiligde Toegang")
    pwd = st.text_input("Wachtwoord", type="password")
    if st.button("Log in"):
        if pwd == BEDRIJFS_WACHTWOORD:
            st.session_state["password_correct"] = True
            st.rerun()
else:
    st.sidebar.header("Instellingen")
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

    st.title("🏗️ Project Auditor (Optimized)")
    
    uploaded_files = st.file_uploader("Upload PDF documenten", type="pdf", accept_multiple_files=True)

    if uploaded_files and api_key:
        genai.configure(api_key=api_key)
        # We gebruiken 1.5-flash voor de ruimste gratis limieten
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="Je bent een Senior Lead Engineer Wegenbouw. Analyseer de tekst op basis van SB250. Geef risico's weer in een tabel: [Fase] | [Vaststelling] | [Impact]."
        )

        query_option = st.selectbox("Wat wil je controleren?", [
            "Volledige audit van studie tot boekhouding",
            "Lijst van alle verhardingen",
            "Ontbrekende posten"
        ])

        if st.button("Start Analyse"):
            with st.spinner("Tekst extraheren en analyseren..."):
                try:
                    # Stap 1: Extractie (bespaart tokens t.o.v. PDF upload)
                    pure_text = extract_text_from_pdf(uploaded_files)
                    
                    # Stap 2: Beperk tekstlengte als het extreem groot is (veiligheidsmarge voor gratis quota)
                    # We sturen de eerste 100.000 karakters als test
                    input_text = pure_text[:100000] 

                    response = model.generate_content(f"Vraag: {query_option}\n\nDocument tekst:\n{input_text}")
                    
                    st.markdown("### Resultaat")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Fout: {e}")
    elif not api_key:
        st.warning("Voer je API-key in de zijbalk in.")
