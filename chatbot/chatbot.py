import os
import re
from difflib import get_close_matches

def load_custom_data():
    """Loads and structures the custom_data.txt file"""
    file_path = os.path.join("chatbot", "custom_data.txt")

    if not os.path.exists(file_path):
        return {"default": "Sorry, I don’t have information about that right now."}

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    qa_pairs = {}
    current_q = None
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect questions
        if line.lower().startswith(("q:", "what", "who", "where", "when", "how", "why", "can", "do", "is", "are", "hi", "hello")):
            current_q = line.replace("Q:", "").strip().lower()
        elif current_q:
            qa_pairs[current_q] = line.replace("A:", "").strip()

    return qa_pairs


def find_best_match(question, qa_pairs):
    """Find closest matching question"""
    keys = list(qa_pairs.keys())
    matches = get_close_matches(question.lower(), keys, n=1, cutoff=0.5)
    return matches[0] if matches else None


def ask_general_chatbot(query: str) -> str:
    """Return best possible answer from local data"""
    qa_pairs = load_custom_data()
    match = find_best_match(query, qa_pairs)

    if match:
        return qa_pairs[match]
    else:
        # Handle greetings or unknown input
        if re.search(r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b', query.lower()):
            return "Hello! 👋 Welcome to Smart Cake Shop. How can I help you today?"
        return "Sorry, I couldn't find that information in my knowledge base."
