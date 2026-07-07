import json
import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_lottie import st_lottie
from utils.logger import get_logger
from ui.theme import html_markdown, get_theme_colors

logger = get_logger("animations")

def load_lottie_url(url: str) -> dict:
    """Download Lottie JSON from URL with caching and error handling."""
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return {}
        return r.json()
    except Exception as exc:
        logger.warning(f"Failed to load Lottie animation from {url}: {exc}")
        return {}

def render_lottie_hero():
    """Render a travel Lottie animation on the landing page."""
    # A standard public travel/map animation
    url = "https://lottie.host/80e9a3ef-ef36-47b2-a4e8-28ffedce7f7c/Y7Qk0lHl4t.json" # modern travel animation
    lottie_json = load_lottie_url(url)
    
    if lottie_json:
        st_lottie(lottie_json, speed=1, height=280, key="hero_lottie")
    else:
        # Fallback static container if offline
        html_markdown(
            """
            <div style='text-align: center; font-size: 80px; margin: 20px 0;'>
                🗺️✈️
            </div>
            """
        )

def render_loading_shimmer():
    """Render a CSS skeleton shimmer loader."""
    shimmer_html = """
    <div class="glass-card fade-in-up" style="padding: 24px; margin: 15px 0;">
        <div class="shimmer" style="height: 28px; width: 60%; margin-bottom: 15px;"></div>
        <div class="shimmer" style="height: 16px; width: 90%; margin-bottom: 8px;"></div>
        <div class="shimmer" style="height: 16px; width: 85%; margin-bottom: 8px;"></div>
        <div class="shimmer" style="height: 16px; width: 40%;"></div>
    </div>
    """
    html_markdown(shimmer_html)

def render_number_count_up(value: float, label: str = "Estimated Total Cost"):
    """
    Render a dynamic JS count-up component for budget totals.
    Uses custom CSS vars to match light/dark styling.
    """
    # Grab colors to keep colors consistent in HTML component
    colors = get_theme_colors()
    color = colors["primary"]
    text_color = colors["text"]
    
    html_content = f"""
    <div style="font-family: 'Poppins', 'Inter', sans-serif; text-align: center; padding: 15px; border-radius: 12px; background: rgba(0,0,0,0.02);">
        <div style="font-size: 14px; font-weight: 500; color: {text_color}; opacity: 0.8; margin-bottom: 5px;">{label}</div>
        <div id="counter" style="font-size: 40px; font-weight: 800; color: {color}; margin: 0;">₹0</div>
    </div>
    <script>
        let target = {int(value)};
        let current = 0;
        let duration = 1200; // 1.2s count up duration
        let startTime = null;
        
        function animate(timestamp) {{
            if (!startTime) startTime = timestamp;
            let progress = timestamp - startTime;
            current = Math.min(Math.floor((progress / duration) * target), target);
            document.getElementById("counter").innerText = "₹" + current.toLocaleString('en-IN');
            if (progress < duration) {{
                window.requestAnimationFrame(animate);
            }} else {{
                document.getElementById("counter").innerText = "₹" + target.toLocaleString('en-IN');
            }}
        }}
        window.requestAnimationFrame(animate);
    </script>
    """
    components.html(html_content, height=110, scrolling=False)
