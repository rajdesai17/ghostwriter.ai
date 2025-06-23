# 📚 Ghostwriter - Detailed Documentation

This document contains comprehensive technical details, performance optimizations, advanced features, and troubleshooting information for Ghostwriter.

## 📖 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Performance Optimizations](#performance-optimizations)
- [Advanced Features](#advanced-features)
- [Technical Details](#technical-details)
- [Customization Guide](#customization-guide)
- [Troubleshooting](#troubleshooting)
- [Development Guide](#development-guide)

## 🏗️ Architecture Overview

### Tech Stack
- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: FastAPI with optimized caching
- **AI Framework**: LangChain with performance optimizations
- **Vector Search**: FAISS with lazy loading
- **Local LLM**: Ollama with cached initialization
- **Embeddings**: OllamaEmbeddings for semantic understanding

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │    │   FastAPI       │    │   Ollama        │
│                 │    │                 │    │                 │
│ • Debounced     │◄──►│ • Cached        │◄──►│ • Llama3:8B     │
│ • Memoized      │    │ • Lazy Loading  │    │ • Local         │
│ • Performance   │    │ • Monitoring    │    │ • Private       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │    │  Feedback       │    │   Vector        │
│                 │    │  System         │    │   Storage       │
│ • Context       │    │                 │    │                 │
│ • Instructions  │    │ • Learning      │    │ • FAISS         │
│ • Feedback      │    │ • Memory        │    │ • Embeddings    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ⚡ Performance Optimizations

### React Frontend Optimizations

#### 1. Debounced Inputs
```typescript
// Before: Every keystroke triggers API calls
onChange={(e) => setContext(e.target.value)}

// After: Debounced with 300ms delay
const debouncedContext = useDebounce(context, 300);
```

#### 2. Memoized Calculations
```typescript
// Expensive profile calculations cached
const profileOptions = useMemo(() => 
  profiles.map(p => ({ value: p.name, label: p.name })), 
  [profiles]
);

const selectedProfileData = useMemo(() => 
  profiles.find(p => p.name === selectedProfile), 
  [profiles, selectedProfile]
);
```

#### 3. Performance Monitoring
```typescript
// Built-in response time tracking
const { measureApiCall } = usePerformance();

const response = await measureApiCall(
  'Generate post',
  () => api.generatePost(data)
);
```

### Backend API Optimizations

#### 1. Cached Global Instances
```python
# Before: New instances every request (SLOW)
feedback_store = FeedbackMemoryStore(PROFILES_DIR)
feedback_generator = FeedbackEnhancedGenerator(feedback_store)

# After: Cached global instances (FAST)
_feedback_store = None
_feedback_generator = None

def get_feedback_store():
    global _feedback_store
    if _feedback_store is None:
        _feedback_store = FeedbackMemoryStore(PROFILES_DIR)
    return _feedback_store
```

#### 2. Lazy Loading AI Components
```python
# Embeddings load only when needed
@property
def embeddings(self):
    if self._embeddings is None:
        self._embeddings = OllamaEmbeddings(model="llama3:8b")
    return self._embeddings

# LLM instances cached
@property
def llm(self):
    if self._llm is None:
        self._llm = OllamaLLM(model="llama3:8b", temperature=0.7)
    return self._llm
```

### Performance Metrics

| Component | Before (Streamlit) | After (React) | Improvement |
|-----------|-------------------|---------------|-------------|
| **Initial Load** | 3-5 seconds | 0.5-1 second | **5-10x faster** |
| **Post Generation** | 8-12 seconds | 3-5 seconds | **2-3x faster** |
| **Feedback Submission** | 2-3 seconds | 0.5-1 second | **3-6x faster** |
| **UI Responsiveness** | Server delays | Real-time | **Instant** |
| **Memory Usage** | High overhead | Optimized | **40-50% reduction** |

## 🚀 Advanced Features

### Learning & Feedback System

#### Vector-Based Memory
- **FAISS Storage**: Feedback stored with vector embeddings
- **Semantic Search**: Similar contexts retrieve relevant feedback
- **Profile Isolation**: Each voice profile learns independently
- **Context Awareness**: Feedback applied to similar future contexts

#### Feedback Types
```python
class FeedbackTypes:
    POSITIVE = "positive"      # "Perfect tone!", "Exactly my style"
    NEGATIVE = "negative"      # "Too formal", "Doesn't sound like me"
    REFINEMENT = "refinement"  # "Make it more vulnerable", "Add emotion"
```

#### Enhanced Prompt Generation
```python
def create_feedback_aware_prompt(self, profile_name, context, instruction, style_examples):
    # Get feedback by type for structured learning
    positive_feedback = self.get_relevant_feedback(profile_name, context, "positive", k=2)
    negative_feedback = self.get_relevant_feedback(profile_name, context, "negative", k=2)
    refinement_feedback = self.get_relevant_feedback(profile_name, context, "refinement", k=2)
    
    # Build structured feedback context
    feedback_context = """
✅ POSITIVE PATTERNS TO FOLLOW:
   1. Perfect vulnerability and authenticity
   2. Great balance of emotion and hope

❌ NEGATIVE PATTERNS TO AVOID:
   1. Too corporate and formal language
   2. Lacks personal connection

🔄 REFINEMENT SUGGESTIONS:
   1. Add more specific emotional details
   2. Include personal struggle stories
"""
```

### Voice Profile Management

#### Profile Structure
```
profiles/
├── default.txt                    # Default writing samples
├── professional.txt               # Professional voice
├── vulnerable.txt                 # Personal/vulnerable voice
└── feedback/                      # Learning data
    ├── default_feedback.json      # Raw feedback entries
    ├── default_feedback_vectors/   # FAISS vector store
    │   ├── index.faiss            # Vector indices
    │   └── index.pkl              # Metadata
    └── [profile]_feedback.*       # Per-profile learning
```

#### Creating Custom Profiles
```python
# Via API
POST /profiles
{
  "name": "startup_founder",
  "samples": "day 1 building our startup...\n\njust raised our seed round..."
}

# Via React UI
1. Click "Create New Profile"
2. Enter profile name
3. Paste 15-30 writing samples
4. Save profile
```

### Real-time Regeneration

#### Workflow
```
User generates post → Provides feedback → System learns → 
Offers regeneration → User sees improvement → Provides more feedback
```

#### Implementation
```typescript
const handleSubmitFeedback = async () => {
  // Submit feedback
  await api.submitFeedback(feedbackData);
  
  // Ask for regeneration
  const regenerate = window.confirm(
    '🔄 Would you like to regenerate with your new feedback?'
  );
  
  if (regenerate) {
    const response = await api.regeneratePost({
      profile: selectedProfile,
      context: context.trim(),
      instruction: instructions.trim()
    });
    setResult(response.result);
  }
};
```

## 🔧 Technical Details

### API Endpoints

#### Core Generation
```
POST /generate
{
  "profile": "default",
  "context": "I failed my coding interview",
  "instruction": "Make it vulnerable but hopeful"
}
```

#### Feedback System
```
POST /feedback
{
  "profile": "default",
  "context": "original context",
  "instruction": "original instruction",
  "generated_post": "the generated post",
  "feedback_type": "positive|negative|refinement",
  "feedback_text": "specific feedback",
  "refinement_instruction": "optional refinement"
}

POST /regenerate
{
  "profile": "default",
  "context": "same context",
  "instruction": "same instruction"
}

POST /refine
{
  "profile": "default",
  "original_post": "original post text",
  "feedback_text": "make it more casual",
  "context": "original context"
}
```

#### Analytics
```
GET /profiles/{name}/feedback
# Returns: total_feedback, positive, negative, refinements, learning_score

GET /profiles/{name}/feedback/relevant?context=...&feedback_type=...
# Returns: relevant feedback entries for context
```

### Database Schema

#### Feedback Entry Structure
```python
@dataclass
class FeedbackEntry:
    timestamp: str                 # ISO format
    profile_name: str             # Profile identifier
    original_context: str         # User's input context
    original_instruction: str     # User's instructions
    generated_post: str           # AI-generated content
    feedback_type: str            # positive/negative/refinement
    feedback_text: str            # User's specific feedback
    refinement_instruction: str   # Optional refinement request
    approved_version: str         # Final approved version
```

#### Vector Storage
```python
# FAISS document structure
Document(
    page_content=f"""
    Context: {feedback.original_context}
    Instruction: {feedback.original_instruction}
    Generated: {feedback.generated_post}
    Feedback Type: {feedback.feedback_type}
    Feedback: {feedback.feedback_text}
    Refinement: {feedback.refinement_instruction}
    """,
    metadata={
        'profile_name': feedback.profile_name,
        'feedback_type': feedback.feedback_type,
        'timestamp': feedback.timestamp
    }
)
```

## 🎨 Customization Guide

### Creating Writing Samples

#### Format Guidelines
```
your first authentic linkedin post here.

maybe something vulnerable about failure.

with short lines and real emotions.

ending with a reflection or lesson.


your second post about a different topic.

showing growth or struggle.

personal and relatable content.

authentic voice throughout.
```

#### Quality Tips
- **Quantity**: 15-30 diverse posts minimum
- **Variety**: Different emotions, topics, and situations
- **Authenticity**: Your real voice, not corporate speak
- **Length**: Mix of short and longer posts
- **Style**: Consistent voice across all samples

### UI Customization

#### Tailwind CSS Classes
```typescript
// Main components use customizable classes
<Button className="bg-orange-500 hover:bg-orange-600">
<Card className="border-2 border-orange-200">
<TextArea className="border-gray-300 focus:border-orange-500">
```

#### Performance Hooks
```typescript
// Custom debounce timing
const debouncedValue = useDebounce(value, 500); // Slower debounce

// Performance monitoring
const { measureApiCall, startTimer, endTimer } = usePerformance();
```

### AI Model Configuration

#### Temperature Settings
```python
# More creative (higher temperature)
OllamaLLM(model="llama3:8b", temperature=0.9)

# More consistent (lower temperature)
OllamaLLM(model="llama3:8b", temperature=0.3)
```

#### Context Length
```python
# Adjust chunk size for longer posts
CharacterTextSplitter(
    separator="\n\n",
    chunk_size=2000,  # Increased from 1000
    chunk_overlap=100,
    length_function=len,
)
```

## 🔧 Troubleshooting

### Common Issues

#### Ollama Connection Failed
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve

# Verify model availability
ollama pull llama3:8b
```

#### React App Won't Start
```bash
# Clear Node modules and reinstall
cd project
rm -rf node_modules package-lock.json
npm install

# Or use legacy peer deps
npm install --legacy-peer-deps
```

#### API Server Issues
```bash
# Check port availability
netstat -tulpn | grep :8000

# Restart with different port
uvicorn api:app --port 8001

# Check Python dependencies
pip install -r requirements.txt
```

#### Performance Issues
```bash
# Check system resources
htop  # Linux/Mac
taskmgr  # Windows

# Reduce model load
# Use smaller context chunks
# Lower temperature settings
```

### Error Messages

#### "Model not found"
```bash
# Download missing model
ollama pull llama3:8b

# Check available models
ollama list
```

#### "FAISS/Vector store error"
```bash
# Reinstall FAISS
pip uninstall faiss-cpu
pip install faiss-cpu==1.8.0
```

#### "No examples found"
- Ensure writing samples file exists
- Check UTF-8 encoding
- Verify posts separated by double line breaks
- Minimum 3-5 posts required

### Performance Optimization

#### Memory Usage
- **Model Loading**: ~3-4GB for Llama3:8B
- **Vector Storage**: ~50-100MB per 1000 feedback entries
- **React App**: ~100-200MB
- **Recommended**: 8GB+ total RAM

#### Speed Optimization
```python
# Cache embeddings globally
@lru_cache(maxsize=128)
def get_cached_embeddings(model_name):
    return OllamaEmbeddings(model=model_name)

# Reduce vector search results
docs = vectorstore.similarity_search(context, k=2)  # Reduced from 3

# Optimize chunk size
chunk_size=500  # Smaller chunks for faster processing
```

## 👩‍💻 Development Guide

### Project Structure
```
ghostwriter/
├── start_app.py                    # Optimized startup script
├── api.py                          # FastAPI backend
├── feedback_system.py              # Learning system
├── requirements.txt                # Python dependencies
├── app_streamlit_old.py            # Old Streamlit app (preserved)
├── project/                        # React frontend
│   ├── src/
│   │   ├── hooks/                  # Performance hooks
│   │   ├── components/             # UI components
│   │   ├── pages/                  # Page components
│   │   ├── contexts/               # React contexts
│   │   └── api/                    # API client
│   ├── package.json               # Node dependencies
│   └── tsconfig.json              # TypeScript config
└── profiles/                       # Voice profiles and feedback
    ├── *.txt                      # Writing samples
    └── feedback/                  # Vector storage
```

### Adding Features

#### New API Endpoint
```python
@app.post("/new-feature")
def new_feature_endpoint(data: NewFeatureRequest):
    try:
        # Your logic here
        return {"result": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### New React Component
```typescript
interface NewComponentProps {
  data: string;
  onUpdate: (value: string) => void;
}

export function NewComponent({ data, onUpdate }: NewComponentProps) {
  return (
    <div className="space-y-4">
      {/* Your component here */}
    </div>
  );
}
```

#### Performance Hook
```typescript
export function useNewFeature() {
  const [state, setState] = useState();
  const debouncedState = useDebounce(state, 300);
  
  const processData = useCallback(async () => {
    // Your logic here
  }, [debouncedState]);
  
  return { state, setState, processData };
}
```

### Testing

#### Backend Tests
```python
# Test feedback system
python test_feedback_vector_integration.py

# Test regeneration
python test_regeneration.py

# Test API
pytest test_api.py  # If you create pytest tests
```

#### Frontend Testing
```bash
cd project

# Run tests
npm test

# Build for production
npm run build
```

### Deployment

#### Local Production Build
```bash
# Build React app
cd project
npm run build

# Serve built files
python -m http.server 3000 -d dist

# Run API in production mode
uvicorn api:app --host 0.0.0.0 --port 8000
```

#### Docker (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

For basic usage and quick start, see the main [README.md](README.md).

For optimization details, see [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md). 