"""
Quran Data Loader
Loads and inspects existing Quran data files from /data directory.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

# Standard Quran surah names (114 surahs)
SURAH_NAMES = {
    1: "Al-Fatihah",
    2: "Al-Baqarah",
    3: "Ali 'Imran",
    4: "An-Nisa",
    5: "Al-Ma'idah",
    6: "Al-An'am",
    7: "Al-A'raf",
    8: "Al-Anfal",
    9: "At-Tawbah",
    10: "Yunus",
    11: "Hud",
    12: "Yusuf",
    13: "Ar-Ra'd",
    14: "Ibrahim",
    15: "Al-Hijr",
    16: "An-Nahl",
    17: "Al-Isra",
    18: "Al-Kahf",
    19: "Maryam",
    20: "Ta-Ha",
    21: "Al-Anbiya",
    22: "Al-Hajj",
    23: "Al-Mu'minun",
    24: "An-Nur",
    25: "Al-Furqan",
    26: "Ash-Shu'ara",
    27: "An-Naml",
    28: "Al-Qasas",
    29: "Al-Ankabut",
    30: "Ar-Rum",
    31: "Luqman",
    32: "As-Sajdah",
    33: "Al-Ahzab",
    34: "Saba",
    35: "Fatir",
    36: "Ya-Sin",
    37: "As-Saffat",
    38: "Sad",
    39: "Az-Zumar",
    40: "Ghafir",
    41: "Fussilat",
    42: "Ash-Shura",
    43: "Az-Zukhruf",
    44: "Ad-Dukhan",
    45: "Al-Jathiyah",
    46: "Al-Ahqaf",
    47: "Muhammad",
    48: "Al-Fath",
    49: "Al-Hujurat",
    50: "Qaf",
    51: "Adh-Dhariyat",
    52: "At-Tur",
    53: "An-Najm",
    54: "Al-Qamar",
    55: "Ar-Rahman",
    56: "Al-Waqi'ah",
    57: "Al-Hadid",
    58: "Al-Mujadila",
    59: "Al-Hashr",
    60: "Al-Mumtahanah",
    61: "As-Saff",
    62: "Al-Jumu'ah",
    63: "Al-Munafiqun",
    64: "At-Taghabun",
    65: "At-Talaq",
    66: "At-Tahrim",
    67: "Al-Mulk",
    68: "Al-Qalam",
    69: "Al-Haqqah",
    70: "Al-Ma'arij",
    71: "Nuh",
    72: "Al-Jinn",
    73: "Al-Muzzammil",
    74: "Al-Muddaththir",
    75: "Al-Qiyamah",
    76: "Al-Insan",
    77: "Al-Mursalat",
    78: "An-Naba",
    79: "An-Nazi'at",
    80: "Abasa",
    81: "At-Takwir",
    82: "Al-Infitar",
    83: "Al-Mutaffifin",
    84: "Al-Inshiqaq",
    85: "Al-Buruj",
    86: "At-Tariq",
    87: "Al-A'la",
    88: "Al-Ghashiyah",
    89: "Al-Fajr",
    90: "Al-Balad",
    91: "Ash-Shams",
    92: "Al-Layl",
    93: "Ad-Duha",
    94: "Ash-Sharh",
    95: "At-Tin",
    96: "Al-Alaq",
    97: "Al-Qadr",
    98: "Al-Bayyinah",
    99: "Az-Zalzalah",
    100: "Al-Adiyat",
    101: "Al-Qari'ah",
    102: "At-Takathur",
    103: "Al-Asr",
    104: "Al-Humazah",
    105: "Al-Fil",
    106: "Quraysh",
    107: "Al-Ma'un",
    108: "Al-Kawthar",
    109: "Al-Kafirun",
    110: "An-Nasr",
    111: "Al-Masad",
    112: "Al-Ikhlas",
    113: "Al-Falaq",
    114: "An-Nas"
}


class QuranLoader:
    """Loads Quran data from existing text files."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the loader.
        
        Args:
            data_dir: Directory containing Quran data files
        """
        self.data_dir = Path(data_dir)
        self.arabic_file = self.data_dir / "quran-uthmani.txt"
        self.english_file = self.data_dir / "en.sahih.txt"
        
    def inspect_files(self) -> Dict:
        """
        Inspect existing Quran data files.
        
        Returns:
            Dictionary with file inspection results
        """
        inspection = {
            "arabic_file": {
                "path": str(self.arabic_file),
                "exists": self.arabic_file.exists(),
                "format": "pipe-separated: surah|ayah|arabic_text",
                "encoding": "utf-8"
            },
            "english_file": {
                "path": str(self.english_file),
                "exists": self.english_file.exists(),
                "format": "pipe-separated: surah|ayah|english_text",
                "encoding": "utf-8"
            }
        }
        
        if self.arabic_file.exists():
            with open(self.arabic_file, encoding="utf-8") as f:
                lines = f.readlines()
                inspection["arabic_file"]["line_count"] = len(lines)
                if lines:
                    sample = lines[0].strip().split("|")
                    inspection["arabic_file"]["sample"] = {
                        "surah": sample[0],
                        "ayah": sample[1],
                        "text_preview": sample[2][:50] + "..." if len(sample[2]) > 50 else sample[2]
                    }
        
        if self.english_file.exists():
            with open(self.english_file, encoding="utf-8") as f:
                lines = f.readlines()
                inspection["english_file"]["line_count"] = len(lines)
                if lines:
                    sample = lines[0].strip().split("|")
                    inspection["english_file"]["sample"] = {
                        "surah": sample[0],
                        "ayah": sample[1],
                        "text_preview": sample[2][:50] + "..." if len(sample[2]) > 50 else sample[2]
                    }
        
        return inspection
    
    def load_raw_data(self) -> Tuple[Dict[Tuple[int, int], str], Dict[Tuple[int, int], str]]:
        """
        Load raw Arabic and English data from files.
        
        Returns:
            Tuple of (arabic_dict, english_dict) where keys are (surah, ayah) tuples
        """
        arabic_data = {}
        english_data = {}
        
        # Load Arabic text
        if not self.arabic_file.exists():
            raise FileNotFoundError(f"Arabic file not found: {self.arabic_file}")
        
        logger.info(f"Loading Arabic text from {self.arabic_file}")
        with open(self.arabic_file, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    parts = line.split("|", 2)
                    if len(parts) != 3:
                        logger.warning(f"Skipping malformed line {line_num}: {line[:50]}")
                        continue
                    surah, ayah, text = parts
                    key = (int(surah), int(ayah))
                    arabic_data[key] = text
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error parsing line {line_num}: {e}")
                    continue
        
        # Load English text
        if not self.english_file.exists():
            raise FileNotFoundError(f"English file not found: {self.english_file}")
        
        logger.info(f"Loading English text from {self.english_file}")
        with open(self.english_file, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    parts = line.split("|", 2)
                    if len(parts) != 3:
                        logger.warning(f"Skipping malformed line {line_num}: {line[:50]}")
                        continue
                    surah, ayah, text = parts
                    key = (int(surah), int(ayah))
                    english_data[key] = text
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error parsing line {line_num}: {e}")
                    continue
        
        logger.info(f"Loaded {len(arabic_data)} Arabic ayahs and {len(english_data)} English ayahs")
        
        return arabic_data, english_data

