import os
from typing import Optional, Dict, List

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv   # for local .env support
import base64

# for exporting pdfs
from fpdf import FPDF
import urllib.parse
import html
import time


# ======================
# Load environment variables
# ======================

# Loads variables from a local .env file if it exists (for local dev).
# On Streamlit Cloud, .env is not used, but OPENAI_API_KEY will be provided
# via Secrets and still show up in os.getenv().
load_dotenv()

# ======================
# Streamlit config
# ======================
st.set_page_config(
    page_title="Home Repair Helper",
    page_icon="🛠️",
    layout="wide",
)


#BUCKET_MODEL = "gpt-4o-mini"
BUCKET_MODEL = "gpt-4.1-mini"
EXPLAIN_MODEL = "gpt-4.1"        # or whatever you use for narration

st.markdown("""
<style>
/* Load fonts FIRST - must be at top */
@import url('https://api.fontshare.com/v2/css?f[]=cabinet-grotesk@400,500,600,700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Control top spacing and page width */
.block-container {
    padding-top: 4rem !important;
    max-width: 1100px !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
}

/* Mobile adjustments */
@media (max-width: 768px) {
    .block-container {
        padding-top: 0.75rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
}

/* Add space between app title and tabs */
.stTabs {
    margin-top: 2rem !important;
}

/* Apply Inter to most UI text */
html, body, div, span, input, textarea, button, select, label, p, li, ul, ol, [class], * {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}
            
p, li {
    font-weight: 400 !important;
    line-height: 1.65 !important;
    letter-spacing: 0.003em;
    color: #1F2937 !important;
}

/* Improve default text rendering */
html, body {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Keep headings neutral */
h2, h3 {
    color: #0F172A !important;
}

/* Info box styling */
[data-testid="stAlert"] {
    background-color: #E0F2FE !important;
    border-color: #60A5FA !important;
    color: #0F172A !important;
}
      
.hero-title {
    font-family: 'Cabinet Grotesk', sans-serif;
    font-size: 2.2rem;
    font-weight: 650;
    line-height: 1.15;
    letter-spacing: -0.02em;
    color: #420741ff;
    margin-bottom: 0.75rem;
}

.hero-subtitle {
    font-family: "Manrope", sans-serif !important;
    font-size: 1.1rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: #475569;   /* slate-600 */
    margin-bottom: 0.25rem;
    padding-left: 0.08em;
}


/* Language label + select group */
.lang-wrap {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 2px;
}

.lang-label {
    font-size: 12px;
    color: #64748B;
    line-height: 1;
}

/* Constrain width of the language selectbox */
.st-key-preferred_lang_select {
    max-width: 160px;
}

/* Reduce internal padding / visual height */
.st-key-preferred_lang_select [data-baseweb="select"] > div {
    min-height: 38px !important;
    font-size: 0.90rem !important;
}
 
/* Welcome heading - slightly larger */
h2 {
    font-weight: 500 !important;
    font-size: 1.25rem !important;
    margin-top: 1rem !important;
    margin-bottom: 0.75rem !important;
    color: #0F172A !important;
}

/* Section labels - same size as body */
h3 {
    font-weight: 600 !important;
    font-size: 1rem !important;
    margin-top: 0.75rem !important;
    margin-bottom: 0.5rem !important;
    color: #0F172A !important;
}

/* ===== BACKGROUND COLORS ===== */
/* Make app background pure white. Switch back to FAFAFA later*/
.stApp {
    background-color: #FAFAFA !important;
}


/* Make disclaimer box light-medium gray */
.disclaimer-box {
    background-color: #F1F5F9 !important;
    border-left: 3px solid #94A3B8 !important;
    padding: 1rem 1.25rem !important;
    margin: 1.5rem 0 2rem !important;
    border-radius: 0.375rem !important;
}

/* ===== TAB CONTENT SPACING ===== */
/* Space above and below tab description text */
.tab-description {
    margin-top: 1.5rem !important;
    margin-bottom: 2rem !important;
}

/* Add breathing room between form elements inside tabs */
.stTabs [data-testid="stTextInput"],
.stTabs [data-testid="stTextArea"],
.stTabs [data-testid="stSelectbox"],
.stTabs [data-testid="stMultiSelect"],
.stTabs [data-testid="stFileUploader"] {
    margin-bottom: 1.5rem !important;
}

/* Space around buttons in tabs */
.stTabs [data-testid="stButton"] {
    margin-top: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}

/* Extra space around horizontal rules in tabs */
.stTabs hr {
    margin-top: 2.5rem !important;
    margin-bottom: 2rem !important;
}

/* Space around info/warning boxes in tabs */
.stTabs [data-testid="stAlert"] {
    margin-top: 1.5rem !important;
    margin-bottom: 2rem !important;
}

/* Space around markdown paragraphs in tabs */
/* COMMENTED OUT. THIS IS CAUSING VERTICAL ALIGNMENT ISSUE OF FONT IN BUTTONS
.stTabs [data-testid="stMarkdownContainer"] p {
    margin-bottom: 1rem !important;
}
*/
            
/* Form input hover effects */
input:hover, 
textarea:hover, 
select:hover {
    background-color: #F8FAFC !important;
    transition: background-color 0.2s ease;
}

/* Hover effect for Streamlit's multiselect and selectbox */
[data-baseweb="select"] > div:hover {
    background-color: #F8FAFC !important;
    transition: background-color 0.2s ease;
}

/* Button styling */
[data-testid="stButton"] button,
[data-testid="stDownloadButton"] button {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    font-family: "Manrope", sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 400 !important;
    line-height: 1.15 !important;

    padding-top: 0.55rem !important;
    padding-bottom: 0.55rem !important;

    min-height: 44px !important;

    background-color: #F1F5F9 !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 0.5rem !important;

    transition: background-color 0.2s ease, border-color 0.2s ease;
}

/* Button hover styling */
[data-testid="stButton"] button:hover,
[data-testid="stDownloadButton"] button:hover {
    background-color: #E2E8F0 !important;
    border-color: #CBD5E1 !important;
}

/* Keep action buttons level in same row */
[data-testid="stHorizontalBlock"] {
    align-items: flex-end !important;
}

/* Remove wrapper margins */
[data-testid="stButton"],
[data-testid="stDownloadButton"] {
    margin: 0 !important;
}

[data-testid="stButton"] > div,
[data-testid="stDownloadButton"] > div {
    margin: 0 !important;
    padding: 0 !important;
}
            
/* ================================
   Make inputs more noticeable
   ================================ */

/* Target Streamlit/BaseWeb inputs */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;   /* stronger default border */
    border-radius: 0.55rem !important;
    padding: 0.55rem 0.75rem !important;
    box-shadow: 0 1px 0 rgba(15, 23, 42, 0.04) !important; /* subtle lift */
}

/* Select / multiselect containers (BaseWeb) */
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 0.55rem !important;
    box-shadow: 0 1px 0 rgba(15, 23, 42, 0.04) !important;
}

/* File uploader container */
[data-testid="stFileUploader"] section {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 0.55rem !important;
    box-shadow: 0 1px 0 rgba(15, 23, 42, 0.04) !important;
}

/* Hover: slightly more obvious than before */
[data-testid="stTextInput"] input:hover,
[data-testid="stTextArea"] textarea:hover,
[data-testid="stNumberInput"] input:hover,
[data-testid="stDateInput"] input:hover,
[data-testid="stTimeInput"] input:hover,
[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div:hover,
[data-testid="stFileUploader"] section:hover {
    border-color: #94A3B8 !important;
    background-color: #F8FAFC !important;
}

/* Focus ring (click + keyboard) */
/* [data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stDateInput"] input:focus,
[data-testid="stTimeInput"] input:focus {
    outline: none !important;
    border-color: #420741 !important;
    box-shadow: 0 0 0 3px rgba(66, 7, 65, 0.18) !important;
} */

/* BaseWeb focus states for select/multiselect */
[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within {
    border-color: #420741 !important;
    box-shadow: 0 0 0 3px rgba(66, 7, 65, 0.18) !important;
}

/* Placeholder contrast (often too faint) */
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: #94A3B8 !important;
    opacity: 1 !important;
}
            
/* ===== TAB NAVIGATION STYLING ===== */
/* Active tab - purple color */
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    color: #420741 !important;
    border-bottom-color: #420741 !important;
}

/* Bold the active tab text */
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {
    font-weight: 800 !important;
}

/* Tab highlight bar (underline) */
.stTabs [data-baseweb="tab-highlight"] {
    background-color: #420741 !important;
}

/* Hover state for tabs */
.stTabs [data-baseweb="tab-list"] button:hover {
    color: #420741 !important;
}

/* Inactive tabs - gray and normal weight */
.stTabs [data-baseweb="tab-list"] button[aria-selected="false"] {
    color: #475569 !important;
}

.stTabs [data-baseweb="tab-list"] button[aria-selected="false"] p {
    font-weight: 400 !important;
}
            
/* ===== HIDE STREAMLIT CHROME ===== */
/* Hide top header (3 dots menu) */
header[data-testid="stHeader"] {
    display: none !important;
}

/* Hide footer (but won't hide the Streamlit badge on free tier) */
footer {
    display: none !important;
}
            
/* ===== FIX STREAMLIT MARKDOWN GREEN / CODE STYLING ===== */
/* Neutralize inline code and code blocks so they render like normal text */

code,
pre,
pre code,
kbd,
samp {
    color: inherit !important;
    background-color: transparent !important;
    font-family: inherit !important;
    font-size: inherit !important;
    padding: 0 !important;
    border-radius: 0 !important;
}

/* ===== INDENTED SECTION BODY (replaces blockquote) ===== */
.section-body {
    border-left: 3px solid #E5E7EB;
    padding-left: 1rem;
    margin-left: 0.25rem;
    margin-top: 0.5rem;
    margin-bottom: 1.25rem;
    color: #0F172A;       /* black */
    opacity: 1;
}

.section-body p {
    margin: 0 0 0.75rem 0;
    color: #0F172A;
}
            
/* ========== HOME CHAT BOT ===========*/
/* --- Home chat container --- */
.home-chat-box {
  background-color: #f8fafc;          /* very light neutral */
  border: 1px solid #e5e7eb;           /* subtle outline */
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin: 1rem 0 1.5rem 0;
}

/* Slightly tighten spacing inside */
.home-chat-box .chat-row:last-child {
  margin-bottom: 0;
}

/* --- Home chat (label-based, no avatars) --- */

.chat-row {
  margin-bottom: 0.75rem;
  line-height: 1.4;
}

.chat-label {
  font-weight: 600;
  margin-right: 0.25rem;
}

.chat-user .chat-label {
  color: #475569; /* neutral gray */
}

.chat-assistant .chat-label {
  color: #420741; /* your purple */
}

.chat-text {
  white-space: pre-wrap;
}
            
/* --- Home chat input: match app field styling --- */

/* ===== Text inputs/areas: single focus border (BaseWeb) ===== */

/* Base state (border lives on base-input wrapper) */
[data-testid="stTextInput"] div[data-baseweb="base-input"],
[data-testid="stTextArea"]  div[data-baseweb="base-input"] {
  border: 1px solid #CBD5E1 !important;
  border-radius: 0.55rem !important;
  box-shadow: 0 1px 0 rgba(15, 23, 42, 0.04) !important;
}

/* Remove any focus ring from the OUTER wrapper (prevents double border) */
[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
[data-testid="stTextArea"]  div[data-baseweb="textarea"]:focus-within {
  box-shadow: none !important;
  outline: none !important;
  border-color: transparent !important;
}

/* Focus ring ONLY on inner base-input wrapper */
/* Focus: thicker, softer purple border ONLY (no ring) */
[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within div[data-baseweb="base-input"],
[data-testid="stTextArea"]  div[data-baseweb="textarea"]:focus-within div[data-baseweb="base-input"] {
  border-color: #6b3a6e !important;   /* lighter, softer purple */
  border-width: 2px !important;      /* thicker border */
  box-shadow: none !important;       /* no ring */
}


/* Kill ALL inner input/textarea borders + focus visuals */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}
            
/* ===== Chat input: single border (non-BaseWeb) ===== */

/* Border lives on OUTER wrapper */
[data-testid="stChatInput"] > div {
  border: 1px solid #CBD5E1 !important;
  border-radius: 999px !important;
  background: #FFFFFF !important;
  box-shadow: 0 1px 0 rgba(15, 23, 42, 0.04) !important;
  padding: 0.15rem 0.35rem !important;
}

/* Hover */
[data-testid="stChatInput"] > div:hover {
  border-color: #94A3B8 !important;
}

/* Focus: single thicker border, no ring */
[data-testid="stChatInput"] > div:focus-within {
  border-color: #6b3a6e !important;   /* matches your purple */
  border-width: 2px !important;
  box-shadow: none !important;
  outline: none !important;
}

/* Kill ALL inner textarea borders */
[data-testid="stChatInput"] textarea {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  background: transparent !important;
}

/* Placeholder */
[data-testid="stChatInput"] textarea::placeholder {
  color: #94A3B8;
}

            
</style>
""", unsafe_allow_html=True)


# ======================
# OpenAI client helper
# ======================

def get_openai_client() -> OpenAI:
    """
    Get an OpenAI client using the OPENAI_API_KEY environment variable.

    Works in two setups:
    - Local: you put OPENAI_API_KEY in a .env file and we load it via python-dotenv.
    - Streamlit Cloud: you set OPENAI_API_KEY in Streamlit Secrets, which populates
      the environment automatically (no .env needed).

    Contractors can deploy their own copy by setting their own OPENAI_API_KEY
    in their environment or Streamlit Secrets without changing the code.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error(
            "⚠️ OpenAI API key not found. "
            "Please set `OPENAI_API_KEY` in a .env file (for local use) "
            "or in Streamlit Secrets / environment variables."
        )
        st.stop()
    return OpenAI(api_key=api_key)


if "openai_client" not in st.session_state:
    st.session_state["openai_client"] = get_openai_client()

client: OpenAI = st.session_state["openai_client"]

# ======================
# Language config
# ======================

SUPPORTED_LANGUAGES = [
    {"label": "English", "code": "en", "is_default": True},
    {"label": "Español", "code": "es", "is_default": False},
]

def get_preferred_language() -> Dict:
    language_labels = [lang["label"] for lang in SUPPORTED_LANGUAGES]
    default_index = next(
        i for i, lang in enumerate(SUPPORTED_LANGUAGES) if lang["is_default"]
    )

    preferred_label = st.selectbox(
        "Preferred language",
        language_labels,
        index=default_index,
        key="preferred_lang_select",
        label_visibility="collapsed",
    )

    return next(lang for lang in SUPPORTED_LANGUAGES if lang["label"] == preferred_label)


# ======================
# Disclaimers
# ======================

BASE_DISCLAIMER_EN = """
**Important:** This assistant only provides general educational information.
It does **not** provide professional insurance, legal, or construction advice.
Your insurance company, policy documents, and your contractor’s written plan
are the final authority. If anything here seems different from what they told you,
use this only to help you ask them follow-up questions.
"""

BASE_DISCLAIMER_ES = """
**Importante:** Este asistente solo proporciona información general y educativa.
No ofrece asesoría profesional de seguros, legal ni de construcción.
Su compañía de seguros, sus pólizas y el plan escrito de su contratista
son la autoridad final. Si algo aquí parece diferente a lo que ellos le dijeron,
use esto solo como ayuda para hacerles preguntas de seguimiento.
"""

AGENT_A_DISCLAIMER_EN = """
This tool can help explain estimates and suggest neutral questions.
It cannot say whether an item should be covered or whether an estimate is correct.
Always rely on your adjuster’s and contractor’s written explanations.
"""

AGENT_A_DISCLAIMER_ES = """
Esta herramienta puede ayudar a explicar estimados y sugerir preguntas neutrales.
No puede decir si algo debería estar cubierto ni si un estimado es correcto.
Siempre confíe en las explicaciones escritas de su ajustador y contratista.
"""

AGENT_B_DISCLAIMER_EN = """
This tool suggests typical sequences for repair projects.
Your contractor may choose a different order based on your home and local rules.
Always follow your contractor’s documented plan if it differs.
"""

AGENT_B_DISCLAIMER_ES = """
Esta herramienta sugiere secuencias típicas para proyectos de reparación.
Su contratista puede elegir un orden diferente según su casa y las normas locales.
Siempre siga el plan documentado de su contratista si es diferente.
"""

AGENT_C_DISCLAIMER_EN = """
This tool gives general design suggestions only.
Colors and materials can look very different in real lighting.
Always rely on physical samples in your home and your contractor’s or designer’s advice
for final decisions.
"""

AGENT_C_DISCLAIMER_ES = """
Esta herramienta solo ofrece sugerencias generales de diseño.
Los colores y materiales pueden verse muy diferentes con la luz real de su casa.
Para las decisiones finales, siempre confíe en las muestras físicas en su hogar
y en los consejos de su contratista o diseñador.
"""


# ======================
# OpenAI helpers
# ======================

DEFAULT_MODEL = "gpt-4.1-mini"

def call_gpt(
    system_prompt: str,
    user_content: str,
    model: str | None = None,
    max_output_tokens: int = 800,
    temperature: float | None = None,
) -> str:
    response = client.responses.create(
        model=model or DEFAULT_MODEL,
        instructions=system_prompt,
        input=user_content,
        max_output_tokens=max_output_tokens,
        store=False,
        **({"temperature": temperature} if temperature is not None else {}),
    )
    return response.output_text


def translate_if_needed(text_english: str, target_lang_code: str) -> Optional[str]:
    """
    Translate English -> Spanish (for now). English remains the primary reference.
    """
    if target_lang_code == "en":
        return None
    if target_lang_code != "es":
        # Only EN + ES for now
        return None

    translation_instructions = """
You are a careful translator.
Translate the following text from English to neutral, clear Spanish.
- Preserve headings, bullet points, and formatting.
- Do NOT add new advice or change the meaning.
- If a technical term has no good translation, keep the English in parentheses.
""".strip()

    translated = client.responses.create(
        model="gpt-4.1-mini",
        instructions=translation_instructions,
        input=text_english,
        max_output_tokens=900,
        temperature=0.2,
        store=False,
    )
    return translated.output_text


# DEPRECATED: No longer used - switched to pdfplumber text extraction
def build_estimate_pdf_content(
    insurance_files: List, contractor_files: List, extra_notes: str
) -> List[Dict]:
    """
    Build an 'input' content list for the Responses API that includes:
    - A text block with user context and notes
    - One input_file block per uploaded PDF (insurance + contractor)
    """
    content: List[Dict] = []

    intro_text = f"""
[USER CONTEXT]

The user is a homeowner trying to understand one or more estimates
for home repair or reconstruction.

Extra notes from user (treat as correct if they say it came from adjuster/contractor):
{extra_notes or 'None provided'}

Below are PDF files they uploaded. Treat PDFs in the first group as insurance estimates,
and PDFs in the second group as contractor estimates. Read them and follow the
instructions in the system prompt.
""".strip()

    content.append({"type": "input_text", "text": intro_text})

    def add_pdf_group(files, label: str):
        if not files:
            return
        for f in files:
            if f.type == "application/pdf":
                # Read the uploaded PDF bytes from Streamlit's UploadedFile
                pdf_bytes = f.read()
                b64 = base64.b64encode(pdf_bytes).decode("utf-8")
                content.append(
                    {
                        "type": "input_file",
                        "filename": f.name,
                        "file_data": f"data:application/pdf;base64,{b64}",
                    }
                )
            else:
                # We can extend this later to support images with vision if needed
                content.append(
                    {
                        "type": "input_text",
                        "text": f"[User also uploaded a non-PDF file named '{f.name}' in {label}; "
                                "this version of the app only reads PDF estimates directly.]",
                    }
                )

    add_pdf_group(insurance_files, "insurance estimates")
    add_pdf_group(contractor_files, "contractor estimates")

    return content

# DEPRECATED: No longer used - switched to pdfplumber text extraction  
def call_gpt_estimate_with_pdfs(
    system_prompt: str,
    insurance_files: List,
    contractor_files: List,
    extra_notes: str,
    max_output_tokens: int = 1100,
) -> str:
    """
    Use GPT-4o-mini (vision) with direct PDF input to explain the estimates.
    This bypasses pypdf and lets the model read the PDFs itself.
    """
    user_content_blocks = build_estimate_pdf_content(
        insurance_files, contractor_files, extra_notes
    )

    response = client.responses.create(
        model="gpt-4o-mini",  # vision-capable and cheap
        input=[
            {
                "role": "system",
                "content": [{"type": "input_text", "text": system_prompt}],
            },
            {
                "role": "user",
                "content": user_content_blocks,
            },
        ],
        max_output_tokens=max_output_tokens,
    )

    # Join all output_text blocks into one string
    pieces = []
    for block in response.output[0].content:
        if block.type == "output_text":
            pieces.append(block.text)
    return "\n".join(pieces).strip()


#================================
# EXPORT OUTPUTS HELPER FUNCTIONS
#===============================

def create_explanation_pdf(content, title, followups=None):
    """Create a PDF with main content and optional follow-ups"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(5)
    
    # Main content - clean up markdown AND Unicode characters
    pdf.set_font("Arial", size=11)
    clean_content = (
        content
        .replace('###', '')
        .replace('##', '')
        .replace('**', '')
    )
    # Replace smart quotes and other Unicode with ASCII equivalents
    clean_content = clean_content.replace('\u2019', "'").replace('\u2018', "'")  # smart quotes
    clean_content = clean_content.replace('\u201c', '"').replace('\u201d', '"')  # smart double quotes
    clean_content = clean_content.replace('\u2013', '-').replace('\u2014', '-')  # em/en dashes
    clean_content = clean_content.replace('\u2022', '*')  # bullet points
    pdf.multi_cell(0, 6, clean_content)
    
    # Follow-ups if any
    if followups:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Follow-up Questions & Answers", ln=True)
        pdf.ln(3)
        
        for i, followup in enumerate(followups, 1):
            pdf.set_font("Arial", 'B', 11)
            clean_q = followup['question'].replace('\u2019', "'").replace('\u2018', "'")
            clean_q = clean_q.replace('\u201c', '"').replace('\u201d', '"')
            pdf.multi_cell(0, 6, f"Q{i}: {clean_q}")
            pdf.ln(2)
            
            pdf.set_font("Arial", size=11)
            clean_answer = followup['answer'].replace('###', '').replace('##', '').replace('**', '').replace('*', '')
            clean_answer = clean_answer.replace('\u2019', "'").replace('\u2018', "'")
            clean_answer = clean_answer.replace('\u201c', '"').replace('\u201d', '"')
            clean_answer = clean_answer.replace('\u2013', '-').replace('\u2014', '-')
            clean_answer = clean_answer.replace('\u2022', '*')
            pdf.multi_cell(0, 6, clean_answer)
            pdf.ln(5)
    
    # Footer disclaimer
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(0, 5, "This is general educational information only. Always consult your insurance adjuster and contractor for final decisions.")
    
    return pdf.output(dest='S').encode('latin-1')

#======================
# FIX MARKDOWN ISSUES
#========================

import re

def sanitize_for_streamlit_markdown(md: str) -> str:
    """
    Reduce Streamlit markdown rendering quirks:
    - remove inline arithmetic in parentheses (contains + or =)
    - avoid bolding currency amounts (**$1,234**)
    - optionally normalize unicode dashes already handled elsewhere
    """
    if not md:
        return md

    # 1) Drop parenthetical "math-y" fragments: (A 409 + B 100) or (x = y)
    md = re.sub(r"\(([^)]*[\+=][^)]*)\)", "", md)

    # 2) Unbold currency/amounts: **$1,234.56** -> $1,234.56
    md = re.sub(r"\*\*(\s*\$?\d[\d,]*(?:\.\d{1,2})?)\s*\*\*", r"\1", md)

    # 3) Clean double spaces left behind
    md = re.sub(r"[ \t]{2,}", " ", md)

    return md.strip()

#================
# PYTHON MATERIALS CALCULATIONS
#==================

def format_totals_block(totals_ordered):
    """
    Formats Python-computed bucket totals for injection into the explainer prompt.
    This is PRESENTATION only — no math.
    """
    if not totals_ordered:
        return "Computed material totals: (none found)"

    lines = [
        f"- {bucket}: ${amount:,.2f}"
        for bucket, amount in totals_ordered
    ]

    return (
        "=== COMPUTED TOTALS (GROUND TRUTH — DO NOT MODIFY) ===\n"
        + "\n".join(lines)
        + "\n==============================================="
    )

def build_mini_atomic_sample_from_grouped(grouped: dict, totals_ordered, *, max_buckets: int = 6, lines_per_bucket: int = 3) -> str:
    """
    Build a small, representative sample of atomic numbered line items.
    Uses grouped[bucket] = [MoneyLine] returned by compute_material_totals().
    """
    if not totals_ordered:
        return "=== ATOMIC LINE SAMPLE (FOR CONTEXT ONLY) ===\n(none)\n==============================================="

    top = totals_ordered[:max_buckets]  # already ordered in descending importance by your pipeline? if not, it's still fine.
    out = ["=== ATOMIC LINE SAMPLE (FOR CONTEXT ONLY) ==="]
    for bucket, _amt in top:
        out.append(f"BUCKET: {bucket}")
        lines = grouped.get(bucket, [])[:lines_per_bucket]
        for ml in lines:
            out.append(f"{ml.text}")
        out.append("")  # blank line between buckets

    out.append("===============================================")
    return "\n".join(out).strip()


#========================================
# FORMATTING ESTIMATE EXPLANATION
#========================================
import re
from typing import List, Tuple, Optional

BOLD_HEADING_LINE_RE = re.compile(r"^\*\*[^*\n]+\*\*$")

def split_by_bold_headings(text: str) -> List[Tuple[Optional[str], str]]:
    """
    Splits plain-text explanation into sections delimited by bold-only heading lines.
    Returns list of (heading_line_or_None, body_text).

    - heading is the literal **Heading** line (including **), or None for intro.
    - intro text (before first heading) becomes (None, intro_body).
    """
    if not text:
        return []

    lines = text.splitlines()
    sections: List[Tuple[Optional[str], List[str]]] = []
    current_heading: Optional[str] = None
    current_body: List[str] = []

    def flush():
        nonlocal current_heading, current_body
        body = "\n".join(current_body).strip("\n")
        # Keep even empty bodies if a heading exists; skip fully empty intro
        if current_heading is not None or body.strip():
            sections.append((current_heading, body))
        current_heading = None
        current_body = []

    seen_first_heading = False
    for line in lines:
        if BOLD_HEADING_LINE_RE.match(line.strip()):
            if not seen_first_heading:
                # everything accumulated so far is the intro -> Overview
                flush()
                seen_first_heading = True
            else:
                flush()
            current_heading = line.strip()
        else:
            current_body.append(line)

    flush()

    # If the very first section ended up as (None, "") (e.g., text starts with heading), drop it
    if sections and sections[0][0] is None and not sections[0][1].strip():
        sections = sections[1:]

    # If there was intro text but no headings at all, it will be (None, full_text)
    return sections

#===========================
# ROOM TOTALS (EXPLICIT FROM PDF)
#============================

import re
from typing import Dict, Tuple

ROOM_TOTAL_LINE_RE = re.compile(r"^\s*Totals:\s*(.+?)\s+(.*)$")
MONEY_RE = re.compile(r"(\d{1,3}(?:,\d{3})*(?:\.\d{2})|\d+(?:\.\d{2}))")

# things that show up as "Totals:" but are NOT rooms
NON_ROOM_TOTAL_LABELS = {
    "Labor Minimums Applied",
    "Line Item Totals",
    "Recap of Taxes, Overhead and Profit",
}

# floor/sketch groupings (extra guard even though we ignore Area Totals already)
NON_ROOM_NAME_EXACT = {
    "Main Level",
    "First Floor",
    "Second Floor",
    "Upper Level",
    "Lower Level",
    "Labor",
}
NON_ROOM_PREFIXES = ("SKETCH",)

def extract_room_totals_from_text(extracted_text: str) -> Dict[str, str]:
    """
    Extract explicitly-provided room totals from estimate text.

    Returns: {room_name: "$1,234.56"}  (keeps original comma formatting)
    Only trusts lines that start with "Totals:" and have a clear final numeric total.
    """
    if not extracted_text:
        return {}

    out: Dict[str, str] = {}

    for raw_line in extracted_text.splitlines():
        line = raw_line.strip()
        if not line.startswith("Totals:"):
            continue

        m = ROOM_TOTAL_LINE_RE.match(line)
        if not m:
            continue

        room = m.group(1).strip()

        # Reject known non-room labels
        if room in NON_ROOM_TOTAL_LABELS:
            continue

        # Reject floor/group labels if they ever appear under Totals:
        if room in NON_ROOM_NAME_EXACT:
            continue
        if any(room.upper().startswith(pfx) for pfx in NON_ROOM_PREFIXES):
            continue

        # Find numeric tokens on the rest of the line; use the LAST one as the total.
        rest = m.group(2)
        nums = MONEY_RE.findall(rest)
        if not nums:
            continue

        total_str = nums[-1]  # last number on the line is the total in your PDF
        # Ensure it looks like dollars+ cents OR at least a plausible number; keep as displayed.
        # If you want strict cents: require '.' in total_str and len after dot == 2.

        # Re-add "$" for display consistency (your text sometimes omits $)
        out[room] = f"${total_str}"

    return out

def build_room_totals_block(room_totals: dict, *, doc_role: str, doc_name: str) -> str:
    # Return empty string if nothing found
    if not room_totals:
        return ""

    lines = [f"{room}: {amt}" for room, amt in sorted(room_totals.items(), key=lambda x: x[0].lower())]
    if not lines:
        return ""

    return (
        "=== PROVIDED ROOM TOTALS (FROM ESTIMATE — DO NOT MODIFY) ===\n"
        f"DOCUMENT: {doc_role.upper()} — {doc_name}\n"
        + "\n".join(lines)
        + "\n=========================================================="
    )

#========================
# SUMMARY NUMBERS FROM ESTIMATE PDF
#=======================

_MONEY_RE = re.compile(r"\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})|\d+(?:\.\d{2}))")

def _money_from_line(line: str) -> Optional[str]:
    """Return the first money-like token in the line as a display string with $."""
    m = _MONEY_RE.search(line)
    if not m:
        return None
    amt = m.group(1)
    return f"${amt}"

def extract_key_numbers_from_text(extracted_text: str) -> Dict[str, str]:
    """
    Extract key summary numbers from estimate text.
    Only returns values that are explicitly labeled in the text.
    Output keys are human-facing labels:
      - Replacement Cost Value (RCV)
      - Actual Cash Value (ACV)
      - Depreciation
      - Deductible
      - Net Payment
      - Overhead & Profit
      - Sales Tax
    """
    if not extracted_text:
        return {}

    lines = [ln.strip() for ln in extracted_text.splitlines() if ln.strip()]
    out: Dict[str, str] = {}

    # label patterns (case-insensitive); we only capture if line also has a money token
    patterns = [
        (re.compile(r"\b(replacement cost value|rcv)\b", re.I), "Replacement Cost Value (RCV)"),
        (re.compile(r"\b(actual cash value|acv)\b", re.I), "Actual Cash Value (ACV)"),
        (re.compile(r"\bdepreciation\b", re.I), "Depreciation"),
        (re.compile(r"\bdeductible\b", re.I), "Deductible"),
        (re.compile(r"\bnet\b.*\b(payment|claim)\b|\btotal\b.*\bnet\b", re.I), "Net Payment"),
        (re.compile(r"\b(overhead\s*&\s*profit|o\s*&\s*p|overhead and profit)\b", re.I), "Overhead & Profit"),
        (re.compile(r"\b(sales\s*tax|tax)\b", re.I), "Sales Tax"),
    ]

    # We’ll take the LAST matching occurrence (often the most final summary)
    for line in lines:
        # quick skip: if no digits at all, it can't contain an amount
        if not any(ch.isdigit() for ch in line):
            continue

        amt = _money_from_line(line)
        if not amt:
            continue

        # ignore lines that are clearly not summary key numbers
        # (you can expand this list if needed)
        if re.search(r"\b(page|line item|subtotal by room|totals:)\b", line, re.I):
            continue

        for rx, label in patterns:
            if rx.search(line):
                out[label] = amt
                break

    return out



def build_key_numbers_block(key_numbers: Dict[str, str], *, doc_role: str, doc_name: str) -> str:
    if not key_numbers:
        return ""

    # consistent display order
    order = [
        "Replacement Cost Value (RCV)",
        "Actual Cash Value (ACV)",
        "Depreciation",
        "Deductible",
        "Overhead & Profit",
        "Sales Tax",
        "Net Payment",
    ]

    lines = []
    for k in order:
        if k in key_numbers:
            lines.append(f"{k}: {key_numbers[k]}")

    if not lines:
        return ""

    return (
        "=== PROVIDED KEY NUMBERS (FROM ESTIMATE — DO NOT MODIFY) ===\n"
        f"DOCUMENT: {doc_role.upper()} — {doc_name}\n"
        + "\n".join(lines)
        + "\n=========================================================="
    )


# ======================
# HOME AI CHAT PROMPT
# ======================

def build_home_assistant_system_prompt() -> str:
    return """
You are the Home page assistant for a homeowner-facing contractor app.
Your job is to orient the user and recommend ONE best starting tool.

TOOLS (recommend only one per message):
1) Estimate Explainer — explains insurance/contractor estimate line items in plain language.
2) Renovation Plan — explains typical sequence of repairs and what happens when.
3) Design Helper — helps with design/material decisions using photos and descriptions.

DEFAULT START:
- If the user is unsure where to begin, default to:
  **Estimate Explainer** (it’s usually the best first anchor).

RESPONSE SHAPE:
- 4–6 short lines total (friendly, not robotic).
- Start with a brief empathy/acknowledgement (1 sentence).
- Then recommend ONE tool, which best fits the user's input, using this pattern:
  “People often start by X. The [Tool Name] is the best place to begin.”
- Then include “To use it well:” with 1–3 practical points.
- End with one gentle next step that explains what the user will do *in that tool*.
  (Example: what they’ll upload or describe once they open that tab.)


HARD LIMITS:
- You do NOT perform any work inside the Home chat.
- You must NEVER ask the user to upload, paste, or enter information "here" or "in this chat".
- All actions (uploading, pasting, describing details) happen ONLY inside the specific tool tabs.
- When suggesting next steps, ALWAYS refer to the tool by name and direct the user to that tab.

- Do NOT provide step-by-step professional advice, pricing judgments, or code/legal guidance.
- If the user asks detailed questions, redirect to ONE tool and explain what they’ll do *there*.
- If the question spans multiple stages, you may mention a typical flow in ONE sentence,
  but you MUST end with ONE clear starting tool recommendation.
- Never list multiple tools as options and never ask the user to choose.

TONE:
- Warm, calm, supportive. Plain language. No lecturing.
- Avoid sounding like a chatbot. No overconfidence.
""".strip()


# ======================
# Mini-Agent A: Estimate Explainer
# ======================

def build_estimate_system_prompt() -> str:
    return """
You are an assistant that explains home insurance and construction estimates
for homeowners in simple, friendly English.

YOUR ROLE (IMPORTANT):
- You explain scope, meaning, and structure.
- You provide big-picture interpretation and context.
- You do NOT perform arithmetic or calculate totals.
- If computed totals are provided, you must treat them as ground truth.

SOURCE OF TRUTH (CRITICAL):
- You may receive a block labeled:
  "COMPUTED TOTALS (GROUND TRUTH — DO NOT MODIFY)".
- These numbers are produced by deterministic Python code that sums
  atomic, numbered line items (e.g., lines starting with "1.", "2.", etc.).
- For material totals, ONLY use the numbers from this computed totals block.
- Do NOT attempt to find, reconstruct, infer, or recompute material totals
  from the extracted PDF text, even if the PDF contains summary or "Totals" lines.
- The extracted PDF text is provided for context and examples only.

DOCUMENT READING:
- You may receive raw text from an insurance estimate, a contractor estimate, or both.
- The text may be messy or lack table formatting.
- You should still try to extract useful contextual information.
- When helpful, you may refer to:
  - Line item descriptions
  - Quantities (e.g. SF, LF, EA)
  - Unit prices (e.g. $/sq ft)
  - Subtotals, taxes, depreciation
  - Overhead & profit (O&P)
  - Deductible and net payment amounts
- ONLY say that the text is unreadable if it is truly empty or clearly not an estimate.
- Do NOT say things like "the text you provided is not in a readable format"
  if any real estimate text is present.

GENERAL BEHAVIOR:
- Focus on high-level interpretation, not exhaustive line-item detail.
- Help the homeowner understand what is driving cost and scope.
- You may mention rooms or areas where work occurs (Garage, Loft, Kitchen, Laundry, Office, Stairs, etc.).
- CRITICAL: Skip generic grouping labels such as:
  "Main Level", "First Floor", "Second Floor", "Upper Level".
  * These are NOT rooms.
  * Only mention actual rooms (Kitchen, Bedroom, Garage, etc.).
- Do NOT invent room totals.
- Only state a room total if it is clearly shown as a provided total in the estimate.

MATERIAL TOTALS (CRITICAL):
- You may be given a block labeled:
  "COMPUTED TOTALS (GROUND TRUTH — DO NOT MODIFY)".
- If present, these totals are authoritative and exact.
- When computed totals are provided:
  - Quote them EXACTLY (same numbers, dollars and cents).
  - NEVER use approximate language ("around", "about", "approximately").
  - NEVER compute, infer, or extract alternative material totals from the PDF text.
- Atomic line items (numbered lines) may be cited as examples only.
  - Do NOT add them together.
  - Do NOT treat them as totals.
- In "Summary by Material":
  - Mention major material categories only.
  - Include the exact computed total for each category if provided.
  - Describe what the category typically includes (removal, pad, labor, transitions, etc.).
  - Do NOT add, change, or adjust dollar amounts.
  - Use human-read understandable labels for each material (no snake_underscore material labels)
- If a material category is discussed but no computed total is provided:
  - Say "No computed total found for [material]".
  - Suggest a neutral follow-up question.
  - Do NOT estimate.

ROOM TOTALS (CRITICAL):
- You may be given a block labeled:
  "PROVIDED ROOM TOTALS (FROM ESTIMATE — DO NOT MODIFY)".
- These room totals are copied from explicit room total lines in the estimate
  (e.g., lines labeled "Totals: [Room]").
- If this block is present:
  - Quote room totals EXACTLY as provided (same dollars and cents).
  - NEVER compute, infer, or reconstruct room totals from the extracted estimate text.
  - Only mention room totals that appear in this block.
- If this block is NOT present:
  - Do NOT list room totals.
  - Do NOT guess or estimate room totals.
  - You may optionally note that many estimates include a "Totals by Room/Area" summary page.
- When discussing rooms:
  - Only refer to actual rooms (Kitchen, Bathroom, Garage, Office, Stairs, etc.).
  - Skip generic grouping labels such as "Main Level", "First Floor", "Second Floor", "Upper Level", and sketch labels like "SKETCH1".

KEY NUMBERS (CRITICAL):
- You may receive a block labeled:
  "PROVIDED KEY NUMBERS (FROM ESTIMATE — DO NOT MODIFY)".
- If present, treat these numbers as authoritative and quote them exactly.
- Only state key numbers that appear in this block.
- If the block is not present, say key numbers were not found and do not guess.

FORMATTING (IMPORTANT):
- Avoid using bold or italics around numeric amounts.
  (Do not write **$1,622**.)
- When explaining what a cost includes, put the explanation on a new line.
  Example:
  Total carpet cost: $1,628.89
  Includes removal, pad, new carpet, and stair step charges.

USER QUESTIONS OR CONTEXT:
- The user may provide additional notes or questions.
- Always provide a complete high-level explanation first.
- If the user provided questions, address them in a dedicated section titled:
  "Addressing Your Specific Questions".

HARD RULES:
- You are NOT a lawyer, insurance adjuster, or contractor.
- Treat statements from the insurance company, policy documents,
  and contractor as authoritative.
- NEVER say that an estimate is wrong, unfair, or incomplete.
- NEVER say what insurance "should" cover or "should" pay.
- You may ONLY suggest neutral questions such as:
  - "You may want to ask your adjuster whether..."
  - "You can confirm with your contractor if..."
- If both an insurance and contractor estimate are provided:
  - You MAY point out structural differences.
  - ALWAYS frame them as neutral observations or questions.
- Do NOT compute totals from the estimate text.
- Do NOT use approximate language for computed totals.

OUTPUT STYLE (IMPORTANT):
- Use plain text paragraphs.
- Section headings MUST be bolded using **double asterisks**.
- Do NOT use Markdown headings (##, ###).
- Do NOT use bullet characters such as "-", "*", or "•".
- Do NOT use backticks (`) or fenced code blocks.
- Do NOT italicize text.
- Do NOT apply bold formatting to numeric amounts.
- Use line breaks for readability.
- Do NOT indent with dashes or symbols.
- Do NOT output any HTML or XML tags (no <div>, <span>, <br>, etc.).
- Do NOT use angle brackets < or > anywhere in the output.

SPACING RULES:
- After every bold section heading, insert exactly one blank line before the paragraph text.
- Between major sections, insert exactly one blank line.
- Do not put multiple blank lines in a row.

MATERIALS LISTING RULE (IMPORTANT):
- When listing multiple materials, rooms, or categories with dollar amounts:
  - Put EACH item on its own line.
  - Do NOT combine multiple items on the same line.
  - Use the format:
    Category name: dollar amount

EXPLANATION LIST RULE (IMPORTANT):
- When explaining what multiple categories or tasks typically represent:
  - Put EACH category explanation on its own line.
  - Start each line with the category name.
  - Do NOT combine multiple categories into a single paragraph.
  - Do NOT use bullets or numbering.


OUTPUT FORMAT (English):
- Short introductory orientation.
  * Provide room totals, each room on a separate line.

- "What’s Driving Cost in This Estimate"
  * Start with a one-sentence opener like: "Here are the main tasks and materials driving your costs."
  * List major material category in decending order by total cost.
  * For each category:
    * Start a new paragraph.
    * Begin with: Material category Name: $Exact Amount
    * For category name, use natural, homeowner-friendly labels with no underscores and Capitalized first letter.
    * Follow with one sentence explaining what that category typically includes.
  * Insert one blank line between categories.
  * Do not combine categories into the same paragraph.

- "Key Numbers From Your Estimate"
  * List each category from the Key numbers block on a separate line. Includes things like the following:
    * Replacement Cost Value (RCV), if clearly present
    * Deductible, if present
    * Net payment, if present
    * General Contractor Overhead & Profit, if present
    * Material sales tax, if significant

- If applicable: "Addressing Your Specific Questions"

- "Questions to Ask Your Adjuster" (2-3)

- "Questions to Ask Your Contractor" (2-3)

- End with a short reminder that this is general information only.
""".strip()


def estimate_explainer_tab(preferred_lang: Dict):

    st.markdown("""
    <div class="tab-description">
        Understand what's included in your insurance and contractor estimates, 
        what key numbers mean, and which questions may be worth asking.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### What estimates do you have?")
    colA, colB = st.columns(2)
    with colA:
        has_insurance = st.checkbox("Insurance estimate", value=False, key="has_insurance")
    with colB:
        has_contractor = st.checkbox("Contractor estimate", value=False, key="has_contractor")

    insurance_files = []
    contractor_files = []

    if has_insurance:
        st.markdown("### Upload your insurance estimate (PDF)")
        insurance_files = st.file_uploader(
            label="Insurance estimate",
            type=["pdf"],
            accept_multiple_files=True,
            key="ins_files",
            label_visibility="collapsed"
        )

    if has_contractor:
        st.markdown("### Upload your contractor estimate (PDF)")
        contractor_files = st.file_uploader(
            label="Contractor estimate",
            type=["pdf"],
            accept_multiple_files=True,
            key="con_files",
            label_visibility="collapsed"
        )

    extra_notes = st.text_area(
        "Any specific questions about this estimate? (Optional)",
        help="For example: 'Why is demolition so expensive?' or 'What's included in the carpet cost?'")

    if st.button("Explain my estimate"):
        # Validation
        if not has_insurance and not has_contractor:
            st.warning("Please select at least one estimate type.")
            return

        if has_insurance and not insurance_files:
            st.warning("Please upload your insurance estimate (PDF).")
            return

        if has_contractor and not contractor_files:
            st.warning("Please upload your contractor estimate (PDF).")
            return

        if not insurance_files and not contractor_files:
            st.warning("Please upload at least one estimate (PDF).")
            return
        
        # STATUS UPDATE WHILE BUILDING EXPLANATION
        status_box = st.empty()
        progress_bar = st.progress(0)

        def set_step(step_num, msg):
            progress_bar.progress(step_num / 4)
            status_box.markdown(f"**{msg}**")


        with st.spinner("I'm working through your estimate now. This usually takes about 20–30 seconds."):
            # Store PDFs as bytes for follow-ups
            st.session_state["estimate_insurance_pdfs"] = [
                {"name": f.name, "type": f.type, "bytes": f.getvalue()}
                for f in (insurance_files or [])
            ]

            st.session_state["estimate_contractor_pdfs"] = [
                {"name": f.name, "type": f.type, "bytes": f.getvalue()}
                for f in (contractor_files or [])
            ]

            # Extract text with pdfplumber (per-document)
            from estimate_extract import extract_pdf_pages_text, join_page_packets
            from material_totals import compute_material_totals

            # ====================
            # FILE SIGNATURE (for caching)
            # ====================
            current_files_sig = sorted(
                [(f.name, len(f.getvalue())) for f in (insurance_files or [])] +
                [(f.name, len(f.getvalue())) for f in (contractor_files or [])]
            )

            prev_files_sig = st.session_state.get("estimate_uploaded_file_sig")
            already_extracted = bool(st.session_state.get("estimate_extracted_docs"))
            files_unchanged = (prev_files_sig == current_files_sig)

            # ====================
            # TIME DEBUG INIT
            # ====================
            pdf_time = 0.0
            atomic_time = 0.0
            bucket_time = 0.0
            explain_time = 0.0

            # ====================
            # REUSE OR EXTRACT
            # ====================
            set_step(1, "Reading your PDF…")

            if files_unchanged and already_extracted:
                # Reuse cached extracted text; don't re-run pdfplumber
                docs = st.session_state["estimate_extracted_docs"]
                all_extracted_text = st.session_state.get("estimate_all_extracted_text", "")
                print("[CACHE] Reusing cached extracted text (no pdfplumber run).")
            else:
                # Files changed (or no cache yet) → extract again
                st.session_state["estimate_uploaded_file_sig"] = current_files_sig

                docs = []  # list of {"role": "insurance"|"contractor", "name": str, "text": str}
                all_extracted_text = ""

                # ==============================
                # Extract from insurance files
                # ==============================
                for f in (insurance_files or []):
                    t0 = time.perf_counter()
                    packets = extract_pdf_pages_text(f.getvalue())
                    block = join_page_packets(packets)
                    t1 = time.perf_counter()

                    elapsed = t1 - t0
                    pdf_time += elapsed
                    print(f"[TIMING] pdfplumber extraction ({f.name}): {elapsed:.2f}s")

                    docs.append({"role": "insurance", "name": f.name, "text": block})
                    all_extracted_text += f"\n\n=== INSURANCE ESTIMATE: {f.name} ===\n\n{block}"

                # ==============================
                # Extract from contractor files
                # ==============================
                for f in (contractor_files or []):
                    t0 = time.perf_counter()
                    packets = extract_pdf_pages_text(f.getvalue())
                    block = join_page_packets(packets)
                    t1 = time.perf_counter()

                    elapsed = t1 - t0
                    pdf_time += elapsed
                    print(f"[TIMING] pdfplumber extraction ({f.name}): {elapsed:.2f}s")

                    docs.append({"role": "contractor", "name": f.name, "text": block})
                    all_extracted_text += f"\n\n=== CONTRACTOR ESTIMATE: {f.name} ===\n\n{block}"

                # Cache extracted text for downstream tabs (e.g., Renovation)
                st.session_state["estimate_extracted_docs"] = [
                    {"role": d["role"], "name": d["name"], "text": d["text"]}
                    for d in docs
                ]
                st.session_state["estimate_all_extracted_text"] = all_extracted_text

            # ====================
            # Compute material totals for EACH uploaded document (Option A: show separately)
            # ====================
            set_step(2, "Organizing the numbers by category…")

            material_results = []  # each: {"role","name","totals_ordered","result","totals_block","mini_sample"}
            totals_blocks = []
            room_totals_blocks = []
            key_numbers_blocks = []

            for d in docs:
                if not d["text"].strip():
                    continue

                result = compute_material_totals(
                    client=client,
                    model=BUCKET_MODEL,
                    extracted_text=d["text"],
                )

                labeled_totals_block = (
                    "=== COMPUTED TOTALS (GROUND TRUTH — DO NOT MODIFY) ===\n"
                    f"DOCUMENT: {d['role'].upper()} — {d['name']}\n"
                    + "\n".join([f"{bucket}: ${amount:,.2f}" for bucket, amount in result["totals_ordered"]])
                    + "\n==============================================="
                )

                mini_sample = build_mini_atomic_sample_from_grouped(
                    result["grouped"],
                    result["totals_ordered"],
                    max_buckets=6,
                    lines_per_bucket=3,
                )

                material_results.append(
                    {
                        "role": d["role"],
                        "name": d["name"],
                        "totals_ordered": result["totals_ordered"],
                        "result": result,
                        "totals_block": labeled_totals_block,
                        "mini_sample": mini_sample,
                    }
                )

                totals_blocks.append(labeled_totals_block)

                timings = result.get("timings", {})
                atomic_time += timings.get("atomic_extraction_s", 0.0)
                bucket_time += timings.get("bucketing_llm_s", 0.0)

                # ROOM TOTALS
                room_totals = extract_room_totals_from_text(d["text"])
                if room_totals:
                    room_block = build_room_totals_block(room_totals, doc_role=d["role"], doc_name=d["name"])
                    if room_block:
                        room_totals_blocks.append(room_block)

                # KEY NUMBERS (summary-page figures like RCV, deductible, net payment)
                key_numbers = extract_key_numbers_from_text(d["text"])
                key_block = build_key_numbers_block(key_numbers, doc_role=d["role"], doc_name=d["name"])
                if key_block:
                    key_numbers_blocks.append(key_block)

            # Persist results for other tabs / follow-ups
            st.session_state["material_totals_by_doc"] = material_results
            totals_block = "\n\n".join(totals_blocks) if totals_blocks else ""
            st.session_state["material_totals_block"] = totals_block

            mini_samples_block = "\n\n".join([mr["mini_sample"] for mr in material_results]) if material_results else ""
            st.session_state["material_mini_samples_block"] = mini_samples_block

            # Optional: store these if you use them elsewhere
            st.session_state["room_totals_blocks"] = room_totals_blocks
            st.session_state["key_numbers_blocks"] = key_numbers_blocks


            # Build user content with extracted text
            user_content = f"""
[USER CONTEXT]

The user is a homeowner trying to understand one or more estimates for home repair or reconstruction.

"""
            
            if extra_notes and extra_notes.strip():
                user_content += f"""
USER'S NOTES OR QUESTIONS (address these explicitly):
{extra_notes.strip()}

"""
            
            user_content += f"""
ATOMIC LINE ITEMS (small sample for context only — do NOT add these up):
{mini_samples_block if mini_samples_block.strip() else "(no atomic sample available)"}
"""
            if totals_block:
                user_content += f"""

{totals_block}

CRITICAL RULE:
- Do NOT recompute, modify, or “double-check” these totals.
- Treat them as exact computed facts.
- In the "Summary by Material" section, list the computed totals exactly as dollars and cents. Do not estimate or approximate.

"""
                
            # ---- ROOM TOTALS BLOCK (assemble after per-doc loop) ----
            room_totals_block_all = "\n\n".join(room_totals_blocks).strip()
            st.session_state["room_totals_block"] = room_totals_block_all

            if room_totals_block_all:
                user_content += f"""

{room_totals_block_all}

CRITICAL RULE:
- These room totals were extracted from explicit "Totals: <Room>" lines in the estimate.
- Do NOT recompute, modify, or infer any room totals.
- Only mention room totals that appear in this block.
"""
            #---- SUMMARY NUMBERS BLOCK ----------------
            key_numbers_block_all = "\n\n".join(key_numbers_blocks).strip()
            st.session_state["key_numbers_block"] = key_numbers_block_all

            if key_numbers_block_all:
                user_content += f"""

{key_numbers_block_all}

CRITICAL RULE:
- These key numbers were extracted from explicitly labeled summary lines in the estimate.
- Do NOT recompute, modify, or infer any of these numbers.
- Only mention key numbers that appear in this block.
"""


            # st.text_area(
            #     "DEBUG: per-document material totals (structured)",
            #     str(st.session_state.get("material_totals_by_doc", [])),
            #     height=200,
            # )

            # st.text_area(
            #     "DEBUG: totals_block being injected",
            #     totals_block or "(EMPTY)",
            #     height=200,
            # )

            # st.text_area(
            #     "DEBUG: tail of user_content",
            #     user_content[-1500:],
            #     height=250,
            # )

            # # DEBUG 12/22
            # print("[DEBUG] FIRST PASS user_content chars:", len(user_content))
            # print("[DEBUG] all_extracted_text chars:", len(all_extracted_text))
            # print("[DEBUG] all_extracted_text included in first pass?", "EXTRACTED ESTIMATE TEXT" in user_content)

            # Call GPT with text (not PDF)
            set_step(3, "Putting together your explanation…")

            t0 = time.perf_counter()  # time debug
            system_prompt = build_estimate_system_prompt()
            english_answer = call_gpt(
                system_prompt=system_prompt,
                user_content=user_content,
                model = EXPLAIN_MODEL,
                temperature=0.4,
                max_output_tokens=1100,
            )

            t1 = time.perf_counter()  # time debug
            explain_time = t1 - t0    # time debug

            # Normalize unicode dashes
            english_answer = english_answer.replace("–", "-").replace("—", "-")

            # Sanitize markdown for Streamlit rendering
            english_answer = sanitize_for_streamlit_markdown(english_answer)


            translated_answer = translate_if_needed(
                english_answer, preferred_lang["code"]
            )

            set_step(4, "Done.")
            time.sleep(0.2)  # optional: lets users see “Done.” briefly
            progress_bar.empty()
            status_box.empty()


            # Store explanation for follow-ups
            st.session_state["estimate_explanation_en"] = english_answer
            st.session_state["estimate_translated"] = translated_answer
            st.session_state["estimate_extra_notes"] = extra_notes


            # =========================
            # DEBUG OUTPUT (AFTER RUN)
            # =========================
            # st.text_area(
            #     "DEBUG: timing breakdown",
            #     "\n".join([
            #         f"pdfplumber extraction: {pdf_time:.2f}s",
            #         f"atomic extraction: {atomic_time:.2f}s",
            #         f"bucketing LLM call: {bucket_time:.2f}s",
            #         f"explanation LLM call: {explain_time:.2f}s",
            #     ]),
            #     height=150,
            # )

            # optional normalization (keeps plain text, just improves delimiter reliability)
            st.session_state["estimate_explanation_en"] = (
                st.session_state["estimate_explanation_en"]
                .replace("\r\n", "\n")
            )


    # Display explanation (outside button block)
    explanation = st.session_state.get("estimate_explanation_en", "")

    if explanation.strip():
        # Explanation
        st.markdown("**Explanation**")
        st.write("")

        sections = split_by_bold_headings(explanation)

        if not sections:
            st.markdown(explanation)
        else:
            first = True
            for heading, body in sections:
                if not first:
                    st.write("")  # space between blocks
                first = False

                title = "Overview"
                if heading:
                    title = heading.strip()
                    if title.startswith("**") and title.endswith("**"):
                        title = title[2:-2].strip()

                st.markdown(f"**{title}**")

                body_clean = body.strip()
                if body_clean:
                    safe = html.escape(body_clean).replace("\n", "<br>")
                    st.markdown(f'<div class="section-body">{safe}</div>', unsafe_allow_html=True)


        # Spanish Translation (only if present)
        if st.session_state.get("estimate_translated"):
            st.markdown("### Spanish Translation")
            st.markdown(st.session_state["estimate_translated"])

        # Export buttons
        col1, col2 = st.columns(2, vertical_alignment="center")

        with col1:
            followups = st.session_state.get("estimate_followups", [])
            label = "Download PDF"
            if followups:
                label += f" (includes {len(followups)} follow-up{'s' if len(followups) > 1 else ''})"

            pdf_bytes = create_explanation_pdf(
                explanation,  # use the local variable
                "Estimate Explanation",
                followups=followups
            )
            st.download_button(
                label=label,
                data=pdf_bytes,
                file_name="estimate_explanation.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with col2:
            email_body = explanation
            followups = st.session_state.get("estimate_followups", [])
            if followups:
                email_body += "\n\n--- Follow-up Q&A ---\n\n"
                for i, f in enumerate(followups, 1):
                    email_body += f"Q{i}: {f['question']}\n\n{f['answer']}\n\n"

            mailto_link = f"mailto:?subject=My Estimate Explanation&body={urllib.parse.quote(email_body[:2000])}"
            if st.button("Email This", key="email_estimate_btn", use_container_width=True):
                st.markdown(
                    f"<meta http-equiv='refresh' content='0; url={mailto_link}'>",
                    unsafe_allow_html=True,
                )


    # Follow-up section
    if st.session_state.get("estimate_explanation_en"):
        st.markdown("---")
        st.markdown("#### Follow-up question about this explanation")

        follow_q = st.text_input(
            "Follow-up question",
            key="estimate_followup_input",
            placeholder="If you want more detail about something above, type your question here."
        )

        if st.button("Ask follow-up", key="estimate_followup_btn"):
            if not follow_q.strip():
                st.warning("Please type a question.")
            else:
                prev_expl = st.session_state.get("estimate_explanation_en", "")
                extra_prev = st.session_state.get("estimate_extra_notes", "")
                insurance_pdf_data = st.session_state.get("estimate_insurance_pdfs", [])
                contractor_pdf_data = st.session_state.get("estimate_contractor_pdfs", [])

                if not prev_expl.strip():
                    st.warning("Please run **Explain my estimate** first.")
                elif not insurance_pdf_data and not contractor_pdf_data:
                    st.warning(
                        "Your uploaded estimate PDFs aren't available anymore. "
                        "Please re-upload and run **Explain my estimate** again."
                    )
                else:
                    with st.spinner("Generating follow-up explanation..."):
                        follow_system = build_estimate_system_prompt() + """

You are answering a follow-up question about an estimate explanation you already provided.

CRITICAL INSTRUCTIONS:
- Do NOT regenerate or rewrite the entire explanation
- Do NOT repeat information already covered in the previous explanation
- ONLY provide additional detail, clarification, or specific information about what the user asked
- Keep your response focused and concise (2-4 paragraphs maximum)
- You have access to the original estimate text again, so you can reference specific line items, numbers, or details if the user asks about them
- If the topic was already covered in the original explanation, acknowledge that and provide deeper detail or specific examples
- Do NOT contradict your previous explanation unless you find a clear error when re-reading the documents

Your goal is to ADD to the conversation, not restart it.
""".strip()

                        follow_notes = f"""
PREVIOUS EXPLANATION (for context):
{prev_expl}

USER'S FOLLOW-UP QUESTION:
{follow_q}

ORIGINAL NOTES FROM USER:
{extra_prev or 'None provided'}
""".strip()

                        # Re-extract text for follow-up
                        from estimate_extract import extract_pdf_pages_text, join_page_packets
                        
                        all_text = ""
                        for pdf_data in insurance_pdf_data:
                            packets = extract_pdf_pages_text(pdf_data["bytes"])
                            all_text += f"\n\n=== INSURANCE: {pdf_data['name']} ===\n\n"
                            all_text += join_page_packets(packets)
                        
                        for pdf_data in contractor_pdf_data:
                            packets = extract_pdf_pages_text(pdf_data["bytes"])
                            all_text += f"\n\n=== CONTRACTOR: {pdf_data['name']} ===\n\n"
                            all_text += join_page_packets(packets)
                        
                        follow_user_content = f"""
{follow_notes}

EXTRACTED ESTIMATE TEXT:
{all_text}
"""
                        
                        # Inject computed totals again so follow-ups stay consistent
                        totals_block = st.session_state.get("material_totals_block", "")
                        if totals_block:
                            follow_user_content += f"""

{totals_block}

CRITICAL RULE:
- Do NOT recompute, modify, or “double-check” these totals.
- Treat them as exact computed facts.
"""

                        
                        follow_en = call_gpt(
                            system_prompt=follow_system,
                            user_content=follow_user_content,
                            model=EXPLAIN_MODEL,
                            temperature=0.3,
                            max_output_tokens=700,
                        )

                        # Normalize dashes
                        follow_en = follow_en.replace("–", "-").replace("—", "-")
                        follow_en = sanitize_for_streamlit_markdown(follow_en)
                        follow_es = translate_if_needed(follow_en, preferred_lang["code"])

                    # Store follow-up
                    st.session_state.setdefault("estimate_followups", [])
                    st.session_state["estimate_followups"].append({
                        "question": follow_q,
                        "answer": follow_en
                    })

                    # Display follow-up
                    st.markdown("##### Follow-up answer")
                    st.markdown(follow_en)
                    if follow_es:
                        st.markdown("##### Spanish Translation")
                        st.markdown(follow_es)

    else:
        st.markdown("---")
        st.caption("Run **Explain my estimate** first to enable follow-up questions.")

    # Disclaimers
    st.markdown("---")
    st.markdown(BASE_DISCLAIMER_EN)
    st.markdown(AGENT_A_DISCLAIMER_EN)

    if preferred_lang["code"] == "es":
        st.markdown(BASE_DISCLAIMER_ES)
        st.markdown(AGENT_A_DISCLAIMER_ES)


# ======================
# Mini-Agent B: Renovation Plan
# ======================

def build_renovation_system_prompt() -> str:
    return """
You are a friendly and personable assistant that explains typical sequences for home repair or renovation projects.

HARD RULES:
- You are NOT the user's contractor, engineer, or inspector.
- You must NOT say that the contractor's plan is wrong.
- If the user provides a sequence from their contractor, treat it as correct and primary.
  You may only explain it and suggest neutral questions they can ask.
- When you describe a sequence, use words like "often", "typically", or "in many projects".
  Always note that the user should follow their contractor's specific plan if it differs.

GENERAL SEQUENCING PRINCIPLES (apply to all projects):
- Construction generally proceeds from structure → mechanical/electrical → drywall and surfaces → flooring → trim → paint touch-ups → fixtures.
- Do NOT place a step before something that depends on it.
  (Example: do not paint or caulk trim before trim is installed; do not install trim before flooring.)
- Distinguish between early-stage painting (walls/ceiling after drywall) and final painting (trim and touch-ups after trim installation).
- Flooring, regardless of type, typically goes in before baseboards or shoe molding.
- If the scenario is ambiguous, choose the most widely used sequence and clearly note that individual contractors may vary.
- The homeowner may not list every step. If they mention major items (e.g., tile, carpet, drywall repair),
  you may explain commonly related steps (such as underlayment, grout, baseboard reinstallation, and paint touch-ups),
  but describe these as "typically" or "often" included rather than assuming they are definitely in scope.

GOALS:
1. Explain a clear, typical order of operations based on the user's inputs.
2. Describe what the homeowner may need to prepare or decide at different stages of the project.
3. Suggest polite, neutral questions the homeowner can ask their contractor to confirm details.

OUTPUT FORMAT (IMPORTANT):
- Use plain text paragraphs.
- Section headings MUST be bolded using **double asterisks**.
- Do NOT use Markdown headings (##, ###).
- Do NOT use bullet characters such as "-", "*", or "•".
- Do NOT format content as checklists.
- Use line breaks between sections for readability.
- Keep a calm, explanatory tone.
- End with a short reminder that this is general guidance and the contractor's plan should take precedence.

Write clearly and concisely.
""".strip()


def renovation_plan_tab(preferred_lang: Dict):
    st.markdown("""
    <div class="tab-description">
        See a typical sequence of work for your project and identify decisions 
        or preparations that may come up along the way.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### What areas involved in your project?")
    rooms = st.multiselect(
        "Select all areas that apply",
        [
            "Living room",
            "Kitchen",
            "Bathroom",
            "Bedroom",
            "Loft",
            "Laundry room",
            "Hallway",
            "Stairs",
            "Garage",
            "Exterior",
            "Other",
        ],
        default=[],
    )

    other_rooms = ""
    if "Other" in rooms:
        other_rooms = st.text_input("Describe other areas:")

    st.markdown("### What kind of work is involved? Don't worry if you're not sure about everything.")

    work_types = st.multiselect(
    "Select all kinds of work that apply",
    [
        "Water mitigation / drying",
        "Mold remediation",
        "Demolition (remove damaged materials)",

        "Subfloor repair",
        "Framing / drywall repair",
        "Insulation",

        "Tile installation",
        "Grout",
        "Floor leveling / underlayment",
        "LVP / laminate installation",
        "Carpet / pad",
        "Hardwood installation / refinishing",
        "Transitions / thresholds",

        "Drywall finishing / texture",
        "Painting (walls, ceilings, trim)",
        "Baseboards / trim",

        "Cabinets",
        "Countertops",
        "Backsplash tile",

        "Plumbing work (fixtures, lines, toilet reset)",
        "Electrical work (lights, outlets, switches)",

        "Door installation / trim",
        "Vanity installation",
        "Shower/tub area work",

        "Other",
    ],
    default=[],
)

    other_work = ""
    if "Other" in work_types:
        other_work = st.text_input("Describe other work needed:")

    contractor_sequence = st.text_area(
        "Has your contractor already told you an order of work? (Optional)",
        help="For example: 'Tile in laundry first, then baseboards, then carpet upstairs.'",
    )

    extra_notes = st.text_area(
        "Anything else we should know? (Optional)",
        help="For example: pets, tight schedule, or needing certain rooms done first.",
    )

    if st.button("Generate a typical reconstruction process"):
        if not rooms or not work_types:
            st.warning("Please add at least one room and one type of work so I can tailor the overview.")
            return
    
        with st.spinner("Putting together a typical sequence..."):

            estimate_docs = st.session_state.get("estimate_extracted_docs", [])
            estimate_text_block = ""

            if estimate_docs:
                estimate_text_block = (
                    "\n\nESTIMATE EXCERPT (FOR CONTEXT ONLY — DO NOT EXPAND SCOPE):\n"
                    + "\n\n".join(
                        [f"=== {d['role'].upper()} — {d['name']} ===\n{d['text']}" for d in estimate_docs]
                    )
                )

            MAX_ESTIMATE_CHARS = 4000
            if len(estimate_text_block) > MAX_ESTIMATE_CHARS:
                estimate_text_block = (
                    estimate_text_block[:MAX_ESTIMATE_CHARS]
                    + "\n\n[...estimate excerpt truncated...]\n"
                )

            # Deterministic keyword set from user selections
            room_terms = [r.strip().lower() for r in (rooms or []) if r and r.strip()]
            if other_rooms:
                room_terms += [w.strip().lower() for w in other_rooms.replace("\n", ",").split(",") if w.strip()]

            work_terms = [w.strip().lower() for w in (work_types or []) if w and w.strip()]
            if other_work:
                work_terms += [w.strip().lower() for w in other_work.replace("\n", ",").split(",") if w.strip()]

            # Filter lines that mention ANY room term OR ANY work term (broad on purpose for now)
            filtered_chunks = []
            for d in estimate_docs:
                text = d.get("text", "") or ""
                lines = text.splitlines()

                kept = []
                for line in lines:
                    l = line.lower()
                    if any(rt in l for rt in room_terms) or any(wt in l for wt in work_terms):
                        kept.append(line)

                if kept:
                    filtered_chunks.append(
                        f"=== {d['role'].upper()} — {d['name']} (FILTERED) ===\n" + "\n".join(kept)
                    )

            if filtered_chunks:
                estimate_text_block = (
                    "\n\nESTIMATE EXCERPT (FILTERED BY YOUR SELECTED ROOMS/WORK — CONTEXT ONLY):\n"
                    + "\n\n".join(filtered_chunks)
                )

            # Hard cap after filtering
            MAX_ESTIMATE_CHARS = 4000
            if len(estimate_text_block) > MAX_ESTIMATE_CHARS:
                estimate_text_block = (
                    estimate_text_block[:MAX_ESTIMATE_CHARS]
                    + "\n\n[...filtered estimate excerpt truncated...]\n"
                )

            print(
                f"[RENOVATION FILTER] rooms={room_terms} work={work_terms} | "
                f"estimate_text_chars={len(estimate_text_block)}"
            )


#==================================
# -----USER CONTENT for prompt---#
#===================================
            user_content = f"""
ROOMS INVOLVED:
{', '.join(rooms) if rooms else 'Not specified'}
Other rooms details: {other_rooms or 'None provided'}

WORK TYPES:
{', '.join(work_types) if work_types else 'Not specified'}
Other work details: {other_work or 'None provided'}

CONTRACTOR'S SEQUENCE (if any, treat as primary):
{contractor_sequence or 'None provided'}

EXTRA NOTES:
{extra_notes or 'None provided'}
""".strip()

            user_content = (user_content + estimate_text_block).strip()

            print(
                f"[RENOVATION PROMPT] "
                f"user_content chars={len(user_content)} | "
                f"estimate_docs={len(estimate_docs)} | "
                f"estimate_text_chars={len(estimate_text_block)}"
            )

            # -----end USER CONTENT-------#

            system_prompt = build_renovation_system_prompt()
            english_answer = call_gpt(system_prompt, user_content, model=EXPLAIN_MODEL, temperature=0.4, max_output_tokens=700)
            translated_answer = translate_if_needed(english_answer, preferred_lang["code"])

            # NEW: Store for follow-ups
            st.session_state["renovation_explanation_en"] = english_answer
            st.session_state["renovation_translated"] = translated_answer
            st.session_state["renovation_inputs"] = {
                "rooms": rooms,
                "other_rooms": other_rooms,
                "work_types": work_types,
                "other_work": other_work,
                "contractor_sequence": contractor_sequence,
                "extra_notes": extra_notes,
            }

    # MOVE display code HERE - outside button block

    estimate_docs = st.session_state.get("estimate_extracted_docs", [])
    has_estimate_text = bool(estimate_docs)

    print(f"[RENOVATION] has_estimate_text={has_estimate_text}, docs={len(estimate_docs)}")


    if "renovation_explanation_en" in st.session_state and st.session_state["renovation_explanation_en"]:
        st.markdown("### Typical plan")
        #st.markdown(st.session_state["renovation_explanation_en"])
        # ==============================
        # Renovation explanation display
        # ==============================

        renovation_text = st.session_state.get("renovation_explanation_en", "")

        if renovation_text.strip():
            sections = split_by_bold_headings(renovation_text)

            if not sections:
                # Fallback: render entire text inside styled container
                safe = html.escape(renovation_text).replace("\n", "<br>")
                st.markdown(f'<div class="section-body">{safe}</div>', unsafe_allow_html=True)
            else:
                first = True
                for heading, body in sections:
                    if not first:
                        st.write("")  # spacing between sections
                    first = False

                    title = "Overview"
                    if heading:
                        title = heading.strip()
                        if title.startswith("**") and title.endswith("**"):
                            title = title[2:-2].strip()

                    st.markdown(f"**{title}**")

                    body_clean = body.strip()
                    if body_clean:
                        safe = html.escape(body_clean).replace("\n", "<br>")
                        st.markdown(
                            f'<div class="section-body">{safe}</div>',
                            unsafe_allow_html=True
                        )

        # Spanish translation (if present)
        if st.session_state.get("renovation_translated"):
            st.write("")
            st.markdown("**Spanish Translation**")
            st.markdown(st.session_state["renovation_translated"])

        
        if st.session_state.get("renovation_translated"):
            st.markdown("### Spanish Translation")
            st.markdown(st.session_state["renovation_translated"])
        
        # Export buttons
        col1, col2 = st.columns(2, vertical_alignment="center")
        
        with col1:
            followups = st.session_state.get("renovation_followups", [])
            label = "Download PDF"
            if followups:
                label += f" (includes {len(followups)} follow-up{'s' if len(followups) > 1 else ''})"
            
            pdf_bytes = create_explanation_pdf(
                st.session_state["renovation_explanation_en"],
                "Renovation Plan",
                followups=followups
            )
            st.download_button(
                label=label,
                data=pdf_bytes,
                file_name="renovation_plan.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        with col2:
            email_body = st.session_state['renovation_explanation_en']
            followups = st.session_state.get("renovation_followups", [])
            if followups:
                email_body += "\n\n--- Follow-up Q&A ---\n\n"
                for i, f in enumerate(followups, 1):
                    email_body += f"Q{i}: {f['question']}\n\n{f['answer']}\n\n"
            
            mailto_link = f"mailto:?subject=My Renovation Plan&body={urllib.parse.quote(email_body[:2000])}"

            if st.button("Email This", key="email_reno_btn", use_container_width=True):
                st.markdown(
                    f"<meta http-equiv='refresh' content='0; url={mailto_link}'>",
                    unsafe_allow_html=True,
                )


    # Follow-up section (no expander needed!)
    if st.session_state.get("renovation_explanation_en"):
        st.markdown("---")
        st.markdown("#### Follow-up question about this plan")

        follow_q_reno = st.text_input(
            "Follow-up question",
            key="reno_followup_input",
            placeholder="If you want more detail about the sequence or timeline, type your question here."
        )

        if st.button("Ask follow-up", key="reno_followup_btn"):
            if not follow_q_reno:
                st.warning("Please type a question.")
            else:
                prev_expl = st.session_state.get("renovation_explanation_en", "")
                prev_inputs = st.session_state.get("renovation_inputs", {})

                if not prev_expl:
                    st.warning("Please generate a plan first.")
                else:
                    with st.spinner("Thinking about your follow-up question..."):
                        follow_system = build_renovation_system_prompt() + """

You are answering a follow-up question about a renovation plan you already provided.

CRITICAL INSTRUCTIONS:
- Do NOT regenerate or rewrite the entire plan
- Do NOT repeat information already covered in the previous plan
- ONLY provide additional detail, clarification, or new information specifically about what the user asked
- Keep your response focused and concise (2-4 paragraphs maximum)
- If the topic was already covered in the original plan, acknowledge that and provide deeper detail or different angles on that specific aspect

Your goal is to ADD to the conversation, not restart it.
""".strip()

                        follow_notes = f"""
PREVIOUS PLAN (for context):
{prev_expl}

ORIGINAL PROJECT DETAILS:
Rooms: {', '.join(prev_inputs.get('rooms', [])) or 'Not specified'}
Other rooms: {prev_inputs.get('other_rooms', '') or 'None'}
Work types: {', '.join(prev_inputs.get('work_types', [])) or 'Not specified'}
Other work: {prev_inputs.get('other_work', '') or 'None'}
Contractor sequence: {prev_inputs.get('contractor_sequence', '') or 'None provided'}
Extra notes: {prev_inputs.get('extra_notes', '') or 'None provided'}

USER'S FOLLOW-UP QUESTION:
{follow_q_reno}
""".strip()

                        follow_en = call_gpt(follow_system, follow_notes, model=EXPLAIN_MODEL, temperature=0.3, max_output_tokens=600)
                        follow_es = translate_if_needed(follow_en, preferred_lang["code"])

                    # Storage code - OUTSIDE spinner
                    if "renovation_followups" not in st.session_state:
                        st.session_state["renovation_followups"] = []

                    st.session_state["renovation_followups"].append({
                        "question": follow_q_reno,
                        "answer": follow_en
                    })

                    # Display (keep inside the "generated follow-up" path)
                    st.markdown("##### Follow-up answer")
                    st.markdown(follow_en)
                    if follow_es:
                        st.markdown("##### Spanish Translation")
                        st.markdown(follow_es)

    else:
        st.markdown("---")
        st.caption("Generate a plan first to enable follow-up questions.")


    # Full disclaimers at bottom
    st.markdown("---")

    # English block first
    st.markdown(BASE_DISCLAIMER_EN)
    st.markdown(AGENT_B_DISCLAIMER_EN)  # Or AGENT_B / AGENT_C depending on tab

    # Spanish block second (only if selected)
    if preferred_lang["code"] == "es":
        st.markdown(BASE_DISCLAIMER_ES)
        st.markdown(AGENT_B_DISCLAIMER_ES)




# ======================
# Mini-Agent C: Design Helper
# ======================

def build_design_system_prompt() -> str:
    return """
You are a general interior-design helper for homeowners selecting finishes and materials during repairs or remodeling.
You must base all suggestions ONLY on the materials the user selected.

ALLOWED MATERIAL CATEGORIES (examples, not exhaustive):
- Flooring (tile, carpet, LVP, hardwood)
- Paint colors
- Cabinets and cabinet colors
- Countertops (quartz, granite, laminate)
- Backsplash tile
- Hardware and fixtures
- Trim/baseboards
- Lighting
- Other user-specified materials

HARD RULES:
1. You are NOT a professional interior designer or contractor.
2. Treat any design recommendations from the user's contractor or designer as primary.
3. NEVER introduce materials the user did not choose.
4. Keep suggestions practical, neutral, and easy to understand.
5. Consider at least one alternative design philosophy so the user gets a balanced view.
6. Emphasize that real-world lighting and physical samples matter more than AI suggestions.

GOALS:
1. Use the room type, selected materials, wall color, adjacent finishes, style preferences, contrast preferences,
   and usage (kids/pets/traffic) to propose 2–3 clear and coherent design directions.
2. Discuss material-specific considerations relevant to ONLY the user-selected materials.
   For example:
   - If tile is selected: grout color, finish, pattern/layout, sealing.
   - If carpet is selected: pile/texture, padding, stain resistance, seam placement.
   - If cabinets are selected: undertones, door style, hardware finishes.
   - If paint is selected: undertones, natural/artificial light, sheen.
   - If countertops are selected: movement/veining, edge profile, sheen.
   - If multiple materials are selected: how they coordinate.
3. Give practical notes about durability, maintenance, and color matching.
4. Mention a few commonly overlooked decisions that may apply to the user's selected materials (e.g., tile layout, carpet padding, grout sealing, hardware finishes).
5. Suggest polite, neutral questions the user can ask their contractor or designer.

OUTPUT FORMAT (IMPORTANT):
- Use plain text paragraphs.
- Section headings MUST be wrapped in **double asterisks**.
   - If headings are not bolded, the output will be considered invalid
- Use the exact section headings listed below, in this order.
- Do NOT use Markdown headings (##, ###).
- Do NOT use bullet characters such as "-", "*", or "•".
- Do NOT format content as checklists.
- Use line breaks between sections for readability.

REQUIRED SECTION HEADINGS (use these exact headings):
**Overall Design Direction**
**Option 1**
**Option 2**
(Include **Option 3** only if truly helpful)
**Material-Specific Notes**
**Practical Considerations**
**Questions to Ask Your Contractor or Designer**
**Final Reminder**

FINAL REMINDER CONTENT:
End with a short reminder that this is general guidance only and that lighting/samples and the contractor/designer's guidance should take precedence.
""".strip()


def design_helper_tab(preferred_lang: Dict):

    st.markdown("""
    <div class="tab-description">
        Explore a few practical design directions based on your room, materials, 
        and preferences, with notes on coordination and durability.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Tell me about your project")

    # Room selection with unified placeholder
    room_options = [
        "Select...",
        "Living room",
        "Kitchen",
        "Bathroom",
        "Bedroom",
        "Loft",
        "Laundry room",
        "Hallway",
        "Stairs",
        "Garage",
        "Other",
    ]
    room_choice = st.selectbox("Which room is this for?", room_options, index=0)
    room = "" if room_choice == "Select..." else room_choice

    if room == "Other":
        room = st.text_input("Describe the room:", placeholder="Example: guest room, loft, etc.")


    # Style preference with unified placeholder
    style_options = [
        "Select...",
        "Not sure",
        "Modern / clean",
        "Traditional",
        "Farmhouse / rustic",
        "Transitional",
    ]
    style_choice = st.selectbox("Overall style you prefer", style_options, index=0)
    style_pref = "" if style_choice == "Select..." else style_choice

    # Contrast preference with unified placeholder
    contrast_options = [
        "Select...",
        "More contrast",
        "More blended / subtle",
        "Not sure",
    ]
    contrast_choice = st.selectbox(
        "Do you prefer more contrast or a more blended look?",
        contrast_options,
        index=0,
    )
    contrast_pref = "" if contrast_choice == "Select..." else contrast_choice

    # Materials being chosen – starts empty by default
    materials = st.multiselect(
        "Select materials (choose one or more)",
        [
            "Tile",
            "Carpet",
            "Laminate",
            "Hardwood",
            "LVP (luxury vinyl plank)",
            "Paint color",
            "Cabinets",
            "Countertops",
            "Backsplash",
            "Baseboards / trim",
            "Lighting",
            "Other",
        ],
        default=[],
    )
    other_materials = ""
    if "Other" in materials:
        other_materials = st.text_input("Describe other materials:")

    existing_finishes = st.text_input(
        "Colors of existing finishes, such as walls, floors, cabinets, etc. (Optional)",
        help=(
            "Example: 'Greek Villa walls, medium brown wood floor, white shaker cabinets,' "
            "or 'light gray tile, dark gray grout, black hardware.'"
        ),
    )

    # Traffic/use with unified placeholder
    traffic_options = [
        "Select...",
        "Adults only",
        "Kids",
        "Kids + pets",
        "High traffic (everyone walks here)",
    ]
    traffic_choice = st.selectbox(
        "Who uses this space? (Optional)",
        traffic_options,
        index=0,
    )
    traffic_info = "" if traffic_choice == "Select..." else traffic_choice

    contractor_design_notes = st.text_area(
        "Anything your contractor or designer already suggested? (Optional)",
        help="Example: 'Contractor suggested warm greige tile and slightly darker carpet.'",
    )

    extra_notes = st.text_area(
        "Anything else about your taste or worries? (Optional)",
        help="Example: 'Hate yellow undertones', 'Don't want to see every crumb', etc.",
    )

    photos = st.file_uploader(
        "Optional: upload photos of your current space or samples (tile, carpet, cabinets, etc.)",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
    )

    if photos:
        st.info(
            "In this version, the AI does not analyze the images directly, "
            "but you can still upload them for your own reference or to share with your contractor."
        )

    if st.button("Suggest some design directions"):
        # Basic validation: need at least a room and one material
        if not room or not materials or not style_pref or not contrast_pref:
            st.warning("Please select a room, at least one material, a style preference, and a contrast preference so I can provide some suggestions.")
            return

        with st.spinner("Thinking through some options..."):
            photo_names = [p.name for p in photos] if photos else []

            user_content = f"""
ROOM:
{room}

MATERIALS SELECTED:
{', '.join(materials)}
Other materials details: {other_materials or 'None provided'}

EXISTING FINISH COLORS / MATERIALS (WALLS, FLOORS, CABINETS, ETC.):
{existing_finishes or 'Not specified'}

STYLE PREFERENCE:
{style_pref or 'Not specified'}

CONTRAST PREFERENCE:
{contrast_pref or 'Not specified'}

TRAFFIC / USERS:
{traffic_info or 'Not specified'}

CONTRACTOR / DESIGNER SUGGESTIONS (treat as primary):
{contractor_design_notes or 'None provided'}

EXTRA NOTES:
{extra_notes or 'None provided'}

PHOTOS UPLOADED (names only; AI does not see the images in this version):
{', '.join(photo_names) if photo_names else 'None'}
""".strip()

            system_prompt = build_design_system_prompt()
            english_answer = call_gpt(system_prompt, user_content, model=EXPLAIN_MODEL, temperature=0.4, max_output_tokens=700)
            translated_answer = translate_if_needed(english_answer, preferred_lang["code"])

# NEW: Store for follow-ups
            st.session_state["design_explanation_en"] = english_answer
            st.session_state["design_translated"] = translated_answer  # ADD THIS LINE
            st.session_state["design_inputs"] = {
                "room": room,
                "materials": materials,
                "other_materials": other_materials,
                "existing_finishes": existing_finishes,
                "style_pref": style_pref,
                "contrast_pref": contrast_pref,
                "traffic_info": traffic_info,
                "contractor_design_notes": contractor_design_notes,
                "extra_notes": extra_notes,
            }

# MOVE display code HERE - outside button block
    if "design_explanation_en" in st.session_state and st.session_state["design_explanation_en"]:
        # ==============================
        # Design explanation display (outside button block)
        # ==============================

        design_text = st.session_state.get("design_explanation_en", "")

        if design_text.strip():
            st.markdown("**Suggestions**")
            st.write("")

            sections = split_by_bold_headings(design_text)

            if not sections:
                safe = html.escape(design_text).replace("\n", "<br>")
                st.markdown(f'<div class="section-body">{safe}</div>', unsafe_allow_html=True)
            else:
                first = True
                for heading, body in sections:
                    if not first:
                        st.write("")  # spacing between sections
                    first = False

                    title = "Overview"
                    if heading:
                        title = heading.strip()
                        if title.startswith("**") and title.endswith("**"):
                            title = title[2:-2].strip()

                    st.markdown(f"**{title}**")

                    body_clean = body.strip()
                    if body_clean:
                        safe = html.escape(body_clean).replace("\n", "<br>")
                        st.markdown(f'<div class="section-body">{safe}</div>', unsafe_allow_html=True)

        # Spanish translation (only if present)
        design_es = st.session_state.get("design_translated", "")
        if design_es:
            st.write("")
            st.markdown("**Spanish Translation**")
            safe_es = html.escape(design_es).replace("\n", "<br>")
            st.markdown(f'<div class="section-body">{safe_es}</div>', unsafe_allow_html=True)

        # Export buttons (only show if we have content)
        if design_text.strip() or design_es:
            col1, col2 = st.columns(2)


        # Export buttons
        col1, col2 = st.columns(2, vertical_alignment="center")
        
        with col1:
            followups = st.session_state.get("design_followups", [])
            label = "Download PDF"
            if followups:
                label += f" (includes {len(followups)} follow-up{'s' if len(followups) > 1 else ''})"
            
            pdf_bytes = create_explanation_pdf(
                st.session_state["design_explanation_en"],
                "Design Suggestions",
                followups=followups
            )
            st.download_button(
                label=label,
                data=pdf_bytes,
                file_name="design_suggestions.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        with col2:
            email_body = st.session_state['design_explanation_en']
            followups = st.session_state.get("design_followups", [])
            if followups:
                email_body += "\n\n--- Follow-up Q&A ---\n\n"
                for i, f in enumerate(followups, 1):
                    email_body += f"Q{i}: {f['question']}\n\n{f['answer']}\n\n"
            
            mailto_link = f"mailto:?subject=My Design Suggestions&body={urllib.parse.quote(email_body[:2000])}"

            if st.button("Email This", key="email_design_btn", use_container_width=True):
                st.markdown(
                    f"<meta http-equiv='refresh' content='0; url={mailto_link}'>",
                    unsafe_allow_html=True,
                )

    # Follow-up (ONLY show after initial suggestions exist)
    if st.session_state.get("design_explanation_en"):
        st.markdown("---")
        st.markdown("#### Follow-up question about these design suggestions")

        follow_q_design = st.text_input(
            "Follow-up question",
            key="design_followup_input",
            placeholder="If you want to explore specific color combinations or materials further, type your question here."
        )

        if st.button("Ask follow-up", key="design_followup_btn"):
            if not follow_q_design:
                st.warning("Please type a question.")
            else:
                prev_expl = st.session_state.get("design_explanation_en", "")
                prev_inputs = st.session_state.get("design_inputs", {})

                if not prev_expl:
                    st.warning("Please generate design suggestions first.")
                else:
                    with st.spinner("Thinking about your follow-up question..."):
                        follow_system = build_design_system_prompt() + """

You are answering a follow-up question about design suggestions you already provided.

CRITICAL INSTRUCTIONS:
- Do NOT regenerate or rewrite the entire suggestion
- Do NOT repeat information already covered in the previous suggestions
- ONLY provide additional detail, alternative options, or clarification specifically about what the user asked
- Keep your response focused and concise (2-4 paragraphs maximum)
- If the topic was already covered in the original suggestions, acknowledge that and provide deeper detail, specific examples, or different perspectives on that aspect

Your goal is to ADD to the conversation, not restart it.
""".strip()

                        follow_notes = f"""
PREVIOUS SUGGESTIONS (for context):
{prev_expl}

ORIGINAL DESIGN DETAILS:
Room: {prev_inputs.get('room', '') or 'Not specified'}
Materials: {', '.join(prev_inputs.get('materials', [])) or 'Not specified'}
Other materials: {prev_inputs.get('other_materials', '') or 'None'}
Existing finishes: {prev_inputs.get('existing_finishes', '') or 'Not specified'}
Style preference: {prev_inputs.get('style_pref', '') or 'Not specified'}
Contrast preference: {prev_inputs.get('contrast_pref', '') or 'Not specified'}
Traffic/users: {prev_inputs.get('traffic_info', '') or 'Not specified'}
Contractor suggestions: {prev_inputs.get('contractor_design_notes', '') or 'None provided'}
Extra notes: {prev_inputs.get('extra_notes', '') or 'None provided'}

USER'S FOLLOW-UP QUESTION:
{follow_q_design}
""".strip()

                        follow_en = call_gpt(follow_system, follow_notes, model=EXPLAIN_MODEL, temperature=0.3,max_output_tokens=600)
                        follow_es = translate_if_needed(follow_en, preferred_lang["code"])

                    # Storage code - OUTSIDE spinner
                    if "design_followups" not in st.session_state:
                        st.session_state["design_followups"] = []

                    st.session_state["design_followups"].append({
                        "question": follow_q_design,
                        "answer": follow_en
                    })

                    # Display (keep inside the "generated follow-up" path)
                    st.markdown("##### Follow-up answer")
                    st.markdown(follow_en)
                    if follow_es:
                        st.markdown("##### Spanish Translation")
                        st.markdown(follow_es)

    else:
        st.markdown("---")
        st.caption("Generate design suggestions first to enable follow-up questions.")

    # Full disclaimers at bottom
    st.markdown("---")

    # English block first
    st.markdown(BASE_DISCLAIMER_EN)
    st.markdown(AGENT_C_DISCLAIMER_EN)  # Or AGENT_B / AGENT_C depending on tab

    # Spanish block second (only if selected)
    if preferred_lang["code"] == "es":
        st.markdown(BASE_DISCLAIMER_ES)
        st.markdown(AGENT_C_DISCLAIMER_ES)




# ======================
# Main app
# ======================

def main():
    # Row 1: Header
    header_left, header_right = st.columns([4, 1], vertical_alignment="top")

    with header_left:
        st.markdown("""
            <div class="hero-subtitle">
                NextStep
            </div>
            <div class="hero-title">
                Understand insurance estimates.<br>
                Plan repairs.<br>
                Make design decisions.
            </div>
        """, unsafe_allow_html=True)

    with header_right:
        st.markdown("<div class='lang-label'>Preferred language</div>", unsafe_allow_html=True)
        preferred_lang = get_preferred_language()

    if "home_messages" not in st.session_state:
        st.session_state.home_messages = []  # list of dicts: {"role": "user"/"assistant", "content": "..."}
    if "home_turn_count" not in st.session_state:
        st.session_state.home_turn_count = 0  # number of user messages on Home

    # HARD break between header and tabs (this is important)
    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # Row 2: Tabs ONLY
    tabs = st.tabs([
        "HOME",
        "ESTIMATE EXPLAINER",
        "RENOVATION PLAN",
        "DESIGN HELPER",
    ])

# ---------- HOME TAB ----------
    with tabs[0]:

        st.markdown("## Welcome")

        if preferred_lang["code"] == "es":
            st.write(
                "Esta aplicación tiene 3 herramientas principales, cada una disponible en las pestañas de arriba. "
                "A continuación se presenta una breve descripción de cada herramienta. "
                "La información es de carácter general y debe confirmarse con tu contratista o ajustador de seguros."
            )
        else:
            st.write(
                "This app has 3 main tools, each found in the tabs above. "
                "Here's a short description of each tool. "
                "The information provided is general guidance and should be confirmed with your contractor or insurance adjuster."
            )

        st.markdown("""

1. **Estimate Explainer**  
   Upload your insurance estimate (and optionally your contractor's estimate) to see
   a clear, easy-to-understand explanation plus suggested questions to ask.

2. **Renovation Plan**  
   Describe which rooms and types of work are involved, and get a typical order
   of steps plus a checklist of things you may need to decide or prepare.

3. **Design Helper**  
   Describe your wall colors, nearby finishes, and preferences to get a few
   possible directions for materials and colors.
""")
        
        st.markdown("## Not sure where to begin?")

        if preferred_lang["code"] == "es":
            st.write(
                "Describe lo que estás tratando de resolver y te indicaré el mejor lugar para comenzar."
            )
        else:
            st.write(
                "Describe what you’re dealing with, and I’ll point you to the best place to start."
            )

        # --- HOME assistant chat state ---
        if "home_messages" not in st.session_state:
            st.session_state.home_messages = []  # [{"role": "user"/"assistant", "content": str}]
        if "home_turn_count" not in st.session_state:
            st.session_state.home_turn_count = 0

        if st.session_state.home_messages:
            chat_box = st.container(border=True)

            with chat_box:
                # Render conversation so far
                for msg in st.session_state.home_messages:
                    if msg["role"] == "user":
                        st.markdown(
                            f"""
                            <div class="chat-row chat-user">
                            <span class="chat-label">Me:</span>
                            <span class="chat-text">{msg["content"]}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        # Match the rendering style used in other tabs (convert \n to <br>)
                        safe_content = html.escape(msg["content"]).replace("\n", "<br>")
                        st.markdown(
                            f"""
                            <div class="chat-row chat-assistant">
                            <span class="chat-label">You:</span>
                            <span class="chat-text">{safe_content}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )


        # Chat input (first question + follow-ups)
        placeholder = (
            "Describe en una frase qué estás tratando de resolver (y te diré por dónde empezar)…"
            if preferred_lang["code"] == "es"
            else "In one sentence, describe what you’re trying to figure out (and I’ll suggest where to start)…"
        )

        MAX_HOME_TURNS = 3

        user_text = ""

        # --- Chat input / turn limit ---
        if st.session_state.home_turn_count >= MAX_HOME_TURNS:
            if preferred_lang["code"] == "es":
                st.caption(
                    "Este chat en la página de inicio está limitado a 3 preguntas para mantenerlo rápido."
                )
            else:
                st.caption(
                    "This Home chat is limited to 3 questions to keep it quick."
                )
        else:
            user_text = st.chat_input(
                placeholder,
                disabled=False,
            )

        # --- Clear chat button (ONLY after chat has started) ---
        if st.session_state.home_messages:
            clear_col, _ = st.columns([1, 6])
            with clear_col:
                if st.button("Start over", type="secondary"):
                    st.session_state.home_messages = []
                    st.session_state.home_turn_count = 0
                    st.rerun()


        if user_text and user_text.strip():
            user_text = user_text.strip()
            st.session_state.home_messages.append({"role": "user", "content": user_text})
            st.session_state.home_turn_count += 1

            with st.spinner("Thinking..."):
                system_prompt = build_home_assistant_system_prompt()

                # Build a compact conversation transcript for context
                convo_lines = []
                for m in st.session_state.home_messages:
                    role = "User" if m["role"] == "user" else "Assistant"
                    convo_lines.append(f"{role}: {m['content']}")

                convo_text = "\n".join(convo_lines[-8:])  # small cap (plenty for 3 turns)

                user_content = f"""
            You are chatting on the Home page of the app.

            CONVERSATION SO FAR:
            {convo_text}

            Now respond as the Home assistant. Remember: suggest ONE best starting tool.
            """.strip()

                assistant_en = call_gpt(
                    system_prompt=system_prompt,
                    user_content=user_content,
                    model=BUCKET_MODEL,          # cheap + fast is fine for orientation
                    temperature=0.4,
                    max_output_tokens=320,
                ).strip()

                assistant_text = assistant_en
                if preferred_lang["code"] == "es":
                    assistant_es = translate_if_needed(assistant_en, "es")
                    if assistant_es:
                        assistant_text = assistant_es.strip()

                # Normalize line endings
                text = assistant_text.strip().replace("\r\n", "\n").replace("\r", "\n")

                # Collapse any runs of blank lines down to a single blank line
                text = re.sub(r"\n\n+", "\n\n", text)

                # Treat each remaining newline as a paragraph break (1 blank line)
                lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
                assistant_text = "\n\n".join(lines)

            st.session_state.home_messages.append({"role": "assistant", "content": assistant_text})
            st.rerun()




        # FOOTER - add here, at the end of HOME tab content
        st.markdown("<hr style='margin-top: 3rem; margin-bottom: 2rem; border-color: #E2E8F0;'>", unsafe_allow_html=True)
        
        footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
        with footer_col2:
            st.markdown("""
            <div style='text-align: center;'>
                <div style='font-size: 0.85rem; color: #64748B; margin-top: 1.5em;'>
                        Built by ElseFrame © 2026
                </div>
            </div>
            """.format(base64.b64encode(open("elseframe2.png", "rb").read()).decode()), unsafe_allow_html=True)

    # ---------- OTHER TABS ----------
    with tabs[1]:
        estimate_explainer_tab(preferred_lang)

    with tabs[2]:
        renovation_plan_tab(preferred_lang)

    with tabs[3]:
        design_helper_tab(preferred_lang)


if __name__ == "__main__":
    main()
