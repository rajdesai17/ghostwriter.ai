import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter

@dataclass
class FeedbackEntry:
    """Represents a single feedback entry with context and learning"""
    timestamp: str
    profile_name: str
    original_context: str
    original_instruction: str
    generated_post: str
    feedback_type: str  # 'positive', 'negative', 'refinement'
    feedback_text: str
    refinement_instruction: str = ""
    approved_version: str = ""

class FeedbackMemoryStore:
    """Manages feedback storage and retrieval using LangChain memory components"""
    
    def __init__(self, profiles_dir: str = "profiles"):
        self.profiles_dir = profiles_dir
        self.feedback_dir = os.path.join(profiles_dir, "feedback")
        os.makedirs(self.feedback_dir, exist_ok=True)
        
        # Initialize LangChain components (cached for performance)
        self._embeddings = None
        self.conversation_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Profile-specific feedback stores (lazy loaded)
        self.feedback_stores: Dict[str, FAISS] = {}
        self.load_existing_feedback()
    
    @property
    def embeddings(self):
        """Lazy load embeddings for better performance"""
        if self._embeddings is None:
            self._embeddings = OllamaEmbeddings(model="llama3:8b")
        return self._embeddings
    
    def get_feedback_file(self, profile_name: str) -> str:
        """Get the feedback file path for a profile"""
        return os.path.join(self.feedback_dir, f"{profile_name}_feedback.json")
    
    def get_feedback_vector_store(self, profile_name: str) -> str:
        """Get the feedback vector store path for a profile"""
        return os.path.join(self.feedback_dir, f"{profile_name}_feedback_vectors")
    
    def load_existing_feedback(self):
        """Load existing feedback for all profiles"""
        if not os.path.exists(self.feedback_dir):
            return
            
        for filename in os.listdir(self.feedback_dir):
            if filename.endswith("_feedback.json"):
                profile_name = filename.replace("_feedback.json", "")
                self._load_profile_feedback(profile_name)
    
    def _load_profile_feedback(self, profile_name: str):
        """Load feedback vector store for a specific profile"""
        feedback_file = self.get_feedback_file(profile_name)
        vector_store_path = self.get_feedback_vector_store(profile_name)
        
        if os.path.exists(feedback_file) and os.path.exists(vector_store_path):
            try:
                # Load the FAISS vector store
                self.feedback_stores[profile_name] = FAISS.load_local(
                    vector_store_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            except Exception as e:
                print(f"Error loading feedback vectors for {profile_name}: {e}")
    
    def store_feedback(self, feedback: FeedbackEntry) -> bool:
        """Store feedback entry and update vector store"""
        try:
            feedback_file = self.get_feedback_file(feedback.profile_name)
            
            # Load existing feedback
            feedback_list = []
            if os.path.exists(feedback_file):
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    feedback_list = json.load(f)
            
            # Add new feedback
            feedback_dict = asdict(feedback)
            feedback_list.append(feedback_dict)
            
            # Save updated feedback
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedback_list, f, indent=2, ensure_ascii=False)
            
            # Update vector store
            self._update_feedback_vectors(feedback)
            return True
            
        except Exception as e:
            print(f"Error storing feedback: {e}")
            return False
    
    def _update_feedback_vectors(self, feedback: FeedbackEntry):
        """Update the FAISS vector store with new feedback"""
        try:
            # Create a document from the feedback for embedding
            feedback_content = f"""
            Context: {feedback.original_context}
            Instruction: {feedback.original_instruction}
            Generated: {feedback.generated_post}
            Feedback Type: {feedback.feedback_type}
            Feedback: {feedback.feedback_text}
            Refinement: {feedback.refinement_instruction}
            """
            
            doc = Document(
                page_content=feedback_content.strip(),
                metadata={
                    'profile_name': feedback.profile_name,
                    'feedback_type': feedback.feedback_type,
                    'timestamp': feedback.timestamp
                }
            )
            
            # Create or update vector store
            if feedback.profile_name in self.feedback_stores:
                # Add to existing store
                self.feedback_stores[feedback.profile_name].add_documents([doc])
            else:
                # Create new store
                self.feedback_stores[feedback.profile_name] = FAISS.from_documents(
                    [doc], self.embeddings
                )
            
            # Save the updated vector store
            vector_store_path = self.get_feedback_vector_store(feedback.profile_name)
            self.feedback_stores[feedback.profile_name].save_local(vector_store_path)
            
        except Exception as e:
            print(f"Error updating feedback vectors: {e}")
    
    def get_relevant_feedback(self, profile_name: str, context: str, 
                            feedback_type: str = None, k: int = 3) -> List[Dict]:
        """Retrieve relevant feedback based on context similarity"""
        if profile_name not in self.feedback_stores:
            return []
        
        try:
            # Search for similar feedback
            docs = self.feedback_stores[profile_name].similarity_search(
                context, k=k*2  # Get more docs initially for better filtering
            )
            
            # Filter by feedback type if specified
            if feedback_type:
                docs = [doc for doc in docs 
                       if doc.metadata.get('feedback_type') == feedback_type]
            
            # Sort by timestamp (most recent first) and limit to k results
            docs_with_timestamps = []
            for doc in docs:
                timestamp = doc.metadata.get('timestamp', '1970-01-01T00:00:00')
                docs_with_timestamps.append((doc, timestamp))
            
            # Sort by timestamp descending (most recent first)
            docs_with_timestamps.sort(key=lambda x: x[1], reverse=True)
            
            # Take top k results
            final_docs = [doc for doc, _ in docs_with_timestamps[:k]]
            
            return [
                {
                    'content': doc.page_content,
                    'metadata': doc.metadata
                }
                for doc in final_docs
            ]
            
        except Exception as e:
            print(f"Error retrieving feedback: {e}")
            return []
    
    def get_strongest_feedback_patterns(self, profile_name: str, k: int = 5) -> Dict[str, List[Dict]]:
        """Get the strongest feedback patterns for a profile"""
        feedback_file = self.get_feedback_file(profile_name)
        
        if not os.path.exists(feedback_file):
            return {'positive': [], 'negative': [], 'refinement': []}
        
        try:
            with open(feedback_file, 'r', encoding='utf-8') as f:
                feedback_list = json.load(f)
            
            # Group by feedback type
            patterns = {'positive': [], 'negative': [], 'refinement': []}
            
            for feedback in feedback_list:
                feedback_type = feedback.get('feedback_type', 'unknown')
                if feedback_type in patterns:
                    patterns[feedback_type].append(feedback)
            
            # Sort each type by timestamp (most recent first) and limit
            for feedback_type in patterns:
                patterns[feedback_type] = sorted(
                    patterns[feedback_type], 
                    key=lambda x: x.get('timestamp', ''), 
                    reverse=True
                )[:k]
            
            return patterns
            
        except Exception as e:
            print(f"Error getting feedback patterns: {e}")
            return {'positive': [], 'negative': [], 'refinement': []}
    
    def get_profile_feedback_summary(self, profile_name: str) -> Dict[str, Any]:
        """Get a summary of feedback for a profile"""
        feedback_file = self.get_feedback_file(profile_name)
        
        if not os.path.exists(feedback_file):
            return {
                'total_feedback': 0,
                'positive': 0,
                'negative': 0,
                'refinements': 0,
                'recent_patterns': []
            }
        
        try:
            with open(feedback_file, 'r', encoding='utf-8') as f:
                feedback_list = json.load(f)
            
            summary = {
                'total_feedback': len(feedback_list),
                'positive': len([f for f in feedback_list if f['feedback_type'] == 'positive']),
                'negative': len([f for f in feedback_list if f['feedback_type'] == 'negative']),
                'refinements': len([f for f in feedback_list if f['feedback_type'] == 'refinement']),
                'recent_patterns': []
            }
            
            # Get recent feedback patterns
            recent_feedback = sorted(
                feedback_list, 
                key=lambda x: x['timestamp'], 
                reverse=True
            )[:5]
            
            summary['recent_patterns'] = [
                {
                    'feedback_text': f['feedback_text'],
                    'feedback_type': f['feedback_type'],
                    'timestamp': f['timestamp']
                }
                for f in recent_feedback
            ]
            
            return summary
            
        except Exception as e:
            print(f"Error getting feedback summary: {e}")
            return {'total_feedback': 0, 'positive': 0, 'negative': 0, 'refinements': 0, 'recent_patterns': []}

class FeedbackEnhancedGenerator:
    """Enhanced post generator that incorporates user feedback"""
    
    def __init__(self, feedback_store: FeedbackMemoryStore):
        self.feedback_store = feedback_store
        self._llm = None
    
    @property
    def llm(self):
        """Lazy load LLM for better performance"""
        if self._llm is None:
            self._llm = OllamaLLM(model="llama3:8b", temperature=0.7)
        return self._llm
    
    def create_feedback_aware_prompt(self, profile_name: str, context: str, 
                                   instruction: str, style_examples: str) -> PromptTemplate:
        """Create a prompt that incorporates relevant feedback"""
        
        # Get relevant feedback for this context - separate positive and negative
        positive_feedback = self.feedback_store.get_relevant_feedback(
            profile_name, context, feedback_type="positive", k=2
        )
        negative_feedback = self.feedback_store.get_relevant_feedback(
            profile_name, context, feedback_type="negative", k=2
        )
        refinement_feedback = self.feedback_store.get_relevant_feedback(
            profile_name, context, feedback_type="refinement", k=2
        )
        
        # Build structured feedback context
        feedback_context = ""
        
        if positive_feedback or negative_feedback or refinement_feedback:
            feedback_context = "\nBased on previous user feedback for similar content:\n"
            
            if positive_feedback:
                feedback_context += "\n✅ POSITIVE PATTERNS TO FOLLOW:\n"
                for i, feedback in enumerate(positive_feedback):
                    lines = feedback['content'].split('\n')
                    feedback_text = next((line.split('Feedback:')[1].strip() for line in lines if 'Feedback:' in line), 'Unknown feedback')
                    feedback_context += f"   {i+1}. {feedback_text}\n"
            
            if negative_feedback:
                feedback_context += "\n❌ NEGATIVE PATTERNS TO AVOID:\n"
                for i, feedback in enumerate(negative_feedback):
                    lines = feedback['content'].split('\n')
                    feedback_text = next((line.split('Feedback:')[1].strip() for line in lines if 'Feedback:' in line), 'Unknown feedback')
                    feedback_context += f"   {i+1}. {feedback_text}\n"
            
            if refinement_feedback:
                feedback_context += "\n🔄 REFINEMENT SUGGESTIONS TO CONSIDER:\n"
                for i, feedback in enumerate(refinement_feedback):
                    lines = feedback['content'].split('\n')
                    feedback_text = next((line.split('Feedback:')[1].strip() for line in lines if 'Feedback:' in line), 'Unknown feedback')
                    refinement_text = next((line.split('Refinement:')[1].strip() for line in lines if 'Refinement:' in line and line.split('Refinement:')[1].strip()), None)
                    if refinement_text:
                        feedback_context += f"   {i+1}. {feedback_text} → {refinement_text}\n"
                    else:
                        feedback_context += f"   {i+1}. {feedback_text}\n"
            
            feedback_context += "\nIMPORTANT: Use the positive patterns, avoid the negative patterns, and consider the refinement suggestions when generating the post.\n"
        
        template = f"""You are an AI assistant helping to write LinkedIn posts in the user's authentic voice and style.

Here are some examples of the user's writing style:

{"{style_examples}"}
{feedback_context}
Now create a LinkedIn post about the following topic:

Context: {"{context}"}

Additional Instructions: {"{custom_instruction}"}

CRITICAL INSTRUCTIONS:
- Write ONLY the LinkedIn post content
- Do NOT include any explanations, analysis, or meta-commentary
- Do NOT mention feedback patterns or voice analysis
- Do NOT start with phrases like "Here's a LinkedIn post that..."
- Write as if you ARE the user posting directly

LinkedIn Post:"""

        return PromptTemplate(
            input_variables=["style_examples", "context", "custom_instruction"],
            template=template
        )
    
    def generate_with_feedback(self, profile_name: str, context: str, 
                             instruction: str, style_examples: str) -> str:
        """Generate a post incorporating feedback learning"""
        try:
            # Create feedback-aware prompt
            prompt_template = self.create_feedback_aware_prompt(
                profile_name, context, instruction, style_examples
            )
            
            # Create chain
            chain = prompt_template | self.llm
            
            # Generate the post
            result = chain.invoke({
                "style_examples": style_examples,
                "context": context,
                "custom_instruction": instruction or "Write in your authentic style."
            })
            
            return result.strip()
            
        except Exception as e:
            print(f"Error generating post with feedback: {e}")
            return None
    
    def refine_post(self, profile_name: str, original_post: str, 
                   feedback_text: str, context: str) -> str:
        """Refine a post based on specific feedback"""
        
        refinement_template = PromptTemplate(
            input_variables=["original_post", "feedback", "context"],
            template="""You are helping to refine a LinkedIn post based on user feedback.

Original Post:
{original_post}

User Feedback:
{feedback}

Context: {context}

CRITICAL INSTRUCTIONS:
- Revise the post incorporating the feedback
- Write ONLY the revised LinkedIn post content
- Do NOT include explanations or meta-commentary
- Do NOT mention the revision process
- Write as if you ARE the user posting directly

Revised Post:"""
        )
        
        chain = refinement_template | self.llm
        
        try:
            result = chain.invoke({
                "original_post": original_post,
                "feedback": feedback_text,
                "context": context
            })
            return result.strip()
        except Exception as e:
            print(f"Error refining post: {e}")
            return original_post

def create_feedback_entry(profile_name: str, context: str, instruction: str,
                         generated_post: str, feedback_type: str, 
                         feedback_text: str, refinement_instruction: str = "",
                         approved_version: str = "") -> FeedbackEntry:
    """Helper function to create a feedback entry"""
    return FeedbackEntry(
        timestamp=datetime.now().isoformat(),
        profile_name=profile_name,
        original_context=context,
        original_instruction=instruction,
        generated_post=generated_post,
        feedback_type=feedback_type,
        feedback_text=feedback_text,
        refinement_instruction=refinement_instruction,
        approved_version=approved_version
    ) 