import json
import os
import re

import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------------------------
# Paths and page configuration
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_CANDIDATES = [
    os.path.join(BASE, "data"),
    BASE,
]
DATA = next(
    (path for path in DATA_CANDIDATES if os.path.isdir(path)),
    os.path.join(BASE, "data"),
)
MEMORY_FILE = os.path.join(BASE, "memory.json")

st.set_page_config(
    page_title="CampusMate AI",
    page_icon="🎓",
    layout="centered",
)


# ---------------------------------------------------------------------------
# Student memory
# ---------------------------------------------------------------------------
def load_memory():
    default_memory = {
        "student_name": "",
        "department": "",
        "year": "",
        "history": [],
    }

    if os.path.isfile(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as file:
                loaded = json.load(file)

            if not isinstance(loaded, dict):
                return default_memory

            # Keep expected fields even if an older/incomplete JSON file exists.
            for key, default_value in default_memory.items():
                if key not in loaded or not isinstance(loaded[key], type(default_value)):
                    loaded[key] = default_value

            return loaded
        except (OSError, json.JSONDecodeError):
            pass

    return default_memory


def save_memory(memory):
    """Save memory where the app has write access."""
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(memory, file, indent=2, ensure_ascii=False)
        return True
    except OSError as error:
        st.warning(f"Memory could not be saved on this deployment: {error}")
        return False


# ---------------------------------------------------------------------------
# Campus document loading and retrieval (RAG)
# ---------------------------------------------------------------------------
def load_documents():
    """Load non-empty .txt files from the data folder or project root."""
    docs = []

    if not os.path.isdir(DATA):
        return docs

    try:
        filenames = sorted(os.listdir(DATA))
    except OSError:
        return docs

    for filename in filenames:
        if not filename.lower().endswith(".txt"):
            continue

        path = os.path.join(DATA, filename)
        if not os.path.isfile(path):
            continue

        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read().strip()

            if content:
                docs.append({"name": filename, "text": content})
        except (OSError, UnicodeDecodeError):
            # Skip unreadable files rather than crashing the whole app.
            continue

    return docs


DOCS = load_documents()
VECTORIZER = None
MATRIX = None

if DOCS:
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform([doc["text"] for doc in DOCS])
        VECTORIZER = vectorizer
        MATRIX = matrix
    except ValueError:
        # For example, documents may contain no usable words.
        VECTORIZER = None
        MATRIX = None


def retrieve(query, k=3):
    if MATRIX is None or VECTORIZER is None or not query.strip():
        return []
