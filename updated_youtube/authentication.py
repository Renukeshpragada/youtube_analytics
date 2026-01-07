import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from extraction.youtube_api import get_youtube_channel_info

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Login | YouTube Analytics", layout="centered")

# [YOUR CSS CODE - UNCHANGED
st.markdown("""
<style>
section[data-testid="stSidebar"] { display: none !important; }
.stApp { background: radial-gradient(circle at top left, #0a2a43 0%, #04111d 40%, #000000 75%); color: #eaeaea; font-family: 'Segoe UI', sans-serif; }
.login-wrapper { display: flex; margin-top: 60px; justify-content: center; height: 41vh; width: 100%; margin-bottom: 40px; }
.login-card { background: linear-gradient(145deg, #0b253a, #081a2a); padding: 48px; padding-top: 26px; width: 1000px; border-radius: 22px; box-shadow: 0 0 35px rgba(0,140,255,0.25); text-align: center; margin-bottom: 10px; }
.login-title { font-size: 75px; font-weight: 700; color: #e6f1ff; margin-bottom: 10px; }
.login-sub { font-size: 28px; color: #9bbcd6; margin-bottom: 36px; }
.google-login-btn { display: flex; align-items: center; justify-content: center; gap: 12px; width: 100%; max-width: 520px; height: 48px; background-color: #ffffff; color: #3c4043; font-family: 'Roboto', 'Segoe UI', sans-serif; font-size: 19px; font-weight: 500; border: 1px solid #dadce0; border-radius: 6px; text-decoration: none; cursor: pointer; transition: background-color 0.2s ease, box-shadow 0.2s ease; }
.google-login-btn:hover { background-color: #f7f8f8; box-shadow: 0 1px 2px rgba(60,64,67,0.15); }
.google-login-btn img { padding-right: 7px; width: 28px; height: 28px; }
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

# ADDED YOUTUBE SCOPE HERE
SCOPES = ["openid", "email", "profile", "https://www.googleapis.com/auth/youtube.readonly"]

st.markdown("""
<div class="login-wrapper">
  <div class="login-card">
    <div class="login-title">YouTube Analytics</div>
    <div class="login-sub">Sign in to access insights & performance dashboards</div>
  </div>
</div>
""", unsafe_allow_html=True)

oauth = OAuth2Session(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope=SCOPES, redirect_uri=REDIRECT_URI)
authorization_url, state = oauth.create_authorization_url(AUTH_URL, access_type="offline")

st.markdown(f"""
<div style="display:flex; justify-content:center;">
  <a class="google-login-btn" href="{authorization_url}">
    <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" />
    Continue with Google
  </a>
</div>
""", unsafe_allow_html=True)

# ==============================
# HANDLE REDIRECT + AUTO CHANNEL FETCH
# ==============================
query_params = st.query_params
if "code" in query_params:
    token = oauth.fetch_token(TOKEN_URL, code=query_params["code"])
    user_info = oauth.get(USERINFO_URL).json()
    
    # FETCH YOUTUBE CHANNEL AUTOMATICALLY
    yt_info = get_youtube_channel_info(token['access_token'])

    st.session_state["authenticated"] = True
    st.session_state["user"] = user_info
    st.session_state["user_yt_channel"] = yt_info  # Save the fetched channel
    
    st.success(f"Welcome {user_info['name']} 👋")
    st.switch_page("pages/app.py")