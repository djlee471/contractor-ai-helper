import os
from typing import Optional, Dict, List

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv   # for local .env support
import base64

# for exporting pdfs
from fpdf import FPDF
import urllib.parse



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

# Hide Streamlit's automatic "Press Enter to..." hints under text inputs
st.markdown("""
<style>
/* Hide the helper text that appears below text_input widgets */
[data-testid="stTextInput"] div[data-testid="stCaptionContainer"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)


# Hide the sidebar collapse/expand button (and its stray text)
st.markdown(
    """
    <style>
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Reduce size of white space at top of page + Force white background + Set width

st.markdown("""
<style>
/* Remove Streamlit's default top banner spacing */
[data-testid="stAppViewContainer"] {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}

section.main > div {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}

/* Force pure white backgrounds */
html, body, [data-testid="stAppViewContainer"], .block-container {
    background-color: #FFFFFF !important;
}

/* Control content container - all properties in one place */
.block-container {
    padding-top: 3rem !important;  /* Desktop - comfortable breathing room */    max-width: 1100px;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
}
            
/* Tighter spacing ONLY on mobile */
@media (max-width: 768px) {
    .block-container {
        padding-top: 2rem !important;  /* Mobile - slightly tighter */        
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
}

            
</style>
""", unsafe_allow_html=True)


# ======================
# Hide Streamlit Top-Right Menu + Footer + Header
# ======================
st.markdown("""
<style>
/* Hide the header toolbar area (cloud only) - multiple selectors */
header[data-testid="stHeader"],
section[data-testid="stHeader"],
div[data-testid="stHeader"],
.stApp > header {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Hide the top-right hamburger menu */
#MainMenu {
    visibility: hidden !important;
    display: none !important;
}

/* Hide the "Made with Streamlit" footer */
footer {
    visibility: hidden !important;
    display: none !important;
}

/* Force app to start at top */
.stApp {
    margin-top: 0 !important;
    padding-top: 0 !important;
}
</style>
""", unsafe_allow_html=True)


# ==================
# FONTS and colors
# ==================

st.markdown("""
<style>
/* Load Inter (UI/body) + Sora (app title) */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@500;600;700&display=swap');

/* Apply Inter to most UI text */
html, body, div, span, input, textarea, button, select, label, p, li, ul, ol, [class], * {
    font-family: "Inter", sans-serif !important;
}

/* Optional: slightly improve default text rendering */
html, body {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* Keep headings neutral so the UI feels more “studio” than “dashboard” */
h2, h3 {
    color: #0F172A !important;
}

/* Keep your info box styling (optional: we can purple-ize later) */
[data-testid="stAlert"] {
    background-color: #E0F2FE !important;
    border-color: #60A5FA !important;
    color: #0F172A !important;
}
</style>
""", unsafe_allow_html=True)



#=================
## TITLE FONT
#=================

st.markdown("""
<style>
.custom-app-title {
    font-family: 'Inter', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 385 !important;
    margin: 0 0 0.25rem 0;
    padding: 0;
    line-height: 1.1;
    letter-spacing: -0.02em;
    color: #0F172A;
}
</style>
""", unsafe_allow_html=True)


#=========================================
# Formating headings - getting rid of bold
#=========================================

st.markdown("""
<style>
/* Section headings: larger, not bold */
h2 {
    font-weight: 400 !important;     /* regular */
    font-size: 1.6rem !important;    /* larger for separation */
    margin-top: 2.75rem !important;
    margin-bottom: 0.75rem !important;
    letter-spacing: -0.015em;
    color: #0F172A;
}

/* Subsection headings */
h3 {
    font-weight: 400 !important;
    font-size: 1.2rem !important;
    margin-top: 1.75rem !important;
    margin-bottom: 0.5rem !important;
    letter-spacing: -0.01em;
    color: #0F172A;
}
</style>
""", unsafe_allow_html=True)

#==========================
## TAB DESCRIPTION WHITESPACE AND FONT SIZE
#===========================
st.markdown("""
<style>
/* Custom description styling - larger since no title */
.tab-description {
    margin-top: 1.5rem !important;  /* Force space above */
    margin-bottom: 2rem !important;
    font-size: 1rem !important;
    color: #475569 !important;
    line-height: 1.7 !important;
}
</style>
""", unsafe_allow_html=True)

#======================
# NUCLEAR OPTION FOR TOP WHITE SPACE AND OTHER ATTEMPTS
#============================

# After your existing whitespace CSS, add just this:
st.markdown("""
<style>
/* Fine-tune: remove any gap between app container and first element */
div[data-testid="stVerticalBlock"] {
    gap: 0rem !important;
}

div[data-testid="stVerticalBlock"] > div:first-child {
    padding-top: 0 !important;
}
</style>
""", unsafe_allow_html=True)

#======================
# ADD BACK SELECTIVE SPACING
#============================

st.markdown("""
<style>
/* Add breathing room between major UI elements */

/* Space between form elements */
[data-testid="stTextInput"],
[data-testid="stTextArea"],
[data-testid="stSelectbox"],
[data-testid="stMultiSelect"] {
    margin-bottom: 1.25rem !important;
}

/* Space between buttons and surrounding content */
[data-testid="stButton"] {
    margin-top: 1rem !important;
    margin-bottom: 1rem !important;
}

/* Space around info/warning boxes */
[data-testid="stAlert"] {
    margin-top: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}

/* Extra space around horizontal rules */
hr {
    margin-top: 2rem !important;
    margin-bottom: 2rem !important;
}

/* Space around file uploader specifically */
[data-testid="stFileUploader"] {
    margin-top: 0.5rem !important;
    margin-bottom: 1.5rem !important;
}

/* Space only for markdown INSIDE tabs, not at top */
.stTabs [data-testid="stMarkdownContainer"] {
    margin-bottom: 0.75rem !important;
}
</style>
""", unsafe_allow_html=True)

#=========================
# HOVER EFFECT
#========================

st.markdown("""
<style>
/* Subtle hover effect on form inputs */
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
</style>
""", unsafe_allow_html=True)

#============================================
# SHADE THE ACTION (GENERATE RESPONSE) BUTTONS
#============================================

st.markdown("""
<style>
/* Style action buttons with subtle background */
button[kind="primary"],
button[kind="secondary"] {
    background-color: #F1F5F9 !important;
    border: 1px solid #E2E8F0 !important;
    transition: all 0.2s ease;
}

button[kind="primary"]:hover,
button[kind="secondary"]:hover {
    background-color: #E2E8F0 !important;
    border-color: #CBD5E1 !important;
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
        "",
        language_labels,
        index=default_index,
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

def call_gpt(system_prompt: str, user_content: str,
             max_output_tokens: int = 800,
             temperature: float = 0.4) -> str:
    """
    Call the OpenAI Responses API with:
    - system_prompt as `instructions`
    - user_content as `input` (string)

    Uses a moderately small max_output_tokens to help stay within budget.
    """
    response = client.responses.create(
        model="gpt-4.1-mini",  # you can bump up if you want more power
        instructions=system_prompt,
        input=user_content,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        store=False,  # do not store conversation server-side
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
    clean_content = content.replace('###', '').replace('##', '').replace('**', '').replace('*', '')
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
# ======================
# Mini-Agent A: Estimate Explainer
# ======================

def build_estimate_system_prompt() -> str:
    return """
You are an assistant that explains home insurance and construction estimates
for homeowners in simple, friendly English.

DOCUMENT READING:
- You will receive raw text from an insurance estimate and (optionally) a contractor estimate.
- The text may be messy or lack table formatting. You MUST still try to read it and extract useful information.
- Look for, and when helpful refer to:
  - Line item descriptions
  - Quantities (e.g. SF, LF, EA)
  - Unit prices (e.g. $/sq ft)
  - Line totals
  - Subtotals, taxes, depreciation
  - Overhead & profit (O&P)
  - Deductible and net payment amounts
- ONLY say that the text is unreadable if it is truly empty or clearly not an estimate at all.
- Do NOT say things like "the text you provided is not in a readable format" if any real text is present. In that case, always do your best to extract key numbers, even if formatting is imperfect.

GENERAL BEHAVIOR:
- Explain what the estimate is doing in plain English, grouped by room/area when possible.
- Identify key decisions the homeowner needs to make (materials, areas, scope choices).
- When the user asks about price points, allowances, or overages, you may:
  - Point out what unit prices or allowances the estimate appears to use for materials like tile, carpet, baseboards, etc.
  - Explain in plain language how choosing more expensive materials could create out-of-pocket costs.
  - Suggest specific questions they can ask their adjuster or contractor about these numbers.

GENERAL MARKET RANGES:
- You may also provide very general, approximate price ranges for common materials
  (for example, basic vs mid-grade carpet or tile), to help the user understand
  how their estimate compares to typical ranges.
- When you do this:
  - Make it clear these are broad, approximate ranges, not a quote for their project.
  - Keep the ranges conservative and generic, not tied to a specific city.
  - Clearly separate "numbers from your estimate" from "typical market ranges".

HARD RULES:
- You are NOT a lawyer, insurance adjuster, or contractor.
- Treat any statements from the insurance company, policy documents,
  or contractor as authoritative.
- NEVER say that an estimate is wrong, unfair, or incomplete.
- NEVER say what the insurance company "should" cover or "should" pay.
- You may ONLY suggest neutral questions the user can ask their adjuster
  or contractor, such as:
  - "You may want to ask your adjuster whether..."
  - "You can confirm with your contractor if..."
- If the user uploads both an insurance estimate and a contractor estimate:
  - You MAY point out clear structural differences (e.g., one includes paint and the other does not),
    but ALWAYS frame them as questions to ask:
    - "Your insurance estimate includes X but your contractor's estimate also includes Y.
       You may want to ask which parts you pay out of pocket."
  - NEVER say that insurance 'should' pay for anything.

PRICE AND ALLOWANCE QUESTIONS:
- When the user asks what price point they should shop at (for tile, carpet, etc.):
  1) First, look for any relevant numbers in the estimate (unit prices, allowances).
     - Explain in plain language what those numbers mean and how they relate to
       the user's choices (for example, "This estimate appears to use about $3.20/sq ft
       for carpet materials and about $4.50/sq ft for tile materials.").
  2) Second, if helpful, provide broad, typical market ranges for those materials
     (for example, basic vs mid-range materials).
  3) Emphasize that:
     - These are general ranges, not a quote.
     - Their adjuster and contractor can give exact allowances and pricing for their project.
  4) Do NOT judge whether the estimate is "too high" or "too low."
  5) Encourage the user to confirm with their adjuster or contractor:
     - "You may want to ask, 'What is my material allowance per square foot for tile and carpet,
        and how are any overages calculated?'"

GOALS:
1. Explain major sections of the estimate in plain English, grouped by room/area when possible.
2. Identify decisions the homeowner needs to make (materials, rooms/areas, scope choices).
3. Read and use specific numbers from the estimate to help the user understand
   approximate price levels and how overages might occur.
4. When useful, give separate, clearly-labeled general market ranges for common materials
   so the user has context.
5. Suggest polite, neutral follow-up questions for their adjuster and contractor.
6. Remind the user that their insurance company and contractor have the final say.

OUTPUT FORMAT (English):
- Short intro
- "Summary by Area"
- "Summary by material / task type" (if helpful)
- "Decisions You May Need to Make"
- A section called "Key Numbers From Your Estimate" where you list important totals and unit prices you found (even if incomplete).
- If useful, a brief section called "Typical Market Ranges" where you give general ranges for comparable materials.
- "Questions to Ask Your Adjuster"
- "Questions to Ask Your Contractor"
- End with a short reminder that this is general information only.
""".strip()

def estimate_explainer_tab(preferred_lang: Dict):

    st.markdown("""
    <div class="tab-description">
        Understand what's included in your insurance and contractor estimates, 
        what key numbers mean, and which questions may be worth asking.
    </div>
    """, unsafe_allow_html=True)


    st.markdown("### Upload your insurance estimate")
    insurance_files = st.file_uploader(
        "Insurance estimate (PDF preferred)",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="ins_files",
    )

    st.markdown("### Optional: upload your contractor's estimate")
    contractor_files = st.file_uploader(
        "Contractor estimate (PDF preferred)",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="con_files",
    )

    extra_notes = st.text_area(
        "Anything your adjuster or contractor already explained that we should treat as correct? (Optional)",
        help="For example: 'Insurance will only replace the bedroom carpet, not the hallway.'",
    )

    if st.button("Explain my estimate"):
        if not insurance_files:
            st.warning("Please upload at least your insurance estimate (PDF).")
            return

        with st.spinner("Reading your estimate PDFs and preparing an explanation..."):
            # STORE PDFs as bytes for follow-ups
            st.session_state["estimate_insurance_pdfs"] = [
                {"name": f.name, "type": f.type, "bytes": f.getvalue()} 
                for f in insurance_files
            ]
            
            if contractor_files:
                st.session_state["estimate_contractor_pdfs"] = [
                    {"name": f.name, "type": f.type, "bytes": f.getvalue()} 
                    for f in contractor_files
                ]
            else:
                st.session_state["estimate_contractor_pdfs"] = []
            
            system_prompt = build_estimate_system_prompt()
            english_answer = call_gpt_estimate_with_pdfs(
                system_prompt=system_prompt,
                insurance_files=insurance_files,
                contractor_files=contractor_files or [],
                extra_notes=extra_notes or "",
                max_output_tokens=1100,
            )
            translated_answer = translate_if_needed(
                english_answer, preferred_lang["code"]
            )

            # Store explanation for follow-ups
            st.session_state["estimate_explanation_en"] = english_answer
            st.session_state["estimate_translated"] = translated_answer  # ADD THIS
            st.session_state["estimate_extra_notes"] = extra_notes

    # MOVE display code HERE - outside button block
    if "estimate_explanation_en" in st.session_state and st.session_state["estimate_explanation_en"]:
        st.markdown("### Explanation")
        st.markdown(st.session_state["estimate_explanation_en"])

        if st.session_state.get("estimate_translated"):
            st.markdown("### Spanish Translation")
            st.markdown(st.session_state["estimate_translated"])

        # Export buttons - indented inside the if block
        col1, col2 = st.columns(2)
        
        with col1:
            followups = st.session_state.get("estimate_followups", [])
            label = "Download PDF"
            if followups:
                label += f" (includes {len(followups)} follow-up{'s' if len(followups) > 1 else ''})"
            
            pdf_bytes = create_explanation_pdf(
                st.session_state["estimate_explanation_en"],
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
            email_body = st.session_state['estimate_explanation_en']
            followups = st.session_state.get("estimate_followups", [])
            if followups:
                email_body += "\n\n--- Follow-up Q&A ---\n\n"
                for i, f in enumerate(followups, 1):
                    email_body += f"Q{i}: {f['question']}\n\n{f['answer']}\n\n"
            
            mailto_link = f"mailto:?subject=My Estimate Explanation&body={urllib.parse.quote(email_body[:2000])}"
            st.markdown(f'''
                <a href="{mailto_link}" target="_blank" style="text-decoration: none;">
                    <button style="
                        width: 100%;
                        padding: 0.5rem 1rem;
                        background-color: #F1F5F9;
                        border: 1px solid #E2E8F0;
                        border-radius: 0.5rem;
                        cursor: pointer;
                        font-size: 0.875rem;
                        font-weight: 400;
                    ">Email This</button>
                </a>
            ''', unsafe_allow_html=True)

    # Follow-up
    st.markdown("---")
    st.markdown("#### Follow-up question about this explanation")
        
    follow_q = st.text_input(
        "Follow-up question",
        placeholder="If you want more detail about something above, type your question here."
    )
    
    if st.button("Ask follow-up"):
        if not follow_q:
            st.warning("Please type a question.")
        else:
            prev_expl = st.session_state.get("estimate_explanation_en", "")
            extra_prev = st.session_state.get("estimate_extra_notes", "")
            
            # RETRIEVE stored PDFs
            insurance_pdf_data = st.session_state.get("estimate_insurance_pdfs", [])
            contractor_pdf_data = st.session_state.get("estimate_contractor_pdfs", [])

            if not prev_expl and not insurance_pdf_data:
                st.warning("Please run an explanation first.")
            else:
                with st.spinner("Generating follow-up explanation..."):
                    follow_system = build_estimate_system_prompt() + """

You are answering a follow-up question about an estimate explanation you already provided.

CRITICAL INSTRUCTIONS:
- Do NOT regenerate or rewrite the entire explanation
- Do NOT repeat information already covered in the previous explanation
- ONLY provide additional detail, clarification, or specific information about what the user asked
- Keep your response focused and concise (2-4 paragraphs maximum)
- You have access to the original estimate PDFs again, so you can reference specific line items, numbers, or details if the user asks about them
- If the topic was already covered in the original explanation, acknowledge that and provide deeper detail or specific examples
- Do NOT contradict your previous explanation unless you find a clear error when re-reading the documents

Your goal is to ADD to the conversation, not restart it.
""".strip()

                    # Build follow-up notes including previous explanation
                    follow_notes = f"""
PREVIOUS EXPLANATION (for context):
{prev_expl}

USER'S FOLLOW-UP QUESTION:
{follow_q}

ORIGINAL NOTES FROM USER:
{extra_prev or 'None provided'}
""".strip()

                    # RECONSTRUCT file-like objects from stored bytes
                    from io import BytesIO
                    
                    insurance_files_reconstructed = []
                    for pdf_data in insurance_pdf_data:
                        file_obj = BytesIO(pdf_data["bytes"])
                        file_obj.name = pdf_data["name"]
                        file_obj.type = pdf_data["type"]
                        insurance_files_reconstructed.append(file_obj)
                    
                    contractor_files_reconstructed = []
                    for pdf_data in contractor_pdf_data:
                        file_obj = BytesIO(pdf_data["bytes"])
                        file_obj.name = pdf_data["name"]
                        file_obj.type = pdf_data["type"]
                        contractor_files_reconstructed.append(file_obj)
                    
                    # CALL WITH PDFs (not just text)
                    follow_en = call_gpt_estimate_with_pdfs(
                        system_prompt=follow_system,
                        insurance_files=insurance_files_reconstructed,
                        contractor_files=contractor_files_reconstructed,
                        extra_notes=follow_notes,
                        max_output_tokens=700,
                    )
                    follow_es = translate_if_needed(
                        follow_en, preferred_lang["code"]
                    )

                # Storage code - OUTSIDE spinner
                if "estimate_followups" not in st.session_state:
                    st.session_state["estimate_followups"] = []
                
                st.session_state["estimate_followups"].append({
                    "question": follow_q,
                    "answer": follow_en
                })

            # Display - OUTSIDE spinner, OUTSIDE else, but INSIDE the button block (3 indents)
            st.markdown("##### Follow-up answer")
            st.markdown(follow_en)
            if follow_es:
                st.markdown("##### Spanish Translation")
                st.markdown(follow_es)

    # Full disclaimers at bottom
    st.markdown("---")

    # English block first
    st.markdown(BASE_DISCLAIMER_EN)
    st.markdown(AGENT_A_DISCLAIMER_EN)  # Or AGENT_B / AGENT_C depending on tab

    # Spanish block second (only if selected)
    if preferred_lang["code"] == "es":
        st.markdown(BASE_DISCLAIMER_ES)
        st.markdown(AGENT_A_DISCLAIMER_ES)



# ======================
# Mini-Agent B: Renovation Plan
# ======================

def build_renovation_system_prompt() -> str:
    return """
You are an assistant that explains typical sequences for home repair projects,
especially after water damage (e.g., laundry room leaks, bedroom carpet damage).

HARD RULES:
- You are NOT the user's contractor, engineer, or inspector.
- You must NOT say that the contractor's plan is wrong.
- If the user provides a sequence from their contractor, treat it as correct and primary.
  You may only explain it and suggest neutral questions they can ask.
- When you describe a sequence, use words like "often", "typically", or "in many projects".
  Always add that the user should follow their contractor's specific plan if it differs.

GENERAL SEQUENCING PRINCIPLES (apply to all projects):
- Construction generally proceeds from structure → mechanical/electrical → drywall and surfaces → flooring → trim → paint touch-ups → fixtures.
- Do NOT place a step before something that depends on it. 
  (Example: do not paint or caulk trim before trim is installed; do not install trim before flooring.)
- Distinguish between early-stage painting (walls/ceiling after drywall) and final painting (trim and touch-ups after trim installation).
- Flooring, regardless of type, typically goes in before baseboards or shoe molding.
- If the user scenario is ambiguous, choose the most widely used sequence and clearly note that individual contractors may vary.
- The homeowner may not list every step. If they mention major items (e.g., tile, carpet, drywall repair),
  you may include standard related steps (such as underlayment, grout, baseboard reinstallation, and paint touch-ups),
  but describe these as "typically" or "often" included rather than assuming they are definitely in the contractor's scope.

GOALS:
1. Suggest a clear, typical order of operations based on the user inputs
   (demo, subfloor repair, tile, grout, baseboards, paint, carpet, cabinets, countertops, etc.).
2. Provide a short checklist of what the homeowner may need to prepare or decide before each step.
3. Suggest polite questions they can ask their contractor to confirm details.

OUTPUT FORMAT (English):
- "Typical Sequence for Your Project"
- "What You May Need to Prepare"
- "Questions to Ask Your Contractor"
- Short reminder at the end that this is general guidance only.

""".strip()


def renovation_plan_tab(preferred_lang: Dict):
    st.markdown("""
    <div class="tab-description">
        See a typical sequence of work for your project and identify decisions 
        or preparations that may come up along the way.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Areas involved")
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

    st.markdown("### Kinds of work")

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
        with st.spinner("Putting together a typical sequence..."):
            # -----USER CONTENT for prompt---#
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
            # -----end USER CONTENT-------#

            system_prompt = build_renovation_system_prompt()
            english_answer = call_gpt(system_prompt, user_content, max_output_tokens=700)
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
    if "renovation_explanation_en" in st.session_state and st.session_state["renovation_explanation_en"]:
        st.markdown("### Typical plan")
        st.markdown(st.session_state["renovation_explanation_en"])
        
        if st.session_state.get("renovation_translated"):
            st.markdown("### Spanish Translation")
            st.markdown(st.session_state["renovation_translated"])
        
        # Export buttons
        col1, col2 = st.columns(2)
        
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
            st.markdown(f'''
                <a href="{mailto_link}" target="_blank" style="text-decoration: none;">
                    <button style="
                        width: 100%;
                        padding: 0.5rem 1rem;
                        background-color: #F1F5F9;
                        border: 1px solid #E2E8F0;
                        border-radius: 0.5rem;
                        cursor: pointer;
                        font-size: 0.875rem;
                        font-weight: 400;
                    ">Email This</button>
                </a>
            ''', unsafe_allow_html=True)
    # Follow-up section (no expander needed!)
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

                    follow_en = call_gpt(follow_system, follow_notes, max_output_tokens=600)
                    follow_es = translate_if_needed(follow_en, preferred_lang["code"])

                # Storage code - OUTSIDE spinner
                if "renovation_followups" not in st.session_state:
                    st.session_state["renovation_followups"] = []
                
                st.session_state["renovation_followups"].append({
                    "question": follow_q_reno,
                    "answer": follow_en
                })

            # Display - OUTSIDE spinner, OUTSIDE else, INSIDE button block
            st.markdown("##### Follow-up answer")
            st.markdown(follow_en)
            if follow_es:
                st.markdown("##### Spanish Translation")
                st.markdown(follow_es)

    # Full disclaimers at bottom
    st.markdown("---")

    # English block first
    st.markdown(BASE_DISCLAIMER_EN)
    st.markdown(AGENT_A_DISCLAIMER_EN)  # Or AGENT_B / AGENT_C depending on tab

    # Spanish block second (only if selected)
    if preferred_lang["code"] == "es":
        st.markdown(BASE_DISCLAIMER_ES)
        st.markdown(AGENT_A_DISCLAIMER_ES)




# ======================
# Mini-Agent C: Design Helper
# ======================

def build_design_system_prompt() -> str:
    return """
You are a general interior-design helper for homeowners selecting finishes
and materials during repairs or remodeling.
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
5. Consider alternative design philosophies to ensure you give the user a balanced view.
6. Emphasize that real-world lighting and samples matter more than AI suggestions.

GOALS:
1. Use the room type, selected materials, wall color, adjacent finishes,
   style preferences, contrast preferences, and usage (kids/pets/traffic)
   to propose 2–3 clear and coherent "design directions."
2. Discuss material-specific considerations:
   - If tile is selected → grout color, finish, pattern.
   - If cabinets are selected → undertones, hardware finishes.
   - If paint is selected → undertones, natural/artificial light.
   - If countertops are selected → veining, movement, sheen.
   - If multiple materials are selected → how they coordinate.
3. Give practical notes about durability, maintenance, and color matching.
4. Also discuss additional factors and decisions the user may need to consider, such as tile layout, carpet padding, grout sealing, cabinet hardware styles, etc.
4. Suggest polite, neutral questions the user can ask their contractor or designer.

OUTPUT FORMAT (English):
- "Overall Design Direction"
- "Option 1"
- "Option 2"
- (Option 3 if helpful)
- "Material-Specific Notes"
- "Practical Considerations"
- "Questions to Ask Your Contractor or Designer"
- Short reminder that this is general guidance only.
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
        "Garage"
        "Other",
    ]
    room_choice = st.selectbox("Which room is this for?", room_options, index=0)
    room = "" if room_choice == "Select..." else room_choice

    if room == "Other":
        room = st.text_input("Describe the room:", placeholder="Example: guest room, loft, etc.")

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
        "Colors of existing finishes (walls, floors, cabinets, etc.)",
        help=(
            "Example: 'Greek Villa walls, medium brown wood floor, white shaker cabinets,' "
            "or 'light gray tile, dark gray grout, black hardware.'"
        ),
    )


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

    # Traffic/use with unified placeholder
    traffic_options = [
        "Select...",
        "Adults only",
        "Kids",
        "Kids + pets",
        "High traffic (everyone walks here)",
    ]
    traffic_choice = st.selectbox(
        "Who uses this space?",
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
        if not room or not materials:
            st.warning("Please select a room and at least one material before asking for suggestions.")
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
            english_answer = call_gpt(system_prompt, user_content, max_output_tokens=700)
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
        st.markdown("### Suggestions")
        st.markdown(st.session_state["design_explanation_en"])
        
        if st.session_state.get("design_translated"):
            st.markdown("### Spanish Translation")
            st.markdown(st.session_state["design_translated"])
        
        # Export buttons
        col1, col2 = st.columns(2)
        
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
            st.markdown(f'''
                <a href="{mailto_link}" target="_blank" style="text-decoration: none;">
                    <button style="
                        width: 100%;
                        padding: 0.5rem 1rem;
                        background-color: #F1F5F9;
                        border: 1px solid #E2E8F0;
                        border-radius: 0.5rem;
                        cursor: pointer;
                        font-size: 0.875rem;
                        font-weight: 400;
                    ">Email This</button>
                </a>
            ''', unsafe_allow_html=True)

    # Follow-up section
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

                    follow_en = call_gpt(follow_system, follow_notes, max_output_tokens=600)
                    follow_es = translate_if_needed(follow_en, preferred_lang["code"])

                # Storage code - OUTSIDE spinner
                if "design_followups" not in st.session_state:
                    st.session_state["design_followups"] = []
                
                st.session_state["design_followups"].append({
                    "question": follow_q_design,
                    "answer": follow_en
                })

            # Display - OUTSIDE spinner, OUTSIDE else, INSIDE button block
            st.markdown("##### Follow-up answer")
            st.markdown(follow_en)
            if follow_es:
                st.markdown("##### Spanish Translation")
                st.markdown(follow_es)

    # Full disclaimers at bottom
    st.markdown("---")

    # English block first
    st.markdown(BASE_DISCLAIMER_EN)
    st.markdown(AGENT_A_DISCLAIMER_EN)  # Or AGENT_B / AGENT_C depending on tab

    # Spanish block second (only if selected)
    if preferred_lang["code"] == "es":
        st.markdown(BASE_DISCLAIMER_ES)
        st.markdown(AGENT_A_DISCLAIMER_ES)




# ======================
# Main app
# ======================

def main():
    # Header row: title on the left, language dropdown on the right
    header_left, header_right = st.columns([4, 1])

    with header_left:
        st.markdown("""
        <div class="custom-app-title">Home Repair Assistant</div>
        <div style="
            font-size: 0.95rem;
            color: #475569;
            margin-bottom: 1.25rem;
        ">
            Understand insurance estimates. Plan repairs. Make design decisions.
        </div>
        """, unsafe_allow_html=True)

    with header_right:
        st.markdown(
            "<div style='font-size: 13px; color: #666; margin-bottom: -6px;'>Preferred language for responses</div>",
            unsafe_allow_html=True,
        )
        preferred_lang = get_preferred_language()

    ## Add whitespace
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Tabs
    tabs = st.tabs(
        [
            "HOME",
            "ESTIMATE EXPLAINER",
            "RENOVATION PLAN",
            "DESIGN HELPER",
        ]
    )

# ---------- HOME TAB ----------
    with tabs[0]:
        # Strong HOME-PAGE Disclaimer (only in HOME tab)
        if preferred_lang["code"] == "es":
            st.markdown("""
            <div style="
                background-color: #F8FAFC;
                border-left: 3px solid #94A3B8;
                padding: 1rem 1.25rem;
                margin: 1.5rem 0 2rem 0;
                border-radius: 0.375rem;
            ">
            Esta herramienta en versión beta solo proporciona información educativa general 
            y puede estar incompleta o contener errores. No ofrece asesoría profesional en 
            seguros, asuntos legales, construcción, seguridad ni diseño. Todas las decisiones 
            finales deben basarse en la guía de su contratista con licencia, diseñador, 
            ajustador de seguros y en los códigos de construcción y documentos de póliza aplicables.
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div style="
                background-color: #F8FAFC;
                border-left: 3px solid #94A3B8;
                padding: 1rem 1.25rem;
                margin: 1.5rem 0 2rem 0;
                border-radius: 0.375rem;
            ">
            This beta tool provides general educational information only and may be incomplete or 
            incorrect. It does not provide professional insurance, legal, construction, safety, or 
            design advice. All final decisions must be based on the guidance of your licensed contractor, 
            designer, insurance adjuster, and applicable building codes and policy documents.
            </div>
            """, unsafe_allow_html=True)

        st.subheader("Welcome")
        st.write(
            "This app is designed to help you understand your home repair project at every stage. "
            "Use the tabs above to explore your insurance estimate, see how repairs typically unfold, "
            "and review design considerations—so you can stay informed and prepared."
        )

        st.markdown("""
### What you can do here

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

        # FOOTER - add here, at the end of HOME tab content
        st.markdown("<hr style='margin-top: 3rem; margin-bottom: 2rem; border-color: #E2E8F0;'>", unsafe_allow_html=True)
        
        footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
        with footer_col2:
            st.markdown("""
            <div style='text-align: center;'>
                <img src='data:image/png;base64,{}' width='180' style='margin-bottom: -2rem;'>
                <div style='font-size: 0.85rem; color: #64748B; margin-top: -0.5rem;'>
                    Built by Nareum AI Studio
                </div>
            </div>
            """.format(base64.b64encode(open("logo4_h.png", "rb").read()).decode()), unsafe_allow_html=True)

    # ---------- OTHER TABS ----------
    with tabs[1]:
        estimate_explainer_tab(preferred_lang)

    with tabs[2]:
        renovation_plan_tab(preferred_lang)

    with tabs[3]:
        design_helper_tab(preferred_lang)


if __name__ == "__main__":
    main()
