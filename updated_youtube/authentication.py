import streamlit as st
from authlib.integrations.requests_client import OAuth2Session

# Note: Extraction logic for channel info must exist in your directory structure
try:
    from extraction.youtube_api import get_youtube_channel_info
except ImportError:
    # Fallback placeholder if file is not found
    def get_youtube_channel_info(token): return {}

# ==============================
# 1. PAGE CONFIG & GOOGLE OAUTH CONFIG
# ==============================
st.set_page_config(page_title="YTAI Analytics | Login", layout="centered")

# Retrieve Google credentials from streamlit secrets
# These must be set in your .streamlit/secrets.toml
CLIENT_ID = st.secrets.get("google", {}).get("client_id", "")
CLIENT_SECRET = st.secrets.get("google", {}).get("client_secret", "")
REDIRECT_URI = st.secrets.get("google", {}).get("redirect_uri", "")

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
SCOPES = ["openid", "email", "profile", "https://www.googleapis.com/auth/youtube.readonly"]

# Initialize OAuth Session
oauth = OAuth2Session(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope=SCOPES, redirect_uri=REDIRECT_URI)
authorization_url, _ = oauth.create_authorization_url(AUTH_URL, access_type="offline")

# ==============================
# 2. FINAL CLEAN CSS
# ==============================
st.markdown("""
<style>
/* Global Setup */
section[data-testid="stSidebar"] { display: none !important; }
.stApp { 
    background: radial-gradient(circle at bottom left, #071726 30%, #04111d 65%, #000000 85%);
    color: #eaeaea; 
}

/* Hero Section / Title Card */
.hero-card {
    width: 100%; max-width: 800px;
    background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
    border-radius: 28px; padding: 60px 40px; text-align: center;
    box-shadow: 0 30px 80px rgba(0,0,0,0.5);
    
    margin: 40px auto 60px auto; /* 60px bottom margin for spacing to search bar */
}
.app-logo {
    width: 80px; height: 80px; border-radius: 20px; 
    background: linear-gradient(135deg,#ff3b1f 0%, #ff6a3d 60%);
    display: flex; align-items: center; justify-content: center; margin: 0 auto 20px auto;
}
.app-title { font-size: 60px; font-weight: 800; color: white; margin-bottom: 5px; }
.app-tagline { font-size: 18px; color: #bcd3e0; opacity: 0.8; }

/* THE PILL SEARCH FIELD (Professional Match) */
div[data-testid="stForm"] {
    background: linear-gradient(90deg, rgba(6,30,60,0.6), rgba(8,45,85,0.6)) !important;
    border: 1px solid rgba(40,80,140,0.12) !important;
    border-radius: 100px !important;
    padding: 6px 6px 6px 22px !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: space-between !important;
    max-width: 700px !important;
    margin: 0 auto !important;
    box-shadow: 0 10px 40px rgba(0,0,0,0.45) inset, 0 8px 30px rgba(0,0,0,0.35) !important;
}

/* Hide Streamlit label spacers completely */
div[data-testid="stForm"] label { display: none !important; height: 0 !important; }
div[data-testid="column"] { padding: 0 !important; flex: 1 1 auto !important; margin: 0 !important; }
div[data-testid="stVerticalBlock"] { gap: 0 !important; }

/* Text Input Styling */
.stTextInput input {
    /* subtle filled background so the placeholder doesn't sit on pure black */
    background:inherit !important;
    border: linear-gradient(90deg, rgba(6, 30, 60, 0.6), rgba(8, 45, 85, 0.6)) !important;
    width:1000px;
    box-shadow: none !important;
    color: white !important;
    font-size: 22px !important;
    padding: 9px 12px !important;
    border-radius: 8px !important;
}

/* Placeholder styling (cross-browser) */
.stTextInput input::placeholder { color: rgba(255,255,255,0.87) !important; opacity: 1;
           
             }
.stTextInput input::-webkit-input-placeholder { color: rgba(255,255,255,0.55) !important; }
.stTextInput input:-ms-input-placeholder { color: rgba(255,255,255,0.55) !important; }
.stTextInput input::-ms-input-placeholder { color: rgba(255,255,255,0.55) !important; }

/* THE BUTTON: BLUE GRADIENT FIX */
button[kind="primaryFormSubmit"], 
button[data-testid="stBaseButton-secondaryFormSubmit"] {
        /* Updated gradient: teal → blue for clearer, fresher contrast */
        background: linear-gradient(90deg, #0ecff0, #063562);
            margin-left:14px;
    color: white !important;
    border: 0px solid rgba(255,255,255,0.04) !important;
    
    border-radius: 100px !important;
    padding: 2px 33px !important;
    font-weight: 700 !important;
    height: 44px !important;
    transition: all 0.22s ease-in-out !important;
    box-shadow: 0 8px 24px rgba(6,70,140,0.18) !important;
}
button:hover { 
    transform: translateY(-1px); 
    opacity: 0.9;
    box-shadow: 0 0 20px rgba(30, 144, 255, 0.4) !important;
}

/* Divider & Login Elements */
.divider { display:flex; align-items:center; margin: 40px auto; max-width: 550px; color:#555; font-size: 12px; font-weight: bold; }
.divider::before, .divider::after { content:''; flex:1; height:1px; background: #333; margin: 0 15px; }

.google-login-btn {
    display: inline-flex; align-items: center; justify-content: center; gap: 12px;
    width: 480px; height: 50px; background-color: #ffffff; color: #3c4043;
    font-weight: 700; border-radius: 100px; text-decoration: none; 
    font-size:19px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: 0.2s;
}
.google-login-btn:hover { background: #f1f1f1; transform: translateY(-1px); }
</style>
""", unsafe_allow_html=True)

# ==============================
# 3. PAGE CONTENT & UI
# ==============================

# HERO TITLE SECTION
st.markdown("""
<div class="hero-card">
    <div class="app-logo"><span style="color:white; font-size:38px; font-weight:bold;">▶</span></div>
    <div class="app-title">YouTube Analytics</div>
    <div class="app-tagline">Deep dive into performance metrics and channel growth</div>
</div>
""", unsafe_allow_html=True)

# ANALYZE PILL FORM
with st.form("analyze_channel_form", clear_on_submit=False):
    # Split the row: 4 parts for input, 1 part for button
    col_input, col_btn = st.columns([4, 1.2])
    
    with col_input:
        channel_input = st.text_input(
            "label_not_visible", 
            placeholder="Enter the channel name.....", 
            label_visibility="collapsed"
        )
    
    with col_btn:
        submitted = st.form_submit_button("Analyze")

# Search Field Functionality
if submitted and channel_input.strip():
    st.session_state["authenticated"] = True
    st.session_state["pending_channel"] = channel_input.strip()
    st.info(f"Checking access for: {channel_input}")
    st.switch_page("pages/app.py")

# AUTH SECTION (GOOGLE LOGIN)
st.markdown('<div class="divider">OR</div>', unsafe_allow_html=True)

st.markdown(f"""
<div style="text-align: center;">
    <a class="google-login-btn" href="{authorization_url}">
        <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" width="20" height="20" />
        Continue with Google
    </a>
</div>
""", unsafe_allow_html=True)

# ==============================
# 4. HANDLE OAUTH REDIRECT LOGIC
# ==============================
# Checks for the URL 'code' parameter after Google Redirect
query_params = st.query_params
if "code" in query_params:
    try:
        token = oauth.fetch_token(TOKEN_URL, code=query_params["code"])
        user_info = oauth.get(USERINFO_URL).json()
        
        # Get extra YT details via the imported function
        yt_info = get_youtube_channel_info(token['access_token'])

        # Store user state
        # Store auth state
        st.session_state["authenticated"] = True
        st.session_state["user"] = user_info

# Store user's own YouTube channel (identity-linked)
        st.session_state["user_yt_channel"] = yt_info

# 🔑 IMPORTANT: sync with analytics state
        if yt_info and yt_info.get("channel_name"):
            st.session_state["user_channel"] = yt_info["channel_name"]

    # Set default analytics channel ONLY if user
    # has not already been analyzing something
            if not st.session_state.get("search_value"):
                st.session_state["search_value"] = yt_info["channel_name"]

        st.success(f"Signed in as {user_info.get('name', 'User')}")
        st.switch_page("pages/app.py")

    except Exception as e:
        st.error(f"Login failed: {e}")