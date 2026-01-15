from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import logging

logger = logging.getLogger(__name__)

class GenerativeQuranLLM:
    def __init__(self, model_name: str = "google/flan-t5-base"):
        logger.info(f"Loading LLM: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        self.generator = pipeline(
            "text2text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=200,
            temperature=0.4
        )

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        prompt = system_prompt + "\n\n" + user_prompt
        result = self.generator(prompt)[0]["generated_text"]
        return result.strip()
