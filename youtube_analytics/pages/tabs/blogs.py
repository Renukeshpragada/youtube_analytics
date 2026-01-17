import streamlit as st

def render(df=None):
    # ==============================
    # 1. LUXURY UI CSS & GRID LOGIC
    # ==============================
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
        
        .blog-wrapper {
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: white;
            animation: fadeIn 0.8s ease-out;
        }

        @keyframes fadeIn { from {opacity: 0; transform: translateY(20px);} to {opacity: 1; transform: translateY(0);} }

        /* Header Styling */
        .header-section { text-align: center; margin-bottom: 50px; }
        .main-title { font-size: 3rem; font-weight: 800; letter-spacing: -1.5px; margin-bottom: 5px; }
        .main-title span { color: #ff4b4b; }
        .sub-tagline { color: #94a3b8; font-size: 1.1rem; max-width: 600px; margin: 0 auto; }

        /* Metric Cards Row */
        .stat-card {
            background: #0d161f;
            box-shadow: 0 10px 30px rgba(139, 144, 150, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            transition: 0.3s;
        }
        .stat-card:hover { border-color: #ff4b4b; background: rgba(255, 75, 75, 0.03); }
        .stat-val { font-size: 1.6rem; font-weight: 800; color: white; display: block; }
        .stat-lab { color: #64748b; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }

        /* Category Chips */
        .chip-container { display: flex; justify-content: center; gap: 10px; margin: 40px 0; }
        .chip {
            padding: 8px 18px; border-radius: 50px; background: #1a1f26; 
            border: 1px solid #2d3748; color: #94a3b8; font-size: 0.8rem; 
            font-weight: 600; cursor: pointer; transition: 0.3s;
        }
        .chip.active { background: #ff4b4b; color: white; border-color: #ff4b4b; box-shadow: 0 0 15px rgba(255, 75, 75, 0.3); }

        /* THE GRID ARTICLE CARD */
        .grid-card {
            background: #0d121a; 
            border-radius: 18px; 
            border: 1px solid rgba(255,255,255,0.05);
            overflow: hidden; 
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            margin-bottom: 25px;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
                
                /* --- PROMO HERO BANNER CSS --- */
.promo-banner {
    background: linear-gradient(135deg, #0d121a 0%, #1a1f26 100%);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 24px;
    padding: 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 50px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}

.promo-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(255, 75, 75, 0.1) 0%, transparent 70%);
    z-index: 0;
}

.promo-content {
    z-index: 1;
    max-width: 60%;
}

.promo-tag {
    background: rgba(255, 75, 75, 0.15);
    color: #ff4b4b;
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.promo-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: white;
    margin: 15px 0;
    line-height: 1.1;
}

.promo-sub {
    color: #94a3b8;
    font-size: 1rem;
    margin-bottom: 25px;
}

.promo-btn {
    background: #ff4b4b;
    color: white !important;
    padding: 12px 28px;
    border-radius: 10px;
    font-weight: 700;
    text-decoration: none;
    display: inline-block;
    transition: 0.3s;
    box-shadow: 0 8px 20px rgba(255, 75, 75, 0.2);
}

.promo-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 25px rgba(255, 75, 75, 0.4);
    background: #ff3333;
}

/* --- ENHANCED PROMO VISUAL --- */
.promo-visual {
    width: 280px;  /* Increased width */
    height: 320px; /* Increased height */
    background: url('https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?q=80&w=600') center/cover;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    position: relative;
    transform: rotate(6deg); /* Subtle professional tilt */
    box-shadow: -20px 20px 50px rgba(0,0,0,0.6); /* Deep shadow for 3D effect */
    display: flex;
    align-items: flex-end;
    padding: 20px;
    overflow: hidden;
}

.promo-visual::after {
    content: "STRATEGY 2024";
    position: absolute;
    bottom: 20px;
    left: 20px;
    color: white;
    font-weight: 900;
    font-size: 0.9rem;
    letter-spacing: 2px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.8);
}

/* Add a glass overlay to the image to make it look like a real book cover */
.promo-overlay {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(180deg, transparent 50%, rgba(0,0,0,0.8) 100%);
}
                /* --- NEW COMPONENTS CSS --- */
.breaking-news {
    background: linear-gradient(90deg, #ff4b4b 0%, #990000 100%);
    color: white; padding: 10px 20px; border-radius: 10px;
    font-weight: 700; font-size: 0.85rem; margin-bottom: 30px;
    display: flex; align-items: center; gap: 10px;
                margin-top:30px;
            box-shadow:
}

.tool-grid {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 20px;
}
.tool-item {
    background: #1a1f26; border: 1px solid #2d3748;
    padding: 15px; border-radius: 12px; text-align: center;
    transition: 0.3s; cursor: pointer;
}
.tool-item:hover { border-color: #ff4b4b; transform: scale(1.05); }

.newsletter-card {
    background: linear-gradient(135deg, #0d121a 0%, #1a1f26 100%);
    border: 1px solid #ff4b4b; border-radius: 24px;
    padding: 40px; text-align: center; margin-top: 60px;
    box-shadow: 0 10px 30px rgba(255, 75, 75, 0.1);
}
.newsletter-title { font-size: 1.8rem; font-weight: 800; margin-bottom: 10px; }
        .grid-card:hover { 
            transform: translateY(-8px); 
            border-color: #ff4b4b; 
            box-shadow: 0 15px 30px rgba(0,0,0,0.4);
        }
        .card-img { 
            width: 100%; 
            height: 180px; 
            object-fit: cover; 
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .card-body { padding: 20px; flex-grow: 1; display: flex; flex-direction: column; }
        .card-cat { color: #ff4b4b; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; }
        .card-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 10px; line-height: 1.4; color: white; }
        .card-desc { color: #94a3b8; font-size: 0.85rem; line-height: 1.5; margin-bottom: 20px; flex-grow: 1; }
        .card-foot { display: flex; justify-content: space-between; color: #4a5568; font-size: 0.7rem; font-weight: 600; border-top: 1px solid rgba(255,255,255,0.03); padding-top: 15px; }
        
        .read-more { color: #ff4b4b; font-weight: 700; text-decoration: none; font-size: 0.85rem; margin-top: 10px; }

        /* Featured Card logic */
        .feat-card {
            background: #0d121a; border-radius: 20px; border: 1px solid #1e293b;
            display: flex; overflow: hidden; margin-bottom: 50px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="blog-wrapper">', unsafe_allow_html=True)

    # --- 1. HEADER & METRICS ---
    st.markdown("""
    <div class="header-section">
        <h1 class="main-title">YouTube Growth <span>Insights</span></h1>
        <div class="sub-tagline">Data-driven strategies and expert analysis to help you scale your channel.</div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown('<div class="stat-card"><span class="stat-val">150+</span><span class="stat-lab">Articles</span></div>', unsafe_allow_html=True)
    with m2: st.markdown('<div class="stat-card"><span class="stat-val">50K+</span><span class="stat-lab">Readers</span></div>', unsafe_allow_html=True)
    with m3: st.markdown('<div class="stat-card"><span class="stat-val">200+</span><span class="stat-lab">Stories</span></div>', unsafe_allow_html=True)
    with m4: st.markdown('<div class="stat-card"><span class="stat-val">1M+</span><span class="stat-lab">Views</span></div>', unsafe_allow_html=True)

    # --- 2. CATEGORY CHIPS ---
   # --- BREAKING UPDATE BANNER ---
    st.markdown("""
      <div class="breaking-news">
        <span style="background:white; color:black; padding:2px 8px; border-radius:4px; font-size:0.7rem;">NEW</span>
        YouTube Algorithm Update: Watch time retention is now weighted 20% higher for shorts.
      </div>
    """, unsafe_allow_html=True)
    # --- CREATOR TOOLKIT SECTION ---
    st.markdown("### 🧰 Essential Creator Toolkit")
    st.markdown("""
      <div class="tool-grid">
      <div class="tool-item"><div style="font-size:1.5rem;">🔍</div><div style="font-size:0.8rem; font-weight:700; color:white; margin-top:5px;">SEO AI</div></div>
      <div class="tool-item"><div style="font-size:1.5rem;">🎨</div><div style="font-size:0.8rem; font-weight:700; color:white; margin-top:5px;">Thumbnail</div></div>
      <div class="tool-item"><div style="font-size:1.5rem;">✂️</div><div style="font-size:0.8rem; font-weight:700; color:white; margin-top:5px;">Editor</div></div>
      <div class="tool-item"><div style="font-size:1.5rem;">🎵</div><div style="font-size:0.8rem; font-weight:700; color:white; margin-top:5px;">Music</div></div>
      </div>
      """, unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    # --- THE HIGH-IMPACT PROMO BANNER ---
    # --- THE PROFESSIONAL PROMO BANNER ---
    st.markdown("""
<div class="promo-banner">
    <div class="promo-content">
        <span class="promo-tag">Free Masterclass</span>
        <div class="promo-title">The 2024 YouTube <br>Growth Roadmap</div>
        <p class="promo-sub">Download our comprehensive 50-page guide on mastering the algorithm, increasing retention, and scaling to your first 100k subscribers.</p>
        <a href="#" class="promo-btn">Download Guide PDF →</a>
    </div>
    <div class="promo-visual">
        <div class="promo-overlay"></div>
    </div>
</div>
    """, unsafe_allow_html=True)
    # --- 3. THE 3-COLUMN ARTICLE GRID ---
    articles = [
        {
            "cat": "Analytics",
            "title": "Understanding YouTube Analytics: A Complete Guide",
            "desc": "Learn how to interpret your dashboard metrics to make high-impact content decisions.",
            "img": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=500",
            "date": "Jan 8, 2024", "read": "12 min"
        },
        {
            "cat": "Strategy",
            "title": "The Algorithm Decoded: What Gets Views",
            "desc": "An in-depth analysis of YouTube's recommendation system for new channels.",
            "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=500",
            "date": "Jan 5, 2024", "read": "10 min"
        },
        {
            "cat": "Design",
            "title": "Thumbnail Design Psychology: Colors That Win",
            "desc": "Research-backed insights into color psychology and visual principles that drive CTR.",
            "img": "https://images.unsplash.com/photo-1558655146-d09347e92766?q=80&w=500",
            "date": "Jan 3, 2024", "read": "6 min"
        },
        {
            "cat": "Monetization",
            "title": "Beyond AdSense: Diverse Revenue Streams",
            "desc": "Explore brand deals, memberships, and digital products to maximize your channel's earnings.",
            "img": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?q=80&w=500",
            "date": "Dec 28, 2023", "read": "15 min"
        },
        {
            "cat": "Content",
            "title": "Audience Retention Secrets From Top Creators",
            "desc": "Practical editing and pacing techniques to keep viewers hooked from start to finish.",
            "img": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=500",
            "date": "Dec 20, 2023", "read": "9 min"
        },
        {
            "cat": "Growth",
            "title": "Scaling From 0 to 10k Subscribers Fast",
            "desc": "The exact roadmap used by successful creators to build momentum in their first year.",
            "img": "https://images.unsplash.com/photo-1512314889357-e157c22f938d?q=80&w=500",
            "date": "Dec 15, 2023", "read": "11 min"
        }
    ]

    # Use a loop to create rows of 3 columns
    for i in range(0, len(articles), 3):
        cols = st.columns(3)
        # Select 3 articles at a time
        chunk = articles[i : i + 3]
        
        for idx, art in enumerate(chunk):
            with cols[idx]:
                st.markdown(f"""
                <div class="grid-card">
                    <img src="{art['img']}" class="card-img">
                    <div class="card-body">
                        <div class="card-cat">{art['cat']}</div>
                        <div class="card-title">{art['title']}</div>
                        <p class="card-desc">{art['desc']}</p>
                        <div class="card-foot">
                            <span>📅 {art['date']}</span>
                            <span>⏱️ {art['read']} read</span>
                        </div>
                        <a href="#" class="read-more">Read Full Article →</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # Close blog-wrapper
