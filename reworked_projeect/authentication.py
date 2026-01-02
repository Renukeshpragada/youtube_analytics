import streamlit as st
import os
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# ==============================
# PAGE CONFIG (UNCHANGED)
# ==============================
st.set_page_config(
    page_title="Login | YouTube Analytics",
    layout="centered"
)

# ==============================
# YOUR UI / CSS (UNCHANGED)
# ==============================
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    display: none !important;
}

.stApp {
    background: radial-gradient(
        circle at top left,
        #0a2a43 0%,
        #04111d 40%,
        #000000 75%
    );
    color: #eaeaea;
    font-family: 'Segoe UI', sans-serif;
}

.login-wrapper {
    display: flex;
    margin-top: 60px;
    justify-content: center;
    height: 41vh;
    width: 100%;
    margin-bottom: 40px;
}

.login-card {
    background: linear-gradient(145deg, #0b253a, #081a2a);
    padding: 48px;
    padding-top: 26px;
    width: 1000px;
    border-radius: 22px;
    box-shadow: 0 0 35px rgba(0,140,255,0.25);
    text-align: center;
    margin-bottom: 10px;
}

.login-title {
    font-size: 75px;
    font-weight: 700;
    color: #e6f1ff;
    margin-bottom: 10px;
}

.login-sub {
    font-size: 28px;
    color: #9bbcd6;
    margin-bottom: 36px;
}

.google-login-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    width: 100%;
    max-width: 520px;
    height: 48px;
    background-color: #ffffff;
    color: #3c4043;
    font-family: 'Roboto', 'Segoe UI', sans-serif;
    font-size: 19px;
    font-weight: 500;
    border: 1px solid #dadce0;
    border-radius: 6px;
    text-decoration: none;
    cursor: pointer;
    transition: background-color 0.2s ease, box-shadow 0.2s ease;
}

.google-login-btn:hover {
    background-color: #f7f8f8;
    box-shadow: 0 1px 2px rgba(60,64,67,0.15);
}

.google-login-btn img {
    padding-right: 7px;
    width: 28px;
    height: 28px;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# LOGIN CARD (UNCHANGED)
# ==============================
st.markdown("""
<div class="login-wrapper">
  <div class="login-card">
    <div class="login-title">YouTube Analytics</div>
    <div class="login-sub">
      Sign in to access insights & performance dashboards
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ==============================
# GOOGLE OAUTH CONFIG (FIXED)
# ==============================
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # localhost only

CLIENT_CONFIG = {
    "web": {
        "client_id": st.secrets["google"]["client_id"],
        "client_secret": st.secrets["google"]["client_secret"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [st.secrets["google"]["redirect_uri"]],
    }
}

SCOPES = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/youtube.readonly"
]

flow = Flow.from_client_config(
    CLIENT_CONFIG,
    scopes=SCOPES,
    redirect_uri=st.secrets["google"]["redirect_uri"]
)

# ==============================
# STEP 1: SHOW LOGIN BUTTON
# ==============================
if "code" not in st.query_params:
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline"
    )

    st.markdown(f"""
    <div style="display:flex; justify-content:center;">
      <a class="google-login-btn" href="{auth_url}">
        <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" />
        Continue with Google
      </a>
    </div>
    """, unsafe_allow_html=True)

    st.stop()

# ==============================
# STEP 2: HANDLE CALLBACK
# ==============================
try:
    flow.fetch_token(code=st.query_params["code"])
except Exception:
    st.error("Authentication failed. Please restart the app and try again.")
    st.stop()

credentials = flow.credentials

# ==============================
# STEP 3: FETCH USER YOUTUBE CHANNEL (VIDIQ STYLE)
# ==============================
youtube = build("youtube", "v3", credentials=credentials)

channel_res = youtube.channels().list(
    part="snippet,statistics",
    mine=True
).execute()

if not channel_res["items"]:
    st.error("No YouTube channel found for this Google account.")
    st.stop()

channel = channel_res["items"][0]

# ==============================
# STEP 4: SAVE SESSION STATE
# ==============================
st.session_state["authenticated"] = True
st.session_state["user_email"] = credentials.id_token.get("email")
st.session_state["channel_id"] = channel["id"]
st.session_state["channel_name"] = channel["snippet"]["title"]

# IMPORTANT: clear OAuth params
st.query_params.clear()

st.success(f"Welcome {channel['snippet']['title']} 👋")
st.info("Redirecting to dashboard...")

# ==============================
# REDIRECT TO DASHBOARD
# ==============================
st.switch_page("pages/app.py")
