import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# --- CONFIGURATIE ---
BEDRIJFS_WACHTWOORD = "Wegenbouw2026" 

# Interface instellingen
st.set_page_config(page_title="Wegenbouw Auditor v2.1", layout="wide", page_icon="🏗️")

def extract_text_from_pdf(uploaded_files):
    """Haalt tekst uit PDF's om tokens te besparen en quota-fouten te verminderen."""
    combined_text = ""
    for file in uploaded_files:
        try:
            reader = PdfReader(file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    combined_text += text + "\n"
        except Exception as e:
            st.error(f"Kon tekst niet uit bestand halen: {e}")
    return combined_text

# --- LOGIN LOGICA ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.title("🏗️ Bedrijfsportaal Project Auditor")
    pwd = st.text_input("Voer het bedrijfswachtwoord in", type="password")
    if st.button("Log in"):
        if pwd == BEDRIJFS_WACHTWOORD:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Onjuist wachtwoord.")
else:
    # --- HOOFDAPP ---
    st.sidebar.header("⚙️ Instellingen")
    api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Plak hier je AIzaSy... sleutel")
    
    st.sidebar.markdown("---")
    st.sidebar.warning("Let op: De gratis API heeft limieten bij grote bestanden. Wacht 1 minuut bij een 'Quota' fout.")

    st.title("🏗️ Project Auditor (Zuinige Modus)")
    st.info("Deze versie zet PDF's eerst om in tekst om de gratis limieten van Google minder snel te overschrijden.")
    
    uploaded_files = st.file_uploader("Upload PDF documenten (Bestek, Meetstaat...)", type="pdf", accept_multiple_files=True)

    if uploaded_files and api_key:
        try:
            genai.configure(api_key=api_key)
            
            # De exacte modelnaam inclusief 'models/' prefix om 404 te voorkomen
            model = genai.GenerativeModel(
                model_name="models/gemini-1.5-flash",
                system_instruction=(
                    "Je bent een Senior Lead Engineer Wegenbouw, expert in SB250 en Vlario. "
                    "Analyseer de aangeleverde tekst op inconsistenties tussen studie, uitvoering en boekhouding. "
                    "Geef risico's weer in een tabel: [Fase] | [Vaststelling] | [SB250 Referentie] | [Impact & Actie]."
                )
            )

            query_option = st.selectbox("Wat wilt u controleren?", [
                "Voer een volledige audit uit (Studie tot Boekhouding)",
                "Geef een overzicht van alle verhardingen",
                "Check op ontbrekende posten in de meetstaat"
            ])

            if st.button("Start Analyse"):
                with st.spinner("Tekst extraheren en Gemini 1.5 raadplegen..."):
                    try:
                        # Stap 1: Tekst extractie
                        pure_text = extract_text_from_pdf(uploaded_files)
                        
                        if not pure_text.strip():
                            st.error("Geen leesbare tekst gevonden in de PDF's.")
                        else:
                            # Stap 2: We beperken de invoer tot de eerste 150.000 karakters 
                            # Dit is meestal genoeg voor de essentie en voorkomt de 429-fout.
                            input_limit = 150000
                            truncated_text = pure_text[:input_limit]
                            
                            if len(pure_text) > input_limit:
                                st.warning(f"Bestand is erg groot. Alleen de eerste {input_limit} tekens worden geanalyseerd om de gratis limiet te respecteren.")

                            # Stap 3: Genereren
                            prompt = f"Vraag: {query_option}\n\nDocument data:\n{truncated_text}"
                            response = model.generate_content(prompt)
                            
                            st.markdown("---")
                            st.subheader("📋 Resultaat Analyse")
                            st.write(response.text)
                            
                    except Exception as e:
                        if "429" in str(e):
                            st.error("Quota overschreden (429). Wacht 60 seconden en probeer het opnieuw. De gratis API laat slechts een beperkt aantal woorden per minuut toe.")
                        else:
                            st.error(f"Fout tijdens analyse: {e}")
                            
        except Exception as e:
            st.error(f"Configuratie fout: {e}")
    elif not api_key:
        st.warning("Voer a.u.b. uw API-sleutel in de zijbalk in.")

st.markdown("---")
st.caption("Interne tool v2.1 - Geoptimaliseerd voor gratis API gebruik.")
