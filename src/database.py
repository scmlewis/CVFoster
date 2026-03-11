"""
SQLite persistence layer for CVFoster.
Phase 2 feature: Store CV parsing history, matching results, and rewrites.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import os

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

logger = logging.getLogger(__name__)

# Determine database path - use writable location
def _get_db_path() -> Path:
    """Get database path, prioritizing writable locations for Streamlit Cloud."""
    # Try project data directory first (local development)
    project_db = Path(__file__).parent.parent / "data" / "cvfoster.db"
    if project_db.parent.exists() and os.access(project_db.parent, os.W_OK):
        logger.info(f"Using project data directory: {project_db.parent}")
        return project_db
    
    # Fall back to home directory for Streamlit Cloud
    home_db = Path.home() / ".cvfoster" / "cvfoster.db"
    logger.info(f"Using home directory for database: {home_db.parent}")
    return home_db

DB_PATH = _get_db_path()

class DatabaseManager:
    """Manage SQLite database for CVFoster."""
    
    def __init__(self, db_path: Path = DB_PATH):
        """Initialize database manager."""
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.init_db()
    
    def _connect(self):
        """Get database connection."""
        if self.conn is None:
            # check_same_thread=False allows SQLite to be used across threads
            # SQLite handles locking internally, which is safe for our use case
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False, timeout=10)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def init_db(self):
        """Initialize database schema."""
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            # CVs table - stores uploaded CV metadata and content
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cvs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    original_text TEXT NOT NULL,
                    sections JSON,
                    num_words INTEGER,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    parsed_date TIMESTAMP
                )
            ''')
            
            # Matches table - stores job matching results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cv_id INTEGER NOT NULL,
                    job_id TEXT NOT NULL,
                    job_title TEXT,
                    company TEXT,
                    match_score REAL,
                    semantic_score REAL,
                    keyword_score REAL,
                    seniority_score REAL,
                    match_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cv_id) REFERENCES cvs(id) ON DELETE CASCADE
                )
            ''')
            
            # Rewrites table - stores CV section rewrites
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rewrites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cv_id INTEGER NOT NULL,
                    section_name TEXT NOT NULL,
                    original_text TEXT NOT NULL,
                    rewritten_text TEXT NOT NULL,
                    mode TEXT,
                    method TEXT,
                    num_words_original INTEGER,
                    num_words_rewritten INTEGER,
                    rewrite_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cv_id) REFERENCES cvs(id) ON DELETE CASCADE
                )
            ''')
            
            # Variants table - stores multi-variant rewrite results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS variants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cv_id INTEGER NOT NULL,
                    section_name TEXT NOT NULL,
                    original_text TEXT NOT NULL,
                    variant_num INTEGER,
                    rewritten_text TEXT NOT NULL,
                    mode TEXT,
                    method TEXT,
                    temperature REAL,
                    num_words_original INTEGER,
                    num_words_rewritten INTEGER,
                    variant_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cv_id) REFERENCES cvs(id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
        
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def save_cv(self, filename: str, text: str, sections: Dict[str, str]) -> int:
        """
        Save uploaded CV to database.
        
        Args:
            filename: Original filename
            text: Full CV text
            sections: Parsed sections dict
        
        Returns:
            CV ID
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO cvs (filename, original_text, sections, num_words, parsed_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                filename,
                text,
                json.dumps(sections),
                len(text.split()),
                datetime.now()
            ))
            
            conn.commit()
            cv_id = cursor.lastrowid
            logger.info(f"Saved CV: {filename} (ID: {cv_id}) to {self.db_path}")
            return cv_id
        
        except sqlite3.OperationalError as e:
            logger.error(f"Database operational error (readonly or locked): {e}")
            logger.error(f"Database path: {self.db_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to save CV: {e}")
            raise
    
    def get_cv(self, cv_id: int) -> Optional[Dict]:
        """
        Retrieve CV by ID.
        
        Args:
            cv_id: CV database ID
        
        Returns:
            CV data dict or None
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM cvs WHERE id = ?', (cv_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'filename': row['filename'],
                    'text': row['original_text'],
                    'sections': json.loads(row['sections']),
                    'num_words': row['num_words'],
                    'upload_date': row['upload_date'],
                    'parsed_date': row['parsed_date']
                }
        
        except Exception as e:
            logger.error(f"Failed to retrieve CV: {e}")
        
        return None
    
    def list_cvs(self, limit: int = 20) -> List[Dict]:
        """
        List all uploaded CVs.
        
        Args:
            limit: Max number of CVs to return
        
        Returns:
            List of CV metadata dicts
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, filename, num_words, upload_date, parsed_date
                FROM cvs
                ORDER BY upload_date DESC
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
        
        except Exception as e:
            logger.error(f"Failed to list CVs: {e}")
        
        return []
    
    def save_match(self, cv_id: int, match_data: Dict) -> int:
        """
        Save job matching result.
        
        Args:
            cv_id: CV database ID
            match_data: Match result dict
        
        Returns:
            Match ID
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO matches 
                (cv_id, job_id, job_title, company, match_score, 
                 semantic_score, keyword_score, seniority_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cv_id,
                match_data.get('job_id', ''),
                match_data.get('job_title', ''),
                match_data.get('company', ''),
                match_data.get('score', 0.0),
                match_data.get('semantic_score', 0.0),
                match_data.get('keyword_score', 0.0),
                match_data.get('seniority_score', 0.0)
            ))
            
            conn.commit()
            match_id = cursor.lastrowid
            logger.info(f"Saved match: {match_data.get('job_title')} (ID: {match_id})")
            return match_id
        
        except Exception as e:
            logger.error(f"Failed to save match: {e}")
            raise
    
    def save_rewrite(self, cv_id: int, rewrite_data: Dict) -> int:
        """
        Save single CV rewrite result.
        
        Args:
            cv_id: CV database ID
            rewrite_data: Rewrite result dict
        
        Returns:
            Rewrite ID
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO rewrites
                (cv_id, section_name, original_text, rewritten_text, mode, method,
                 num_words_original, num_words_rewritten)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cv_id,
                rewrite_data.get('section_name', 'unknown'),
                rewrite_data.get('original', ''),
                rewrite_data.get('rewritten', ''),
                rewrite_data.get('mode', ''),
                rewrite_data.get('method', ''),
                rewrite_data.get('original_length', 0),
                rewrite_data.get('rewritten_length', 0)
            ))
            
            conn.commit()
            rewrite_id = cursor.lastrowid
            logger.info(f"Saved rewrite (ID: {rewrite_id})")
            return rewrite_id
        
        except Exception as e:
            logger.error(f"Failed to save rewrite: {e}")
            raise
    
    def save_variants(self, cv_id: int, section_name: str, variants: List[Dict]) -> List[int]:
        """
        Save multi-variant rewrite results.
        
        Args:
            cv_id: CV database ID
            section_name: Section name
            variants: List of variant dicts
        
        Returns:
            List of variant IDs
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            variant_ids = []
            for variant in variants:
                cursor.execute('''
                    INSERT INTO variants
                    (cv_id, section_name, original_text, variant_num, rewritten_text,
                     mode, method, temperature, num_words_original, num_words_rewritten)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cv_id,
                    section_name,
                    variant.get('original', ''),
                    variant.get('variant_num', 0),
                    variant.get('rewritten', ''),
                    variant.get('mode', ''),
                    variant.get('method', ''),
                    variant.get('temperature', None),
                    variant.get('original_length', 0),
                    variant.get('rewritten_length', 0)
                ))
                variant_ids.append(cursor.lastrowid)
            
            conn.commit()
            logger.info(f"Saved {len(variants)} variants (IDs: {variant_ids})")
            return variant_ids
        
        except Exception as e:
            logger.error(f"Failed to save variants: {e}")
            raise
    
    def get_cv_history(self, cv_id: int) -> Dict:
        """
        Get complete history for a CV (matches, rewrites, variants).
        
        Args:
            cv_id: CV database ID
        
        Returns:
            History dict with all related data
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            # Get CV info
            cursor.execute('SELECT * FROM cvs WHERE id = ?', (cv_id,))
            cv_row = cursor.fetchone()
            if not cv_row:
                return {}
            
            # Get matches
            cursor.execute(
                'SELECT * FROM matches WHERE cv_id = ? ORDER BY match_date DESC',
                (cv_id,)
            )
            matches = [dict(row) for row in cursor.fetchall()]
            
            # Get rewrites
            cursor.execute(
                'SELECT * FROM rewrites WHERE cv_id = ? ORDER BY rewrite_date DESC',
                (cv_id,)
            )
            rewrites = [dict(row) for row in cursor.fetchall()]
            
            # Get variants
            cursor.execute(
                'SELECT * FROM variants WHERE cv_id = ? ORDER BY variant_date DESC',
                (cv_id,)
            )
            variants = [dict(row) for row in cursor.fetchall()]
            
            return {
                'cv': dict(cv_row),
                'matches': matches,
                'rewrites': rewrites,
                'variants': variants
            }
        
        except Exception as e:
            logger.error(f"Failed to get CV history: {e}")
        
        return {}
    
    def delete_cv(self, cv_id: int) -> bool:
        """
        Delete a CV and all related data (matches, rewrites, variants).
        Foreign key constraints with ON DELETE CASCADE handle related records.
        
        Args:
            cv_id: CV database ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            # Delete CV - cascade will remove all related records
            cursor.execute('DELETE FROM cvs WHERE id = ?', (cv_id,))
            conn.commit()
            
            logger.info(f"Deleted CV (ID: {cv_id}) and all related records")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete CV: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

# Global instance
_db_instance = None

def get_db() -> DatabaseManager:
    """
    Get or create database instance.
    Uses @st.cache_resource if Streamlit is available for proper session management.
    Falls back to global singleton otherwise.
    Cache version: 2 (includes delete_cv method)
    """
    global _db_instance
    
    if STREAMLIT_AVAILABLE:
        @st.cache_resource(show_spinner=False)
        def _init_db():
            return DatabaseManager()
        return _init_db()
    else:
        if _db_instance is None:
            _db_instance = DatabaseManager()
        return _db_instance
