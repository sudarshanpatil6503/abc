import json, os, re
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE = os.path.dirname(__file__)
DATA_CANDIDATES = [
    os.path.join(BASE, "data"),
    BASE,
]
DATA = next((path for path in DATA_CANDIDATES if os.path.isdir(path)), os.path.join(BASE, "data"))
MEMORY_FILE = os.path.join(BASE, "memory.json")

st.set_page_config(page_title="CampusMate AI", page_icon="🎓", layout="centered")


def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"student_name": "", "department": "", "year": "", "history": []}


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def load_documents():
    docs = []
    if not os.path.isdir(DATA):
        return docs

    for fn in sorted(os.listdir(DATA)):
        if fn.lower().endswith(".txt"):
            path = os.path.join(DATA, fn)
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    docs.append({"name": fn, "text": f.read()})
    return docs


DOCS = load_documents()
VECTORIZER = TfidfVectorizer(stop_words="english")
MATRIX = VECTORIZER.fit_transform([d["text"] for d in DOCS]) if DOCS else None


def retrieve(query, k=3):
    if MATRIX is None:
        return []
    q = VECTORIZER.transform([query])
    scores = cosine_similarity(q, MATRIX)[0]
    order = scores.argsort()[::-1][:k]
    return [(DOCS[i], float(scores[i])) for i in order if scores[i] > 0.05]


def find_notice(keyword):
    path = os.path.join(DATA, "notices.txt")
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lines = [x.strip() for x in text.splitlines() if keyword.lower() in x.lower()]
    return lines


def calculator(expression):
    if not re.fullmatch(r"[0-9+\-*/(). %]+", expression.strip()):
        return "For safety, only basic arithmetic is allowed."
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception:
        return "I could not calculate that expression."


def agent_answer(query, memory):
    q = query.lower().strip()

    # Tool routing
    if q.startswith("calculate ") or q.startswith("calc "):
        expr = re.sub(r"^(calculate|calc)\s+", "", query, flags=re.I)
        return f"🧮 **Calculator tool:** {calculator(expr)}", []

    if "notice" in q or "circular" in q:
        keyword = "exam" if "exam" in q else "holiday" if "holiday" in q else "placement" if "placement" in q else ""
        if keyword:
            hits = find_notice(keyword)
            if hits:
                return "📢 **Notice tool result:**\n\n" + "\n".join(f"- {h}" for h in hits), []
        # fall back to RAG

    results = retrieve(query)
    if not results:
        return ("I could not find reliable information in the campus knowledge base. "
                "Please contact the department office for official confirmation."), []

    context = "\n\n".join(
        f"[{doc['name']}]\n{doc['text']}" for doc, score in results
    )

    # Lightweight answer synthesis from retrieved content.
    sentences = re.split(r"(?<=[.!?])\s+|\n+", context)
    q_terms = set(re.findall(r"[a-zA-Z]{3,}", q))
    ranked = []
    for s in sentences:
        s_terms = set(re.findall(r"[a-zA-Z]{3,}", s.lower()))
        overlap = len(q_terms & s_terms)
        if overlap:
            ranked.append((overlap, s.strip()))
    ranked.sort(reverse=True)

    selected = []
    seen = set()
    for _, s in ranked:
        if s and s not in seen:
            selected.append(s)
            seen.add(s)
        if len(selected) >= 5:
            break

    if not selected:
        selected = [doc["text"].splitlines()[0] for doc, _ in results]

    answer = "🎓 **CampusMate AI**\n\n" + "\n\n".join(f"• {s}" for s in selected)
    answer += "\n\n_Answer generated from the campus knowledge base (RAG)._"
    return answer, [(doc["name"], round(score, 3)) for doc, score in results]


if "memory" not in st.session_state:
    st.session_state.memory = load_memory()
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🎓 CampusMate AI")
st.caption("Agentic AI Student Support Assistant • RAG + Tools + Memory")

with st.sidebar:
    st.header("Student Memory")
    name = st.text_input("Name", st.session_state.memory.get("student_name", ""))
    dept = st.text_input("Department", st.session_state.memory.get("department", ""))
    year = st.text_input("Year", st.session_state.memory.get("year", ""))
    if st.button("Save memory"):
        st.session_state.memory.update({"student_name": name, "department": dept, "year": year})
        save_memory(st.session_state.memory)
        st.success("Memory saved.")

    st.divider()
    st.subheader("Agent capabilities")
    st.write("• RAG over campus documents")
    st.write("• Notice search tool")
    st.write("• Calculator tool")
    st.write("• Student memory")
    st.write("• Safe fallback when data is missing")

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("sources"):
            st.caption("Sources: " + ", ".join(f"{n} ({s})" for n, s in m["sources"]))

prompt = st.chat_input("Ask about regulations, syllabus, notices, placements, etc.")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.memory["history"].append({"user": prompt})
    answer, sources = agent_answer(prompt, st.session_state.memory)
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
    st.session_state.memory["history"][-1]["assistant"] = answer
    save_memory(st.session_state.memory)

    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        st.markdown(answer)
        if sources:
            st.caption("Sources: " + ", ".join(f"{n} ({s})" for n, s in sources))
