"""
CSS Injection Utility for CVFoster Dark Theme

Provides safe, efficient CSS injection into Streamlit applications.
Reads theme CSS from file and injects via st.markdown for consistency across all components.
"""

import streamlit as st
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def inject_theme_css(theme_file: str = "src/theme.css") -> bool:
    """
    Inject custom dark theme CSS into Streamlit app.
    
    Reads a CSS file and injects it via st.markdown with unsafe_allow_html=True.
    Called once at app startup to ensure consistent styling across all components.
    
    Args:
        theme_file: Path to CSS file (relative to app root). Default: src/theme.css
    
    Returns:
        True if injection succeeded, False if file not found (fallback to minimal CSS)
    
    Example:
        # At top of app.py, after st.set_page_config
        inject_theme_css()
    """
    try:
        css_path = Path(__file__).parent / theme_file.replace("src/", "")
        
        # Try alternate paths if first doesn't exist
        if not css_path.exists():
            css_path = Path(__file__).parent.parent / theme_file
        
        if not css_path.exists():
            logger.warning(f"Theme CSS file not found at {css_path}. Using fallback styles.")
            _inject_fallback_css()
            return False
        
        # Read CSS file
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Inject into Streamlit
        st.markdown(
            f"<style>{css_content}</style>",
            unsafe_allow_html=True
        )
        
        logger.info(f"✅ Theme CSS injected successfully from {css_path}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to inject theme CSS: {e}")
        _inject_fallback_css()
        return False


def _inject_fallback_css() -> None:
    """
    Inject minimal fallback CSS if theme file not found.
    
    Ensures app remains functional with basic dark mode styling,
    even if theme.css is missing or unreadable.
    """
    fallback_css = """
    <style>
    :root {
        --primary-color: #06A87D;
        --bg-base: #1A1A1A;
        --text-primary: #FFFFFF;
        --text-secondary: #B0B0B0;
    }
    
    html { 
        color-scheme: dark; 
        background-color: var(--bg-base);
        color: var(--text-primary);
    }
    
    body {
        background-color: var(--bg-base);
        color: var(--text-primary);
    }
    
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb { background: var(--primary-color); border-radius: 5px; }
    ::-webkit-scrollbar-thumb:hover { background: #48C9B0; }
    
    a { color: var(--primary-color); }
    a:hover { color: #48C9B0; }
    </style>
    """
    st.markdown(fallback_css, unsafe_allow_html=True)
    logger.warning("⚠️ Using fallback CSS. Some styling may be limited.")


def get_theme_color(color_type: str) -> str:
    """
    Get a color from the theme palette for dynamic styling.
    
    Args:
        color_type: Color variable name (e.g., 'primary-main', 'success-color')
    
    Returns:
        Hex color value, or default if not found
    
    Example:
        primary = get_theme_color('primary-main')  # Returns '#06A87D'
    """
    colors = {
        'primary-dark': '#0F2D2D',
        'primary-main': '#06A87D',
        'primary-light': '#00A86B',
        'primary-lighter': '#48C9B0',
        'secondary-teal': '#20B2AA',
        'bg-base': '#1A1A1A',
        'bg-surface': '#242424',
        'bg-hover': '#2E2E2E',
        'text-primary': '#FFFFFF',
        'text-secondary': '#B0B0B0',
        'text-muted': '#808080',
        'text-accent': '#06A87D',
        'success-color': '#4CAF50',
        'warning-color': '#FFA726',
        'error-color': '#EF5350',
        'info-color': '#29B6F6',
    }
    return colors.get(color_type, '#06A87D')  # Default to primary-main
