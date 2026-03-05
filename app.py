import streamlit as st
import google.generativeai as genai

# --- CONFIGURATIE EN BEVEILIGING ---
# Dit is het wachtwoord dat werknemers moeten invullen
BEDRIJFS_WACHTWOORD = "Wegenbouw2026" 

# --- INTERFACE INSTELLINGEN ---
st.set_page_config(page_title="Wegenbouw Project Auditor", layout="wide", page_icon="🏗️")

def check_password():
    """Retourneert True als de gebruiker het juiste wachtwoord heeft ingevoerd."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Inlogscherm layout
    st.markdown("<h1 style='text-align: center;'>Bedrijfsportaal Project Auditor</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password = st.text_input("Voer het bedrijfswachtwoord in", type="password")
        if st.button("Toegang verlenen"):
            if password == BEDRIJFS_WACHTWOORD:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Onjuist wachtwoord. Toegang geweigerd.")
    return False

if check_password():
    # --- ZIJBALK VOOR INSTELLINGEN ---
    st.sidebar.header("⚙️ Instellingen")
    api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Plak hier je AIzaSy... sleutel")
    
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Hoe werkt het?**
    1. Voer je API-key in.
    2. Upload projectdocumenten (PDF).
    3. Kies een analyse-type of stel een vraag.
    """)

    # --- HOOFDSCHERM ---
    st.title("🏗️ Wegenbouw & Omgevingswerken Auditor")
    st.markdown("""
    Dit portaal analyseert projectdocumenten op basis van de volledige bedrijfsketen: 
    **Studie & Calculatie → Overdracht → Uitvoering → Boekhouding & Administratie.**
    """)

    if api_key:
        try:
            genai.configure(api_key=api_key)
            # Aangepaste modelnaam om 404 te voorkomen
            model = genai.GenerativeModel(
                model_name="models/gemini-1.5-flash",
                system_instruction="""
                Je bent de 'Lead Engineer & Project Controller' voor infrastructuurwerken in Vlaanderen. 
                Je bent een expert in het SB250 (v5.0) en Vlario-richtlijnen.
                
                Jouw Missie: Analyseer documenten op inconsistenties die leiden tot technische faalkosten of financiële verliezen over de hele keten:
                1. Studie: Klopt de materiaalkeuze en de meetstaat?
                2. Overdracht: Waar moet de werfleider op letten?
                3. Uitvoering: Voldoen de proeven aan de eisen?
                4. Boekhouding: Zijn er risico's op onverrekenbaar meerwerk of boetes?
                
                Stijl: Zakelijk, kritisch en adviserend.
                Output Formaat: Gebruik ALTIJD een tabel voor audits:
                [Fase] | [Vaststelling] | [SB250 Referentie] | [Bedrijfsimpact & Actie]
                """
            )

            # --- BESTANDS-UPLOAD ---
            uploaded_files = st.file_uploader("Upload Bestek, Meetstaat of Verslagen (Meerdere PDF's mogelijk)", type="pdf", accept_multiple_files=True)

            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} document(en) geladen.")
                
                # Snelkeuze menu
                query_option = st.selectbox("Kies een actie:", [
                    "Voer een volledige lifecycle audit uit",
                    "Overzicht van alle verhardingen (Meetstaat check)",
                    "Controle op ontbrekende posten en verborgen kosten",
                    "Vrije vraag stellen..."
                ])

                custom_query = ""
                if query_option == "Voer een volledige lifecycle audit uit":
                    custom_query = "Voer een volledige technische en financiële audit uit van dit project. Kijk naar risico's van de studie-fase tot de boekhoudkundige afwikkeling."
                elif query_option == "Overzicht van alle verhardingen (Meetstaat check)":
                    custom_query = "Geef een tabel met alle verhardingen uit de meetstaat, inclusief SB250 codes en eenheden."
                elif query_option == "Controle op ontbrekende posten en verborgen kosten":
                    custom_query = "Vergelijk de meetstaat met de beschrijvingen. Welke essentiële posten (zoals kleeflagen, aansluitingen, keuringen) ontbreken volgens het SB250?"
                else:
                    custom_query = st.text_area("Stel je specifieke vraag over deze documenten:")

                if st.button("Analyse Starten"):
                    if not custom_query:
                        st.warning("Typ eerst een vraag.")
                    else:
                        with st.spinner("De AI analyseert de documenten aan de hand van het SB250..."):
                            try:
                                # PDF data voorbereiden voor API
                                pdf_parts = []
                                for uploaded_file in uploaded_files:
                                    pdf_parts.append({
                                        "mime_type": "application/pdf",
                                        "data": uploaded_file.getvalue()
                                    })
                                
                                # Verstuur naar Gemini
                                response = model.generate_content([custom_query] + pdf_parts)
                                
                                st.markdown("---")
                                st.subheader("📋 Analyse Resultaat")
                                st.markdown(response.text)
                                
                            except Exception as e:
                                st.error(f"Er ging iets mis bij de analyse: {e}")
        except Exception as e:
            st.error(f"Fout bij configureren van de API: {e}")
    else:
        st.warning("⚠️ Voer je API-sleutel in de zijbalk in om de auditor te activeren.")

# Voettekst
st.markdown("---")
st.caption("Interne Bedrijfsapplicatie - Gebaseerd op SB250 v5.0 en Vlario-normen.")
