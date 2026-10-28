# CampusMate AI – Agentic AI Student Support Assistant

## Use Case
**AI Student Support Assistant** from the TNSDC–IBM Agentic AI internship/project list.

The application answers college-related questions using:
- **RAG (Retrieval-Augmented Generation):** searches the local campus knowledge base.
- **Tools:** notice search and calculator.
- **Memory:** stores a student's name, department, year and chat history.
- **Agentic routing:** decides whether to use a tool or the knowledge base.
- **Safe fallback:** refuses to invent official information when no useful source is found.

## Project Structure

```text
CampusMate_AI_Student_Support/
│
├── app.py
├── requirements.txt
├── README.md
├── memory.json
└── data/
    ├── regulations.txt
    ├── syllabus.txt
    ├── faqs.txt
    └── notices.txt
```

## How to Run

### 1. Install Python
Python 3.10+ is recommended.

### 2. Open terminal in this folder

```bash
pip install -r requirements.txt
```

### 3. Start the application

```bash
streamlit run app.py
```

The browser will open the CampusMate AI interface.

## Demo Questions

Try:
1. `What are the attendance requirements?`
2. `What is the examination procedure?`
3. `Show exam notices`
4. `What documents are needed for a bonafide certificate?`
5. `Calculate 75 * 8 / 100`
6. `What subjects are covered in the AI course?`

## Important
The included data is **demo campus data**. Replace the files in `data/` with your actual college regulations, syllabus, FAQs and notices before presenting it as an official assistant.

## 5-Day Development Plan

### Day 1 – Foundation
- Select use case
- Create UI
- Add sample knowledge documents

### Day 2 – RAG
- Build document retrieval
- Rank relevant campus information
- Display sources

### Day 3 – Agent + Tools
- Add notice-search tool
- Add calculator tool
- Add simple intent routing

### Day 4 – Memory + Testing
- Store student profile
- Store conversation history
- Test normal, unknown and tool-based questions

### Day 5 – Final Demo
- Replace demo documents with real college data
- Improve UI
- Prepare architecture diagram
- Demonstrate RAG, tool calling and memory

## Architecture

```text
Student
   ↓
CampusMate AI UI
   ↓
Agent Router
 ┌─┴──────────────┐
 ↓                ↓
RAG Retriever    Tools
 ↓              ┌─┴─────────────┐
Campus Docs     Notice Search   Calculator
 └───────┬──────────────┘
         ↓
    Answer + Sources
         ↓
       Student

Memory Store ↔ Agent
```

## Future Enhancements
- Connect an LLM such as IBM watsonx or another approved model.
- Add PDF ingestion.
- Add semantic embeddings/vector database.
- Add college timetable and event tools.
- Add multilingual Tamil + English support.
- Add authentication for students and staff.
