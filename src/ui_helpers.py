"""
UI helper functions for Streamlit components.
Provides reusable UI elements and formatting utilities.
"""

import streamlit as st
from typing import List, Dict, Optional
import pandas as pd

def render_section_header(title: str, level: int = 1):
    """Render a section header."""
    marker = "#" * level
    st.markdown(f"{marker} {title}")

def render_score_breakdown(scores: Dict[str, str]) -> None:
    """
    Render score breakdown as visual components with styled metrics.
    
    Args:
        scores: Dict with semantic_pct, keyword_pct, seniority_pct
    """
    col1, col2, col3 = st.columns(3)
    
    # Format percentages with 2 decimal places
    semantic_pct = f"{scores.get('semantic_pct', 0):.2f}%" if isinstance(scores.get('semantic_pct'), (int, float)) else 'N/A'
    keyword_pct = f"{scores.get('keyword_pct', 0):.2f}%" if isinstance(scores.get('keyword_pct'), (int, float)) else 'N/A'
    seniority_pct = f"{scores.get('seniority_pct', 0):.2f}%" if isinstance(scores.get('seniority_pct'), (int, float)) else 'N/A'
    
    with col1:
        _render_styled_metric("Semantic Match", semantic_pct, "🧠")
    
    with col2:
        _render_styled_metric("Keyword Overlap", keyword_pct, "🔑")
    
    with col3:
        _render_styled_metric("Seniority Match", seniority_pct, "📈")

def render_match_result(match: Dict, index: int = 0) -> None:
    """
    Render a single job match result with professional styling.
    
    Args:
        match: Match dict from matcher
        index: Result index for display
    """
    score = match.get('match_score', 0)
    score_pct = score * 100
    
    # Render styled match card
    st.markdown(f"""
    <div class="match-card" style="animation: fadeIn 0.3s ease-out;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
            <div>
                <div class="match-card-title">#{index + 1}: {match.get('title', 'Unknown')}</div>
                <div class="match-card-subtitle">
                    {match.get('company', 'Unknown')}
                    {' • ' + match.get('location', '') if match.get('location') else ''}
                </div>
            </div>
            <div class="match-card-score" style="font-size: 1.5rem; padding: 0.75rem 1rem; min-width: 80px;">
                {score:.2f}
                <br/>
                <span style="font-size: 0.75rem; opacity: 0.9;">{score_pct:.0f}%</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show description if available
    description = match.get('description', 'No description available')
    if description and description != 'No description':
        st.markdown(f"**Description:** {description}")
    
    # Show score breakdown
    st.markdown("**Score Breakdown** (weighted: Semantic 50% • Keyword 30% • Seniority 20%)")
    render_score_breakdown(match.get('score_breakdown', {}))
    
    # Show matched chunk
    if match.get('matched_chunks'):
        with st.expander("📌 Matched CV Section"):
            chunk = match['matched_chunks'][0]
            st.text(chunk.get('chunk_text', 'N/A'))

def render_matches_list(matches: List[Dict]) -> None:
    """
    Render all job matches.
    
    Args:
        matches: List of match dicts
    """
    if not matches:
        st.warning("No matches found. Try different CV content.")
        return
    
    st.markdown(f"### Found {len(matches)} Match(es)")
    
    for idx, match in enumerate(matches):
        render_match_result(match, idx)

def render_rewrite_result(result: Dict) -> None:
    """
    Render rewrite result with before/after comparison.
    
    Args:
        result: Rewrite result dict
    """
    with st.container(border=True):
        if not result.get('success'):
            st.error(f"Rewrite failed: {result.get('error', 'Unknown error')}")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Original**")
            st.text_area(
                "Original text",
                value=result['original'],
                height=200,
                disabled=True,
                label_visibility="collapsed",
                key="rewrite_result_original"
            )
            st.caption(f"Length: {result.get('original_length', 0)} words")
        
        with col2:
            st.markdown("**Rewritten**")
            st.text_area(
                "Rewritten text",
                value=result['rewritten'],
                height=200,
                disabled=True,
                label_visibility="collapsed",
                key="rewrite_result_rewritten"
            )
            st.caption(f"Length: {result.get('rewritten_length', 0)} words")
        
        # Download button
        st.download_button(
            label="📥 Download Rewritten Text",
            data=result['rewritten'],
            file_name="rewritten_section.txt",
            mime="text/plain"
        )

def render_rewrite_variants(result: Dict) -> None:
    """
    Render multi-variant rewrite results with comparison and selection.
    Phase 2 feature: Display multiple rewrites and let user pick best.
    
    Args:
        result: Multi-variant rewrite result dict
    """
    with st.container(border=True):
        if not result.get('success') or not result.get('variants'):
            st.error(f"Variant generation failed: {result.get('error', 'Unknown error')}")
            return
        
        variants = result.get('variants', [])
        num_variants = len(variants)
        
        st.markdown(f"### Generated {num_variants} Variant{'s' if num_variants > 1 else ''}")
        st.caption(f"Mode: **{result.get('mode', 'unknown').upper()}** | Original: {result.get('original_length', 0)} words")
        
        # Create tabs for each variant
        tabs = st.tabs([f"Variant {i+1}" for i in range(num_variants)])
        
        for idx, (tab, variant) in enumerate(zip(tabs, variants)):
            with tab:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Original**")
                    st.text_area(
                        f"original_{idx}",
                        value=variant['original'],
                        height=150,
                        disabled=True,
                        label_visibility="collapsed",
                        key=f"orig_{idx}"
                    )
                    st.caption(f"Length: {variant.get('original_length', 0)} words")
                
                with col2:
                    st.markdown("**Variant Rewrite**")
                    st.text_area(
                        f"variant_{idx}",
                        value=variant['rewritten'],
                        height=150,
                        disabled=True,
                        label_visibility="collapsed",
                        key=f"var_{idx}"
                    )
                    st.caption(f"Length: {variant.get('rewritten_length', 0)} words")
                
                # Variant metadata
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    method = variant.get('method', 'unknown')
                    st.metric("Method", "Azure" if method == 'azure_openai' else "Template")
                
                with col_b:
                    if 'temperature' in variant:
                        st.metric("Temperature", f"{variant['temperature']:.1f}")
                
                with col_c:
                    length_diff = variant.get('rewritten_length', 0) - variant.get('original_length', 0)
                    st.metric("Length Δ", f"{length_diff:+d} words")
                
                # Download button for this variant
                st.download_button(
                    label=f"📥 Download Variant {idx+1}",
                    data=variant['rewritten'],
                    file_name=f"rewritten_variant_{idx+1}.txt",
                    mime="text/plain",
                    key=f"download_{idx}"
                )
                
                st.divider()
        
        # Comparison view
        st.markdown("### Quick Comparison")
        
        comparison_data = []
        for idx, variant in enumerate(variants):
            comparison_data.append({
                'Variant': f"#{idx+1}",
                'Method': variant.get('method', 'unknown'),
                'Original Length': variant.get('original_length', 0),
                'New Length': variant.get('rewritten_length', 0),
                'Reduction': f"{((variant.get('original_length', 1) - variant.get('rewritten_length', 0)) / variant.get('original_length', 1) * 100):.1f}%"
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Download all variants as zip
        st.markdown("### Export All Variants")
        all_text = "\n\n---\n\n".join([
            f"## Variant {idx+1}\n\n{variant['rewritten']}"
            for idx, variant in enumerate(variants)
        ])
        
        st.download_button(
            label="📦 Download All Variants (TXT)",
            data=all_text,
            file_name="all_variants.txt",
            mime="text/plain",
            use_container_width=True
        )

def render_file_upload_section(key: str = "file_uploader") -> Optional[bytes]:
    """
    Render file upload section.
    
    Args:
        key: Streamlit component key
    
    Returns:
        Uploaded file content or None
    """
    uploaded_file = st.file_uploader(
        "Upload your CV",
        type=['pdf', 'docx', 'txt'],
        key=key,
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    if uploaded_file:
        return uploaded_file.getvalue()
    
    return None

def render_job_upload_section(key: str = "job_uploader") -> Optional[bytes]:
    """
    Render job postings upload section (CSV/JSON).
    
    Args:
        key: Streamlit component key
    
    Returns:
        Uploaded file content or None
    """
    uploaded_file = st.file_uploader(
        "Upload job postings CSV/JSON",
        type=['csv', 'json'],
        key=key,
        help="Expected columns: job_id, title, description, company, skills, seniority"
    )
    
    if uploaded_file:
        return uploaded_file.getvalue()
    
    return None

def render_sampling_info(stats: Dict) -> None:
    """
    Render indexing statistics.
    
    Args:
        stats: Stats dict from EmbeddingIndex
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Chunks", stats.get('total_chunks', 0))
    
    with col2:
        st.metric("Embedding Dim", stats.get('embedding_dim', 0))
    
    with col3:
        st.metric("Index Size", stats.get('index_size', 0))

def render_page_header(title: str, subtitle: str = "", emoji: str = "📄", style: str = "blue") -> None:
    """
    Render a styled page header with emoji and subtitle using CVFoster dark theme.
    
    Args:
        title: Main page title
        subtitle: Optional subtitle/description
        emoji: Emoji to display
        style: Color style (teal, green, orange, warning, error, etc.)
    """
    # CVFoster color palette
    color_map = {
        'teal': '#06A87D',
        'green': '#00A86B',
        'orange': '#FFA726',
        'warning': '#FFA726',
        'error': '#EF5350',
        'blue': '#29B6F6',
        'success': '#4CAF50',
        'purple': '#AB47BC',
    }
    
    color = color_map.get(style, '#06A87D')
    
    st.markdown(f"""
    <div class="page-header" style="
        background: linear-gradient(135deg, rgba(6, 168, 125, 0.1) 0%, rgba(6, 168, 125, 0.05) 100%);
        padding: 20px;
        margin: -20px -20px 20px -20px;
        border-left: 4px solid {color};
        border-radius: 0 8px 8px 0;
        animation: slideInLeft 0.3s ease-out;
    ">
        <h1 style="margin: 0; color: {color}; font-weight: 700;">{emoji} {title}</h1>
        {f'<p style="margin: 5px 0 0 0; color: #B0B0B0; font-size: 0.95em;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_cv_sections_professional(sections: Dict[str, str]) -> None:
    """
    Render parsed CV sections in a professional format with styled expanders.
    
    Args:
        sections: Dict of section_name -> section_text
    """
    for idx, (section_name, section_text) in enumerate(sections.items()):
        with st.expander(f"📄 {section_name.title()}", expanded=False):
            st.text(section_text[:500] + ('...' if len(section_text) > 500 else ''))
            st.caption(f"Length: {len(section_text)} characters")
            # Add subtle progress bar for section completion
            text_length = len(section_text)
            max_length = 2000
            progress = min(text_length / max_length, 1.0)
            st.progress(progress, text="Section completeness")

def render_cv_sections(sections: Dict[str, str]) -> None:
    """
    Render parsed CV sections.
    
    Args:
        sections: Dict of section_name -> section_text
    """
    st.markdown("### Detected CV Sections")
    
    for section_name, section_text in sections.items():
        with st.expander(f"📄 {section_name.title()}"):
            st.text(section_text[:500] + ('...' if len(section_text) > 500 else ''))

def render_loading_placeholder(message: str = "Processing..."):
    """Render a loading placeholder."""
    with st.spinner(message):
        st.write("")

def format_download_text(text: str, title: str = "") -> str:
    """Format text for download."""
    if title:
        content = f"{title}\n{'=' * len(title)}\n\n{text}"
    else:
        content = text
    
    return content


# ============================================
# STYLED COMPONENT UTILITIES
# ============================================

def _render_styled_metric(label: str, value: str, icon: str = "") -> None:
    """
    Render a styled metric card with icon.
    
    Args:
        label: Metric label
        value: Metric value
        icon: Optional emoji/icon
    """
    st.markdown(f"""
    <div class="metric" style="animation: fadeIn 0.3s ease-out;">
        <div class="metric-label">{icon} {label if not icon else label}</div>
        <div class="metric-value accent">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(status: str, style: str = "success") -> str:
    """
    Create a styled status badge.
    
    Args:
        status: Status text
        style: Style type (success, warning, error, info)
    
    Returns:
        HTML string for badge
    """
    color_map = {
        'success': ('#4CAF50', '#1B5E20'),
        'warning': ('#FFA726', '#E65100'),
        'error': ('#EF5350', '#B71C1C'),
        'info': ('#29B6F6', '#01579B'),
    }
    fg, bg = color_map.get(style, color_map['success'])
    
    return f"""
    <span style="
        background-color: {bg};
        color: {fg};
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    ">{status}</span>
    """


def render_info_box(title: str, content: str, icon: str = "ℹ️", style: str = "info") -> None:
    """
    Render styled info/alert box.
    
    Args:
        title: Box title
        content: Box content
        icon: Emoji/icon for box
        style: Style type (success, warning, error, info)
    """
    color_map = {
        'success': '#4CAF50',
        'warning': '#FFA726',
        'error': '#EF5350',
        'info': '#29B6F6',
    }
    color = color_map.get(style, color_map['info'])
    
    st.markdown(f"""
    <div class="alert alert-{style}" style="border-radius: 8px; padding: 1rem;">
        <div class="alert-icon" style="color: {color}; font-size: 1.25rem;">{icon}</div>
        <div class="alert-content">
            <div class="alert-title" style="color: {color};">{title}</div>
            <div class="alert-message">{content}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_progress_indicator(step: int, total_steps: int, step_name: str = "") -> None:
    """
    Render step progress indicator.
    
    Args:
        step: Current step (1-indexed)
        total_steps: Total number of steps
        step_name: Optional name of current step
    """
    progress = step / total_steps
    st.progress(progress, text=f"Step {step}/{total_steps}: {step_name}" if step_name else f"Step {step}/{total_steps}")
