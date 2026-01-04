import streamlit as st

def render(df=None):
    st.subheader("📰 Creator Resources")

    st.markdown("Learn what actually moves the needle. No fluff.")

    # -------- CATEGORY 1 --------
    with st.expander("📈 Growth & Algorithm",expanded=True):
        st.markdown("""
        **Understand how YouTube really works**
        
        - 🔗 [2024 Algorithm Guide](https://vidiq.com/blog)  
          *How YouTube recommends videos and what impacts reach.*
        
        - 🔗 [Why Your Videos Stop Getting Views](https://vidiq.com/blog)  
          *Retention, satisfaction signals, and timing.*
        """)

    # -------- CATEGORY 2 --------
    with st.expander("🎯 Titles & Thumbnails"):
        st.markdown("""
        **Increase CTR without clickbait**
        
        - 🔗 [How to Write Titles That Go Viral](https://vidiq.com/blog)  
          *Psychology-backed title frameworks.*
        
        - 🔗 [Thumbnail Design Secrets](https://vidiq.com/blog)  
          *Contrast, faces, emotion, and clarity.*
        """)

    # -------- CATEGORY 3 --------
    with st.expander("💰 Monetization"):
        st.markdown("""
        **Turn views into money**
        
        - 🔗 [Increase RPM Without More Views](https://vidiq.com/blog)  
          *Ad types, niches, and audience value.*
        
        - 🔗 [Why Some Channels Earn More](https://vidiq.com/blog)  
          *CPM myths vs reality.*
        """)

    # -------- CATEGORY 4 --------
    with st.expander("🛠 Analytics & Tools"):
        st.markdown("""
        **Use data properly**
        
        - 🔗 [How to Read YouTube Analytics](https://vidiq.com/blog)  
          *Metrics that matter vs vanity metrics.*
        
        - 🔗 [CTR, AVD & Retention Explained](https://vidiq.com/blog)  
          *What to fix first.*
        """)

    # -------- SMART SUGGESTION (OPTIONAL BUT POWERFUL) --------
    if df is not None and not df.empty:
        st.divider()
        st.subheader("📌 Suggested for You")

        st.markdown("""
        Based on your channel data, focus on:
        - Improving **titles & thumbnails** if CTR is low
        - Improving **retention** if views drop early
        - Monetization strategies if RPM is below average
        """)
    with st.expander("🚨 Common Creator Mistakes"):
        st.markdown("""
        **Avoid mistakes that silently kill growth**
    
        - ❌ Obsessing over subscribers instead of CTR & retention  
        - ❌ Uploading without checking past video performance  
        - ❌ Changing niches too frequently  
        - ❌ Ignoring first 30 seconds of the video  
        - ❌ Overloading thumbnails with text  
        *Fixing these alone improves performance for most small channels.*
        """)
    with st.expander("✅ Quick Wins (Do This Today)"):
        st.markdown("""
        **High-impact actions you can apply immediately**
    
        - Rewrite titles using curiosity + clarity  
        - Simplify thumbnails to ONE clear idea  
        - Hook viewers in first 5 seconds  
        - Remove long intros  
        - Upload consistently (even once a week beats randomness)
        """)
    if df is not None and not df.empty:
        st.divider()
        st.subheader("📊 Insights Based on Your Data")

        st.markdown("""
        Based on common analytics patterns:
    
        - 📉 **Low views?** → Focus on titles & thumbnails  
        - ⏱ **Low watch time?** → Improve pacing & hooks  
        - 💸 **Low earnings?** → Check RPM & niche demand  
        - 📈 **Spikes then drops?** → Retention problem in first 30 sec
        """)
    with st.expander("🧰 Recommended Creator Tools",expanded=True):
        st.markdown("""
        - 🔗 **vidIQ / TubeBuddy** – SEO & optimization  
        - 🔗 **Canva** – Thumbnail design  
        - 🔗 **CapCut / Premiere Pro** – Editing  
        - 🔗 **Google Trends** – Topic research  
        - 🔗 **YouTube Studio** – Core analytics
        """)

