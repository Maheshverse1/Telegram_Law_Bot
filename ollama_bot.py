from langchain_ollama.llms import OllamaLLM
import re

# Load local phi3 model
llm = OllamaLLM(model="phi3:mini")

def cleanup_fake_sections(response: str) -> str:
    """
    Identifies suspicious legal section references and replaces them with a warning.
    Only keeps known valid Motor Vehicle Act sections like 129, 130, 185, 194.
    """
    allowed_sections = {"129", "130", "185", "194"}
    pattern = r"Section\s+([0-9A-Z]+(?:\([a-zA-Z0-9]+\))?)"

    def replace_if_fake(match):
        section = match.group(1)
        section_number = section.split("(")[0]  # Extract base number before any (x)
        if section_number not in allowed_sections:
            return "[invalid section]"
        return match.group(0)

    return re.sub(pattern, replace_if_fake, response)

def get_response(user_input: str, history: list) -> str:
    # Format history with clear turn separators
    formatted_history = ""
    for msg in history:
        role = msg['role'].capitalize()
        content = msg['content']
        formatted_history += f"{role}: {content}\n---\n"

    # Add system instruction for better legal, focused replies
    system_instruction = (
        "You are an Indian law assistant. Answer user queries factually. "
        "Refer to Indian laws like MV Act, RTI Act, IT Act, etc. "
        "Do not invent or refer to previous questions unless asked directly. "
        "Be concise and avoid generic inspirational or global content.\n\n"
    )

    # Final prompt
    prompt = f"{system_instruction}{formatted_history}User: {user_input}\nBot:"

    try:
        response = llm.invoke(prompt)
        cleaned = cleanup_fake_sections(response.strip())
        return cleaned
    except Exception as e:
        return f"⚠️ Ollama Error: {e}"
