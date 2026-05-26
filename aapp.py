import streamlit as st
import streamlit.components.v1 as components
import joblib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import base64
from pathlib import Path

st.set_page_config(
    page_title="Autism Early Screener",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Load & encode all background videos ───────────────────────────────────────
def get_video_base64(path: str):
    p = Path(path)
    if p.exists():
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# Handles bg_video1.mp4 AND bg_video1.mp4.mp4 (Windows double-extension)
def find_video_path(n):
    for name in [f"bg_video{n}.mp4", f"bg_video{n}.mp4.mp4"]:
        if Path(name).exists():
            return name
    return f"bg_video{n}.mp4"

VIDEO_FILES = [find_video_path(i) for i in range(1, 6)]
videos_b64  = [get_video_base64(v) for v in VIDEO_FILES]
found       = [(i, v) for i, v in enumerate(videos_b64) if v is not None]
found_count = len(found)

source_tags  = "\n".join(
    [f'<source src="data:video/mp4;base64,{b64}" type="video/mp4">'
     for _, b64 in found]
) if found else ""

# playlist_js replaced by playlist_array below

# Build playlist as JS array of base64 strings
playlist_array = "[" + ",".join([f'`data:video/mp4;base64,{b64}`' for _,b64 in found]) + "]" if found else "[]"

video_block = f"""
<video id="bgVid" autoplay muted playsinline
  style="position:fixed;top:0;left:0;width:100vw;height:100vh;
         object-fit:cover;z-index:0;pointer-events:none;
         transition:opacity 1.2s ease;opacity:1;">
  {source_tags}
</video>
<img src="x" onerror="
  (function(){{
    var pl={playlist_array};
    if(pl.length<2)return;
    var i=0, v=document.getElementById('bgVid');
    if(!v)return;
    function sw(){{
      v.style.opacity='0';
      setTimeout(function(){{
        i=(i+1)%pl.length;
        v.src=pl[i];
        v.load();
        v.play();
        v.style.opacity='1';
      }},1200);
    }}
    setInterval(sw,5000);
  }})();
" style="display:none">
""" if found else ""

st.markdown(video_block, unsafe_allow_html=True)

# ── ALL CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Fraunces:ital,wght@0,300;0,400;1,300;1,400&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* ── Base app — gradient fallback shown BEHIND the video ── */
.stApp {
    font-family: 'DM Sans', sans-serif !important;
    background: linear-gradient(135deg, #4a2080 0%, #1a6b60 100%) !important;
    min-height: 100vh;
}

/* ── OVERLAY: lighter so video shows through AND text is readable ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    /* semi-transparent dark layer — light enough to see video clearly */
    background: rgba(10, 5, 30, 0.28);
    z-index: 1;
    pointer-events: none;
}

/* ── Subtle colour tint that doesn't kill the video ── */
.stApp::after {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 70% 50% at 10% 5%,  rgba(120,70,210,0.22) 0%, transparent 55%),
        radial-gradient(ellipse 60% 45% at 90% 95%, rgba(20,160,140,0.18) 0%, transparent 55%);
    z-index: 2;
    pointer-events: none;
    animation: tintShift 20s ease-in-out infinite alternate;
}
@keyframes tintShift {
    0%   { opacity: 0.7; }
    100% { opacity: 1.0; }
}

/* ── All Streamlit content sits above overlays ── */
.main .block-container {
    position: relative;
    z-index: 10;
    max-width: 700px !important;
    padding: 0 1.6rem 4rem !important;
    margin: 0 auto;
}

/* ── Force ALL streamlit text white so it shows on dark bg ── */
.stApp p, .stApp span, .stApp div, .stApp label,
.stMarkdown p, .stMarkdown div, .stMarkdown span,
.stSelectbox label, .stNumberInput label,
.stRadio label span, .stSlider label {
    color: rgba(255,255,255,0.93) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   HERO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.hero-wrap {
    text-align: center;
    padding: 3.5rem 1rem 2.2rem;
}
.hero-pill {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.32);
    color: #ffffff !important;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    border-radius: 999px;
    padding: 0.34rem 1.1rem;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(10px);
}
.hero-title {
    font-family: 'Fraunces', serif !important;
    font-size: 3.4rem !important;
    font-weight: 300 !important;
    line-height: 1.14 !important;
    color: #ffffff !important;
    letter-spacing: -0.03em;
    margin-bottom: 1rem !important;
    text-shadow: 0 3px 30px rgba(0,0,0,0.55), 0 1px 6px rgba(0,0,0,0.4);
}
.hero-title em {
    font-style: italic;
    color: #6ef0e0 !important;
    text-shadow: 0 0 40px rgba(110,240,224,0.4);
}
.hero-sub {
    font-size: 1.05rem !important;
    color: rgba(255,255,255,0.88) !important;
    max-width: 480px;
    margin: 0 auto 1.2rem;
    line-height: 1.75;
    text-shadow: 0 1px 10px rgba(0,0,0,0.5);
    font-weight: 400;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(255,255,255,0.13);
    border: 1px solid rgba(255,255,255,0.28);
    color: rgba(255,255,255,0.9) !important;
    font-size: 0.8rem;
    font-weight: 500;
    border-radius: 999px;
    padding: 0.35rem 1.1rem;
    backdrop-filter: blur(10px);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SECTION HEADERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.sec-head {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin: 2.2rem 0 1rem;
}
.sec-icon {
    width: 34px; height: 34px;
    border-radius: 10px;
    background: linear-gradient(135deg, rgba(160,100,255,0.75), rgba(30,185,165,0.75));
    border: 1px solid rgba(255,255,255,0.25);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
    backdrop-filter: blur(8px);
    box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}
.sec-label {
    font-family: 'Fraunces', serif !important;
    font-size: 1.3rem !important;
    font-weight: 400 !important;
    color: #ffffff !important;
    letter-spacing: -0.01em;
    text-shadow: 0 2px 12px rgba(0,0,0,0.4);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   GLASS CARDS  (child info + questions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

/* Style the native Streamlit container that wraps child-info widgets */
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(15, 8, 40, 0.52) !important;
    backdrop-filter: blur(28px) !important;
    -webkit-backdrop-filter: blur(28px) !important;
    border: 1px solid rgba(255,255,255,0.22) !important;
    border-radius: 22px !important;
    padding: 1.2rem 1.4rem !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.18) !important;
}

.info-card, .q-card {
    background: rgba(15, 8, 40, 0.52);
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    border: 1px solid rgba(255, 255, 255, 0.22);
    border-radius: 22px;
    padding: 1.5rem 1.7rem;
    margin-bottom: 1rem;
    box-shadow:
        0 8px 32px rgba(0,0,0,0.22),
        inset 0 1px 0 rgba(255,255,255,0.18);
    transition: box-shadow 0.3s ease, transform 0.3s ease;
}
.q-card { padding: 1.2rem 1.6rem 0.5rem; }
.q-card:hover, .info-card:hover {
    box-shadow: 0 14px 48px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.24);
    transform: translateY(-3px);
}
.q-label {
    font-size: 1rem !important;
    font-weight: 500;
    color: #ffffff !important;
    margin-bottom: 0.55rem;
    line-height: 1.55;
    text-shadow: 0 1px 6px rgba(0,0,0,0.3);
}
.q-hint {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.65) !important;
    margin-bottom: 0.4rem;
    font-style: italic;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   FORM ELEMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
/* Selectbox */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.14) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 12px !important;
    color: white !important;
    backdrop-filter: blur(12px);
}
.stSelectbox > div > div:hover {
    border-color: rgba(255,255,255,0.5) !important;
    background: rgba(255,255,255,0.2) !important;
}
.stSelectbox svg { fill: rgba(255,255,255,0.8) !important; }
[data-baseweb="select"] span { color: white !important; }

/* Number input */
.stNumberInput > div > div > input {
    background: rgba(255,255,255,0.14) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 12px !important;
    color: white !important;
}

/* Radio */
.stRadio > div { gap: 0.55rem; }
.stRadio > div > label {
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.26) !important;
    border-radius: 11px !important;
    padding: 0.55rem 1.2rem !important;
    font-size: 0.92rem !important;
    color: rgba(255,255,255,0.92) !important;
    cursor: pointer;
    transition: all 0.2s ease !important;
    backdrop-filter: blur(10px);
}
.stRadio > div > label:hover {
    border-color: rgba(160,220,255,0.55) !important;
    background: rgba(255,255,255,0.22) !important;
}
/* Selected radio highlight */
.stRadio > div > label[data-checked="true"],
.stRadio > div > label:has(input:checked) {
    background: rgba(110,240,224,0.18) !important;
    border-color: rgba(110,240,224,0.5) !important;
}

/* Slider track */
.stSlider > div > div > div {
    background: linear-gradient(90deg, #a060f0, #20c4b0) !important;
}
.stSlider > div > div > div > div {
    background: white !important;
    border: 2.5px solid #a060f0 !important;
    box-shadow: 0 2px 12px rgba(160,96,240,0.45) !important;
}
/* Slider label text */
.stSlider span { color: rgba(255,255,255,0.85) !important; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   CTA BUTTON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stButton > button {
    background: linear-gradient(135deg, rgba(150,85,240,0.9), rgba(20,175,158,0.9)) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.28) !important;
    border-radius: 15px !important;
    padding: 0.9rem 2rem !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    font-family: 'DM Sans', sans-serif !important;
    width: 100% !important;
    letter-spacing: 0.03em;
    box-shadow: 0 6px 28px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.2) !important;
    backdrop-filter: blur(12px);
    transition: all 0.24s ease !important;
    text-transform: uppercase;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 40px rgba(0,0,0,0.38) !important;
    background: linear-gradient(135deg, rgba(165,100,255,1), rgba(25,195,175,1)) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   RESULT CARDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.result-card {
    border-radius: 22px;
    padding: 2rem 2.2rem;
    margin: 1.2rem 0;
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    box-shadow: 0 8px 40px rgba(0,0,0,0.28);
}
.result-low    { background: rgba(15,80,70,0.65);  border: 1px solid rgba(80,220,200,0.35); }
.result-medium { background: rgba(80,60,5,0.65);   border: 1px solid rgba(240,190,55,0.35); }
.result-high   { background: rgba(80,15,15,0.65);  border: 1px solid rgba(240,100,100,0.35); }

.result-title-low    { font-family:'Fraunces',serif; font-size:1.6rem; font-weight:400; color:#6ef0e0 !important; margin-bottom:0.45rem; }
.result-title-medium { font-family:'Fraunces',serif; font-size:1.6rem; font-weight:400; color:#f5d06a !important; margin-bottom:0.45rem; }
.result-title-high   { font-family:'Fraunces',serif; font-size:1.6rem; font-weight:400; color:#f59898 !important; margin-bottom:0.45rem; }

.pbar-track { background:rgba(255,255,255,0.15); border-radius:999px; height:8px; margin:0.8rem 0 1.2rem; overflow:hidden; }
.pbar-low    { height:100%; border-radius:999px; background:linear-gradient(90deg,#1a9486,#52d5c5); }
.pbar-medium { height:100%; border-radius:999px; background:linear-gradient(90deg,#c8880a,#f0c030); }
.pbar-high   { height:100%; border-radius:999px; background:linear-gradient(90deg,#b82828,#e04848); }

.rec-pill {
    display:inline-block; font-size:0.72rem; font-weight:700;
    letter-spacing:0.12em; text-transform:uppercase;
    border-radius:999px; padding:0.3rem 0.9rem; margin-bottom:0.7rem;
}
.rec-low    { background:rgba(80,220,200,0.2); color:#6ef0e0 !important; border:1px solid rgba(80,220,200,0.4); }
.rec-medium { background:rgba(240,190,55,0.2); color:#f5d06a !important; border:1px solid rgba(240,190,55,0.4); }
.rec-high   { background:rgba(240,100,100,0.2);color:#f59898 !important; border:1px solid rgba(240,100,100,0.4); }

.concern-tag {
    display:inline-block;
    background:rgba(240,100,100,0.15);
    border:1px solid rgba(240,100,100,0.35);
    color:#f59898 !important;
    border-radius:10px; padding:0.3rem 0.8rem; margin:0.25rem;
    font-size:0.82rem; font-weight:500;
}

.disclaimer {
    background:rgba(255,255,255,0.08);
    border:1px solid rgba(255,255,255,0.18);
    border-radius:16px; padding:1.1rem 1.4rem;
    font-size:0.83rem; color:rgba(255,255,255,0.75) !important;
    margin-top:1.6rem; line-height:1.68; backdrop-filter:blur(14px);
}

/* Notice bar */
.notice {
    background: rgba(255,210,60,0.12);
    border: 1px solid rgba(255,210,60,0.3);
    border-radius: 12px; padding: 0.7rem 1.1rem;
    font-size: 0.82rem; color: rgba(255,225,120,0.95) !important;
    margin-bottom: 0.5rem; text-align: center;
    backdrop-filter: blur(10px);
}

hr { border:none; border-top:1px solid rgba(255,255,255,0.14) !important; margin:2.2rem 0 !important; }

.footer-text {
    text-align:center; color:rgba(255,255,255,0.42) !important;
    font-size:0.77rem; margin-top:0.8rem; line-height:1.72;
}

#MainMenu {visibility:hidden;}
footer     {visibility:hidden;}
header     {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ── Load model ──────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    model    = joblib.load('autism_model.pkl')
    features = joblib.load('feature_columns.pkl')
    return model, features

model, feature_columns = load_model()

FEATURE_IMPORTANCE = {
    'A1':0.034,'A2':0.035,'A3':0.096,'A4':0.077,
    'A5':0.122,'A6':0.162,'A7':0.039,'A8':0.043,
    'A9':0.117,'A10':0.076,'Age':0.180,
    'Sex_encoded':0.008,'Jauundice_encoded':0.006,'Family_ASD_encoded':0.006
}
QUESTION_LABELS = {
    'A1':'Eye contact','A2':'Social smile','A3':'Responds to name',
    'A4':'Points to show interest','A5':'Pretend / imaginative play',
    'A6':'Follows gaze','A7':'Comfort seeking','A8':'First words',
    'A9':'Simple gestures','A10':'Stares at nothing'
}

# ── Video status ────────────────────────────────────────────────────────────
if found_count == 0:
    st.markdown(
        '<div class="notice">⚠️ No video files found — gradient background active.<br>'
        'Add <code>bg_video1.mp4</code> → <code>bg_video5.mp4</code> beside app.py to enable videos.</div>',
        unsafe_allow_html=True)
elif found_count < 5:
    missing = [VIDEO_FILES[i] for i in range(5) if videos_b64[i] is None]
    st.markdown(
        f'<div class="notice">🎬 {found_count}/5 videos active. '
        f'Missing: <code>{"</code>, <code>".join(missing)}</code></div>',
        unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero-wrap">
    <div class="hero-pill">🌸 Early Developmental Screening</div>
    <h1 class="hero-title">Notice the signs, <em>early</em></h1>
    <p class="hero-sub">A gentle, science-backed screener to help parents understand
    their child's developmental milestones — from the comfort of home.</p>
    <span class="hero-badge">✦ Takes about 2 minutes &nbsp;·&nbsp; No sign-up needed</span>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="sec-head">
    <div class="sec-icon">👶</div>
    <span class="sec-label">About Your Child</span>
</div>""", unsafe_allow_html=True)

with st.container(border=True):
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("Age (in months)", min_value=18, max_value=48,
                              value=24, step=1, help="Designed for 18–48 months")
    with c2:
        sex_input = st.selectbox("Sex at birth", ["Male","Female"])
    c3, c4 = st.columns(2)
    with c3:
        jaundice_input = st.selectbox("Born with jaundice?", ["No","Yes"])
    with c4:
        family_asd_input = st.selectbox("Family history of ASD?", ["No","Yes"])

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="sec-head">
    <div class="sec-icon">🧩</div>
    <span class="sec-label">Your Child's Behaviours</span>
</div>
<p style="font-size:0.9rem;color:rgba(255,255,255,0.68);margin-bottom:1.2rem;font-style:italic;">
Answer based on what you <em>usually</em> observe at home. There are no right or wrong answers.
</p>""", unsafe_allow_html=True)

q_responses = {}

def q_select(key, num, text, hint=None):
    st.markdown(
        f'<div class="q-card"><p class="q-label">{num}. {text}</p>'
        + (f'<p class="q-hint">{hint}</p>' if hint else '') + '</div>',
        unsafe_allow_html=True)
    v = st.select_slider("", ["Never","Sometimes","Always"],
                         value="Always", key=key)
    return 1 if v == "Never" else 0

def q_radio(key, num, text, hint=None, default=0, rev=False):
    st.markdown(
        f'<div class="q-card"><p class="q-label">{num}. {text}</p>'
        + (f'<p class="q-hint">{hint}</p>' if hint else '') + '</div>',
        unsafe_allow_html=True)
    v = st.radio("", ["Yes","No"], key=key,
                 horizontal=True, index=default)
    return (1 if v=="Yes" else 0) if rev else (1 if v=="No" else 0)

q_responses['A1']  = q_select("a1", 1, "Does your child make eye contact with you?")
q_responses['A2']  = q_select("a2", 2, "Does your child smile back when you smile at them?")
q_responses['A3']  = q_select("a3", 3, "Does your child respond when you call their name?")
q_responses['A4']  = q_radio("a4",  4, "Does your child point at things to show you something interesting?")
q_responses['A5']  = q_radio("a5",  5, "Does your child engage in pretend or imaginative play?",
                              hint="e.g. feeding a doll, pretending to cook")
q_responses['A6']  = q_radio("a6",  6, "When you look at something, does your child follow your gaze?")
q_responses['A7']  = q_radio("a7",  7, "Does your child come to you for comfort when hurt or upset?")
q_responses['A8']  = q_radio("a8",  8, "Has your child said their first words yet?")
q_responses['A9']  = q_radio("a9",  9, "Does your child use simple gestures?",
                              hint="e.g. waving bye-bye, clapping")
q_responses['A10'] = q_radio("a10",10, "Does your child stare at nothing or seem to look past people?",
                              default=1, rev=True)

# ══════════════════════════════════════════════════════════════════════════════
# PREDICT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)
predict_clicked = st.button("✦ View Screening Result")

if predict_clicked:
    sex_enc        = 1 if sex_input        == "Male" else 0
    jaundice_enc   = 1 if jaundice_input   == "Yes"  else 0
    family_asd_enc = 1 if family_asd_input == "Yes"  else 0

    input_data = np.array([[
        q_responses['A1'],q_responses['A2'],q_responses['A3'],
        q_responses['A4'],q_responses['A5'],q_responses['A6'],
        q_responses['A7'],q_responses['A8'],q_responses['A9'],
        q_responses['A10'],age,sex_enc,jaundice_enc,family_asd_enc
    ]])

    prob = model.predict_proba(input_data)[0][1]
    pct  = round(prob * 100, 1)

    if pct < 30:
        rl="Low Risk";    rc="low";    em="✦"
        rt="Monitor at home"
        rd=("Your child's responses suggest typical developmental patterns. "
            "Continue engaging through play, reading, and conversation.")
        msg="Every child develops at their own pace. The responses you've shared look encouraging. Keep nurturing your child with love and play — you're doing wonderfully. 💚"
    elif pct < 65:
        rl="Medium Risk"; rc="medium"; em="◆"
        rt="Consult a pediatrician"
        rd=("Some responses suggest behaviours worth discussing with your child's doctor. "
            "A pediatrician can advise if a developmental assessment is needed.")
        msg="Seeking answers is one of the most loving things a parent can do. This is not a diagnosis — a conversation with your doctor is a worthwhile next step. You are not alone. 💛"
    else:
        rl="High Risk";   rc="high";   em="▲"
        rt="Seek specialist evaluation"
        rd=("Several responses indicate behaviours commonly associated with ASD. "
            "We strongly recommend consulting a developmental pediatrician.")
        msg="We understand this may feel overwhelming. Many children with ASD lead joyful lives — especially with early support. A specialist can give you clarity and a path forward. 🧡"

    st.markdown("---")
    st.markdown("""<div class="sec-head">
        <div class="sec-icon">📋</div>
        <span class="sec-label">Screening Result</span>
    </div>""", unsafe_allow_html=True)

    st.markdown(
        f'<div class="result-card result-{rc}">'
        f'<span class="rec-pill rec-{rc}">{rt}</span>'
        f'<div class="result-title-{rc}">{em} {rl} — {pct}%</div>'
        f'<div class="pbar-track"><div class="pbar-{rc}" style="width:{pct}%"></div></div>'
        f'<p style="font-size:0.93rem;line-height:1.68;color:rgba(255,255,255,0.85);">{rd}</p>'
        f'</div>', unsafe_allow_html=True)
    st.info(msg)

    concerning = [QUESTION_LABELS[q] for q in
                  ['A1','A2','A3','A4','A5','A6','A7','A8','A9']
                  if q_responses[q]==0]
    if q_responses['A10']==1:
        concerning.append(QUESTION_LABELS['A10'])

    if concerning:
        st.markdown("#### Behaviours that may need attention")
        st.markdown("".join([f'<span class="concern-tag">↗ {c}</span>'
                             for c in concerning]), unsafe_allow_html=True)
        st.caption("These specific responses contributed to the risk score.")
    else:
        st.success("✅ No specific behavioural concerns flagged.")

    st.markdown("#### Factors That Influenced This Result")
    st.caption("Which inputs carry the most weight in the model's prediction.")

    dlabels = {
        'A1':'Eye contact','A2':'Social smile','A3':'Responds to name',
        'A4':'Points / interest','A5':'Pretend play','A6':'Follows gaze',
        'A7':'Comfort seeking','A8':'First words','A9':'Gestures',
        'A10':'Stares at nothing','Age':'Age (months)',
        'Sex_encoded':'Sex','Jauundice_encoded':'Jaundice at birth',
        'Family_ASD_encoded':'Family history'
    }
    items  = sorted(FEATURE_IMPORTANCE.items(), key=lambda x:x[1])
    labs   = [dlabels[k] for k,v in items]
    vals   = [v for k,v in items]
    med    = np.median(vals)
    cols   = ['#a060f0' if v>med else '#20c4b0' for v in vals]

    fig,ax = plt.subplots(figsize=(7,3.8))
    fig.patch.set_facecolor('#120830')
    ax.set_facecolor('#120830')
    ax.barh(labs, vals, color=cols, edgecolor='none', height=0.55)
    ax.set_xlabel('Importance score', fontsize=8.5, color='rgba(255,255,255,0.6)')
    ax.tick_params(colors='rgba(255,255,255,0.72)', labelsize=8)
    for s in ax.spines.values(): s.set_visible(False)
    ax.xaxis.grid(True, color='rgba(255,255,255,0.07)', linewidth=0.8)
    ax.set_axisbelow(True)
    p1=mpatches.Patch(color='#a060f0',label='Higher importance')
    p2=mpatches.Patch(color='#20c4b0',label='Lower importance')
    ax.legend(handles=[p1,p2],fontsize=8,loc='lower right',
              facecolor='#120830',labelcolor='white',framealpha=1,
              edgecolor='rgba(255,255,255,0.1)')
    plt.tight_layout()
    st.pyplot(fig); plt.close()

    st.markdown(
        '<div class="disclaimer"><strong>⚕ Important Disclaimer</strong><br>'
        'This tool is for informational purposes only — it is <strong>not a medical diagnosis</strong>. '
        'Only a qualified healthcare professional can diagnose Autism Spectrum Disorder. '
        'If you have concerns, please consult a doctor.</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    '<p class="footer-text">Built with care · scikit-learn &amp; Streamlit · '
    'UCI Autism Screening Dataset · Not a substitute for professional medical advice</p>',
    unsafe_allow_html=True)
