import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from extraction.youtube_api import get_youtube_channel_info

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="YTAI Analytics | Login", layout="centered")

# ==============================
# CUSTOM CSS
# ==============================
st.markdown("""
<style>
section[data-testid="stSidebar"] { display: none !important; }
.stApp { 
    background: radial-gradient(circle at bottom left, #0a2a43 35%, #04111d 70%, #000000 80%);
    color: #eaeaea; 
    font-family: 'Segoe UI', sans-serif; 
}

.auth-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 40px;
    margin-bottom: 20px;
}

.login-btn-header {
    background: linear-gradient(135deg, #FF0000, #CC0000);
    color: white;
    padding: 10px 24px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    transition: transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 4px 15px rgba(255, 0, 0, 0.3);
}

.auth-main-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 70vh;
    padding: 40px 20px;
}

.app-logo {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #FF0000, #CC0000);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    box-shadow: 0 8px 25px rgba(255, 0, 0, 0.4);
}

.app-logo-icon {
    font-size: 48px;
    color: white;
}

.app-title {
    font-size: 56px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 12px;
    text-shadow: 0 4px 15px rgba(255, 255, 255, 0.2);
}

.app-subtitle {
    font-size: 20px;
    color: #9bbcd6;
    margin-bottom: 50px;
    text-align: center;
}

.analyze-section {
    background: linear-gradient(145deg, #0b253a, #081a2a);
    padding: 35px;
    border-radius: 16px;
    width: 100%;
    max-width: 600px;
    margin-bottom: 30px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.divider {
    display: flex;
    align-items: center;
    text-align: center;
    margin: 30px 0;
    color: #9bbcd6;
    width: 100%;
    max-width: 600px;
}

.divider::before,
.divider::after {
    content: '';
    flex: 1;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.divider span {
    padding: 0 15px;
    font-size: 14px;
}

.google-login-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    width: 100%;
    max-width: 600px;
    height: 52px;
    background-color: #ffffff;
    color: #3c4043;
    font-family: 'Roboto', 'Segoe UI', sans-serif;
    font-size: 18px;
    font-weight: 500;
    border: 1px solid #dadce0;
    border-radius: 10px;
    text-decoration: none;
    cursor: pointer;
    transition: background-color 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.google-login-btn:hover {
    background-color: #f7f8f8;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.google-login-btn img {
    width: 24px;
    height: 24px;
}

.welcome-back {
    text-align: center;
    margin-top: 30px;
    color: #ffffff;
    font-size: 18px;
}

.dashboard-link {
    color: #FF0000;
    text-decoration: none;
    font-weight: 600;
    margin-top: 10px;
    display: inline-block;
    transition: color 0.2s;
}

.dashboard-link:hover {
    color: #FF4444;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# GOOGLE OAUTH CONFIG
# ==============================
CLIENT_ID = st.secrets["google"]["client_id"]
CLIENT_SECRET = st.secrets["google"]["client_secret"]
REDIRECT_URI = st.secrets["google"]["redirect_uri"]

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

SCOPES = ["openid", "email", "profile", "https://www.googleapis.com/auth/youtube.readonly"]

# ==============================
# HEADER WITH LOGIN BUTTON
# ==============================
st.markdown("""
<div class="auth-header">
    <div style="font-size: 24px; font-weight: 700; color: #ffffff;">YTAI Analytics</div>
    <div style="color: #9bbcd6;">Already have an account?</div>
</div>
""", unsafe_allow_html=True)

# ==============================
# MAIN CONTENT
# ==============================
st.markdown("""
<div class="auth-main-container">
    <div class="app-logo">
        <div class="app-logo-icon">▶</div>
    </div>
    <div class="app-title">YTAI Analytics</div>
    <div class="app-subtitle">Unlock deep insights into any YouTube Channel instantly.</div>
</div>
""", unsafe_allow_html=True)

# ==============================
# ANALYZE SECTION
# ==============================
st.markdown("""
<div class="analyze-section">
""", unsafe_allow_html=True)

with st.form("analyze_form", clear_on_submit=False):
    channel_input = st.text_input(
        "Enter YouTube Channel Name or ID",
        placeholder="Paste YouTube Channel ID here...",
        key="channel_input_auth"
    )
    analyze_submitted = st.form_submit_button("Analyze", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

if analyze_submitted and channel_input.strip():
    st.session_state["authenticated"] = True
    st.session_state["pending_channel"] = channel_input.strip()
    st.switch_page("pages/app.py")

# ==============================
# OAUTH SETUP
# ==============================
oauth = OAuth2Session(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope=SCOPES, redirect_uri=REDIRECT_URI)
authorization_url, state = oauth.create_authorization_url(AUTH_URL, access_type="offline")

# ==============================
# DIVIDER AND GOOGLE LOGIN
# ==============================
st.markdown("""
<div class="divider">
    <span>OR</span>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="width: 100%; max-width: 600px; margin: 0 auto;">
    <a class="google-login-btn" href="{authorization_url}">
        <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" />
        Continue with Google
    </a>
</div>
""", unsafe_allow_html=True)

# ==============================
# HANDLE OAUTH REDIRECT + AUTO CHANNEL FETCH
# ==============================
query_params = st.query_params
if "code" in query_params:
    token = oauth.fetch_token(TOKEN_URL, code=query_params["code"])
    user_info = oauth.get(USERINFO_URL).json()
    
    # FETCH YOUTUBE CHANNEL AUTOMATICALLY
    yt_info = get_youtube_channel_info(token['access_token'])

    st.session_state["authenticated"] = True
    st.session_state["user"] = user_info
    st.session_state["user_yt_channel"] = yt_info
    
    st.success(f"Welcome {user_info['name']} 👋")
    st.switch_page("pages/app.py")
