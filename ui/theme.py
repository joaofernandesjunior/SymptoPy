# ui/theme.py
# Cyber-Minimalista — paleta e CSS global do SymptoPy

BG          = '#0D1117'
PANEL       = '#161B22'
BORDER      = '#30363D'
ACCENT      = '#00F0FF'
ACCENT_DIM  = '#007A8A'
RED         = '#FF6B6B'
RED_DIM     = '#8B0000'
GREEN       = '#3FB950'
YELLOW      = '#F0B429'
TEXT        = '#C9D1D9'
TEXT_DIM    = '#8B949E'
WHITE       = '#E6EDF3'

CSS = f"""
<style>
/* ── Reset Streamlit ─────────────────────────────────────── */
html, body, [class*="css"] {{
    font-family: 'Consolas', 'Courier New', monospace !important;
    background-color: {BG} !important;
    color: {TEXT} !important;
}}
.stApp {{ background-color: {BG} !important; }}
section[data-testid="stSidebar"] {{ display: none; }}

/* ── Esconder barra nativa do Streamlit ──────────────────── */
header[data-testid="stHeader"] {{ display: none !important; }}
#MainMenu {{ display: none !important; }}
footer {{ display: none !important; }}
div[data-testid="stToolbar"] {{ display: none !important; }}
div[data-testid="stDecoration"] {{ display: none !important; }}
div[data-testid="stStatusWidget"] {{ display: none !important; }}
.viewerBadge_container__1QSob {{ display: none !important; }}

/* ── Remove default padding ─────────────────────────────── */
.block-container {{ padding: 1rem 1.5rem 1rem 1.5rem !important; max-width: 100% !important; }}
div[data-testid="stVerticalBlock"] > div {{ gap: 0.3rem; }}

/* ── Header bar ─────────────────────────────────────────── */
.symp-header {{
    background: linear-gradient(90deg, {PANEL} 0%, #0A1628 100%);
    border-bottom: 1px solid {ACCENT};
    padding: 0.6rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.8rem;
    border-radius: 4px;
}}
.symp-logo {{
    font-size: 1.3rem;
    font-weight: bold;
    color: {ACCENT};
    letter-spacing: 2px;
    text-shadow: 0 0 8px {ACCENT}55;
}}
.symp-tagline {{
    font-size: 0.7rem;
    color: {TEXT_DIM};
    letter-spacing: 1px;
}}

/* ── Panels ─────────────────────────────────────────────── */
.panel-left, .panel-right {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 1rem;
    height: calc(100vh - 180px);
    overflow-y: auto;
}}
.panel-right {{
    border-left: 2px solid {ACCENT_DIM};
}}
.panel-title {{
    font-size: 0.65rem;
    letter-spacing: 3px;
    color: {ACCENT};
    text-transform: uppercase;
    border-bottom: 1px solid {BORDER};
    padding-bottom: 0.4rem;
    margin-bottom: 0.8rem;
}}

/* ── Block headers ──────────────────────────────────────── */
.block-header {{
    font-size: 0.7rem;
    letter-spacing: 2px;
    color: {TEXT_DIM};
    text-transform: uppercase;
    margin: 0.8rem 0 0.3rem 0;
    padding-left: 0.3rem;
    border-left: 2px solid {ACCENT_DIM};
}}
.block-header.red {{ border-left-color: {RED}; color: {RED}; }}

/* ── Inputs ─────────────────────────────────────────────── */
div[data-testid="stCheckbox"] label {{
    font-size: 0.82rem !important;
    color: {TEXT} !important;
}}
div[data-testid="stCheckbox"] input:checked + div svg {{
    fill: {ACCENT} !important;
}}
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label {{
    font-size: 0.75rem !important;
    color: {TEXT_DIM} !important;
}}
div[data-testid="stNumberInput"] input,
div[data-testid="stSelectbox"] div,
div[data-testid="stTextInput"] input {{
    background: #0D1117 !important;
    border: 1px solid {BORDER} !important;
    color: {TEXT} !important;
    font-family: 'Consolas', monospace !important;
    font-size: 0.82rem !important;
    border-radius: 4px !important;
}}
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextInput"] input:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 1px {ACCENT}44 !important;
}}

/* ── Buttons ─────────────────────────────────────────────── */
div[data-testid="stButton"] button {{
    background: transparent !important;
    border: 1px solid {ACCENT} !important;
    color: {ACCENT} !important;
    font-family: 'Consolas', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 1px !important;
    border-radius: 4px !important;
    transition: all 0.15s !important;
}}
div[data-testid="stButton"] button:hover {{
    background: {ACCENT}22 !important;
    box-shadow: 0 0 8px {ACCENT}44 !important;
}}
div[data-testid="stButton"] button[kind="primary"] {{
    background: {ACCENT}22 !important;
    border-color: {ACCENT} !important;
    color: {ACCENT} !important;
}}

/* ── SOAP preview ───────────────────────────────────────── */
.soap-block {{
    background: #0A0E14;
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 0.8rem;
    font-size: 0.8rem;
    line-height: 1.6;
    white-space: pre-wrap;
    font-family: 'Consolas', monospace;
    color: {TEXT};
}}
.soap-section {{ color: {ACCENT}; font-weight: bold; }}
.soap-alert  {{ color: {RED}; font-weight: bold; }}
.soap-rx     {{ color: {GREEN}; }}
.soap-flag   {{ color: {YELLOW}; }}
.soap-dim    {{ color: {TEXT_DIM}; }}

/* ── Urgency badges ──────────────────────────────────────── */
.badge {{ display:inline-block; padding:2px 8px; border-radius:3px;
          font-size:0.65rem; letter-spacing:1px; font-weight:bold; margin-left:6px; }}
.badge-emergency {{ background:{RED_DIM}; color:{RED}; border:1px solid {RED}; }}
.badge-urgente   {{ background:#3D2800; color:{YELLOW}; border:1px solid {YELLOW}; }}
.badge-aps       {{ background:#1C3D1C; color:{GREEN}; border:1px solid {GREEN}; }}
.badge-eletivo   {{ background:#1C2D3D; color:#58A6FF; border:1px solid #58A6FF; }}

/* ── Expander ────────────────────────────────────────────── */
div[data-testid="stExpander"] {{
    border: 1px solid {BORDER} !important;
    border-radius: 4px !important;
    background: #0D1117 !important;
    margin-bottom: 4px !important;
}}
div[data-testid="stExpander"] summary {{
    font-size: 0.75rem !important;
    color: {TEXT_DIM} !important;
    letter-spacing: 1px !important;
}}

/* ── Divider ─────────────────────────────────────────────── */
hr {{ border-color: {BORDER} !important; margin: 0.5rem 0 !important; }}

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 2px; }}
::-webkit-scrollbar-thumb:hover {{ background: {ACCENT_DIM}; }}
</style>
"""
