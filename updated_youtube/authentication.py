import streamlit as st
from authlib.integrations.requests_client import OAuth2Session

# Note: Extraction logic for channel info must exist in your directory structure
try:
    from extraction.youtube_api import get_youtube_channel_info
except ImportError:
    def get_youtube_channel_info(token): return {}

# ==============================
# 1. PAGE CONFIG
# ==============================
st.set_page_config(page_title="YTAI Analytics | Professional", layout="wide")

# Retrieve Google credentials from streamlit secrets
CLIENT_ID = st.secrets.get("google", {}).get("client_id", "")
CLIENT_SECRET = st.secrets.get("google", {}).get("client_secret", "")
REDIRECT_URI = st.secrets.get("google", {}).get("redirect_uri", "")

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
SCOPES = ["openid", "email", "profile", "https://www.googleapis.com/auth/youtube.readonly"]

oauth = OAuth2Session(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope=SCOPES, redirect_uri=REDIRECT_URI)
authorization_url, _ = oauth.create_authorization_url(AUTH_URL, access_type="offline")

# ==============================
# 2. ADVANCED CSS & ANIMATIONS
# ==============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    /* Global Background */
    .stApp {
        background: radial-gradient(circle at bottom left, #0a2a43 40%, #04111d 75%, #000000 85%);
        font-family: 'Inter', sans-serif;
    }

    /* Animation Keyframes */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .animate-up {
        animation: fadeInUp 0.8s ease forwards;
    }

    /* Section Headings */
    .section-header {
        color: white;
        text-align: center;
        font-weight: 800;
        font-size: 2.5rem;
        margin: 60px 0 30px 0;
        letter-spacing: -1px;
    }

    /* Hero Section */
    .hero-card {
        text-align: center;
        padding: 40px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        border-radius: 20px;
        width:44%;
        margin-bottom: 50px;
        margin-left:368px;
    
        animation: fadeInUp 0.6s ease;
    }
    .app-logo {
        width: 70px; height: 70px; border-radius: 18px; 
        background: linear-gradient(135deg,#00e5ff 0%, #007bff 100%);
        display: flex; align-items: center; justify-content: center; margin: 0 auto 20px auto;
        box-shadow: 0 10px 30px rgba(0, 229, 255, 0.3);
    }

    /* Custom Cards */
    .custom-card {
        background: rgba(13, 22, 31, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 35px 25px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        height: 100%;
        box-shadow: 5px 15px 25px rgba(0,140,205,0.3);
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .custom-card:hover {
        border-color: #00e5ff;
        transform: translateY(-10px);
        background: rgba(20, 36, 51, 1);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }

    .icon-box {
        background: rgba(0, 229, 255, 0.1);
        width: 55px; height: 55px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        margin-bottom: 20px; color: #00e5ff;
    }

    .card-title { color: white; font-weight: 700; font-size: 1.25rem; margin-bottom: 12px; }
    .card-description { color: #94a3b8; font-size: 0.95rem; line-height: 1.6; }

    /* Step Badges */
    .step-wrapper { position: relative; margin-top: 20px; animation: fadeInUp 0.8s ease forwards; }
    .step-badge {
        background: #00e5ff; color: #050c14; width: 30px; height: 30px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; position: absolute; top: -15px; left: 50%;
        transform: translateX(-50%); z-index: 10;
        box-shadow: 0 4px 10px rgba(0, 229, 255, 0.4);
    }

    /* Search Bar Form Styling */
    div[data-testid="stForm"] {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 100px !important;
        padding: 8px 8px 8px 25px !important;
        max-width: 700px !important; margin: 0 auto !important;
    }
    .stTextInput input {
        background: transparent !important; border: none !important;
        color: white !important; font-size: 1.1rem !important;
    }
    .stTextInput input::placeholder { color: #64748b !important; font-size: 1.1rem !important; }
    .stButton > button {
        height: 45px !important; border-radius: 100px !important;
            }

    /* Google Button */
    .google-login-btn {
        display: inline-flex; align-items: center; justify-content: center; gap: 12px;
        width: 480px; height: 55px; background: white; color: #3c4043;
            font-size: 1.4rem;
        font-weight: 800; border-radius: 100px; text-decoration: none; margin-top: 20px;
        transition: 0.3s;
        box-shadow: 0 5px 15px rgba(255, 255, 255, 0.4);
            margin-bottom: 50px;
    }
    .google-login-btn:hover { transform: scale(1.02); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }

    /* Hide Sidebar */
    [data-testid="stSidebar"] { display: none; }
            
 button[kind="primaryFormSubmit"] {
        background: linear-gradient(135deg, #00e5ff, #007bff) !important; /* Your desired background color */
        color: black !important;              /* Text color */
        border: none !important;
        border-radius: 100px !important;
            margin-left: 13px !important;
        box-shadow: 0 5px 15px rgba(0,123,255,0.3) !important;
        height: 35px !important;
        padding: 0 22px !important;  
        width:110px;   
    }

    /* Optional: Add a hover effect */
    button[kind="primaryFormSubmit"]:hover {
        background:linear-gradient(135deg, #007bff, #00e5ff) !important; /* Darker shade on hover */
        color: black !important;
        border: none !important;
    }
            
    .divider-container {
        display: flex;
        align-items: center;
        text-align: center;
        margin-top: 3px;
        margin-left: 475px;
             max-width: 400px; 
        color: rgb(255 ,255 ,255,60%);
    }

    .divider-container::before,
    .divider-container::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid rgb(255 ,255 ,255,60%);
    }
            

    .divider-container:not(:empty)::before {
        margin-right: .75em;
    }

    .divider-container:not(:empty)::after {
        margin-left: .75em;
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# 3. HELPER COMPONENTS
# =============================
def render_card(icon, title, desc, delay="0.2s"):
    st.markdown(f"""
    <div class="animate-up" style="animation-delay: {delay}">
        <div class="custom-card">
            <div class="icon-box">{icon}</div>
            <div class="card-title">{title}</div>
            <div class="card-description">{desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_step(step, icon, title, desc, delay="0.2s"):
    st.markdown(f"""
    <div class="step-wrapper animate-up" style="animation-delay: {delay}">
        <div class="step-badge">{step}</div>
        <div class="custom-card">
            <div class="icon-box" style="margin-top: 5px;">{icon}</div>
            <div class="card-title">{title}</div>
            <div class="card-description">{desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Icons
icon_ai = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>'
icon_chart = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>'
icon_shield = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
icon_eye = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>'
icon_login = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>'
icon_link = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>'

# ==============================
# 4. MAIN UI LAYOUT
# ==============================

# HERO SECTION
st.markdown("""
<div class="hero-card">
    <div class="app-logo"><span style="color:white; font-size:32px;">▶</span></div>
    <div style="font-size: 50px; font-weight: 800; color: white;">YouTube AI Analytics</div>
    <div style="font-size: 18px; color: #94a3b8; margin-bottom: 30px;">Unlock growth secrets with deep analysis and AI recommendations</div>
</div>
""", unsafe_allow_html=True)

# SEARCH FORM
with st.form("analyze_channel_form"):
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        channel_input = st.text_input("Channel", placeholder="Search any channel name...", label_visibility="collapsed")
    with col_btn:
        submitted = st.form_submit_button("Analyze", type="primary" )

if submitted and channel_input.strip():
    st.session_state["authenticated"] = True
    st.session_state["pending_channel"] = channel_input.strip()
    st.switch_page("pages/app.py")

# GOOGLE AUTH
st.markdown('<div class="divider-container" style="text-align: center;  color:rgb(255 ,255 ,255,60%);">OR</div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center;">
    <a class="google-login-btn" href="{authorization_url}">
        <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" width="20" height="20" />
        Continue with Google
    </a>
</div>
""", unsafe_allow_html=True)

# WHY USE SECTION
st.markdown('<h2 class="section-header animate-up" style="margin-bottom: 30px;">Why use this platform?</h2>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: render_card(icon_ai, "AI-Powered Insights", "Get intelligent recommendations and deep analysis of performance.", "0.2s")
with c2: render_card(icon_chart, "Personalized Analytics", "Track metrics that matter most to your growth and engagement.", "0.4s")
with c3: render_card(icon_shield, "Secure Authentication", "Data protected with enterprise-grade Google OAuth security and auto-linking.", "0.6s")

# HOW IT WORKS SECTION
st.markdown('<h2 class="section-header animate-up" style="margin-bottom: 30px; margin-top: 30px;">How it works</h2>', unsafe_allow_html=True)
s1, s2, s3, s4 = st.columns(4)
with s1: render_step(1, icon_eye, "Preview Analytics", "Explore sample data to see insights first.", "0.2s")
with s2: render_step(2, icon_login, "Login with Google", "Securely authenticate your account.", "0.4s")
with s3: render_step(3, icon_link, "Auto-link Channel", "Connect your channel automatically.", "0.6s")
with s4: render_step(4, icon_ai, "Get AI Insights", "Receive personalized recommendations.", "0.8s")

# ==============================
# 5. OAUTH REDIRECT HANDLING
# ==============================
if "code" in st.query_params:
    try:
        token = oauth.fetch_token(TOKEN_URL, code=st.query_params["code"])
        user_info = oauth.get(USERINFO_URL).json()
        yt_info = get_youtube_channel_info(token['access_token'])
        
        st.session_state["authenticated"] = True
        st.session_state["user"] = user_info
        st.session_state["user_yt_channel"] = yt_info
        
        if yt_info and yt_info.get("channel_name"):
            st.session_state["user_channel"] = yt_info["channel_name"]
            if not st.session_state.get("search_value"):
                st.session_state["search_value"] = yt_info["channel_name"]

        st.success(f"Welcome back, {user_info.get('name')}!")
        st.switch_page("pages/app.py")
    except Exception as e:
        st.error(f"Login Error: {e}")