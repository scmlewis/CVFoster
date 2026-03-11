"""
Job matching and ranking module.
Implements weighted scoring combining semantic similarity, keyword overlap, and heuristics.
"""

import logging
import re
from typing import List, Dict, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

# Seniority levels for hierarchy matching
SENIORITY_LEVELS = {
    'entry': 0,
    'junior': 1,
    'mid': 2,
    'mid-level': 2,
    'senior': 3,
    'lead': 4,
    'principal': 5,
    'director': 6
}

class JobMatcher:
    """Handler for matching CVs against job postings with explainable scoring."""

    @staticmethod
    def extract_skills(text: str) -> set:
        """
        Extract skills from text using simple heuristics and keyword matching.
        
        Args:
            text: Text to extract skills from
        
        Returns:
            Set of lowercase skill tokens
        """
        # Split by common delimiters
        tokens = re.split(r'[,\s/\-+&|]+', text.lower())
        
        # Filter short tokens and common words
        common_words = {'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'with', 'for', 'of', 'to', 'by'}
        skills = {t.strip() for t in tokens if t.strip() and len(t) > 1 and t not in common_words}
        
        return skills

    @staticmethod
    def extract_seniority_level(text: str) -> Optional[str]:
        """
        Infer seniority level from text.
        
        Args:
            text: Text to analyze
        
        Returns:
            Seniority level or None
        """
        text_lower = text.lower()
        
        for level, _ in sorted(SENIORITY_LEVELS.items(), key=lambda x: x[1], reverse=True):
            if re.search(rf'\b{level}\b', text_lower):
                return level
        
        return None

    @staticmethod
    def calculate_semantic_score(retrieval_result: Dict, weight: float = 0.5) -> float:
        """
        Extract semantic similarity score from retrieval result.
        
        Args:
            retrieval_result: Result dict from embedding search
            weight: Weight for this component (0-1)
        
        Returns:
            Weighted score
        """
        semantic_score = retrieval_result.get('semantic_score', 0.0)
        return semantic_score * weight

    @staticmethod
    def calculate_keyword_score(
        cv_text: str,
        job_text: str,
        weight: float = 0.3
    ) -> float:
        """
        Calculate keyword overlap score between CV and job description.
        
        Args:
            cv_text: CV chunk text
            job_text: Job description text
            weight: Weight for this component (0-1)
        
        Returns:
            Weighted keyword overlap score (0-1)
        """
        cv_skills = JobMatcher.extract_skills(cv_text)
        job_skills = JobMatcher.extract_skills(job_text)
        
        if not job_skills:
            return 0.0
        
        overlap = len(cv_skills & job_skills)
        keyword_score = overlap / len(job_skills)
        
        return keyword_score * weight

    @staticmethod
    def calculate_seniority_score(
        cv_text: str,
        job_text: str,
        weight: float = 0.2
    ) -> float:
        """
        Calculate seniority level match score.
        
        Args:
            cv_text: CV chunk text
            job_text: Job description text
            weight: Weight for this component (0-1)
        
        Returns:
            Weighted seniority match score (0-1)
        """
        cv_level = JobMatcher.extract_seniority_level(cv_text)
        job_level = JobMatcher.extract_seniority_level(job_text)
        
        if not cv_level or not job_level:
            return 0.0  # Can't match if levels not detected
        
        cv_rank = SENIORITY_LEVELS.get(cv_level, 2)
        job_rank = SENIORITY_LEVELS.get(job_level, 2)
        
        # Score: 1.0 for exact match, 0.5 for adjacent level, 0.0 otherwise
        level_diff = abs(cv_rank - job_rank)
        if level_diff == 0:
            seniority_score = 1.0
        elif level_diff == 1:
            seniority_score = 0.5
        else:
            seniority_score = 0.0
        
        return seniority_score * weight

    @staticmethod
    def calculate_combined_score(
        retrieval_result: Dict,
        cv_text: str,
        job_data: Dict,
        weights: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate combined weighted score for a match.
        
        Args:
            retrieval_result: Result from embedding search
            cv_text: CV chunk text
            job_data: Job posting data
            weights: Custom weights (default: semantic=0.5, keyword=0.3, seniority=0.2)
        
        Returns:
            Dict with individual scores and total score
        """
        if weights is None:
            weights = {
                'semantic': 0.5,
                'keyword': 0.3,
                'seniority': 0.2
            }
        
        job_text = job_data.get('description', '') + ' ' + job_data.get('skills', '')
        
        semantic = JobMatcher.calculate_semantic_score(retrieval_result, weights['semantic'])
        keyword = JobMatcher.calculate_keyword_score(cv_text, job_text, weights['keyword'])
        seniority = JobMatcher.calculate_seniority_score(cv_text, job_text, weights['seniority'])
        
        total_score = semantic + keyword + seniority
        
        return {
            'semantic': round(semantic, 3),
            'keyword': round(keyword, 3),
            'seniority': round(seniority, 3),
            'total': round(total_score, 3),
            'breakdown': {
                'semantic_pct': f"{max(0, semantic / weights['semantic'] * 100):.1f}%",
                'keyword_pct': f"{max(0, keyword / weights['keyword'] * 100):.1f}%",
                'seniority_pct': f"{max(0, seniority / weights['seniority'] * 100):.1f}%"
            }
        }

    @staticmethod
    def match_cv_to_jobs(
        cv_text: str,
        retrieval_results: List[Dict],
        job_postings: Dict[str, Dict],
        top_k: int = 3,
        weights: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Match retrieved job chunks to full job postings and rerank.
        
        Args:
            cv_text: CV chunk text
            retrieval_results: Results from embedding search
            job_postings: Dict of job_id -> job data
            top_k: Number of top results to return
            weights: Custom weights for scoring
        
        Returns:
            List of top-k ranked job matches with scores
        """
        if not retrieval_results:
            return []
        
        # Group results by job
        job_matches = {}
        
        for result in retrieval_results:
            job_id = result.get('job_id')
            if not job_id or job_id not in job_postings:
                continue
            
            job_data = job_postings[job_id]
            
            scores = JobMatcher.calculate_combined_score(
                result,
                cv_text,
                job_data,
                weights
            )
            
            if job_id not in job_matches:
                job_matches[job_id] = {
                    'job_data': job_data,
                    'scores': scores,
                    'matched_chunks': []
                }
            
            job_matches[job_id]['matched_chunks'].append({
                'chunk_text': result['text'],
                'match_score': scores['total']
            })
        
        # Aggregate scores per job (average of all chunk matches)
        ranked_matches = []
        for job_id, match in job_matches.items():
            avg_score = sum(c['match_score'] for c in match['matched_chunks']) / len(match['matched_chunks'])
            ranked_matches.append({
                'job_id': job_id,
                'title': match['job_data'].get('title', 'Unknown'),
                'company': match['job_data'].get('company', 'Unknown'),
                'description': match['job_data'].get('description', '')[:200] + '...',
                'match_score': round(avg_score, 3),
                'score_breakdown': match['scores']['breakdown'],
                'matched_chunks': match['matched_chunks'][:1]  # Top chunk
            })
        
        # Sort by match score
        ranked_matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return ranked_matches[:top_k]
