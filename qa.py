"""
Q&A API Endpoint
Minimal, presentation-safe version
"""

from fastapi import APIRouter, HTTPException
from ..models.schemas import QARequest, QAResponse, AyahResponse
from ..core.embeddings import EmbeddingGenerator
from ..core.vector_store import VectorStore
from ..core.normalizer import QuranNormalizer
from ..core.llm import GenerativeQuranLLM
from ..core.prompt import build_qa_prompt

router = APIRouter(prefix="/qa", tags=["Q&A"])

# Injected from main.py
embedding_generator: EmbeddingGenerator = None
vector_store: VectorStore = None
normalizer: QuranNormalizer = None
llm: GenerativeQuranLLM = None

MAX_AYAHS = 5


def initialize_qa_module(
    emb_gen: EmbeddingGenerator,
    vec_store: VectorStore,
    norm: QuranNormalizer,
    llm_instance: GenerativeQuranLLM
):
    global embedding_generator, vector_store, normalizer, llm
    embedding_generator = emb_gen
    vector_store = vec_store
    normalizer = norm
    llm = llm_instance


@router.post("", response_model=QAResponse)
async def ask_question(request: QARequest):
    if not embedding_generator or not vector_store or not normalizer or not llm:
        raise HTTPException(status_code=500, detail="Q&A module not initialized")

    # 1. Embed question
    question_embedding = embedding_generator.generate_embedding(request.question)

    # 2. Search
    results = vector_store.search(question_embedding, k=20)
    if not results:
        return QAResponse(
            question=request.question,
            answer="Not describing about it.",
            relevant_ayahs=[]
        )

    # 3. Collect ayahs
    relevant_ayahs = []
    for ayah_id, _ in results[:MAX_AYAHS]:
        ayah = normalizer.get_ayah_by_id(ayah_id)
        if ayah:
            relevant_ayahs.append(ayah.to_dict())

    if not relevant_ayahs:
        return QAResponse(
            question=request.question,
            answer="Not describing about it.",
            relevant_ayahs=[]
        )

    # 4. Build prompt
    system_prompt, user_prompt = build_qa_prompt(
        request.question,
        relevant_ayahs
    )

    # 5. Generate explanation
    answer = llm.generate_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt
    )

    return QAResponse(
        question=request.question,
        answer=answer,
        relevant_ayahs=[AyahResponse(**a) for a in relevant_ayahs]
    )
