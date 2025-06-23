# Ghostwriter – How It Works (Quick Overview)

This doc gives a **concise, plain-English tour** of the project so you can understand _what is used for what_ and how everything fits together.

---

## 1. Big Picture

```
                 ┌─────────────┐        API (FastAPI, LangChain, Ollama)
Frontend (React) │  /project    │  ⇆   ────────────────────────────────────
                 └─────────────┘        │
                                         │
                 ┌─────────────┐         │
 AI + Learning   │ feedback_*.py│  ⇆  Feedback (FAISS + JSON)
                 └─────────────┘         │
                                         │
                 ┌─────────────┐         │
  Voice Samples  │ /profiles    │  ←─────┘
                 └─────────────┘
```

* **Frontend**: React + TypeScript (in `project/`). Handles UI for generating posts and giving feedback.
* **Backend**: FastAPI (`api.py`) exposes REST endpoints. Uses LangChain + local Llama3 via Ollama to write posts.
* **Feedback System**: `feedback_system.py` stores feedback in a vector DB (FAISS) so the AI can learn over time.
* **Profiles**: Each `.txt` file in `profiles/` contains writing samples (e.g., `storytelling.txt`). Feedback vectors live in `profiles/feedback/`.

---

## 2. Key Files / Folders

| Path | Purpose |
|------|---------|
| `api.py` | FastAPI server, routing, generation & feedback endpoints |
| `feedback_system.py` | Logic for storing feedback & generating feedback-aware prompts |
| `profiles/storytelling.txt` | Example voice profile with numbered samples |
| `project/` | React frontend source (hooks, pages, components) |
| `start_app.py` | Convenience script: checks deps & launches backend |
| `requirements.txt` | Python dependencies |
| `tests/*.py` | Simple test suites for feedback & regeneration |
| `.gitignore` | Keeps builds, envs, and logs out of git |

---

## 3. Typical Workflow

1. **Run** `python start_app.py` – starts FastAPI on `localhost:8000`.
2. **Start Frontend**:
   ```bash
   cd project
   npm install   # first time only
   npm run dev   # opens http://localhost:5173
   ```
3. **Generate a Post**
   * Choose a voice profile (samples provide style)
   * Enter context → Backend selects similar samples & creates prompt → Llama3 generates post.
4. **Give Feedback**
   * Mark post 👍/👎/🔄 and add comments.
   * Feedback is embedded, saved in FAISS, and linked to the profile.
5. **Regenerate** (optional)
   * The AI re-prompts using recent feedback, producing an improved post.

---

## 4. How Learning Works (Under the Hood)

* Each feedback entry is embedded → stored in a **FAISS** vector store per profile.
* When generating a post, we query the vector store for similar contexts and inject **positive patterns, negative patterns & refinements** into the prompt.
* Over time the model nudges toward what you like and away from what you don't.

---

## 5. Quick Commands

```bash
# Run tests
pytest -q

# Lint (example)
ruff check .

# Rebuild frontend for production
cd project && npm run build
```

---

## 6. LangChain + Ollama in 60 Seconds

| Piece | Where | What It Does |
|-------|-------|--------------|
| `OllamaLLM` | `feedback_system.py` & `api.py` | Talks to your local Llama 3 model via the **Ollama** runtime to actually generate text. |
| `OllamaEmbeddings` | `feedback_system.py` | Converts feedback text to vectors so FAISS can search by semantic similarity. |
| `PromptTemplate` | `feedback_system.py` & `api.py` | Builds structured prompts that include style examples and feedback patterns. |
| `LCEL` ( `template | llm` ) | Both files | LangChain "chain-of-thought" operator that feeds the prompt straight into Llama and returns the result. |
| `FAISS` VectorStore | `feedback_system.py` | Stores & retrieves embedded feedback vectors quickly on disk. |

**Flow:** 
1. Samples & context build a **PromptTemplate**.  
2. The template is piped into `OllamaLLM` → local Llama 3 writes a post.  
3. Your feedback text is embedded via `OllamaEmbeddings` and saved to **FAISS**.  
4. Next time, LangChain searches FAISS for related feedback → injects best patterns back into the prompt → smarter output.

That's the entire LangChain + Ollama loop in Ghostwriter.

---

### Quick LangChain Primer

LangChain provides **building blocks** that we compose:

1. **PromptTemplate** – parameterised text with slots (style examples, context, instructions).
2. **LLM Wrapper (OllamaLLM)** – standard interface to any language model (here: local Llama 3).
3. **Chain** – simple operator `template | llm` sends the rendered prompt to the model.
4. **Embeddings** – numeric vectors for similarity search (`OllamaEmbeddings`).
5. **VectorStore (FAISS)** – fast nearest-neighbour search over those vectors.
6. **Memory** – optional chat history; we keep feedback vectors instead for long-term learning.

Putting it together: prompts → chain → LLM response, plus embeddings → vector store for feedback retrieval. LangChain takes care of the plumbing so we focus on logic.

---

That's it! You now know **what each part is for** and **how Ghostwriter flows from UI → AI → Learning**. 