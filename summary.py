"""
Summary API Endpoints
Handles surah and ayah summaries based on Quran text only.
"""

from fastapi import APIRouter, HTTPException
from ..models.schemas import SummaryResponse, AyahResponse
from ..core.normalizer import QuranNormalizer
from ..core.prompt import build_summary_prompt
from ..core.llm import GenerativeQuranLLM
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summary", tags=["Summary"])

# Global instances (will be initialized in main.py)
normalizer: QuranNormalizer = None
llm: GenerativeQuranLLM = None


def initialize_summary_module(norm: QuranNormalizer, llm_instance: GenerativeQuranLLM):
    """Initialize the summary module with required components."""
    global normalizer, llm
    normalizer = norm
    llm = llm_instance


@router.get("/surah/{surah_number}", response_model=SummaryResponse)
async def summarize_surah(surah_number: int):
    """
    Summarize a surah based on its text only.
    
    Args:
        surah_number: Surah number (1-114)
    """
    if not normalizer:
        raise HTTPException(status_code=500, detail="Summary module not initialized")
    
    if surah_number < 1 or surah_number > 114:
        raise HTTPException(status_code=400, detail="Surah number must be between 1 and 114")
    
    try:
        # Get all ayahs in the surah
        surah_ayahs = normalizer.get_surah(surah_number)
        
        if not surah_ayahs:
            raise HTTPException(status_code=404, detail=f"Surah {surah_number} not found")
        
        # Convert to dictionaries
        ayahs_dict = [ayah.to_dict() for ayah in surah_ayahs]
        
        # Build summary prompt
        system_prompt, user_prompt = build_summary_prompt("surah", ayahs_dict)
        
        # Generate summary
        summary = llm.generate_response(system_prompt, user_prompt, ayahs_dict)
        
        return SummaryResponse(
            summary=summary,
            ayahs=[AyahResponse(**ayah) for ayah in ayahs_dict]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error summarizing surah {surah_number}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error summarizing surah: {str(e)}")


@router.get("/ayah/{surah}/{ayah}", response_model=SummaryResponse)
async def summarize_ayah(surah: int, ayah: int):
    """
    Summarize a specific ayah based on its text only.
    
    Args:
        surah: Surah number (1-114)
        ayah: Ayah number
    """
    if not normalizer:
        raise HTTPException(status_code=500, detail="Summary module not initialized")
    
    if surah < 1 or surah > 114:
        raise HTTPException(status_code=400, detail="Surah number must be between 1 and 114")
    
    try:
        # Get the ayah
        ayah_model = normalizer.get_ayah(surah, ayah)
        
        if not ayah_model:
            raise HTTPException(status_code=404, detail=f"Ayah {surah}:{ayah} not found")
        
        # Convert to dictionary
        ayah_dict = [ayah_model.to_dict()]
        
        # Build summary prompt
        system_prompt, user_prompt = build_summary_prompt("ayah", ayah_dict)
        
        # Generate summary
        summary = llm.generate_response(system_prompt, user_prompt, ayah_dict)
        
        return SummaryResponse(
            summary=summary,
            ayahs=[AyahResponse(**ayah) for ayah in ayah_dict]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error summarizing ayah {surah}:{ayah}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error summarizing ayah: {str(e)}")

