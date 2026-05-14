import streamlit as st
import pandas as pd
import os
import io
import requests
import folium
import bcrypt
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from datetime import datetime, date, timedelta
import streamlit_authenticator as stauth
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, KeepTogether)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# --- 1. KONFIGURASJON ---
st.set_page_config(page_title="Utrykningsskolen", page_icon="🚑", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
    --primary:        #1e3a8a;
    --primary-light:  #3b5fc9;
    --primary-soft:   #eef2ff;
    --accent:         #ef4444;
    --bg:             #eef1f6;
    --surface:        #ffffff;
    --border:         #d8dce6;
    --text:           #0f172a;
    --text-soft:      #64748b;
}

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    color: var(--text);
}

.stApp {
    background:
        radial-gradient(circle at 0% 0%, #e0e7ff 0%, transparent 50%),
        radial-gradient(circle at 100% 100%, #fef2f2 0%, transparent 40%),
        var(--bg);
    background-attachment: fixed;
}

.block-container { padding-top: 2rem !important; max-width: 1300px !important; }

/* ── HEADER ── */
.app-header {
    background: linear-gradient(135deg, #0b1d52 0%, #1e3a8a 50%, #3b5fc9 100%);
    border-radius: 20px;
    padding: 24px 30px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow:
        0 10px 30px rgba(15,29,82,0.30),
        inset 0 1px 0 rgba(255,255,255,0.12);
    position: relative;
    overflow: hidden;
}
.app-header::before {
    content: "";
    position: absolute;
    top: -40%; right: -10%;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(255,255,255,0.10) 0%, transparent 70%);
    border-radius: 50%;
}
.app-header-title {
    color: white;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.6px;
    position: relative;
}
.app-header-sub {
    color: rgba(255,255,255,0.72);
    font-size: 13px;
    margin-top: 2px;
    font-weight: 500;
    position: relative;
}

/* ── HOME-KORT ── */
[data-testid="stMarkdownContainer"]:has(.hjem-markør)
    + [data-testid="element-container"] .stButton > button {
    height: 150px !important;
    white-space: pre-line !important;
    background: linear-gradient(160deg, #ffffff 0%, #f8faff 100%) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 18px !important;
    box-shadow:
        0 4px 18px rgba(15,29,82,0.06),
        inset 0 1px 0 rgba(255,255,255,1) !important;
    color: var(--primary) !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    padding: 22px 16px !important;
    line-height: 1.7 !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    position: relative !important;
    overflow: hidden !important;
}
[data-testid="stMarkdownContainer"]:has(.hjem-markør)
    + [data-testid="element-container"] .stButton > button::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--primary), var(--primary-light));
    opacity: 0;
    transition: opacity 0.25s;
}
[data-testid="stMarkdownContainer"]:has(.hjem-markør)
    + [data-testid="element-container"] .stButton > button:hover {
    background: white !important;
    color: var(--primary) !important;
    border-color: var(--primary-light) !important;
    box-shadow: 0 14px 38px rgba(30,58,138,0.20) !important;
    transform: translateY(-6px) !important;
}
[data-testid="stMarkdownContainer"]:has(.hjem-markør)
    + [data-testid="element-container"] .stButton > button:hover::before {
    opacity: 1;
}

/* ── GENERELLE KNAPPER ── */
div.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    transition: all 0.2s !important;
    border: 1.5px solid var(--border) !important;
    background: white !important;
    color: var(--primary) !important;
    box-shadow: 0 1px 3px rgba(15,29,82,0.06) !important;
    padding: 8px 18px !important;
}
div.stButton > button:hover {
    background: var(--primary) !important;
    color: white !important;
    border-color: var(--primary) !important;
    box-shadow: 0 6px 18px rgba(30,58,138,0.28) !important;
    transform: translateY(-1px) !important;
}

/* Form submit-knapper (større) */
.stForm div.stButton > button,
button[kind="formSubmit"] {
    background: linear-gradient(135deg, var(--primary), var(--primary-light)) !important;
    color: white !important;
    border: none !important;
    padding: 12px 24px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(30,58,138,0.30) !important;
    border-radius: 12px !important;
}
.stForm div.stButton > button:hover,
button[kind="formSubmit"]:hover {
    background: linear-gradient(135deg, #16276b, var(--primary)) !important;
    box-shadow: 0 8px 24px rgba(30,58,138,0.40) !important;
    transform: translateY(-2px) !important;
}

/* ── SIDE-HEADER ── */
.side-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 22px;
}
.side-header-ikon {
    font-size: 28px;
    background: linear-gradient(135deg, var(--primary-soft), #dbeafe);
    border-radius: 14px;
    padding: 10px 14px;
    box-shadow: 0 2px 8px rgba(30,58,138,0.10);
}
.side-header-tekst {
    font-size: 24px;
    font-weight: 800;
    color: var(--primary);
    letter-spacing: -0.4px;
}

/* ── BIL-BANNER ── */
.bil-banner {
    background: linear-gradient(135deg, #0b1d52 0%, #1e3a8a 50%, #3b5fc9 100%);
    color: white;
    padding: 18px 24px;
    border-radius: 16px;
    margin-bottom: 22px;
    display: flex;
    align-items: center;
    gap: 18px;
    box-shadow:
        0 8px 24px rgba(15,29,82,0.25),
        inset 0 1px 0 rgba(255,255,255,0.10);
    position: relative;
    overflow: hidden;
}
.bil-banner::after {
    content: "";
    position: absolute;
    top: 0; right: 0;
    width: 200px; height: 100%;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
}
.bil-banner .bil-ikon {
    font-size: 38px;
    background: rgba(255,255,255,0.15);
    border-radius: 12px;
    padding: 6px 12px;
    backdrop-filter: blur(10px);
}
.bil-banner .bil-navn  { font-size: 22px; font-weight: 800; letter-spacing: -0.3px; }
.bil-banner .bil-reg   { font-size: 13px; opacity: 0.85; margin-top: 3px; font-weight: 500; }

/* ── SKJEMA-SEKSJON ── */
.form-section-title {
    font-size: 11px;
    font-weight: 700;
    color: var(--text-soft);
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1.5px solid #e8eaf0;
}

/* ── ROLLE-BADGE ── */
.rolle-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.5px;
    margin-left: 8px;
    vertical-align: middle;
    text-transform: uppercase;
}
.rolle-admin      { background: linear-gradient(135deg, #fef3c7, #fde68a); color: #92400e; }
.rolle-instruktør { background: linear-gradient(135deg, #dbeafe, #bfdbfe); color: var(--primary); }

/* ── INFO-KORT (ruter) ── */
.info-card {
    background: white;
    padding: 14px 20px;
    border-radius: 12px;
    border-left: 4px solid var(--primary-light);
    box-shadow: 0 2px 8px rgba(15,29,82,0.06);
    margin-bottom: 10px;
    font-weight: 600;
    color: var(--primary);
}

/* ── STATUS-KORT ── */
.status-kort {
    border-radius: 14px;
    padding: 18px 16px;
    text-align: center;
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 6px;
    transition: transform 0.2s;
}
.status-kort:hover { transform: translateY(-2px); }
.status-ok {
    background: linear-gradient(135deg, #d1fae5, #a7f3d0);
    color: #065f46;
    border: 1.5px solid #6ee7b7;
    box-shadow: 0 4px 14px rgba(6,95,70,0.15);
}
.status-mangler {
    background: linear-gradient(135deg, #fee2e2, #fecaca);
    color: #991b1b;
    border: 1.5px solid #fca5a5;
    box-shadow: 0 4px 14px rgba(153,27,27,0.15);
}

/* ── INNLOGGET-BAR ── */
.innlogget-bar {
    background: linear-gradient(135deg, white, #f8faff);
    border-radius: 12px;
    padding: 11px 18px;
    display: flex;
    align-items: center;
    gap: 10px;
    border: 1.5px solid var(--border);
    box-shadow: 0 2px 8px rgba(15,29,82,0.06);
    font-size: 14px;
    font-weight: 600;
    color: var(--primary);
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: white;
    border-radius: 12px;
    padding: 5px;
    border: 1.5px solid var(--border);
    box-shadow: 0 1px 4px rgba(15,29,82,0.04);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 8px 18px !important;
    color: var(--text-soft) !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: var(--primary) !important;
    color: white !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader,
[data-testid="stExpander"] summary {
    background: white !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    border: 1.5px solid var(--border) !important;
    padding: 12px 18px !important;
}

/* ── INPUT-FELT ── */
.stTextInput > div > div,
.stTextArea > div > div,
.stNumberInput > div > div,
.stDateInput > div > div {
    background: white !important;
    border: 2px solid #c1c9d6 !important;
    border-radius: 10px !important;
    box-shadow:
        0 1px 2px rgba(15,29,82,0.04),
        inset 0 1px 2px rgba(15,29,82,0.04) !important;
    transition: all 0.2s !important;
}
.stTextInput > div > div:hover,
.stTextArea > div > div:hover,
.stNumberInput > div > div:hover,
.stDateInput > div > div:hover {
    border-color: var(--primary-light) !important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
    background: transparent !important;
    border: none !important;
    color: var(--text) !important;
    font-size: 15px !important;
    font-weight: 500 !important;
}
.stTextInput > div > div:focus-within,
.stTextArea > div > div:focus-within,
.stNumberInput > div > div:focus-within,
.stDateInput > div > div:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 4px rgba(30,58,138,0.18) !important;
}

/* Labels */
.stTextInput label, .stTextArea label,
.stNumberInput label, .stDateInput label,
.stSelectbox label {
    font-weight: 600 !important;
    font-size: 13px !important;
    color: var(--primary) !important;
    margin-bottom: 4px !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: white !important;
    border: 2px solid #c1c9d6 !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 2px rgba(15,29,82,0.04) !important;
    cursor: pointer !important;
    min-height: 46px !important;
    transition: all 0.2s !important;
}
.stSelectbox > div > div:hover {
    border-color: var(--primary-light) !important;
}
.stSelectbox > div > div:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 4px rgba(30,58,138,0.18) !important;
}

/* Checkbox */
.stCheckbox label {
    font-weight: 500 !important;
    font-size: 14px !important;
}

/* ── DATAFRAME ── */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    border: 1.5px solid var(--border);
    box-shadow: 0 2px 10px rgba(15,29,82,0.06);
}

/* ── ALERT-BOKSER ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-width: 1.5px !important;
    box-shadow: 0 2px 10px rgba(15,29,82,0.06) !important;
    font-weight: 500 !important;
}

/* ── DIVIDER ── */
hr { border-color: var(--border) !important; opacity: 0.6 !important; }

/* skjul streamlit-elementer ── */
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
</style>
""", unsafe_allow_html=True)

# --- 2. AUTENTISERING ---
hashed = [bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode() for pw in ["instruktør123", "admin123"]]

CONFIG = {
    "credentials": {
        "usernames": {
            "instruktør": {"name": "Instruktør", "password": hashed[0], "rolle": "instruktør"},
            "admin":      {"name": "Administrator", "password": hashed[1], "rolle": "admin"}
        }
    },
    "cookie": {"name": "utrykk_auth", "key": "utrykk_secret_2024", "expiry_days": 1}
}

authenticator = stauth.Authenticate(
    CONFIG["credentials"],
    CONFIG["cookie"]["name"],
    CONFIG["cookie"]["key"],
    CONFIG["cookie"]["expiry_days"]
)

# --- 3. DATA ---
FIL_TURER    = "logg_turer.csv"
FIL_DAGSJEKK = "logg_dagsjekk.csv"
FIL_ATK      = "logg_atk.csv"
FIL_RUTER    = "kjøreruter.csv"
FIL_POSISJON = "bil_posisjoner.csv"

FIL_BILER = "biler.csv"

def last_biler():
    """Les bil-konfig. Opprett standard hvis tom."""
    df = les_csv(FIL_BILER)
    if df.empty:
        std = pd.DataFrame([
            {"Bil": f"Bil {i}", "Reg_nr": r, "Operativ": "Ja" if r else "Nei"}
            for i, r in enumerate(
                ["AA 12345","BB 23456","CC 34567","","","","","","",""], start=1)
        ])
        if _bruk_sheets():
            try:
                ark = _hent_ark(FIL_BILER, opprett_hvis_mangler=True)
                ark.clear()
                ark.update([std.columns.tolist()] + std.astype(str).values.tolist())
            except Exception as e:
                st.warning(f"Kunne ikke opprette bilregister i Sheets: {e}. "
                           f"Bruker standardliste i denne økten.")
        else:
            std.to_csv(FIL_BILER, index=False, encoding="utf-8-sig")
        return std
    return df.astype(str).fillna("")

def aktive_biler():
    """Returner ordbok {bilnavn: regnr} for operative biler."""
    df = last_biler()
    df = df[df['Operativ'].astype(str).str.strip().str.lower().isin(["ja", "true", "1", "yes"])]
    return dict(zip(df['Bil'], df['Reg_nr']))

def alle_biler():
    """Returner ordbok {bilnavn: regnr} for ALLE biler (også ikke-operative)."""
    df = last_biler()
    return dict(zip(df['Bil'], df['Reg_nr']))

POLITIDISTRIKT = ["Oslo","Øst","Innlandet","Sør-Øst","Agder","Sør-Vest","Vest",
                  "Møre og Romsdal","Trøndelag","Nordland","Troms","Finnmark"]
FYLKER = {"Innlandet":"34","Oslo":"03","Trøndelag":"50","Rogaland":"11",
          "Vestland":"46","Agder":"42","Møre og Romsdal":"15","Nordland":"18","Finnmark":"56"}

# --- 4. HJELPEFUNKSJONER ---
# ── GOOGLE SHEETS-INTEGRASJON ─────────────────────────────────────
# Hvis [gcp_service_account] og [google_sheets].sheet_id er satt i
# Streamlit secrets, lagres alle data i Google Sheets. Hvert "filnavn"
# blir et eget ark (worksheet) i samme regneark.
# Hvis ikke konfigurert, faller appen tilbake til lokale CSV-filer.

def _bruk_sheets():
    try:
        return ("gcp_service_account" in st.secrets and
                "google_sheets" in st.secrets and
                "sheet_id" in st.secrets["google_sheets"])
    except Exception:
        return False

@st.cache_resource(show_spinner=False)
def _sheets_klient():
    import gspread
    from google.oauth2.service_account import Credentials
    scopes = ["https://www.googleapis.com/auth/spreadsheets",
              "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=scopes)
    gc = gspread.authorize(creds)
    return gc.open_by_key(st.secrets["google_sheets"]["sheet_id"])

def _ark_navn(filnavn):
    return os.path.splitext(os.path.basename(filnavn))[0]

def _hent_ark(filnavn, opprett_hvis_mangler=True):
    sh = _sheets_klient()
    navn = _ark_navn(filnavn)
    try:
        return sh.worksheet(navn)
    except Exception:
        if opprett_hvis_mangler:
            return sh.add_worksheet(title=navn, rows=1000, cols=30)
        return None

def les_csv(filnavn):
    """Robust leser — Sheets hvis tilgjengelig, ellers lokal CSV."""
    if _bruk_sheets():
        try:
            ark = _hent_ark(filnavn, opprett_hvis_mangler=False)
            if ark is None:
                return pd.DataFrame()
            verdier = ark.get_all_values()
            if not verdier:
                return pd.DataFrame()
            head, *rader = verdier
            return pd.DataFrame(rader, columns=head)
        except Exception as e:
            st.warning(f"Kunne ikke lese {filnavn} fra Google Sheets: {e}")
            return pd.DataFrame()
    if not os.path.exists(filnavn):
        return pd.DataFrame()
    try:
        return pd.read_csv(filnavn, engine='python', on_bad_lines='skip')
    except Exception:
        return pd.DataFrame()

def lagre_data(data, filnavn):
    """Lagrer ny rad — til Sheets hvis konfigurert, ellers lokal CSV."""
    ny_rad = pd.DataFrame([{k: ("" if pd.isna(v) else v) for k, v in data.items()}])
    eksisterende = les_csv(filnavn)
    samlet = pd.concat([eksisterende, ny_rad], ignore_index=True, sort=False)
    samlet = samlet.fillna("")

    if _bruk_sheets():
        try:
            ark = _hent_ark(filnavn, opprett_hvis_mangler=True)
            ark.clear()
            ark.update([samlet.columns.tolist()] + samlet.astype(str).values.tolist())
            return
        except Exception as e:
            st.warning(f"Sheets-skriving feilet for {filnavn}: {e}. Lagrer lokalt.")

    samlet.to_csv(filnavn, index=False, encoding="utf-8-sig")

def oppdater_posisjon(bil, lat, lon):
    data = {"Bil": bil, "Tid": datetime.now().strftime("%H:%M"), "Lat": lat, "Lon": lon}
    df = les_csv(FIL_POSISJON)
    if not df.empty and "Bil" in df.columns:
        df = df[df['Bil'] != bil]
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True, sort=False).fillna("")
    if _bruk_sheets():
        try:
            ark = _hent_ark(FIL_POSISJON, opprett_hvis_mangler=True)
            ark.clear()
            ark.update([df.columns.tolist()] + df.astype(str).values.tolist())
            return
        except Exception:
            pass
    df.to_csv(FIL_POSISJON, index=False, encoding="utf-8-sig")

def sjekk_dagsjekk_status(bil_navn):
    try:
        df = les_csv(FIL_DAGSJEKK)
        if df.empty or "Dato" not in df.columns or "Bil" not in df.columns:
            return False
        return not df[(df['Bil'] == bil_navn) &
                      (df['Dato'].astype(str).str.strip().str[:10] == str(date.today()))].empty
    except Exception:
        return False

@st.cache_data(ttl=60)
def hent_stedsnavn(lat, lon):
    try:
        res = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json"},
            headers={"User-Agent": "UtrykningsskolenApp/1.0"},
            timeout=5)
        if res.status_code == 200:
            d = res.json()
            a = d.get("address", {})
            deler = [a.get("road"), a.get("house_number"), a.get("city") or a.get("town") or a.get("village")]
            return ", ".join(x for x in deler if x)
    except:
        pass
    return None

@st.cache_data(ttl=300)
def hent_veimeldinger(f_id):
    try:
        res = requests.get(f"https://webapi.vegvesen.no/api/v1/trafikkmeldinger?fylke={f_id}", timeout=5)
        return res.json() if res.status_code == 200 else []
    except: return []

def vis_bil_banner(bil_navn):
    reg = alle_biler().get(bil_navn, "")
    st.markdown(f"""
        <div class="bil-banner">
            <div class="bil-ikon">🚑</div>
            <div>
                <div class="bil-navn">{bil_navn}</div>
                <div class="bil-reg">Reg.nr: {reg}</div>
            </div>
        </div>""", unsafe_allow_html=True)

def hent_rolle():
    return CONFIG["credentials"]["usernames"].get(
        st.session_state.get("username", ""), {}).get("rolle", "")

def vis_posisjonskart(lat, lon, bil_navn, høyde=220):
    m = folium.Map(location=[lat, lon], zoom_start=15, tiles="CartoDB positron")
    folium.Marker(
        [lat, lon],
        popup=f"<b>{bil_navn}</b><br>{lat:.5f}, {lon:.5f}",
        tooltip=bil_navn,
        icon=folium.Icon(color="blue", icon="ambulance", prefix="fa")
    ).add_to(m)
    st_folium(m, width="100%", height=høyde, returned_objects=[])

def vis_side_header(ikon, tittel):
    st.markdown(f"""
        <div class="side-header">
            <div class="side-header-ikon">{ikon}</div>
            <div class="side-header-tekst">{tittel}</div>
        </div>""", unsafe_allow_html=True)

def filtrer_periode(df, fra_dato, til_dato):
    """Filtrer DataFrame mellom to datoer (inklusiv)."""
    if df.empty or "Dato" not in df.columns:
        return df
    df = df.copy()
    df['_d'] = pd.to_datetime(df['Dato'].astype(str).str.strip().str[:10], errors='coerce').dt.date
    df = df[(df['_d'] >= fra_dato) & (df['_d'] <= til_dato)]
    return df.drop(columns=['_d'])

def lag_pdf_rapport(fra_dato, til_dato, bil_filter, periodenavn):
    """Generer ryddig, operativt fokusert PDF-rapport."""
    import math
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=14*mm, bottomMargin=14*mm,
        title=f"Utrykningsskolen - {periodenavn}"
    )
    SIDEBREDDE = 180  # mm tilgjengelig

    # ── FARGEPALETT ───────────────────────────────────────────────
    NAVY        = colors.HexColor("#1e3a8a")
    NAVY_DARK   = colors.HexColor("#0b1d52")
    NAVY_LIGHT  = colors.HexColor("#3b5fc9")
    ACCENT      = colors.HexColor("#dc2626")
    SUCCESS     = colors.HexColor("#059669")
    SOFT_BG     = colors.HexColor("#f8fafc")
    LIGHT_BG    = colors.HexColor("#eef2ff")
    GREY_BG     = colors.HexColor("#f1f5f9")
    GREY_BORDER = colors.HexColor("#e2e8f0")
    TEXT        = colors.HexColor("#0f172a")
    TEXT_SOFT   = colors.HexColor("#64748b")

    # ── TEKSTSTILER ───────────────────────────────────────────────
    H1 = ParagraphStyle('H1', fontSize=24, leading=28, textColor=NAVY,
        fontName='Helvetica-Bold', spaceAfter=0)
    H2 = ParagraphStyle('H2', fontSize=12, leading=15, textColor=NAVY,
        fontName='Helvetica-Bold', spaceBefore=16, spaceAfter=8,
        letterSpacing=0.5)
    SUB = ParagraphStyle('SUB', fontSize=10, textColor=TEXT_SOFT,
        fontName='Helvetica', spaceAfter=10)
    BODY = ParagraphStyle('BODY', fontSize=10, leading=13, textColor=TEXT)
    SMALL = ParagraphStyle('SMALL', fontSize=8.5, leading=11, textColor=TEXT)
    CELL = ParagraphStyle('CELL', fontSize=8.5, leading=11, textColor=TEXT)
    META = ParagraphStyle('META', fontSize=8, textColor=TEXT_SOFT)

    flow = []

    # ── HJELPEFUNKSJONER ─────────────────────────────────────────
    def beregn_minutter(start, slutt):
        try:
            s = str(start).strip().replace(".", ":")[:5]
            e = str(slutt).strip().replace(".", ":")[:5]
            sh, sm = int(s.split(":")[0]), int(s.split(":")[1])
            eh, em = int(e.split(":")[0]), int(e.split(":")[1])
            min = (eh * 60 + em) - (sh * 60 + sm)
            return min if min > 0 else 0
        except Exception:
            return 0

    def skoletimer(minutter):
        return math.ceil((minutter / 45.0) * 2) / 2.0

    def fmt_skoletime(n):
        return f"{n:.1f}".replace(".0", "")

    def seksjonshode(ikon, tittel, undertittel=""):
        """Visuell seksjonsoverskrift med farget bånd til venstre."""
        undert = (f"<br/><font color='#64748b' size='9'>{undertittel}</font>"
                  if undertittel else "")
        return Table([[
            Paragraph(f"<font color='#1e3a8a' size='13'><b>{ikon}  {tittel}</b></font>{undert}",
                      BODY)
        ]], colWidths=[SIDEBREDDE*mm], style=TableStyle([
            ('BACKGROUND',  (0, 0), (-1, -1), LIGHT_BG),
            ('LEFTPADDING', (0, 0), (-1, -1), 14),
            ('RIGHTPADDING',(0, 0), (-1, -1), 14),
            ('TOPPADDING',  (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 9),
            ('LINEBEFORE',  (0, 0), (0, -1), 4, NAVY),
        ]))

    # ── HENT OG FILTRER DATA ──────────────────────────────────────
    df_t = filtrer_periode(les_csv(FIL_TURER), fra_dato, til_dato)
    df_a = filtrer_periode(les_csv(FIL_ATK), fra_dato, til_dato)
    if bil_filter != "Alle":
        if not df_t.empty: df_t = df_t[df_t.get('Bil', '') == bil_filter]
        if not df_a.empty: df_a = df_a[df_a.get('Bil', '') == bil_filter]

    # Periode-tekst
    no_måneder = {1:"januar",2:"februar",3:"mars",4:"april",5:"mai",6:"juni",
                  7:"juli",8:"august",9:"september",10:"oktober",
                  11:"november",12:"desember"}
    if fra_dato == til_dato:
        periode_tekst = f"{fra_dato.day}. {no_måneder[fra_dato.month]} {fra_dato.year}"
    else:
        periode_tekst = (f"{fra_dato.day}. {no_måneder[fra_dato.month]} "
                         f"– {til_dato.day}. {no_måneder[til_dato.month]} {til_dato.year}")
    bil_tekst = bil_filter if bil_filter != "Alle" else "Alle operative biler"

    # ── HEADER ─────────────────────────────────────────────────────
    header_inner = Table([
        [Paragraph("<font color='white' size='18'><b>🚑 Utrykningsskolen</b></font>", BODY),
         Paragraph(f"<font color='#cbd5e1' size='9'>"
                   f"Generert {datetime.now().strftime('%d.%m.%Y · %H:%M')}</font>",
                   ParagraphStyle('R', alignment=TA_RIGHT))],
        [Paragraph(f"<font color='white' size='13'><b>{periodenavn}</b></font>"
                   f"<br/><font color='#a5b4fc' size='9'>{periode_tekst}</font>",
                   ParagraphStyle('HW', textColor=colors.white)),
         Paragraph(f"<font color='#a5b4fc' size='9'>FILTER</font><br/>"
                   f"<font color='white' size='11'><b>{bil_tekst}</b></font>",
                   ParagraphStyle('HW2', alignment=TA_RIGHT))],
    ], colWidths=[110*mm, 70*mm])
    header_inner.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, -1), NAVY_DARK),
        ('VALIGN',      (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 18),
        ('RIGHTPADDING',(0, 0), (-1, -1), 18),
        ('TOPPADDING',  (0, 0), (0, 0), 14),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 8),
        ('TOPPADDING',  (0, 1), (-1, 1), 2),
        ('BOTTOMPADDING',(0, 1), (-1, 1), 14),
    ]))
    flow.append(header_inner)
    flow.append(Spacer(1, 12))

    # ── NØKKELTALL ────────────────────────────────────────────────
    antall_turer = len(df_t)
    antall_atk   = len(df_a)
    km_total = 0
    total_min = 0

    if not df_t.empty:
        if "Km_start" in df_t.columns:
            for bil, grp in df_t.groupby('Bil'):
                km_alle = pd.concat([
                    pd.to_numeric(grp.get('Km_start'), errors='coerce'),
                    pd.to_numeric(grp.get('Km_slutt'), errors='coerce')
                ]).dropna()
                if len(km_alle) >= 2:
                    km_total += int(km_alle.max() - km_alle.min())
        for _, r in df_t.iterrows():
            total_min += beregn_minutter(r.get("Starttid",""), r.get("Sluttid",""))

    total_skoletimer = skoletimer(total_min) if total_min else 0

    def nokkel_kort(verdi, etikett, ikon, accent_color):
        return Table([
            [Paragraph(f"<font color='{accent_color}' size='9'><b>{ikon} {etikett.upper()}</b></font>", BODY)],
            [Paragraph(f"<font color='#0f172a' size='22'><b>{verdi}</b></font>", BODY)],
        ], colWidths=[42*mm], style=TableStyle([
            ('BACKGROUND',  (0, 0), (-1, -1), colors.white),
            ('BOX',         (0, 0), (-1, -1), 0.6, GREY_BORDER),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING',(0, 0), (-1, -1), 12),
            ('TOPPADDING',  (0, 0), (0, 0), 10),
            ('BOTTOMPADDING',(0, 0), (0, 0), 2),
            ('TOPPADDING',  (0, 1), (0, 1), 0),
            ('BOTTOMPADDING',(0, 1), (0, 1), 12),
            ('LINEABOVE',   (0, 0), (-1, 0), 3, NAVY_LIGHT),
        ]))

    nokkel_rad = Table([[
        nokkel_kort(antall_turer, "Kjøreturer", "🚗", "#1e3a8a"),
        nokkel_kort(fmt_skoletime(total_skoletimer), "Skoletimer", "🎓", "#1e3a8a"),
        nokkel_kort(f"{km_total}" if km_total else "—", "Km kjørt", "📍", "#059669"),
        nokkel_kort(antall_atk, "ATK-pass.", "📸", "#dc2626"),
    ]], colWidths=[45*mm, 45*mm, 45*mm, 45*mm])
    nokkel_rad.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
    flow.append(nokkel_rad)

    # ── PER-BIL SAMMENDRAG (bare ved Alle) ────────────────────────
    if bil_filter == "Alle" and not df_t.empty and "Bil" in df_t.columns:
        biler_brukt = sorted(df_t['Bil'].dropna().unique().tolist())
        if len(biler_brukt) > 1:
            flow.append(seksjonshode("🚘", "Sammendrag per bil"))
            rader = [["Bil", "Reg.nr", "Turer", "Km", "Skoletimer", "Elever"]]
            biler_konfig = alle_biler()
            for bil in biler_brukt:
                grp = df_t[df_t['Bil'] == bil]
                km_b = 0
                if "Km_start" in grp.columns:
                    km_alle = pd.concat([
                        pd.to_numeric(grp.get('Km_start'), errors='coerce'),
                        pd.to_numeric(grp.get('Km_slutt'), errors='coerce')
                    ]).dropna()
                    if len(km_alle) >= 2:
                        km_b = int(km_alle.max() - km_alle.min())
                min_b = sum(beregn_minutter(r.get("Starttid",""), r.get("Sluttid",""))
                           for _, r in grp.iterrows())
                elever = grp['Elev'].dropna().astype(str).str.strip()
                elever = elever[elever != ""].nunique() if "Elev" in grp.columns else 0
                rader.append([
                    Paragraph(f"<b>{bil}</b>", CELL),
                    Paragraph(biler_konfig.get(bil, "—"), CELL),
                    Paragraph(str(len(grp)), CELL),
                    Paragraph(f"{km_b} km" if km_b else "—", CELL),
                    Paragraph(f"<b>{fmt_skoletime(skoletimer(min_b))}</b>", CELL),
                    Paragraph(str(elever), CELL),
                ])
            tbl = Table(rader, colWidths=[28*mm, 30*mm, 22*mm, 30*mm, 35*mm, 35*mm],
                        repeatRows=1)
            tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), NAVY),
                ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
                ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE',   (0, 0), (-1, 0), 9),
                ('ALIGN',      (2, 0), (-1, -1), 'CENTER'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, SOFT_BG]),
                ('LINEBELOW',  (0, 0), (-1, -1), 0.3, GREY_BORDER),
                ('BOX',        (0, 0), (-1, -1), 0.6, GREY_BORDER),
                ('LEFTPADDING',(0, 0), (-1, -1), 9),
                ('RIGHTPADDING',(0, 0), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING',(0, 0), (-1, -1), 7),
                ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            flow.append(tbl)

    # Beregn skoletimer (vises kompakt nederst)
    elev_timer = {}
    if not df_t.empty and "Elev" in df_t.columns:
        for _, r in df_t.iterrows():
            elev = str(r.get("Elev", "")).strip()
            if not elev or elev.lower() == "nan":
                continue
            m = beregn_minutter(r.get("Starttid", ""), r.get("Sluttid", ""))
            elev_timer[elev] = elev_timer.get(elev, 0) + m

    # ── KJØRETURER ────────────────────────────────────────────────
    flow.append(seksjonshode("📝", "Kjøreturer", f"Totalt {antall_turer} oppføring(er)"))
    if df_t.empty:
        flow.append(Paragraph("<i>Ingen turer registrert i denne perioden.</i>", BODY))
    else:
        kolonner = [("Dato","Dato"),("Bil","Bil"),
                    ("Starttid","Start"),("Sluttid","Slutt"),
                    ("Elev","Elev"),("Instruktør","Instruktør"),
                    ("Fra","Fra"),("Til","Til"),
                    ("Km_start","Km fra"),("Km_slutt","Km til")]
        synlige = [(k, v) for k, v in kolonner if k in df_t.columns]
        head = [Paragraph(f"<font color='white'><b>{v}</b></font>", CELL) for _, v in synlige]
        rader = [head]
        df_t_sortert = df_t.copy()
        if "Dato" in df_t_sortert.columns:
            df_t_sortert = df_t_sortert.sort_values(by=['Dato'] +
                (['Starttid'] if 'Starttid' in df_t_sortert.columns else []))
        for _, r in df_t_sortert.iterrows():
            rad = []
            for k, _ in synlige:
                val = r.get(k, "")
                if pd.isna(val): val = ""
                if k == "Dato":
                    val = str(val)[:10]
                rad.append(Paragraph(str(val), CELL))
            rader.append(rad)
        kol_bredder = [20*mm, 16*mm, 13*mm, 13*mm, 28*mm, 26*mm, 22*mm, 22*mm, 13*mm, 13*mm]
        kol_bredder = kol_bredder[:len(synlige)]
        sum_b = sum(kol_bredder)
        if sum_b < SIDEBREDDE:
            kol_bredder[4 if len(synlige) > 4 else -1] += (SIDEBREDDE - sum_b)
        tbl = Table(rader, colWidths=kol_bredder, repeatRows=1)
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('FONTSIZE',   (0, 0), (-1, 0), 8.5),
            ('ALIGN',      (0, 0), (-1, 0), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, SOFT_BG]),
            ('LINEBELOW',  (0, 0), (-1, -1), 0.3, GREY_BORDER),
            ('BOX',        (0, 0), (-1, -1), 0.6, GREY_BORDER),
            ('LEFTPADDING',(0, 0), (-1, -1), 6),
            ('RIGHTPADDING',(0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 6),
            ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        flow.append(tbl)

    # ── ATK ────────────────────────────────────────────────────────
    flow.append(seksjonshode("📸", "ATK-passeringer", f"Totalt {antall_atk} oppføring(er)"))
    if df_a.empty:
        flow.append(Paragraph("<i>Ingen ATK-passeringer registrert i denne perioden.</i>", BODY))
    else:
        kolonner = [("Dato","Dato"),("Tid","Tid"),("Bil","Bil"),
                    ("Sjåfør","Sjåfør"),("Instruktør","Instruktør"),("Sted","Sted")]
        synlige = [(k, v) for k, v in kolonner if k in df_a.columns]
        head = [Paragraph(f"<font color='white'><b>{v}</b></font>", CELL) for _, v in synlige]
        rader = [head]
        df_a_sortert = df_a.copy()
        if "Dato" in df_a_sortert.columns:
            df_a_sortert = df_a_sortert.sort_values(by=['Dato'] +
                (['Tid'] if 'Tid' in df_a_sortert.columns else []))
        for _, r in df_a_sortert.iterrows():
            rad = []
            for k, _ in synlige:
                val = r.get(k, "")
                if pd.isna(val): val = ""
                if k == "Dato":
                    val = str(val)[:10]
                rad.append(Paragraph(str(val), CELL))
            rader.append(rad)
        kol_bredder = [22*mm, 15*mm, 18*mm, 32*mm, 32*mm, 61*mm]
        kol_bredder = kol_bredder[:len(synlige)]
        sum_b = sum(kol_bredder)
        if sum_b < SIDEBREDDE:
            kol_bredder[-1] += (SIDEBREDDE - sum_b)
        tbl = Table(rader, colWidths=kol_bredder, repeatRows=1)
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
            ('FONTSIZE',   (0, 0), (-1, 0), 8.5),
            ('ALIGN',      (0, 0), (-1, 0), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, SOFT_BG]),
            ('LINEBELOW',  (0, 0), (-1, -1), 0.3, GREY_BORDER),
            ('BOX',        (0, 0), (-1, -1), 0.6, GREY_BORDER),
            ('LEFTPADDING',(0, 0), (-1, -1), 6),
            ('RIGHTPADDING',(0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 6),
            ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        flow.append(tbl)

    # ── SKOLETIMER PER ELEV (kompakt, nederst) ────────────────────
    if elev_timer:
        flow.append(Spacer(1, 14))
        flow.append(Paragraph(
            f"<font color='#64748b' size='9'><b>🎓 SKOLETIMER PER ELEV</b> &nbsp;·&nbsp; "
            f"<font size='8'>1 skoletime = 45 min, rundet opp til nærmeste halve</font></font>",
            BODY))
        flow.append(Spacer(1, 4))
        rader = [[
            Paragraph("<font color='white' size='8'><b>ELEV</b></font>", CELL),
            Paragraph("<font color='white' size='8'><b>TURER</b></font>", CELL),
            Paragraph("<font color='white' size='8'><b>TID</b></font>", CELL),
            Paragraph("<font color='white' size='8'><b>SKOLETIMER</b></font>", CELL),
        ]]
        for elev, min_total in sorted(elev_timer.items(), key=lambda x: -x[1]):
            antall = len(df_t[df_t["Elev"].astype(str).str.strip() == elev])
            t_str  = f"{int(min_total/60)}t {int(min_total % 60)}m"
            sk_str = fmt_skoletime(skoletimer(min_total))
            rader.append([
                Paragraph(f"<font size='8.5'>{elev}</font>", CELL),
                Paragraph(f"<font size='8.5'>{antall}</font>", CELL),
                Paragraph(f"<font size='8.5'>{t_str}</font>", CELL),
                Paragraph(f"<font color='#1e3a8a' size='9'><b>{sk_str}</b></font>", CELL),
            ])
        tbl = Table(rader, colWidths=[78*mm, 25*mm, 35*mm, 42*mm], repeatRows=1)
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('ALIGN',      (1, 0), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, SOFT_BG]),
            ('LINEBELOW',  (0, 0), (-1, -1), 0.3, GREY_BORDER),
            ('BOX',        (0, 0), (-1, -1), 0.5, GREY_BORDER),
            ('LEFTPADDING',(0, 0), (-1, -1), 8),
            ('RIGHTPADDING',(0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
            ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        flow.append(tbl)

    # ── FOOTER ─────────────────────────────────────────────────────
    flow.append(Spacer(1, 20))
    flow.append(Table([[
        Paragraph(f"<font color='#94a3b8' size='8'>🚑 Utrykningsskolen · "
                  f"Konfidensielt internt dokument</font>", META),
        Paragraph(f"<font color='#94a3b8' size='8'>"
                  f"{datetime.now().strftime('%d.%m.%Y · %H:%M')}</font>",
                  ParagraphStyle('F', alignment=TA_RIGHT))
    ]], colWidths=[120*mm, 60*mm], style=TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, GREY_BORDER),
        ('TOPPADDING',(0, 0), (-1, -1), 8),
    ])))

    doc.build(flow)
    buf.seek(0)
    return buf.getvalue()

def vis_km_oversikt(dato, bil_filter):
    """Beregn kjørte km per bil for valgt dato (siste minus første km-avlesning)."""
    df = les_csv(FIL_TURER)
    if df.empty or "Km_start" not in df.columns or "Dato" not in df.columns:
        return
    df = df[df['Dato'].astype(str).str.strip().str[:10] == str(dato)[:10]]
    if bil_filter != "Alle":
        df = df[df['Bil'] == bil_filter]
    if df.empty:
        return

    rader = []
    for bil, grp in df.groupby('Bil'):
        km_alle = pd.concat([
            pd.to_numeric(grp.get('Km_start'), errors='coerce'),
            pd.to_numeric(grp.get('Km_slutt'), errors='coerce')
        ]).dropna()
        if len(km_alle) >= 2:
            min_km, max_km = int(km_alle.min()), int(km_alle.max())
            rader.append((bil, min_km, max_km, max_km - min_km))
        elif len(km_alle) == 1:
            rader.append((bil, int(km_alle.iloc[0]), None, None))

    if not rader:
        return

    st.markdown("""<div style='font-size:13px; font-weight:700; color:#6b7280;
        text-transform:uppercase; letter-spacing:.8px; margin:6px 0 10px;'>
        Kilometer kjørt</div>""", unsafe_allow_html=True)
    cols = st.columns(len(rader))
    for col, (bil, mn, mx, diff) in zip(cols, rader):
        if diff is not None:
            col.markdown(f"""<div style='background:linear-gradient(135deg,#eef2ff,#dbeafe);
                border:1.5px solid #c7d2fe; border-radius:14px; padding:14px 16px; text-align:center;
                box-shadow:0 2px 10px rgba(30,58,138,0.10);'>
                <div style='font-size:12px;color:#6b7280;font-weight:600;text-transform:uppercase;letter-spacing:.5px;'>{bil}</div>
                <div style='font-size:30px;font-weight:800;color:#1e3a8a;line-height:1.2;margin:4px 0;'>{diff} <span style='font-size:14px;font-weight:600;color:#6b7280;'>km</span></div>
                <div style='font-size:12px;color:#6b7280;'>{mn:,} → {mx:,}</div>
            </div>""".replace(",", " "), unsafe_allow_html=True)
        else:
            col.markdown(f"""<div style='background:#fff7ed;border:1.5px solid #fed7aa;
                border-radius:14px;padding:14px 16px;text-align:center;'>
                <div style='font-size:12px;color:#9a3412;font-weight:600;text-transform:uppercase;'>{bil}</div>
                <div style='font-size:14px;color:#9a3412;margin-top:6px;'>Mangler en avlesning</div>
                <div style='font-size:12px;color:#6b7280;margin-top:2px;'>Første: {mn:,} km</div>
            </div>""".replace(",", " "), unsafe_allow_html=True)

def vis_rapport_tabell(fil, dato, bil_filter):
    df = les_csv(fil)
    if df.empty or "Dato" not in df.columns:
        st.info("Ingen data registrert ennå.")
        return
    df = df[df['Dato'].astype(str).str.strip().str[:10] == str(dato)[:10]]
    if bil_filter != "Alle" and "Bil" in df.columns:
        df = df[df['Bil'] == bil_filter]
    if df.empty:
        st.info("Ingen data for valgt dato/bil.")
        return
    rekkefølge = [
        "Tid", "Starttid", "Sluttid",
        "Bil", "Reg_nr",
        "Elev", "Sjåfør", "Instruktør", "Kontrollør",
        "Fra", "Til", "Sted",
        "Km_start", "Km_slutt",
        "Status", "Mønster",
        "Merknad",
    ]
    skjult = {"Lat", "Lon", "Dato"}
    synlige = [c for c in rekkefølge if c in df.columns]
    rest = [c for c in df.columns if c not in synlige and c not in skjult]
    st.dataframe(df[synlige + rest], use_container_width=True, hide_index=True)
    col_a, col_b = st.columns([3, 1])
    col_a.caption(f"{len(df)} oppføring(er) — {bil_filter if bil_filter != 'Alle' else 'alle biler'}")
    csv = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    fil_navn = os.path.splitext(os.path.basename(fil))[0]
    col_b.download_button("⬇️ Last ned CSV", csv,
        file_name=f"rapport_{fil_navn}_{dato}_{bil_filter}.csv",
        mime="text/csv",
        key=f"dl_csv_{fil_navn}_{dato}_{bil_filter}")

# --- 5. NAVIGASJON ---
if 'side' not in st.session_state: st.session_state.side = "Hjem"
def gå_til(s): st.session_state.side = s; st.rerun()

# ================================================================
# TOPPMENY
# ================================================================
er_innlogget = st.session_state.get("authentication_status")
rolle = hent_rolle() if er_innlogget else ""

header_l, header_r = st.columns([5, 3])
with header_l:
    st.markdown("""
        <div class="app-header" style="padding:18px 24px;">
            <div>
                <div class="app-header-title">🚑 Utrykningsskolen</div>
                <div class="app-header-sub">Kjøreregistrering og flåtestyring</div>
            </div>
        </div>""", unsafe_allow_html=True)

with header_r:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if er_innlogget:
        badge = "rolle-admin" if rolle == "admin" else "rolle-instruktør"
        st.markdown(
            f"<div class='innlogget-bar'>👤 {st.session_state['name']}"
            f"<span class='rolle-badge {badge}'>{rolle.upper()}</span></div>",
            unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        if b1.button("📊 Rapport", use_container_width=True): gå_til("Rapport")
        authenticator.logout(location="main", key="logout_top")
    else:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("🔐 Logg inn", use_container_width=True): gå_til("Innlogging")

st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)

# ================================================================
# HJEM
# ================================================================
if st.session_state.side == "Hjem":
    # Vis flash-melding (etter registrering)
    if st.session_state.get("flash_melding"):
        st.success(st.session_state.pop("flash_melding"))

    st.markdown("""
        <div style='font-size:13px; color:#6b7280; font-weight:600;
                    text-transform:uppercase; letter-spacing:.8px; margin-bottom:14px;'>
            Velg registrering
        </div>""", unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown('<span class="hjem-markør"></span>', unsafe_allow_html=True)
        if st.button("📝\nRegistrer Kjøring", key="btn_tur", use_container_width=True): gå_til("Tur")
    with k2:
        st.markdown('<span class="hjem-markør"></span>', unsafe_allow_html=True)
        if st.button("🔧\nDagsjekk", key="btn_ds", use_container_width=True): gå_til("Dagsjekk")
    with k3:
        st.markdown('<span class="hjem-markør"></span>', unsafe_allow_html=True)
        if st.button("📸\nATK-registrering", key="btn_atk", use_container_width=True): gå_til("ATK")
    with k4:
        st.markdown('<span class="hjem-markør"></span>', unsafe_allow_html=True)
        if st.button("🗺️\nKjøreruter", key="btn_ruter", use_container_width=True): gå_til("Ruter")

# ================================================================
# TUR
# ================================================================
elif st.session_state.side == "Tur":
    if st.button("← Tilbake", key="back_tur"): gå_til("Hjem")
    vis_side_header("📝", "Registrer Kjøring")
    loc = get_geolocation()
    AB = aktive_biler()
    if not AB:
        st.error("Ingen operative biler. Be admin om å aktivere biler i admin-panelet.")
        st.stop()
    bil = st.selectbox("Velg bil:", list(AB.keys()), key="tur_bil")
    vis_bil_banner(bil)

    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        sted = hent_stedsnavn(lat, lon)
        st.markdown(f"""<div style='background:#eff6ff; border:1.5px solid #bfdbfe;
            border-radius:10px; padding:10px 16px; margin-bottom:10px;
            font-size:14px; color:#1e40af; font-weight:600;'>
            📍 Nåværende posisjon: {sted or f"{lat:.4f}, {lon:.4f}"}
            {"<span style='font-size:12px;font-weight:400;color:#6b7280;margin-left:8px;'>(" + f"{lat:.4f}, {lon:.4f}" + ")</span>" if sted else ""}
        </div>""", unsafe_allow_html=True)
        vis_posisjonskart(lat, lon, bil)
    else:
        st.caption("⏳ Venter på GPS-posisjon...")

    with st.form("tur_form", clear_on_submit=True):
        st.markdown("<div class='form-section-title'>Grunninfo</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        dato       = c1.date_input("Dato", date.today())
        elev       = c1.text_input("Elev / Sjåfør *")
        instruktor = c1.text_input("Instruktør *")
        start      = c2.text_input("Fra (sted)")
        stopp      = c2.text_input("Til (sted)")
        t1         = c2.text_input("Starttidspunkt  (f.eks. 08:30)")
        t2         = c2.text_input("Sluttidspunkt  (f.eks. 09:45)")

        st.markdown("<div class='form-section-title' style='margin-top:12px'>Kilometerstand "
                    "<span style='text-transform:none;font-weight:500;color:#9ca3af;'>"
                    "— fyll inn på dagens første og siste tur</span></div>", unsafe_allow_html=True)
        km1, km2 = st.columns(2)
        km_start = km1.text_input("Km ved tur-start (valgfritt)")
        km_slutt = km2.text_input("Km ved tur-slutt (valgfritt)")

        st.markdown("<div class='form-section-title' style='margin-top:12px'>Merknad</div>", unsafe_allow_html=True)
        merknad = st.text_area("Eventuelle merknader", label_visibility="collapsed")

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.form_submit_button("🚀  Lagre tur", use_container_width=True):
            if not elev or not instruktor:
                st.error("Elev og instruktør må fylles inn.")
            else:
                data = {"Dato": dato, "Bil": bil, "Reg_nr": AB[bil],
                        "Elev": elev, "Instruktør": instruktor,
                        "Fra": start, "Til": stopp,
                        "Starttid": t1, "Sluttid": t2,
                        "Km_start": km_start, "Km_slutt": km_slutt,
                        "Merknad": merknad}
                if loc:
                    data.update({"Lat": loc['coords']['latitude'], "Lon": loc['coords']['longitude']})
                    oppdater_posisjon(bil, loc['coords']['latitude'], loc['coords']['longitude'])
                lagre_data(data, FIL_TURER)
                st.cache_data.clear()
                st.session_state.flash_melding = (
                    f"✅ Tur lagret — {bil}, elev: {elev}, instruktør: {instruktor}")
                gå_til("Hjem")

# ================================================================
# DAGSJEKK
# ================================================================
elif st.session_state.side == "Dagsjekk":
    if st.button("← Tilbake", key="back_ds"): gå_til("Hjem")
    vis_side_header("🔧", "Kontroll og Vedlikehold")
    AB = aktive_biler()
    if not AB:
        st.error("Ingen operative biler. Be admin om å aktivere biler i admin-panelet.")
        st.stop()
    bil_ds = st.selectbox("Velg kjøretøy:", list(AB.keys()), key="ds_bil")
    vis_bil_banner(bil_ds)

    SEKSJONER = {
        "1. Motorrom": [
            "Renhold (visuell sjekk)",
            "Motorolje (nivå)",
            "Kjølevæske (nivå)",
            "Spylervæske (nivå)",
        ],
        "2. Bremser og styring": [
            "Innslag av servo",
            "Innslag av bremsekraftforsterker",
            "Bremsetrykk i pedal (fasthet/lekkasje)",
        ],
        "3. Dekk og felg": [
            "Sideflater på dekk (skader/rifter)",
            "Rulleflate på dekk (ujevn slitasje)",
            "Felger og hjulbolter (skader/sitter fast)",
            "Lufttrykk",
        ],
        "4. Lys og sikt": [
            "P-lys (parkeringslys)",
            "Nærlys",
            "Fjernlys",
            "LED-bar",
            "Blinklys",
            "Bremselys",
            "Skiltlys",
            "Baklys",
            "Rene lykter og ruter",
            "Rene speil",
            "Varmeapparat / defroster",
            "Varslingsutstyr (blålys og sirene-kontroll)",
            "Automatisk blink fjernlys",
        ],
        "5. Annet": [
            "Løse gjenstander (sikring av last/utstyr i kupé)",
            "Fri for feilmeldinger (instrumentpanel)",
            "Førstehjelpsutstyr i hht. liste",
            "Utstyr i hht. liste (annet operativt utstyr)",
            "Ettertrekke hjulbolter",
        ],
    }

    with st.form("dagsjekk"):
        c1, c2 = st.columns(2)
        kontrollor = c1.text_input("Navn kontrollør *")
        instruktor = c2.text_input("Ansvarlig instruktør *")
        dato       = c1.date_input("Dato", date.today())

        avkrysninger = {}
        for seksjon, punkter in SEKSJONER.items():
            st.markdown(f"<div class='form-section-title' style='margin-top:18px'>{seksjon}</div>",
                        unsafe_allow_html=True)

            if seksjon == "3. Dekk og felg":
                cols = st.columns(2)
                for i, punkt in enumerate(punkter):
                    avkrysninger[punkt] = cols[i % 2].checkbox(punkt, key=f"ds_{punkt}")
                st.markdown("<div style='margin-top:10px;font-weight:600;color:#1e3a8a;'>"
                            "Mønsterdybde (mm) — fyll inn alle fire dekk</div>", unsafe_allow_html=True)
                d1, d2, d3, d4 = st.columns(4)
                m_fv = d1.text_input("Forvenstre", key="ds_m_fv")
                m_fh = d2.text_input("Forhøyre",   key="ds_m_fh")
                m_bv = d3.text_input("Bakvenstre", key="ds_m_bv")
                m_bh = d4.text_input("Bakhøyre",   key="ds_m_bh")
            else:
                cols = st.columns(2)
                for i, punkt in enumerate(punkter):
                    avkrysninger[punkt] = cols[i % 2].checkbox(punkt, key=f"ds_{punkt}")

        st.markdown("<div class='form-section-title' style='margin-top:18px'>Avvik og godkjenning</div>",
                    unsafe_allow_html=True)
        merknad = st.text_area("Eventuelle feil og mangler")
        ok = st.checkbox("✅  Bilen er klar til utrykning")

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.form_submit_button("💾  Lagre kontroll", use_container_width=True):
            if not kontrollor or not instruktor:
                st.error("Kontrollør og instruktør må fylles inn.")
            elif not ok:
                st.error("Bilen må godkjennes (hak av nederst) før lagring.")
            else:
                # Bygg datarad
                data = {"Dato": dato, "Bil": bil_ds, "Reg_nr": AB[bil_ds],
                        "Kontrollør": kontrollor, "Instruktør": instruktor,
                        "Status": "OK", "Merknad": merknad}
                for punkt, verdi in avkrysninger.items():
                    data[punkt] = "Ja" if verdi else "Nei"
                data.update({
                    "Mønster_FV": m_fv, "Mønster_FH": m_fh,
                    "Mønster_BV": m_bv, "Mønster_BH": m_bh,
                })

                # Tell antall ikke-avkryssede punkter (utenom dekk)
                ikke_ok = [p for p, v in avkrysninger.items() if not v]
                if ikke_ok:
                    st.warning(f"⚠️ {len(ikke_ok)} punkt(er) ikke avkrysset — lagret med avvik.")
                lagre_data(data, FIL_DAGSJEKK)
                st.cache_data.clear()
                st.success(f"✅ Dagsjekk lagret for {bil_ds}.")

# ================================================================
# ATK
# ================================================================
elif st.session_state.side == "ATK":
    if st.button("← Tilbake", key="back_atk"): gå_til("Hjem")
    vis_side_header("📸", "ATK-registrering")
    st.caption("GPS-posisjon og stedsnavn logges automatisk ved registrering.")
    loc = get_geolocation()
    AB = aktive_biler()
    if not AB:
        st.error("Ingen operative biler. Be admin om å aktivere biler i admin-panelet.")
        st.stop()
    bil_atk = st.selectbox("Velg bil:", list(AB.keys()), key="atk_bil")
    vis_bil_banner(bil_atk)

    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        sted = hent_stedsnavn(lat, lon)
        st.markdown(f"""<div style='background:#eff6ff; border:1.5px solid #bfdbfe;
            border-radius:10px; padding:10px 16px; margin-bottom:10px;
            font-size:14px; color:#1e40af; font-weight:600;'>
            📍 Din posisjon: {sted or f"{lat:.4f}, {lon:.4f}"}
            {"<span style='font-size:12px;font-weight:400;color:#6b7280;margin-left:8px;'>(" + f"{lat:.4f}, {lon:.4f}" + ")</span>" if sted else ""}
        </div>""", unsafe_allow_html=True)
        vis_posisjonskart(lat, lon, bil_atk)
    else:
        st.caption("⏳ Venter på GPS-posisjon...")

    with st.form("atk_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        sjafor     = c1.text_input("Navn på fører *")
        instruktor = c2.text_input("Instruktør *")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.form_submit_button("📍  Loggfør ATK-passering", use_container_width=True):
            if not sjafor or not instruktor:
                st.error("Både fører og instruktør må fylles inn.")
            else:
                data = {"Dato": str(date.today()), "Tid": datetime.now().strftime("%H:%M"),
                        "Bil": bil_atk, "Reg_nr": AB[bil_atk],
                        "Sjåfør": sjafor, "Instruktør": instruktor}
                sted_tekst = ""
                if loc:
                    lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
                    sted = hent_stedsnavn(lat, lon)
                    data.update({"Lat": lat, "Lon": lon, "Sted": sted or ""})
                    oppdater_posisjon(bil_atk, lat, lon)
                    sted_tekst = f" — {sted}" if sted else f" @ {lat:.4f}, {lon:.4f}"
                lagre_data(data, FIL_ATK)
                st.cache_data.clear()
                st.session_state.flash_melding = (
                    f"✅ ATK loggført — {bil_atk}, {sjafor} / {instruktor}{sted_tekst}"
                    + ("" if loc else " (uten GPS-posisjon)"))
                gå_til("Hjem")

# ================================================================
# RUTER
# ================================================================
elif st.session_state.side == "Ruter":
    if st.button("← Tilbake", key="back_ruter"): gå_til("Hjem")
    vis_side_header("🗺️", "Kjøreruter per politidistrikt")
    df_r   = pd.read_csv(FIL_RUTER) if os.path.exists(FIL_RUTER) else pd.DataFrame(columns=["Distrikt","Navn","URL"])
    d_valg = st.selectbox("Velg distrikt:", POLITIDISTRIKT)
    ruter  = df_r[df_r['Distrikt'] == d_valg]

    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
    if not ruter.empty:
        for _, r in ruter.iterrows():
            rc1, rc2 = st.columns([4, 1])
            rc1.markdown(f"<div class='info-card'>📍 {r['Navn']}</div>", unsafe_allow_html=True)
            rc2.link_button("Åpne i Maps ↗️", r['URL'], use_container_width=True)
    else:
        st.info("Ingen ruter lagt inn for dette distriktet.")

    with st.expander("🔐  Legg til rute (admin)"):
        if hent_rolle() == "admin":
            n_dist = st.selectbox("Politidistrikt:", POLITIDISTRIKT, key="admin_dist")
            n_navn = st.text_input("Navn på ruten:")
            n_url  = st.text_input("Google Maps URL:")
            if st.button("💾 Lagre rute"):
                lagre_data({"Distrikt": n_dist, "Navn": n_navn, "URL": n_url}, FIL_RUTER)
                st.success("Rute lagret!")
                st.rerun()
        else:
            st.info("Logg inn som admin for å legge til ruter.")

# ================================================================
# INNLOGGING
# ================================================================
elif st.session_state.side == "Innlogging":
    if st.button("← Tilbake", key="back_login"): gå_til("Hjem")
    vis_side_header("🔐", "Innlogging")

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        authenticator.login(location="main")
        auth_status = st.session_state.get("authentication_status")
        name        = st.session_state.get("name")
        if auth_status:
            st.success(f"Innlogget som {name}")
            gå_til("Rapport")
        elif auth_status is False:
            st.error("Feil brukernavn eller passord.")
        elif auth_status is None:
            st.info("Skriv inn brukernavn og passord.")

# ================================================================
# RAPPORT
# ================================================================
elif st.session_state.side == "Rapport":
    if not st.session_state.get("authentication_status"):
        st.warning("Du må være innlogget for å se rapporter.")
        gå_til("Innlogging")
    else:
        rolle = hent_rolle()
        badge = "rolle-admin" if rolle == "admin" else "rolle-instruktør"

        vis_side_header("📊", "Dagsrapport")

        # Filter-rad
        filt_c1, filt_c2 = st.columns(2)
        dato = filt_c1.date_input("Dato:", date.today())
        if rolle == "admin":
            bil_filter = filt_c2.selectbox("Bil:", ["Alle"] + list(aktive_biler().keys()))
        else:
            bil_filter = filt_c2.selectbox("Bil:", list(aktive_biler().keys()))

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        # Flåtestatus (admin)
        if rolle == "admin":
            st.markdown("""<div style='font-size:13px; font-weight:700; color:#6b7280;
                text-transform:uppercase; letter-spacing:.8px; margin-bottom:10px;'>
                Flåtestatus i dag</div>""", unsafe_allow_html=True)

            AB = aktive_biler()
            if AB:
                kolonner = st.columns(min(len(AB), 4))
                for i, (bil, reg) in enumerate(AB.items()):
                    ok = sjekk_dagsjekk_status(bil)
                    ikon   = "✅" if ok else "❌"
                    klasse = "status-ok" if ok else "status-mangler"
                    tekst  = "Dagsjekk OK" if ok else "Dagsjekk mangler"
                    with kolonner[i % len(kolonner)]:
                        st.markdown(f"""<div class='status-kort {klasse}'>
                            {ikon} <strong>{bil}</strong><br>
                            <span style='font-size:12px;font-weight:500'>{reg} — {tekst}</span>
                        </div>""", unsafe_allow_html=True)
            else:
                st.info("Ingen operative biler. Aktiver biler i admin-panelet under.")

            if os.path.exists(FIL_POSISJON):
                st.markdown("""<div style='font-size:13px; font-weight:700; color:#6b7280;
                    text-transform:uppercase; letter-spacing:.8px; margin:16px 0 10px;'>
                    Flåteoversikt</div>""", unsafe_allow_html=True)
                df_p = pd.read_csv(FIL_POSISJON)
                m = folium.Map(location=[61.5, 10.0], zoom_start=6)
                for _, r in df_p.iterrows():
                    folium.Marker([r['Lat'], r['Lon']],
                        popup=f"<b>{r['Bil']}</b><br>Sist sett: {r['Tid']}",
                        icon=folium.Icon(color="blue", icon="ambulance", prefix="fa")).add_to(m)
                st_folium(m, width="100%", height=340)

            with st.expander("📍  Veistatus — Statens Vegvesen"):
                f = st.selectbox("Fylke:", list(FYLKER.keys()))
                mld = hent_veimeldinger(FYLKER[f])
                if mld:
                    for item in mld[:5]:
                        st.warning(f"**{item.get('vegnr','')}**: {item.get('overskrift','')}")
                else:
                    st.write("Ingen aktive meldinger.")
        else:
            ok = sjekk_dagsjekk_status(bil_filter)
            if ok:
                st.success(f"✅ Dagsjekk er OK for {bil_filter} i dag")
            else:
                st.error(f"❌ Dagsjekk mangler for {bil_filter} i dag")

        # ── PDF-EKSPORT ──────────────────────────────────────────
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        with st.expander("📄  Last ned PDF-rapport", expanded=False):
            if rolle == "admin":
                pc1, pc2 = st.columns(2)
                periode = pc1.selectbox("Periode:", ["Dag", "Uke", "Måned"], key="pdf_periode")
                pdf_bil = pc2.selectbox("Omfang:", ["Per bil", "Totalt (alle biler)"], key="pdf_omfang")

                if periode == "Dag":
                    fra_d, til_d = dato, dato
                    periodenavn = f"Dag — {dato.strftime('%d.%m.%Y')}"
                elif periode == "Uke":
                    fra_d = dato - timedelta(days=dato.weekday())
                    til_d = fra_d + timedelta(days=6)
                    periodenavn = f"Uke {fra_d.isocalendar().week}"
                else:
                    fra_d = dato.replace(day=1)
                    neste = (fra_d + timedelta(days=32)).replace(day=1)
                    til_d = neste - timedelta(days=1)
                    periodenavn = fra_d.strftime("%B %Y").capitalize()

                if pdf_bil == "Per bil":
                    st.caption(f"Genererer én PDF per bil for {periodenavn.lower()}.")
                    AB = aktive_biler()
                    bcols = st.columns(max(len(AB), 1))
                    for i, (bil, reg) in enumerate(AB.items()):
                        pdf_bytes = lag_pdf_rapport(fra_d, til_d, bil, periodenavn)
                        bcols[i].download_button(
                            f"⬇️ {bil}", pdf_bytes,
                            file_name=f"rapport_{bil.replace(' ','_')}_{fra_d}_{til_d}.pdf",
                            mime="application/pdf", use_container_width=True,
                            key=f"pdf_{bil}_{fra_d}")
                else:
                    pdf_bytes = lag_pdf_rapport(fra_d, til_d, "Alle", periodenavn)
                    st.download_button(
                        f"⬇️  Last ned samlet PDF — {periodenavn}",
                        pdf_bytes,
                        file_name=f"rapport_alle_{fra_d}_{til_d}.pdf",
                        mime="application/pdf", use_container_width=True,
                        key=f"pdf_alle_{fra_d}")
            else:
                # Instruktør: kun valgt dato + valgt bil
                pdf_bytes = lag_pdf_rapport(dato, dato, bil_filter,
                                            f"Dag — {dato.strftime('%d.%m.%Y')}")
                st.download_button(
                    f"⬇️  Last ned PDF — {bil_filter}, {dato.strftime('%d.%m.%Y')}",
                    pdf_bytes,
                    file_name=f"rapport_{bil_filter.replace(' ','_')}_{dato}.pdf",
                    mime="application/pdf", use_container_width=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["🚗  Kjøringer", "🔧  Dagsjekker", "📸  ATK"])
        with t1:
            vis_km_oversikt(dato, bil_filter)
            vis_rapport_tabell(FIL_TURER, dato, bil_filter)
        with t2: vis_rapport_tabell(FIL_DAGSJEKK, dato, bil_filter)
        with t3: vis_rapport_tabell(FIL_ATK,      dato, bil_filter)

        # ── ADMIN: BILREGISTER ─────────────────────────────────────
        if rolle == "admin":
            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

            # Sheets-diagnose
            with st.expander("☁️  Google Sheets-status", expanded=False):
                if _bruk_sheets():
                    st.success("✅ Secrets er konfigurert — appen prøver å bruke Google Sheets.")
                    st.caption(f"Sheet ID: `{st.secrets['google_sheets']['sheet_id']}`")
                    if st.button("🔄 Test tilkobling til Sheets"):
                        try:
                            sh = _sheets_klient()
                            tittel = sh.title
                            ark_navn = [w.title for w in sh.worksheets()]
                            st.success(f"✅ Koblet til regnearket: **{tittel}**")
                            st.write("Ark som finnes:", ark_navn or "(ingen ennå)")
                        except Exception as e:
                            st.error(f"❌ Feil: {e}")
                            st.info("Mulige årsaker:\n"
                                    "1. Service-kontoen mangler tilgang til regnearket\n"
                                    "2. Sheets API eller Drive API er ikke aktivert\n"
                                    "3. private_key i secrets er ikke korrekt formatert")
                else:
                    st.warning("⚠️ Secrets er IKKE konfigurert — appen bruker lokal CSV-lagring "
                               "som forsvinner ved restart på Streamlit Cloud.")
                    st.caption("Sjekk at både `[gcp_service_account]` og `[google_sheets].sheet_id` "
                               "er fylt inn i Settings → Secrets.")

            with st.expander("🛠️  Admin: Bilregister og operativ status", expanded=False):
                st.caption("Rediger registreringsnummer og hak av hvilke biler som er operative. "
                           "Kun operative biler kan brukes i registrering og vises i flåtestatus.")
                df_biler = last_biler()

                with st.form("biler_form"):
                    redigert = []
                    for _, rad in df_biler.iterrows():
                        bil = rad['Bil']
                        c1, c2, c3 = st.columns([2, 3, 1])
                        c1.markdown(f"<div style='padding-top:30px;font-weight:700;color:#1e3a8a;'>{bil}</div>",
                                    unsafe_allow_html=True)
                        ny_reg = c2.text_input("Reg.nr", value=rad['Reg_nr'],
                                               key=f"reg_{bil}", label_visibility="collapsed",
                                               placeholder="f.eks. AA 12345")
                        er_op = (str(rad['Operativ']).strip().lower() in ["ja","true","1","yes"])
                        ny_op = c3.checkbox("Operativ", value=er_op, key=f"op_{bil}")
                        redigert.append({"Bil": bil, "Reg_nr": ny_reg,
                                         "Operativ": "Ja" if ny_op else "Nei"})

                    if st.form_submit_button("💾  Lagre bilregister", use_container_width=True):
                        df_ny = pd.DataFrame(redigert)
                        if _bruk_sheets():
                            try:
                                ark = _hent_ark(FIL_BILER, opprett_hvis_mangler=True)
                                ark.clear()
                                ark.update([df_ny.columns.tolist()] + df_ny.astype(str).values.tolist())
                            except Exception as e:
                                st.error(f"Sheets-skriving feilet: {e}")
                                df_ny.to_csv(FIL_BILER, index=False, encoding="utf-8-sig")
                        else:
                            df_ny.to_csv(FIL_BILER, index=False, encoding="utf-8-sig")
                        st.cache_data.clear()
                        st.success("✅ Bilregister oppdatert.")
                        st.rerun()
