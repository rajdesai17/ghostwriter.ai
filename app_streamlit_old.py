import streamlit as st
import os
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
import tempfile
import traceback
import re
from feedback_system import FeedbackMemoryStore, FeedbackEnhancedGenerator, create_feedback_entry

# Configure page
st.set_page_config(
    page_title="LinkedIn Post Assistant with Learning",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #0077B5;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    
    .generated-post {
        background-color: #f8f9fa;
        border: 2px solid #0077B5;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    
    .feedback-section {
        background-color: #fff8dc;
        border: 2px solid #ffa500;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    
    .info-box {
        background-color: #e7f3ff;
        border-left: 5px solid #0077B5;
        padding: 15px;
        margin: 10px 0;
    }
    
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px;
        margin: 10px 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
    }
    
    .error-box {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

PROFILES_DIR = "profiles"

# Ensure profiles directory exists
os.makedirs(PROFILES_DIR, exist_ok=True)

# Initialize feedback system
@st.cache_resource
def initialize_feedback_system():
    """Initialize the feedback memory store"""
    return FeedbackMemoryStore(PROFILES_DIR)

@st.cache_resource
def initialize_feedback_generator(_feedback_store):
    """Initialize the feedback-enhanced generator"""
    return FeedbackEnhancedGenerator(_feedback_store)

def slugify(text: str) -> str:
    """Simple slugify to create filesystem-friendly names."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9 _-]", "", text)
    text = text.replace(" ", "_")
    return text

def list_profiles():
    """Return a list of available profile names (including 'default')."""
    profiles = [f[:-4] for f in os.listdir(PROFILES_DIR) if f.endswith(".txt")]
    profiles.sort()
    return ["default"] + profiles

def get_profile_file(profile_name: str) -> str:
    """Return path to the profile examples file."""
    if profile_name == "default":
        return "raj_linkedin_examples.txt"
    slug = slugify(profile_name)
    return os.path.join(PROFILES_DIR, f"{slug}.txt")

def create_profile(profile_name: str, samples: str) -> bool:
    """Create a new profile file with given samples. Returns True on success."""
    if not profile_name.strip():
        st.error("Profile name cannot be empty")
        return False
    if not samples.strip():
        st.error("Please provide writing samples for the profile")
        return False
    slug = slugify(profile_name)
    path = os.path.join(PROFILES_DIR, f"{slug}.txt")
    if os.path.exists(path):
        st.error("A profile with this name already exists")
        return False
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(samples.strip())
        st.success(f"Profile '{profile_name}' created!")
        return True
    except Exception as e:
        st.error(f"Failed to create profile: {e}")
        return False

def load_and_index_examples(profile_name):
    """Load LinkedIn examples and create FAISS vector store."""
    try:
        profile_file = get_profile_file(profile_name)
        if not os.path.exists(profile_file):
            st.error(f"❌ Examples file for profile '{profile_name}' not found!")
            return None
            
        # Load the examples
        loader = TextLoader(profile_file, encoding='utf-8')
        documents = loader.load()
        
        # Split into individual posts
        text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=1000,
            chunk_overlap=0,
            length_function=len,
        )
        texts = text_splitter.split_documents(documents)
        
        if len(texts) == 0:
            st.error("❌ No LinkedIn examples found in the file!")
            return None
            
        # Create embeddings using Ollama with llama3:8b
        embeddings = OllamaEmbeddings(model="llama3:8b")
        
        # Create FAISS vector store
        vectorstore = FAISS.from_documents(texts, embeddings)
        
        return vectorstore
        
    except Exception as e:
        st.error(f"❌ Error loading examples: {str(e)}")
        st.error(f"Make sure Ollama is running and the llama3:8b model is available.")
        return None

def retrieve_style_examples(vectorstore, context, num_examples=3):
    """Retrieve relevant style examples based on context."""
    try:
        # Search for similar posts
        docs = vectorstore.similarity_search(context, k=num_examples)
        
        if len(docs) < 2:
            st.warning(f"⚠️ Only found {len(docs)} relevant examples. Consider adding more diverse writing samples.")
        
        # Extract the text content
        examples = [doc.page_content.strip() for doc in docs if doc.page_content.strip()]
        
        return examples
        
    except Exception as e:
        st.error(f"❌ Error retrieving examples: {str(e)}")
        return []

def display_feedback_summary(feedback_store, profile_name):
    """Display feedback summary for the selected profile"""
    summary = feedback_store.get_profile_feedback_summary(profile_name)
    
    if summary['total_feedback'] > 0:
        st.markdown("### 📊 Learning Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Feedback", summary['total_feedback'])
        with col2:
            st.metric("👍 Positive", summary['positive'])
        with col3:
            st.metric("👎 Negative", summary['negative'])
        with col4:
            st.metric("🔄 Refinements", summary['refinements'])
        
        if summary['recent_patterns']:
            st.markdown("#### Recent Learning Patterns:")
            for pattern in summary['recent_patterns'][:3]:
                feedback_color = {
                    'positive': '🟢',
                    'negative': '🔴',
                    'refinement': '🟡'
                }.get(pattern['feedback_type'], '⚪')
                
                st.markdown(f"{feedback_color} **{pattern['feedback_type'].title()}**: {pattern['feedback_text']}")

def main():
    """Main Streamlit application with feedback functionality."""
    
    # Initialize feedback system
    feedback_store = initialize_feedback_system()
    feedback_generator = initialize_feedback_generator(feedback_store)
    
    # Header
    st.markdown('<h1 class="main-header">📝 LinkedIn Post Assistant with Learning</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'generated_post' not in st.session_state:
        st.session_state.generated_post = ""
    if 'show_feedback' not in st.session_state:
        st.session_state.show_feedback = False
    if 'last_context' not in st.session_state:
        st.session_state.last_context = ""
    if 'last_instruction' not in st.session_state:
        st.session_state.last_instruction = ""
    if 'selected_profile' not in st.session_state:
        st.session_state.selected_profile = "default"
    
    # Sidebar with instructions and feedback summary
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        st.markdown("### 🤖 AI Model")
        st.info("Using **Llama3:8B** with **Learning Memory** - gets better with feedback!")

        # Profile selection
        st.markdown("## 🤖 Voice Profiles")
        profiles = list_profiles()
        
        selected_profile = st.selectbox(
            "Select Voice Profile:",
            options=profiles,
            index=profiles.index(st.session_state.selected_profile) if st.session_state.selected_profile in profiles else 0
        )
        st.session_state.selected_profile = selected_profile
        
        # Display feedback summary
        display_feedback_summary(feedback_store, selected_profile)
        
        # Create new profile section toggle
        if 'show_create_profile' not in st.session_state:
            st.session_state.show_create_profile = False

        if st.button("➕ Create New Profile"):
            st.session_state.show_create_profile = not st.session_state.show_create_profile

        if st.session_state.show_create_profile:
            new_name = st.text_input("Profile Name")
            new_samples = st.text_area("Paste sample LinkedIn posts (separate by blank line)", height=200)
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("💾 Save Profile"):
                    if create_profile(new_name, new_samples):
                        st.session_state.show_create_profile = False
                        st.rerun()
            with col_cancel:
                if st.button("❌ Cancel"):
                    st.session_state.show_create_profile = False

        # Option to append samples to current profile
        st.markdown("### ➕ Add Samples to Selected Profile")
        if selected_profile:
            sample_input_key = f"new_samples_{selected_profile}"
            new_profile_samples = st.text_area(
                "Paste additional LinkedIn posts to add to this profile (optional)",
                key=sample_input_key,
                height=150
            )
            if st.button("Append Samples"):
                if not new_profile_samples.strip():
                    st.warning("Please paste some writing samples before appending.")
                else:
                    pf = get_profile_file(selected_profile)
                    try:
                        with open(pf, "a", encoding="utf-8") as f:
                            # Ensure separation
                            f.write("\n\n" + new_profile_samples.strip())
                        st.success("Samples appended to profile!")
                        # Clear textarea by removing key then rerun
                        del st.session_state[sample_input_key]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to append samples: {e}")
        
        st.markdown("## 🚀 How it works")
        st.markdown("""
        1. **Choose Profile**: Select your voice profile.
        2. **Enter Context**: What your post is about.
        3. **Add Instructions**: Optional tone/style hints.
        4. **Generate**: AI creates your post using learned patterns.
        5. **Provide Feedback**: Help AI learn your preferences.
        6. **Refine**: Request changes based on feedback.
        """)
        
        st.markdown("## 💡 Learning Tips")
        st.markdown("""
        - Give specific feedback: "Too formal", "More vulnerable"
        - Use positive feedback: "Perfect tone!", "Exactly my style"
        - Request refinements: "Add more emotion", "Shorter sentences"
        - The AI learns and improves with each interaction!
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Input")
        
        # Context input
        context = st.text_area(
            "Context (What is your post about?)",
            placeholder="e.g., I failed my exam but learned something important, Just got rejected from a job I really wanted...",
            height=150,
            help="Share your personal experience - the more authentic and vulnerable, the better!"
        )
        
        # Custom instruction input
        custom_instruction = st.text_area(
            "Custom Instructions (Optional)",
            placeholder="e.g., Make it vulnerable but hopeful, Share the raw emotions I felt...",
            height=100,
            help="Specify the emotional tone or personal angle you want to emphasize"
        )
        
        # Generate button
        generate_button = st.button("🚀 Generate LinkedIn Post", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("### ✨ Generated Post")
        
        if generate_button:
            # Validation
            if not context.strip():
                st.markdown('<div class="error-box">❌ Please enter a context for your post!</div>', unsafe_allow_html=True)
            else:
                with st.spinner(f"🤖 Using Llama3:8B with learned patterns to generate post..."):
                    # Load and index examples for selected profile
                    vectorstore = load_and_index_examples(st.session_state.selected_profile)
                    
                    if vectorstore is not None:
                        # Retrieve style examples
                        style_examples = retrieve_style_examples(vectorstore, context)
                        
                        if style_examples:
                            # Format examples for the prompt
                            formatted_examples = "\n\n".join([f"Example {i+1}:\n{example}" for i, example in enumerate(style_examples)])
                            
                            # Generate the post using feedback-enhanced generator
                            generated_post = feedback_generator.generate_with_feedback(
                                st.session_state.selected_profile,
                                context,
                                custom_instruction,
                                formatted_examples
                            )
                            
                            if generated_post:
                                st.session_state.generated_post = generated_post
                                st.session_state.last_context = context
                                st.session_state.last_instruction = custom_instruction
                                st.session_state.show_feedback = True
                                st.success("✅ Post generated successfully!")
        
        # Display the generated post
        if st.session_state.generated_post:
            st.markdown('<div class="generated-post">', unsafe_allow_html=True)
            
            # Show the generated post in a text area for easy copying
            st.text_area(
                "Your LinkedIn Post:",
                value=st.session_state.generated_post,
                height=300,
                help="Copy this text and paste it into LinkedIn!"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Copy button
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                st.code(st.session_state.generated_post)
                st.info("📋 Post copied! You can now paste it into LinkedIn.")
    
    # Feedback Section
    if st.session_state.show_feedback and st.session_state.generated_post:
        st.markdown("---")
        st.markdown("### 🎯 Provide Feedback to Improve AI Learning")
        
        feedback_col1, feedback_col2 = st.columns([2, 1])
        
        with feedback_col1:
            st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
            
            # Feedback type selection
            feedback_type = st.radio(
                "How was this post?",
                ["👍 Great! Perfect style", "👎 Not quite right", "🔄 Good but needs refinement"],
                key="feedback_type"
            )
            
            # Feedback text input
            feedback_text = st.text_area(
                "Specific feedback (help AI learn your preferences):",
                placeholder="e.g., 'Too formal, make it more casual', 'Perfect vulnerability!', 'Add more emotion', 'Too long, make it shorter'...",
                height=100,
                key="feedback_text"
            )
            
            # Refinement request
            refinement_requested = False
            refined_post = ""
            
            if feedback_type == "🔄 Good but needs refinement":
                refinement_instruction = st.text_area(
                    "What specific changes would you like?",
                    placeholder="e.g., 'Make it more vulnerable', 'Add a call to action', 'Shorter sentences', 'More personal'...",
                    height=80,
                    key="refinement_instruction"
                )
                
                if st.button("✨ Generate Refined Version", type="secondary"):
                    if refinement_instruction.strip():
                        with st.spinner("🔄 Refining post based on your feedback..."):
                            refined_post = feedback_generator.refine_post(
                                st.session_state.selected_profile,
                                st.session_state.generated_post,
                                refinement_instruction,
                                st.session_state.last_context
                            )
                            
                            if refined_post:
                                st.markdown("#### ✨ Refined Post:")
                                st.text_area(
                                    "Refined version:",
                                    value=refined_post,
                                    height=200,
                                    key="refined_post_display"
                                )
                                refinement_requested = True
            
            # Submit feedback button
            if st.button("💾 Submit Feedback & Learn", type="primary"):
                if feedback_text.strip():
                    # Determine feedback type
                    if feedback_type.startswith("👍"):
                        fb_type = "positive"
                    elif feedback_type.startswith("👎"):
                        fb_type = "negative"
                    else:
                        fb_type = "refinement"
                    
                    # Create feedback entry
                    feedback_entry = create_feedback_entry(
                        profile_name=st.session_state.selected_profile,
                        context=st.session_state.last_context,
                        instruction=st.session_state.last_instruction,
                        generated_post=st.session_state.generated_post,
                        feedback_type=fb_type,
                        feedback_text=feedback_text,
                        refinement_instruction=refinement_instruction if 'refinement_instruction' in locals() else "",
                        approved_version=refined_post if refined_post else ""
                    )
                    
                    # Store feedback
                    if feedback_store.store_feedback(feedback_entry):
                        st.markdown('<div class="success-box">✅ Feedback saved! AI will learn from this for future posts.</div>', unsafe_allow_html=True)
                        
                        # Clear cache to reload feedback
                        st.cache_resource.clear()
                        
                        # Ask if user wants to regenerate with the new feedback
                        st.markdown("### 🔄 Want to see the improvement?")
                        
                        col_regen1, col_regen2 = st.columns(2)
                        with col_regen1:
                            if st.button("🚀 Regenerate with New Learning", type="primary", use_container_width=True):
                                with st.spinner("🤖 Regenerating post with your feedback applied..."):
                                    # Load and index examples for selected profile
                                    vectorstore = load_and_index_examples(st.session_state.selected_profile)
                                    
                                    if vectorstore is not None:
                                        # Retrieve style examples
                                        style_examples = retrieve_style_examples(vectorstore, st.session_state.last_context)
                                        
                                        if style_examples:
                                            # Format examples for the prompt
                                            formatted_examples = "\n\n".join([f"Example {i+1}:\n{example}" for i, example in enumerate(style_examples)])
                                            
                                            # Generate new post using feedback-enhanced generator with updated learning
                                            regenerated_post = feedback_generator.generate_with_feedback(
                                                st.session_state.selected_profile,
                                                st.session_state.last_context,
                                                st.session_state.last_instruction,
                                                formatted_examples
                                            )
                                            
                                            if regenerated_post:
                                                st.session_state.generated_post = regenerated_post
                                                st.success("✅ Post regenerated with your feedback applied!")
                                                st.markdown('<div class="success-box">🎯 Compare this version with the previous one to see how the AI learned from your feedback!</div>', unsafe_allow_html=True)
                                                # Reset feedback form
                                                st.session_state.show_feedback = False
                                                st.rerun()
                        
                        with col_regen2:
                            if st.button("👍 Keep Current Post", use_container_width=True):
                                # Reset feedback form
                                st.session_state.show_feedback = False
                                st.rerun()
                    else:
                        st.markdown('<div class="error-box">❌ Error saving feedback. Please try again.</div>', unsafe_allow_html=True)
                else:
                    st.warning("Please provide specific feedback to help the AI learn!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with feedback_col2:
            st.markdown("#### 💡 Feedback Tips")
            st.markdown("""
            **Positive Feedback:**
            - "Perfect tone!"
            - "Exactly my style"
            - "Great vulnerability"
            
            **Negative Feedback:**
            - "Too corporate"
            - "Not personal enough"
            - "Wrong tone"
            
            **Refinement Requests:**
            - "Add more emotion"
            - "Make it shorter"
            - "More casual language"
            - "Include a question"
            """)
    
    # Clear button
    if st.session_state.generated_post:
        if st.button("🔄 Clear & Start Over", use_container_width=True):
            st.session_state.generated_post = ""
            st.session_state.show_feedback = False
            st.session_state.last_context = ""
            st.session_state.last_instruction = ""
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        🧠 Built with LangChain Memory & Learning | 
        Built with ❤️ using Streamlit, LangChain, and Ollama | 
        <a href="https://ollama.ai" target="_blank">Get Ollama</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 