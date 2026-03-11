"""
LLM module for CV rewriting and summarization.
Phase 1 MVP: Uses template-based rewriting by default.
Phase 1+ with Azure: Uses Azure OpenAI for LLM rewriting with template fallback.
"""

import logging
from typing import Dict, Optional
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file (local development)
load_dotenv()

# Support Streamlit Cloud secrets - map them to os.environ for consistency
try:
    import streamlit as st
    if hasattr(st, 'secrets') and st.secrets:
        try:
            for key, value in st.secrets.items():
                if key not in os.environ:
                    os.environ[key] = str(value)
        except:
            pass  # st.secrets might not be available in all contexts
except ImportError:
    pass

logger = logging.getLogger(__name__)

# Try to import Azure OpenAI client (optional)
try:
    from openai import AzureOpenAI
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logger.warning("Azure OpenAI client not installed. Falling back to template-based rewriting.")


# Cache Azure client - critical for Streamlit Cloud performance
try:
    import streamlit as st
    @st.cache_resource
    def get_azure_client() -> Optional[AzureOpenAI]:
        """
        Initialize Azure OpenAI client using environment variables.
        Cached to avoid reinitializing on every app run.
        
        Returns:
            AzureOpenAI client or None if credentials not available
        """
        if not AZURE_AVAILABLE:
            return None
        
        try:
            api_key = os.getenv('AZURE_OPENAI_API_KEY')
            endpoint = os.getenv('AZURE_ENDPOINT')
            api_version = os.getenv('AZURE_API_VERSION')
            
            if not all([api_key, endpoint, api_version]):
                logger.warning("Azure credentials not configured. Using template-based rewriting.")
                return None
            
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint
            )
            logger.info("Azure OpenAI client initialized successfully (cached)")
            return client
        
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            return None
except ImportError:
    # Fallback for non-Streamlit contexts (testing)
    def get_azure_client() -> Optional[AzureOpenAI]:
        """
        Initialize Azure OpenAI client using environment variables.
        
        Returns:
            AzureOpenAI client or None if credentials not available
        """
        if not AZURE_AVAILABLE:
            return None
        
        try:
            api_key = os.getenv('AZURE_OPENAI_API_KEY')
            endpoint = os.getenv('AZURE_ENDPOINT')
            api_version = os.getenv('AZURE_API_VERSION')
            
            if not all([api_key, endpoint, api_version]):
                logger.warning("Azure credentials not configured. Using template-based rewriting.")
                return None
            
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint
            )
            logger.info("Azure OpenAI client initialized successfully")
            return client
        
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            return None


def expand_common_abbreviations(text: str) -> str:
    """Expand common abbreviations."""
    abbreviations = {
        r'\bCS\b': 'Computer Science',
        r'\bIT\b': 'Information Technology',
        r'\bHR\b': 'Human Resources',
        r'\bAPI\b': 'Application Programming Interface',
        r'\bUML\b': 'Unified Modeling Language',
        r'\bDB\b': 'Database',
        r'\bSQL\b': 'SQL',
        r'\bJSON\b': 'JSON',
        r'\bQA\b': 'Quality Assurance',
    }
    
    for abbrev, full in abbreviations.items():
        text = re.sub(abbrev, full, text, flags=re.IGNORECASE)
    
    return text


def enhance_with_metrics(text: str) -> str:
    """Add emphasis to metrics and numbers."""
    # Highlight percentages
    text = re.sub(
        r'(\d+)\s*(percent|%)',
        r'\1% improvement',
        text
    )
    
    # Highlight increases/decreases with numbers
    text = re.sub(
        r'(increased|decreased|improved|reduced)\s+by\s+(\d+)',
        r'\1 by \2x',
        text,
        flags=re.IGNORECASE
    )
    
    return text


def use_action_verbs(text: str) -> str:
    """Replace weak verbs with strong action verbs."""
    action_verbs = {
        'worked': 'Engineered',
        'did': 'Delivered',
        'made': 'Architected',
        'created': 'Innovated',
        'built': 'Scaled',
        'helped': 'Enabled',
        'managed': 'Led',
        'handled': 'Orchestrated',
        'improved': 'Optimized',
        'increased': 'Accelerated',
        'reduced': 'Minimized',
        'used': 'Leveraged',
        'implemented': 'Deployed',
        'wrote': 'Developed',
        'designed': 'Architected',
        'tested': 'Validated',
        'fixed': 'Resolved',
        'changed': 'Transformed',
        'started': 'Initiated',
        'finished': 'Completed',
    }
    
    for weak, strong in action_verbs.items():
        text = re.sub(rf'\b{weak}\b', strong, text, flags=re.IGNORECASE)
    
    return text


class CVRewriter:
    """Handler for rewriting CV sections using Azure OpenAI (primary) or template-based fallback."""

    # Azure client (initialized once)
    AZURE_CLIENT = None
    AZURE_MODEL = os.getenv('AZURE_MODEL', 'gpt-4o-mini')

    @staticmethod
    def rewrite_section(
        text: str,
        mode: str = 'concise',
        use_azure: bool = True
    ) -> Dict:
        """
        Rewrite a CV section using Azure OpenAI (if available) or template-based approach.
        
        Args:
            text: CV section text (200-500 tokens recommended)
            mode: Rewriting mode (concise, ats, recruiter)
            use_azure: Try to use Azure OpenAI; fall back to template if unavailable
        
        Returns:
            Dict with original and rewritten text
        """
        if not text or len(text.strip()) < 50:
            logger.warning("Input text too short for rewriting")
            return {
                'original': text,
                'rewritten': text,
                'mode': mode,
                'success': False,
                'error': 'Text too short (minimum 50 characters)'
            }
        
        # Try Azure OpenAI first if requested
        if use_azure:
            result = CVRewriter._rewrite_with_azure(text, mode)
            if result and result.get('success'):
                return result
            logger.info("Azure rewriting failed or unavailable; falling back to template-based")
        
        # Fall back to template-based rewriting
        return CVRewriter._rewrite_with_template(text, mode)

    @staticmethod
    def _rewrite_with_azure(text: str, mode: str) -> Optional[Dict]:
        """
        Rewrite using Azure OpenAI LLM.
        
        Args:
            text: CV section text
            mode: Rewriting mode
        
        Returns:
            Dict with rewrite result or None if failed
        """
        if not AZURE_AVAILABLE:
            return None
        
        try:
            # Initialize client if not already done
            if CVRewriter.AZURE_CLIENT is None:
                CVRewriter.AZURE_CLIENT = get_azure_client()
            
            if CVRewriter.AZURE_CLIENT is None:
                return None
            
            # Create prompt based on mode
            mode_prompts = {
                'concise': "Rewrite the following CV section to be more concise and impactful, removing unnecessary words while preserving key information. Return ONLY the rewritten text without any explanation.",
                'ats': "Rewrite the following CV section to be optimized for Applicant Tracking Systems (ATS). Use standard keywords, avoid special characters, and ensure clear formatting. Return ONLY the rewritten text without any explanation.",
                'recruiter': "Rewrite the following CV section to be more appealing to recruiters. Use strong action verbs, highlight metrics and achievements, and emphasize impact. Return ONLY the rewritten text without any explanation."
            }
            
            prompt = mode_prompts.get(mode, mode_prompts['concise'])
            
            # Call Azure OpenAI
            response = CVRewriter.AZURE_CLIENT.chat.completions.create(
                model=CVRewriter.AZURE_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional CV and resume writer. Your task is to rewrite CV sections to improve their effectiveness."
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\n{text}"
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            rewritten_text = response.choices[0].message.content.strip()
            
            return {
                'original': text,
                'rewritten': rewritten_text,
                'mode': mode,
                'success': True,
                'original_length': len(text.split()),
                'rewritten_length': len(rewritten_text.split()),
                'method': 'azure_openai'
            }
        
        except Exception as e:
            logger.error(f"Azure OpenAI rewriting failed: {e}")
            return None

    @staticmethod
    def _rewrite_with_template(text: str, mode: str) -> Dict:
        """
        Fallback: Rewrite using template-based approach (no external APIs).
        
        Args:
            text: CV section text
            mode: Rewriting mode
        
        Returns:
            Dict with rewrite result
        """
        try:
            rewritten_text = text.strip()
            
            if mode == 'concise':
                rewritten_text = CVRewriter._rewrite_concise(rewritten_text)
            elif mode == 'ats':
                rewritten_text = CVRewriter._rewrite_ats(rewritten_text)
            elif mode == 'recruiter':
                rewritten_text = CVRewriter._rewrite_recruiter(rewritten_text)
            else:
                rewritten_text = CVRewriter._rewrite_concise(rewritten_text)
            
            return {
                'original': text,
                'rewritten': rewritten_text,
                'mode': mode,
                'success': True,
                'original_length': len(text.split()),
                'rewritten_length': len(rewritten_text.split()),
                'method': 'template_based'
            }
        
        except Exception as e:
            logger.error(f"Template-based rewriting failed: {e}")
            return {
                'original': text,
                'rewritten': text,
                'mode': mode,
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def _rewrite_concise(text: str) -> str:
        """
        Rewrite to be more concise.
        - Remove redundant words
        - Shorten sentences
        - Use bullet points effectively
        """
        # Remove articles
        text = re.sub(r'\b(a|an|the)\s+', '', text, flags=re.IGNORECASE)
        
        # Remove redundancies
        text = re.sub(r'very\s+(good|bad|important)', lambda m: m.group(1), text, flags=re.IGNORECASE)
        
        # Condense "responsibilities included" type phrases
        text = re.sub(r'(responsibilities included|included the following|such as):', '', text, flags=re.IGNORECASE)
        
        # Remove filler words
        fillers = ['basically', 'actually', 'just', 'really', 'quite', 'somewhat']
        for filler in fillers:
            text = re.sub(rf'\b{filler}\s+', '', text, flags=re.IGNORECASE)
        
        return text.strip()

    @staticmethod
    def _rewrite_ats(text: str) -> str:
        """
        Rewrite for ATS (Applicant Tracking System) compatibility.
        - Remove special characters
        - Standardize formatting
        - Use standard keywords
        - Avoid tables and columns
        """
        # Remove special characters and emojis
        text = re.sub(r'[•★☆→↑↓✓✗✔✘◆●■□○△▲▼]', '', text)
        text = re.sub(r'[^\w\s.,;\-\(\)#]', '', text)
        
        # Standardize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Replace common abbreviations with full forms
        text = expand_common_abbreviations(text)
        
        return text.strip()

    @staticmethod
    def _rewrite_recruiter(text: str) -> str:
        """
        Rewrite to appeal to recruiters.
        - Use strong action verbs
        - Highlight metrics and results
        - Emphasize impact and achievements
        """
        # Replace weak verbs with strong action verbs
        text = use_action_verbs(text)
        
        # Enhance numbers and metrics
        text = enhance_with_metrics(text)
        
        # Remove weak phrases
        weak_phrases = [
            'was responsible for',
            'helped to',
            'was involved in',
            'attempted to',
        ]
        
        for phrase in weak_phrases:
            text = re.sub(phrase, '', text, flags=re.IGNORECASE)
        
        return text.strip()

    @staticmethod
    def rewrite_multiple_sections(
        sections: Dict[str, str],
        mode: str = 'concise'
    ) -> Dict[str, Dict]:
        """
        Rewrite multiple CV sections.
        
        Args:
            sections: Dict of section_name -> section_text
            mode: Rewriting mode
        
        Returns:
            Dict of section_name -> rewrite result
        """
        results = {}
        for section_name, section_text in sections.items():
            results[section_name] = CVRewriter.rewrite_section(section_text, mode)
        
        return results

    @staticmethod
    def rewrite_variants(
        text: str,
        mode: str = 'recruiter',
        num_variants: int = 3,
        use_azure: bool = True
    ) -> Dict:
        """
        Generate multiple variants of a CV section rewrite.
        Phase 2 feature: Users can choose the best variant.
        
        Args:
            text: CV section text
            mode: Rewriting mode (concise, ats, recruiter)
            num_variants: Number of variants to generate (default 3)
            use_azure: Use Azure OpenAI for generation
        
        Returns:
            Dict with variants list and metadata
        """
        if not text or len(text.strip()) < 50:
            logger.warning("Input text too short for multi-variant rewriting")
            return {
                'original': text,
                'variants': [],
                'mode': mode,
                'success': False,
                'error': 'Text too short (minimum 50 characters)'
            }
        
        variants = []
        
        # Generate variants
        for i in range(num_variants):
            # Try Azure first if requested
            if use_azure:
                result = CVRewriter._rewrite_with_azure_variant(text, mode, variant_num=i)
                if result and result.get('success'):
                    variants.append(result)
                    continue
            
            # Fall back to template for this variant
            result = CVRewriter._rewrite_with_template(text, mode)
            result['variant_num'] = i + 1
            variants.append(result)
        
        return {
            'original': text,
            'variants': variants,
            'mode': mode,
            'num_variants': len(variants),
            'success': len(variants) > 0,
            'original_length': len(text.split())
        }
    
    @staticmethod
    def _rewrite_with_azure_variant(
        text: str,
        mode: str,
        variant_num: int = 0
    ) -> Optional[Dict]:
        """
        Generate a single Azure OpenAI variant with different temperature/style.
        
        Args:
            text: CV section text
            mode: Rewriting mode
            variant_num: Variant index (0, 1, 2...) for temperature variation
        
        Returns:
            Dict with rewrite result or None if failed
        """
        if not AZURE_AVAILABLE:
            return None
        
        try:
            # Initialize client if not already done
            if CVRewriter.AZURE_CLIENT is None:
                CVRewriter.AZURE_CLIENT = get_azure_client()
            
            if CVRewriter.AZURE_CLIENT is None:
                return None
            
            # Vary temperature and style per variant
            temperatures = [0.5, 0.7, 0.9]  # More deterministic to more creative
            temp = temperatures[min(variant_num, len(temperatures) - 1)]
            
            # Create variant-specific prompts
            base_prompts = {
                'concise': "Rewrite the following CV section to be more concise and impactful, removing unnecessary words while preserving key information. Return ONLY the rewritten text without any explanation.",
                'ats': "Rewrite the following CV section to be optimized for Applicant Tracking Systems (ATS). Use standard keywords, avoid special characters, and ensure clear formatting. Return ONLY the rewritten text without any explanation.",
                'recruiter': "Rewrite the following CV section to be more appealing to recruiters. Use strong action verbs, highlight metrics and achievements, and emphasize impact. Return ONLY the rewritten text without any explanation."
            }
            
            # Add variant-specific instructions
            variant_styles = [
                "",  # Variant 0: standard
                " Focus on quantifiable results and metrics.",  # Variant 1: metrics-focused
                " Emphasize leadership and strategic impact."   # Variant 2: leadership-focused
            ]
            
            prompt = base_prompts.get(mode, base_prompts['concise'])
            if variant_num < len(variant_styles):
                prompt += variant_styles[variant_num]
            
            # Call Azure OpenAI with temperature variation
            response = CVRewriter.AZURE_CLIENT.chat.completions.create(
                model=CVRewriter.AZURE_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional CV and resume writer. Generate high-quality, distinct rewrites."
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\n{text}"
                    }
                ],
                temperature=temp,
                max_tokens=500
            )
            
            rewritten_text = response.choices[0].message.content.strip()
            
            return {
                'original': text,
                'rewritten': rewritten_text,
                'variant_num': variant_num + 1,
                'mode': mode,
                'temperature': temp,
                'success': True,
                'original_length': len(text.split()),
                'rewritten_length': len(rewritten_text.split()),
                'method': 'azure_openai'
            }
        
        except Exception as e:
            logger.error(f"Azure OpenAI variant {variant_num} rewriting failed: {e}")
            return None

    @staticmethod
    def generate_summary(
        text: str,
        max_words: int = 100
    ) -> str:
        """
        Generate a summary of the input text (simple extractive approach).
        
        Args:
            text: Text to summarize
            max_words: Maximum summary length
        
        Returns:
            Summary text
        """
        try:
            # Simple extractive summarization: take first sentences
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            summary = []
            word_count = 0
            
            for sentence in sentences:
                words = len(sentence.split())
                if word_count + words <= max_words:
                    summary.append(sentence)
                    word_count += words
                else:
                    break
            
            return '. '.join(summary) + '.' if summary else text
        
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return text
