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
_vectorstores = {}  # Cache vectorstores per profile

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

def get_cached_vectorstore(profile_name: str):
    """Get cached vectorstore for profile"""
    global _vectorstores
    if profile_name not in _vectorstores:
        _vectorstores[profile_name] = load_vectorstore(profile_name)
    return _vectorstores[profile_name]

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
            content = f.read()

        # Detect numbered sample markers if present (e.g., "--- SAMPLE 1 START ---")
        marker_lines = [line for line in content.splitlines() if line.strip().startswith("--- SAMPLE") and "START" in line]

        if marker_lines:
            # Each marker corresponds to one sample
            samples = marker_lines
        else:
            # Fallback: split by double newline blocks
            samples = [s for s in content.strip().split("\n\n") if s.strip()]
        
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
    if mode == "w":
        # For new profiles, format samples with proper markers
        formatted_content = format_samples_with_markers(samples)
        with open(path, "w", encoding="utf-8") as f:
            f.write(formatted_content)
        return
    
    # If appending and file contains SAMPLE markers, wrap new content accordingly
    if mode == "a" and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as existing:
            content = existing.read()

        marker_lines = [line for line in content.splitlines() if line.strip().startswith("--- SAMPLE") and "START" in line]

        if marker_lines:
            next_num = len(marker_lines) + 1
            # Use the same conservative logic as format_samples_with_markers
            formatted_content = format_samples_with_markers(samples)
            
            # Extract the samples from the formatted content and renumber them
            import re
            sample_pattern = r'--- SAMPLE \d+ START ---\n(.*?)\n--- SAMPLE \d+ END ---'
            found_samples = re.findall(sample_pattern, formatted_content, re.DOTALL)
            
            formatted_additions = []
            for i, sample_content in enumerate(found_samples):
                sample_num = next_num + i
                formatted_additions.append(f"\n\n--- SAMPLE {sample_num} START ---\n{sample_content}\n--- SAMPLE {sample_num} END ---")
            
            with open(path, "a", encoding="utf-8") as f:
                f.write("".join(formatted_additions))
            return

    # Default behaviour for appending to files without markers
    with open(path, mode, encoding="utf-8") as f:
        if mode == "a":
            f.write("\n\n" + samples.strip())
        else:
            f.write(samples.strip())

def format_samples_with_markers(samples: str) -> str:
    """Format raw samples with proper SAMPLE markers"""
    # Be very conservative - only split on explicit separators
    # Look for explicit separators like "=== NEW POST ===" or "--- NEW SAMPLE ---"
    explicit_separators = [
        "=== NEW POST ===",
        "--- NEW SAMPLE ---", 
        "=== SEPARATE POST ===",
        "--- SEPARATE POST ---",
        "=== NEW ===",
        "--- NEW ---"
    ]
    
    # Check if any explicit separators exist
    content = samples.strip()
    sample_list = [content]  # Default to one sample
    
    for separator in explicit_separators:
        if separator in content:
            # Split on this separator and clean up
            parts = [part.strip() for part in content.split(separator) if part.strip()]
            if len(parts) > 1:
                sample_list = parts
                break
    
    # Fallback: only split if there are 5+ consecutive newlines (very rare)
    if len(sample_list) == 1:
        very_large_gaps = [s.strip() for s in content.split("\n\n\n\n\n") if s.strip()]
        if len(very_large_gaps) > 1:
            # Additional validation: each part should be substantial (200+ chars)
            validated = [part for part in very_large_gaps if len(part) >= 200]
            if len(validated) == len(very_large_gaps):  # All parts are substantial
                sample_list = validated
    
    if not sample_list:
        return samples.strip()
    
    formatted_samples = []
    for i, sample in enumerate(sample_list, 1):
        formatted_sample = f"--- SAMPLE {i} START ---\n{sample}\n--- SAMPLE {i} END ---"
        formatted_samples.append(formatted_sample)
    
    return "\n\n".join(formatted_samples)

# LangChain prompt
def build_prompt():
    template = """Study these writing samples carefully:

{style_examples}

Write a LinkedIn post about: {context}

Instructions: {custom_instruction}

CRITICAL: 
- Copy the EXACT writing style from the samples
- Match the tone, structure, and language patterns
- NO explanations, NO meta-commentary
- Write ONLY the post content
- Follow the samples' style strictly - make NO assumptions

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
    vectorstore = get_cached_vectorstore(profile)
    docs = vectorstore.similarity_search(context, k=2)  # Reduced from 3 to 2
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
        "custom_instruction": instruction or "Write naturally."
    })
    return result.strip()

def generate_post_with_feedback(profile: str, context: str, instruction: str):
    """Generate post using feedback-enhanced generator with fallback"""
    try:
        vectorstore = get_cached_vectorstore(profile)
        docs = vectorstore.similarity_search(context, k=2)  # Reduced from 3 to 2
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
        
    except Exception as e:
        print(f"⚡ Feedback generation failed: {e}")
        # Fallback to basic generation
        return generate_post(profile, context, instruction)

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
        # Try feedback-enhanced generation first
        post = generate_post_with_feedback(body.profile, body.context, body.instruction)
        return {"result": post}
    except Exception as feedback_error:
        print(f"❌ Feedback generation failed: {feedback_error}")
        try:
            # Fallback to basic generation without feedback
            print("🔄 Trying basic generation as fallback...")
            post = generate_post(body.profile, body.context, body.instruction)
            return {"result": post}
        except Exception as basic_error:
            print(f"❌ Basic generation also failed: {basic_error}")
            raise HTTPException(status_code=500, detail=f"Generation failed - Feedback error: {feedback_error}, Basic error: {basic_error}")

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