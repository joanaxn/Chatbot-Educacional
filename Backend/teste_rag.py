from query_data import query_rag
from langchain_ollama import OllamaLLM
from difflib import SequenceMatcher

EVAL_PROMPT = """
Expected Response: {expected_response}
Actual Response: {actual_response}
---
(Answer with 'true' or 'false') Does the actual response match the expected response? 
"""


def test_dados():
    assert query_and_validate(
        question="What is data?",
        expected_response="Data are a large set of bits encoded to represent numbers, texts, images,sounds, videos, etc.",
    )


def test_padronizacao_normalizacao():
    assert query_and_validate(
        question="What is normalization?",
        expected_response="Standardization scales features to have a mean (u) of 0 and standard deviation (a) of 1.",
    )


def similar_enough(a: str, b: str, threshold: float = 0.75) -> bool:
    """
    Compara duas strings com fuzzy matching e retorna True se forem suficientemente semelhantes.
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold


def query_and_validate(question: str, expected_response: str) -> bool:
    response_text = query_rag(question)
    print("\n🧪 Avaliação da Resposta:")
    print(f"Expected: {expected_response}\nActual: {response_text}\n")

    if similar_enough(response_text, expected_response):
        print("\033[92m" + "Resultado: true (semelhança suficiente)" + "\033[0m")
        return True
    else:
        print("\033[91m" + "Resultado: false (resposta diferente demais)" + "\033[0m")
        return False


if __name__ == "__main__":
    test_dados()
    test_padronizacao_normalizacao()
