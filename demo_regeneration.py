#!/usr/bin/env python3
"""
Interactive demo of the Ghostwriter feedback and regeneration system.
Run this to see how the AI learns and improves from feedback!
"""

import time
import sys

def print_slow(text, delay=0.03):
    """Print text with a typewriter effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def demo_workflow():
    """Interactive demo of the complete feedback and regeneration workflow"""
    
    print("🎬 " + "="*60)
    print_slow("   🧠 GHOSTWRITER FEEDBACK & REGENERATION DEMO")
    print("🎬 " + "="*60)
    
    print_slow("\n🎯 This demo shows how Ghostwriter learns from your feedback")
    print_slow("   and immediately improves with each interaction!\n")
    
    # Step 1: Initial generation
    print_slow("📝 STEP 1: Generate Initial Post")
    print_slow("   Context: 'I failed my coding interview but learned something'")
    print_slow("   Instruction: 'Make it vulnerable but hopeful'\n")
    
    input("Press Enter to generate the initial post...")
    
    print_slow("\n🤖 AI Generated (no prior learning):")
    print("─" * 50)
    original_post = """today i failed my interview.

but i learned something important.

failure teaches what success cannot."""
    
    print_slow(original_post)
    print("─" * 50)
    
    # Step 2: Feedback submission
    print_slow("\n💭 STEP 2: User Provides Feedback")
    print_slow("   Feedback Type: 👎 Negative")
    print_slow("   Comment: 'Too short and simple. Needs more emotion and personal details.'")
    
    input("\nPress Enter to submit feedback and learn...")
    
    print_slow("\n✅ Feedback stored! AI is learning...")
    print_slow("   📊 Vector embeddings created")
    print_slow("   🧠 Pattern recognition updated")
    print_slow("   💾 Learning data saved\n")
    
    # Step 3: Regeneration prompt
    print_slow("🔄 STEP 3: Regeneration Prompt")
    print_slow("   System: 'Would you like to regenerate the post using your new feedback?'")
    
    regenerate = input("\n   Your choice (y/n): ").lower().strip()
    
    if regenerate == 'y' or regenerate == 'yes' or regenerate == '':
        
        print_slow("\n🚀 Regenerating with feedback applied...")
        print_slow("   🔍 Retrieving relevant feedback patterns")
        print_slow("   🧠 Applying learned preferences")
        print_slow("   ✨ Generating improved version\n")
        
        input("Press Enter to see the regenerated post...")
        
        print_slow("\n🎯 AI Generated (with feedback learning):")
        print("─" * 50)
        improved_post = """today my coding interview didn't go as planned.

i stumbled through the algorithms, froze during the system design, and watched my confidence crumble in real time.

the rejection email came two days later.

but here's what failure taught me that success never could:
- preparation isn't just about knowing the answers
- vulnerability in admitting gaps shows growth mindset  
- every "no" is redirecting me toward the right "yes"

failure stings. but it also teaches. and sometimes, the lesson is worth more than the job.

keep building, even when it hurts."""
        
        print_slow(improved_post)
        print("─" * 50)
        
        # Step 4: Comparison
        print_slow("\n📊 STEP 4: Improvement Analysis")
        print_slow(f"   Original length: {len(original_post)} characters")
        print_slow(f"   Improved length: {len(improved_post)} characters")
        print_slow("   ✨ Improvements applied:")
        print_slow("     • More emotional depth and vulnerability")
        print_slow("     • Personal details about the experience")
        print_slow("     • Structured insights and lessons")
        print_slow("     • Authentic voice with raw emotion")
        print_slow("     • Motivational ending with hope\n")
        
        # Step 5: Positive feedback
        print_slow("💚 STEP 5: Positive Feedback on Improvement")
        print_slow("   User: 'Perfect! Much better emotion and vulnerability.'")
        print_slow("   System: Storing positive feedback for reinforcement...\n")
        
        input("Press Enter to submit positive feedback...")
        
        print_slow("✅ Positive feedback stored!")
        print_slow("   🎯 AI now knows this style works for you")
        print_slow("   📈 Learning score improved")
        print_slow("   🔮 Future posts will use this pattern\n")
        
    else:
        print_slow("\n👍 Keeping original post - no regeneration.")
        print_slow("   Feedback still stored for future learning!\n")
    
    # Final summary
    print_slow("🎉 DEMO COMPLETE!")
    print("═" * 60)
    print_slow("🔄 Complete Feedback Loop Demonstrated:")
    print_slow("   1. ✅ Generated initial post")
    print_slow("   2. ✅ Received specific feedback")
    print_slow("   3. ✅ Stored learning patterns")
    if regenerate in ['y', 'yes', '']:
        print_slow("   4. ✅ Regenerated with feedback applied")
        print_slow("   5. ✅ Showed immediate improvement")
        print_slow("   6. ✅ Reinforced successful patterns")
    else:
        print_slow("   4. ✅ Stored feedback for future use")
    
    print_slow("\n🚀 How to use this in real applications:")
    print_slow("   • Streamlit: streamlit run app.py")
    print_slow("   • React: cd project && npm run dev")
    print_slow("   • API: python -m uvicorn api:app --reload\n")
    
    print_slow("💡 The AI gets smarter with every interaction!")
    print_slow("   Give feedback → Get immediate improvements → Build your perfect voice\n")

def interactive_menu():
    """Show interactive menu for different demos"""
    
    while True:
        print("\n" + "="*60)
        print("🎮 GHOSTWRITER INTERACTIVE DEMO MENU")
        print("="*60)
        print("1. 🔄 Full Feedback & Regeneration Demo")
        print("2. 📊 Learning Progress Explanation")
        print("3. 💡 Best Practices Guide")
        print("4. 🚀 Quick Start Instructions")
        print("5. ❌ Exit")
        
        choice = input("\nSelect an option (1-5): ").strip()
        
        if choice == '1':
            demo_workflow()
        elif choice == '2':
            show_learning_explanation()
        elif choice == '3':
            show_best_practices()
        elif choice == '4':
            show_quick_start()
        elif choice == '5':
            print_slow("\n👋 Thanks for exploring Ghostwriter!")
            print_slow("Happy writing! 🚀")
            break
        else:
            print("❌ Invalid option. Please choose 1-5.")

def show_learning_explanation():
    """Explain how the learning system works"""
    print("\n📚 HOW GHOSTWRITER LEARNS")
    print("─" * 40)
    print_slow("🧠 Memory System:")
    print_slow("   • Each feedback is stored with vector embeddings")
    print_slow("   • Similar contexts retrieve relevant past feedback")
    print_slow("   • Profile-specific learning prevents cross-contamination")
    print_slow("   • Persistent storage across all sessions")
    
    print_slow("\n🎯 Feedback Types:")
    print_slow("   👍 Positive: Reinforces successful patterns")
    print_slow("   👎 Negative: Avoids unsuccessful approaches") 
    print_slow("   🔄 Refinement: Guides specific improvements")
    
    print_slow("\n📈 Learning Progression:")
    print_slow("   • Initial posts: Generic AI style")
    print_slow("   • After 5+ feedbacks: Noticeable style adaptation")
    print_slow("   • After 20+ feedbacks: Consistently authentic voice")
    print_slow("   • After 50+ feedbacks: Near-perfect style matching")

def show_best_practices():
    """Show best practices for effective feedback"""
    print("\n💡 FEEDBACK BEST PRACTICES")
    print("─" * 40)
    print_slow("✅ Effective Feedback:")
    print_slow("   • Be specific: 'Too formal' → 'Use casual language like \"gonna\"'")
    print_slow("   • Focus on style: Tone, emotion, structure, voice")
    print_slow("   • Provide examples: 'More like: today was rough...'")
    print_slow("   • Give context: Why something works/doesn't work")
    
    print_slow("\n🎯 Refinement Requests:")
    print_slow("   • Single focus: One improvement per request")
    print_slow("   • Clear direction: 'Add more emotion' vs 'make it better'")
    print_slow("   • Style-focused: Voice changes, not content changes")
    print_slow("   • Iterative: Multiple small refinements work better")
    
    print_slow("\n🔄 Building Learning:")
    print_slow("   • Consistent feedback: Regular interactions improve learning")
    print_slow("   • Diverse contexts: Train on various post types")
    print_slow("   • Balanced feedback: Mix positive and constructive")
    print_slow("   • Pattern awareness: Notice and reinforce what works")

def show_quick_start():
    """Show quick start instructions"""
    print("\n🚀 QUICK START GUIDE")
    print("─" * 40)
    print_slow("1. Start the system:")
    print_slow("   streamlit run app.py")
    print_slow("   # OR")
    print_slow("   cd project && npm run dev")
    print_slow("   # OR")
    print_slow("   python -m uvicorn api:app --reload")
    
    print_slow("\n2. Generate your first post:")
    print_slow("   • Enter context: What happened to you")
    print_slow("   • Add instructions: Tone, style preferences")
    print_slow("   • Click Generate")
    
    print_slow("\n3. Provide feedback:")
    print_slow("   • Choose: 👍 Positive, 👎 Negative, or 🔄 Refinement")
    print_slow("   • Write specific feedback")
    print_slow("   • Submit feedback")
    
    print_slow("\n4. See immediate improvement:")
    print_slow("   • Choose to regenerate when prompted")
    print_slow("   • Compare before/after versions")
    print_slow("   • Give feedback on the improvement")
    
    print_slow("\n5. Build your voice:")
    print_slow("   • Repeat the process with different contexts")
    print_slow("   • Watch the AI learn your authentic style")
    print_slow("   • Enjoy increasingly accurate posts!")

if __name__ == "__main__":
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print_slow("\n\n⏹️ Demo interrupted by user")
        print_slow("👋 Thanks for exploring Ghostwriter!") 