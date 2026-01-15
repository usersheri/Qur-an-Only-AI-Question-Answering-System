"""
Quran Data Normalizer
Normalizes raw Quran data into internal Ayah model structure.
"""

from typing import List, Dict, Tuple
from .quran_loader import SURAH_NAMES
import logging

logger = logging.getLogger(__name__)


class AyahModel:
    """Internal Ayah model structure."""
    
    def __init__(self, surah: int, ayah: int, arabic: str, english: str):
        self.surah = surah
        self.ayah = ayah
        self.surah_name = SURAH_NAMES.get(surah, f"Surah {surah}")
        self.arabic = arabic
        self.english = english
        self.id = f"{surah}:{ayah}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "surah": self.surah,
            "surah_name": self.surah_name,
            "ayah": self.ayah,
            "arabic": self.arabic,
            "english": self.english
        }
    
    def to_text_for_embedding(self) -> str:
        """Get text representation for embedding (English only for semantic search)."""
        return self.english


class QuranNormalizer:
    """Normalizes raw Quran data into internal structure."""
    
    def __init__(self):
        self.ayahs: List[AyahModel] = []
        self.ayahs_by_id: Dict[str, AyahModel] = {}
        self.ayahs_by_surah: Dict[int, List[AyahModel]] = {}
    
    def normalize(self, arabic_data: Dict[Tuple[int, int], str], 
                  english_data: Dict[Tuple[int, int], str]) -> List[AyahModel]:
        """
        Normalize raw data into AyahModel list.
        
        Args:
            arabic_data: Dictionary mapping (surah, ayah) -> Arabic text
            english_data: Dictionary mapping (surah, ayah) -> English text
        
        Returns:
            List of normalized AyahModel objects
        """
        self.ayahs = []
        self.ayahs_by_id = {}
        self.ayahs_by_surah = {}
        
        # Get all keys and sort
        all_keys = set(arabic_data.keys()) | set(english_data.keys())
        sorted_keys = sorted(all_keys)
        
        missing_arabic = []
        missing_english = []
        
        for surah, ayah in sorted_keys:
            arabic_text = arabic_data.get((surah, ayah), "")
            english_text = english_data.get((surah, ayah), "")
            
            if not arabic_text:
                missing_arabic.append((surah, ayah))
            if not english_text:
                missing_english.append((surah, ayah))
            
            # Create AyahModel even if one translation is missing
            ayah_model = AyahModel(
                surah=surah,
                ayah=ayah,
                arabic=arabic_text,
                english=english_text
            )
            
            self.ayahs.append(ayah_model)
            self.ayahs_by_id[ayah_model.id] = ayah_model
            
            if surah not in self.ayahs_by_surah:
                self.ayahs_by_surah[surah] = []
            self.ayahs_by_surah[surah].append(ayah_model)
        
        if missing_arabic:
            logger.warning(f"Missing Arabic text for {len(missing_arabic)} ayahs")
        if missing_english:
            logger.warning(f"Missing English text for {len(missing_english)} ayahs")
        
        logger.info(f"Normalized {len(self.ayahs)} ayahs")
        logger.info(f"Covering {len(self.ayahs_by_surah)} surahs")
        
        return self.ayahs
    
    def get_ayah(self, surah: int, ayah: int) -> AyahModel:
        """Get a specific ayah by surah and ayah number."""
        ayah_id = f"{surah}:{ayah}"
        return self.ayahs_by_id.get(ayah_id)
    
    def get_ayah_by_id(self, ayah_id: str) -> AyahModel:
        """Get a specific ayah by ID (format: 'surah:ayah')."""
        return self.ayahs_by_id.get(ayah_id)
    
    def get_surah(self, surah: int) -> List[AyahModel]:
        """Get all ayahs in a surah."""
        return self.ayahs_by_surah.get(surah, [])
    
    def get_all_ayahs(self) -> List[AyahModel]:
        """Get all ayahs."""
        return self.ayahs

