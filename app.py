            break

    if not selected:
        selected = [
            doc["text"].splitlines()[0]
            for doc, _score in results
            if doc["text"].splitlines()
        ]

    answer = "🎓 **CampusMate AI**\n\n" + "\n\n".join(
        f"• {sentence}" for sentence in selected
    )
    answer += "\n\n_Answer generated from the campus knowledge base (RAG)._"

    sources = [
        (doc["name"], round(score, 3))
        for doc, score in results
    ]
    return answer, sources


# ---------------------------------------------------------------------------
# Streamlit session state and interface
# ---------------------------------------------------------------------------
if "memory" not in st.session_state:
    st.session_state.memory = load_memory()

if "messages" not in st.session_state:
    st.session_state.messages = []


st.title("🎓 CampusMate AI")
st.caption("Agentic AI Student Support Assistant • RAG + Tools + Memory")

with st.sidebar:
    st.header("Student Memory")

    name = st.text_input(
        "Name", st.session_state.memory.get("student_name", "")
    )
    department = st.text_input(
        "Department", st.session_state.memory.get("department", "")
    )
    year = st.text_input(
        "Year", st.session_state.memory.get("year", "")
    )

    if st.button("Save memory"):
        st.session_state.memory.update(
            {
                "student_name": name,
                "department": department,
                "year": year,
            }
        )
        if save_memory(st.session_state.memory):
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

if not os.path.isdir(DATA):
    st.warning(
        "The campus data folder is missing. Create a `data` folder in your "
        "GitHub repository and add `.txt` campus documents."
    )
elif not DOCS:
    st.info(
        "No non-empty `.txt` documents were found. Add campus documents to "
        "the `data` folder to enable knowledge-base search."
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            source_labels = []
            for filename, score in message["sources"]:
                label = filename if score is None else f"{filename} ({score})"
                source_labels.append(label)
            st.caption("Sources: " + ", ".join(source_labels))

prompt = st.chat_input(
    "Ask about regulations, syllabus, notices, placements, etc."
)

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    st.session_state.memory.setdefault("history", []).append(
        {"user": prompt}
    )

    answer, sources = agent_answer(prompt, st.session_state.memory)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
        }
    )

    st.session_state.memory["history"][-1]["assistant"] = answer
    save_memory(st.session_state.memory)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        st.markdown(answer)
        if sources:
            source_labels = []
            for filename, score in sources:
                label = filename if score is None else f"{filename} ({score})"
                source_labels.append(label)
            st.caption("Sources: " + ", ".join(source_labels))
