import ast
import json
import operator
import os
import re
from pathlib import Path

import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ----------------------------- Configuration -----------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MEMORY_FILE = BASE_DIR / "memory.json"

st.set_page_config(
    page_title="CampusMate AI",
    page_icon="🎓",
    layout="centered",
)


# ----------------------------- Student memory ----------------------------
def load_memory():
    defaults = {
        "student_name": "",
        "department": "",
        "year": "",
        "history": [],
    }

    if not MEMORY_FILE.is_file():
        return defaults

    try:
        with MEMORY_FILE.open("r", encoding="utf-8") as file:
            stored = json.load(file)

        if not isinstance(stored, dict):
            return defaults

        for key, default_value in defaults.items():
            if key not in stored or not isinstance(stored[key], type(default_value)):
                stored[key] = default_value
        return stored
    except (OSError, json.JSONDecodeError):
        return defaults


def save_memory(memory):
    """Best-effort local JSON persistence; hosted filesystems may be ephemeral."""
    try:
        with MEMORY_FILE.open("w", encoding="utf-8") as file:
            json.dump(memory, file, indent=2, ensure_ascii=False)
        return True
    except OSError:
        return False


# ----------------------------- Campus documents --------------------------
def load_documents():
    """Read non-empty .txt files from data/. Missing data is not fatal."""
    documents = []

    if not DATA_DIR.is_dir():
        return documents

    try:
        paths = sorted(DATA_DIR.glob("*.txt"))
    except OSError:
        return documents

    for path in paths:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeDecodeError):
            continue

        if text:
            documents.append({"name": path.name, "text": text})

    return documents


DOCS = load_documents()
VECTORIZER = None
MATRIX = None

if DOCS:
    try:
        candidate_vectorizer = TfidfVectorizer(stop_words="english")
        candidate_matrix = candidate_vectorizer.fit_transform(
