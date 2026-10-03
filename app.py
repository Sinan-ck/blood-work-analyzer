import html
import re

import streamlit as st
from langchain_ollama import ChatOllama


def md_to_html(text: str) -> str:
    """Turn the LLM's markdown (**bold**, - bullets, # headings) into HTML."""
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    out, in_list = [], False
    for line in text.split("\n"):
        s = line.strip()
        if s.startswith(("- ", "* ", "• ")):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{s[2:].strip()}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if s.startswith("#"):
            out.append(f"<p><strong>{s.lstrip('#').strip()}</strong></p>")
        elif s:
            out.append(f"<p>{s}</p>")
    if in_list:
        out.append("</ul>")
    return "".join(out)

st.set_page_config(page_title="Blood Work Analyzer", page_icon="🩸", layout="wide")

# ---------- Styling ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Page background: deep aurora gradient */
    .stApp {
        background:
            radial-gradient(900px 500px at 12% 8%, rgba(255, 94, 125, 0.22), transparent 60%),
            radial-gradient(800px 500px at 90% 20%, rgba(124, 92, 255, 0.25), transparent 60%),
            radial-gradient(900px 600px at 60% 100%, rgba(0, 214, 180, 0.16), transparent 60%),
            #0d0b1a;
        color: #f4f1ff;
    }

    header[data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 2.5rem; max-width: 1250px; }

    /* Title with gradient text */
    .app-title {
        font-size: 3.4rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.1;
        background: linear-gradient(90deg, #ff5e7d 0%, #b06cff 50%, #00d6b4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .app-sub { color: #a9a3c9; margin-bottom: 2rem; font-size: 1.02rem; }

    .section-head {
        font-size: 1.7rem;
        font-weight: 700;
        margin: 0.5rem 0 0.8rem 0;
        color: #ffffff;
    }

    /* Text area */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(176, 108, 255, 0.45) !important;
        border-radius: 16px !important;
        color: #f4f1ff !important;
        font-size: 0.95rem;
        line-height: 1.6;
        backdrop-filter: blur(10px);
    }
    .stTextArea textarea:focus {
        border-color: #ff5e7d !important;
        box-shadow: 0 0 0 3px rgba(255, 94, 125, 0.25) !important;
    }

    /* Result glass cards */
    .glass {
        background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px;
        padding: 1.3rem 1.5rem;
        min-height: 150px;
        line-height: 1.7;
        backdrop-filter: blur(14px);
        box-shadow: 0 10px 40px rgba(0,0,0,0.35);
    }
    .glass.health { border-left: 4px solid #ff5e7d; }
    .glass.diet   { border-left: 4px solid #00d6b4; }
    .glass.warn   { border-left: 4px solid #ffb347; }
    .glass.warn strong { color: #ffc978; }
    .placeholder  { color: #7d77a3; font-style: italic; }

    /* Button */
    .stButton > button {
        background: linear-gradient(90deg, #ff5e7d, #b06cff);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 0.7rem 1.6rem;
        font-weight: 700;
        font-size: 1rem;
        transition: transform .15s ease, box-shadow .15s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 28px rgba(176, 108, 255, 0.45);
        color: white;
    }

    /* Widget labels (were dark on dark) */
    .stApp label, .stApp label p,
    [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p {
        color: #e4defa !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* Input wrappers: Streamlit paints these white, so override them */
    [data-testid="stTextArea"] div, [data-testid="stTextInput"] div {
        background-color: transparent !important;
    }
    [data-testid="stTextArea"] div[data-baseweb="textarea"],
    [data-testid="stTextInput"] div[data-baseweb="input"],
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1b1634 !important;
        border: 1px solid rgba(176, 108, 255, 0.5) !important;
        border-radius: 14px !important;
    }
    [data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input {
        background-color: #1b1634 !important;
        color: #f4f1ff !important;
        -webkit-text-fill-color: #f4f1ff !important;
        caret-color: #ff5e7d;
        border: none !important;
        border-radius: 14px !important;
    }
    [data-testid="stTextArea"] textarea::selection,
    [data-testid="stTextInput"] input::selection {
        background: rgba(176, 108, 255, 0.55);
        color: #ffffff;
        -webkit-text-fill-color: #ffffff;
    }
    [data-testid="InputInstructions"], [data-testid="InputInstructions"] * {
        color: #8e88b3 !important;
    }

    /* File uploader */
    [data-testid="stFileUploaderDropzone"] {
        background: rgba(255,255,255,0.06) !important;
        border: 1px dashed rgba(176, 108, 255, 0.55) !important;
        border-radius: 14px !important;
    }
    [data-testid="stFileUploaderDropzone"] *,
    [data-testid="stFileUploaderFile"] * { color: #e4defa !important; }
    [data-testid="stFileUploaderDropzone"] button {
        background: rgba(176,108,255,0.25) !important;
        border: 1px solid rgba(176,108,255,0.6) !important;
        border-radius: 10px !important;
    }
    [data-testid="stFileUploaderFile"] {
        background: rgba(255,255,255,0.06) !important;
        border-radius: 12px !important;
    }

    /* Expander + caption */
    [data-testid="stExpander"] { border-color: rgba(255,255,255,0.12) !important; border-radius: 14px !important; }
    [data-testid="stExpander"] summary p { color: #e4defa !important; }
    .stCaption, [data-testid="stCaptionContainer"] { color: #8e88b3 !important; }

    /* Rendered answer text inside cards */
    .glass p { margin: 0 0 0.6rem 0; }
    .glass ul { margin: 0 0 0.8rem 0; padding-left: 1.2rem; }
    .glass li { margin-bottom: 0.35rem; }
    .glass.health strong { color: #ff9db3; }
    .glass.diet strong { color: #6ff0d9; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sample data ----------
SAMPLE = """LIPID PANEL
-----------
Total Cholesterol: 238 mg/dL   (Normal: <200)
LDL Cholesterol:   162 mg/dL   (Normal: <100)
HDL Cholesterol:   36 mg/dL    (Normal: >40)
Triglycerides:     188 mg/dL   (Normal: <150)

METABOLIC PANEL
---------------
Glucose (Fasting): 92 mg/dL    (Normal: 70-99)
HbA1c:             5.3%        (Normal: <5.7%)
Creatinine:        1.0 mg/dL   (Normal: 0.7-1.3)
eGFR:              82 mL/min   (Normal: >60)

LIVER FUNCTION
--------------
ALT:               28 U/L      (Normal: 7-40)
AST:               25 U/L      (Normal: 10-40)
Bilirubin Total:   0.8 mg/dL   (Normal: 0.2-1.2)
"""


BLOOD_TERMS = [
    "hemoglobin", "haemoglobin", "hgb", "hematocrit", "rbc", "wbc", "platelet",
    "cholesterol", "ldl", "hdl", "triglyceride", "glucose", "hba1c", "creatinine",
    "egfr", "alt", "ast", "sgpt", "sgot", "bilirubin", "urea", "bun", "tsh",
    "ferritin", "mcv", "mch", "neutrophil", "lymphocyte", "sodium", "potassium",
    "calcium", "mg/dl", "g/dl", "u/l", "mmol/l", "ml/min",
]


def looks_like_blood_report(text: str, llm) -> bool:
    """0 matching terms -> reject, 2+ -> accept, exactly 1 -> ask the LLM."""
    lowered = text.lower()
    hits = {t for t in BLOOD_TERMS if re.search(rf"(?<![a-z]){re.escape(t)}(?![a-z])", lowered)}
    if len(hits) == 0:
        return False
    if len(hits) >= 2:
        return True
    check = (
        "Is the following text a blood test or lab report with medical test values? "
        "Answer with only YES or NO.\n\n" + text[:2000]
    )
    return llm.invoke(check).content.strip().upper().startswith("YES")


# ---------- LLM helpers ----------
@st.cache_resource
def get_llm(model: str, temperature: float):
    return ChatOllama(model=model, temperature=temperature)


def summary_prompt(data: str, query: str) -> str:
    return f"""You are a blood data analysis expert.
Answer in the following format for the user question.
Blood data:
{data}
Question:
{query}
Answer:
Patient Name:
Age:
Disease and count:
Causes:
Use simple, clear, short sentences."""


def diet_prompt(data: str) -> str:
    return f"""You are a nutrition expert who reads blood reports.
Blood data:
{data}
Give a suggested diet plan based on the abnormal values only.
Format:
Foods to eat:
Foods to avoid:
Sample day (breakfast, lunch, dinner):
Use simple, clear, short sentences."""


# ---------- Layout ----------
st.markdown('<div class="app-title">Blood Work Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-sub">Paste your lab report, ask a question, and get a plain-language summary and diet plan.</div>',
    unsafe_allow_html=True,
)

with st.expander("Settings", expanded=False):
    c1, c2 = st.columns(2)
    model = c1.text_input("Ollama model", value="llama3.2")
    temperature = c2.slider("Temperature", 0.0, 1.0, 0.4, 0.1)

left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown('<div class="section-head">Blood Work Report</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload blood_work.txt (optional)", type=["txt"])
    default_text = uploaded.read().decode("utf-8") if uploaded else SAMPLE

    data = st.text_area(
        "report", value=default_text, height=430, label_visibility="collapsed"
    )
    query = st.text_input("Your question", value="what about my health")
    analyze = st.button("Analyze my report")

with right:
    st.markdown('<div class="section-head">Health Summary</div>', unsafe_allow_html=True)
    summary_slot = st.empty()
    st.markdown('<div class="section-head" style="margin-top:1.6rem">Suggested Diet Plan</div>', unsafe_allow_html=True)
    diet_slot = st.empty()

    placeholder = '<div class="glass {cls}"><span class="placeholder">{msg}</span></div>'
    summary_slot.markdown(
        placeholder.format(cls="health", msg="Your summary will appear here."),
        unsafe_allow_html=True,
    )
    diet_slot.markdown(
        placeholder.format(cls="diet", msg="Your diet plan will appear here."),
        unsafe_allow_html=True,
    )

# ---------- Run ----------
def card(cls: str, body: str) -> str:
    return f'<div class="glass {cls}">{body}</div>'


if analyze:
    if not data.strip():
        st.warning("Please paste or upload a blood work report first.")
    else:
        try:
            with right:
                with st.spinner("Checking your report..."):
                    is_blood = looks_like_blood_report(data, get_llm(model, 0.0))

                if not is_blood:
                    summary_slot.markdown(
                        card(
                            "warn",
                            "<p><strong>This doesn't look like a blood work report.</strong></p>"
                            "<p>Please paste lab results with values like cholesterol, "
                            "glucose, hemoglobin or liver tests.</p>",
                        ),
                        unsafe_allow_html=True,
                    )
                else:
                    llm = get_llm(model, temperature)

                    with st.spinner("Reading your report..."):
                        summary = llm.invoke(summary_prompt(data, query)).content
                    summary_slot.markdown(
                        card("health", md_to_html(summary)), unsafe_allow_html=True
                    )

                    with st.spinner("Building your diet plan..."):
                        diet = llm.invoke(diet_prompt(data)).content
                    diet_slot.markdown(
                        card("diet", md_to_html(diet)), unsafe_allow_html=True
                    )
        except Exception as e:
            st.error(
                f"Could not reach Ollama: {e}\n\n"
                "Make sure Ollama is running (`ollama serve`) and the model is pulled "
                f"(`ollama pull {model}`)."
            )

st.caption("For information only. This is not medical advice; please talk to a doctor about your results.")