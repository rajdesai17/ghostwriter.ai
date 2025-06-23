from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import re

from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from feedback_system import FeedbackMemoryStore, FeedbackEnhancedGenerator, create_feedback_entry

# ------------------ Config ------------------
PROFILES_DIR = "profiles"
DEFAULT_FILE = "storytelling.txt"
os.makedirs(PROFILES_DIR, exist_ok=True)

# Default model is now hardcoded to llama3:8b
DEFAULT_MODEL = "llama3:8b"

# Initialize feedback system (cached for performance)
_feedback_store = None
_feedback_generator = None

def get_feedback_store():
    """Get cached feedback store instance"""
    global _feedback_store
    if _feedback_store is None:
        _feedback_store = FeedbackMemoryStore(PROFILES_DIR)
    return _feedback_store

def get_feedback_generator():
    """Get cached feedback generator instance"""
    global _feedback_generator
    if _feedback_generator is None:
        _feedback_generator = FeedbackEnhancedGenerator(get_feedback_store())
    return _feedback_generator

# ------------------ Helpers ------------------

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9 _-]", "", text)
    return text.replace(" ", "_")

def get_profile_file(name: str) -> str:
    if name == "default":
        return DEFAULT_FILE
    return os.path.join(PROFILES_DIR, f"{slugify(name)}.txt")

def list_profiles() -> List[dict]:
    profiles = ["default"] + [f[:-4] for f in os.listdir(PROFILES_DIR) if f.endswith(".txt")]
    result = []
    feedback_store = get_feedback_store()
    
    for p in profiles:
        path = get_profile_file(p)
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        samples = [s for s in content.split("\n\n") if s.strip()]
        
        # Get feedback summary
        feedback_summary = feedback_store.get_profile_feedback_summary(p)
        
        result.append({
            "name": p, 
            "sampleCount": len(samples),
            "feedbackCount": feedback_summary['total_feedback'],
            "learningScore": feedback_summary['positive'] - feedback_summary['negative']
        })
    return result

def save_samples(path: str, samples: str, mode: str = "w"):
    with open(path, mode, encoding="utf-8") as f:
        if mode == "a":
            f.write("\n\n" + samples.strip())
        else:
            f.write(samples.strip())

# LangChain prompt
def build_prompt():
    template = """You are an AI assistant helping to write LinkedIn posts in the author's authentic voice and style.

Here are some examples of the author's writing style:

{style_examples}

Now, create a LinkedIn post about the following topic:

Context: {context}

Additional Instructions: {custom_instruction}

CRITICAL INSTRUCTIONS:
- Write ONLY the LinkedIn post content
- Do NOT include any explanations, analysis, or meta-commentary
- Do NOT mention voice analysis or style matching
- Do NOT start with phrases like "Here's a LinkedIn post that..."
- Write as if you ARE the user posting directly

LinkedIn Post:"""
    return PromptTemplate(input_variables=["style_examples", "context", "custom_instruction"], template=template)


def load_vectorstore(profile_name: str):
    file_path = get_profile_file(profile_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError("Profile file not found")
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    splitter = CharacterTextSplitter(separator="\n\n", chunk_size=1000, chunk_overlap=0, length_function=len)
    texts = splitter.split_documents(docs)
    if not texts:
        raise ValueError("Profile has no samples")
    embeddings = OllamaEmbeddings(model=DEFAULT_MODEL)
    return FAISS.from_documents(texts, embeddings)


def generate_post(profile: str, context: str, instruction: str):
    vectorstore = load_vectorstore(profile)
    docs = vectorstore.similarity_search(context, k=3)
    examples = [d.page_content.strip() for d in docs if d.page_content.strip()]
    if not examples:
        raise ValueError("No style examples found for generation")
    formatted = "\n\n".join([f"Example {i+1}:\n{ex}" for i, ex in enumerate(examples)])
    prompt = build_prompt()
    llm = OllamaLLM(model=DEFAULT_MODEL, temperature=0.7)
    chain = prompt | llm
    result = chain.invoke({
        "style_examples": formatted,
        "context": context,
        "custom_instruction": instruction or "Write in your authentic style."
    })
    return result.strip()

def generate_post_with_feedback(profile: str, context: str, instruction: str):
    """Generate post using feedback-enhanced generator"""
    vectorstore = load_vectorstore(profile)
    docs = vectorstore.similarity_search(context, k=3)
    examples = [d.page_content.strip() for d in docs if d.page_content.strip()]
    if not examples:
        raise ValueError("No style examples found for generation")
    
    formatted = "\n\n".join([f"Example {i+1}:\n{ex}" for i, ex in enumerate(examples)])
    
    # Use cached feedback-enhanced generator
    feedback_generator = get_feedback_generator()
    result = feedback_generator.generate_with_feedback(
        profile, context, instruction, formatted
    )
    
    if not result:
        raise ValueError("Failed to generate post")
    
    return result

# ------------------ API Schemas ------------------
class ProfileCreate(BaseModel):
    name: str = Field(..., example="professional")
    samples: str = Field(..., example="your first linkedin post...\n\nsecond post...")

class SamplesAppend(BaseModel):
    samples: str

class GenerateRequest(BaseModel):
    profile: str = Field("default")
    context: str
    instruction: Optional[str] = ""

class GenerateResponse(BaseModel):
    result: str

class FeedbackRequest(BaseModel):
    profile: str
    context: str
    instruction: str
    generated_post: str
    feedback_type: str  # 'positive', 'negative', 'refinement'
    feedback_text: str
    refinement_instruction: Optional[str] = ""

class RefineRequest(BaseModel):
    profile: str
    original_post: str
    feedback_text: str
    context: str

class FeedbackSummaryResponse(BaseModel):
    total_feedback: int
    positive: int
    negative: int
    refinements: int
    learning_score: int
    recent_patterns: List[dict]

class RegenerateRequest(BaseModel):
    profile: str
    context: str
    instruction: Optional[str] = ""

# ------------------ FastAPI App ------------------
app = FastAPI(title="Ghostwriter API with Learning")

# Allow CORS for local React dev server
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/profiles")
def api_list_profiles():
    return list_profiles()

@app.post("/profiles")
def api_create_profile(body: ProfileCreate):
    path = get_profile_file(body.name)
    if os.path.exists(path):
        raise HTTPException(status_code=400, detail="Profile already exists")
    save_samples(path, body.samples, "w")
    return {"status": "created"}

@app.post("/profiles/{name}/samples")
def api_append_samples(name: str = Path(...), body: SamplesAppend = ...):
    path = get_profile_file(name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Profile not found")
    save_samples(path, body.samples, "a")
    return {"status": "appended"}

@app.post("/generate", response_model=GenerateResponse)
def api_generate(body: GenerateRequest):
    try:
        # Use feedback-enhanced generation by default
        post = generate_post_with_feedback(body.profile, body.context, body.instruction)
        return {"result": post}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
def api_submit_feedback(body: FeedbackRequest):
    try:
        feedback_entry = create_feedback_entry(
            profile_name=body.profile,
            context=body.context,
            instruction=body.instruction,
            generated_post=body.generated_post,
            feedback_type=body.feedback_type,
            feedback_text=body.feedback_text,
            refinement_instruction=body.refinement_instruction
        )
        
        feedback_store = get_feedback_store()
        if feedback_store.store_feedback(feedback_entry):
            return {"status": "feedback_stored", "message": "Feedback saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to store feedback")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refine")
def api_refine_post(body: RefineRequest):
    try:
        feedback_generator = get_feedback_generator()
        refined_post = feedback_generator.refine_post(
            body.profile,
            body.original_post,
            body.feedback_text,
            body.context
        )
        return {"result": refined_post}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profiles/{name}/feedback", response_model=FeedbackSummaryResponse)
def api_get_feedback_summary(name: str = Path(...)):
    try:
        feedback_store = get_feedback_store()
        summary = feedback_store.get_profile_feedback_summary(name)
        summary["learning_score"] = summary['positive'] - summary['negative']
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profiles/{name}/feedback/relevant")
def api_get_relevant_feedback(name: str = Path(...), context: str = "", feedback_type: str = None):
    try:
        feedback_store = get_feedback_store()
        relevant_feedback = feedback_store.get_relevant_feedback(
            name, context, feedback_type, k=5
        )
        return {"feedback": relevant_feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/regenerate", response_model=GenerateResponse)
def api_regenerate_with_feedback(body: RegenerateRequest):
    """Regenerate a post using the latest feedback learning for the profile"""
    try:
        # Use feedback-enhanced generation with the most recent learning
        post = generate_post_with_feedback(body.profile, body.context, body.instruction)
        return {"result": post}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 