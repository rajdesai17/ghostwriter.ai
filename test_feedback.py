#!/usr/bin/env python3
"""
Test script for the Ghostwriter feedback system.
This script tests the core feedback functionality to ensure it's working properly.
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feedback_system import FeedbackMemoryStore, FeedbackEnhancedGenerator, create_feedback_entry

def test_feedback_system():
    """Test the complete feedback system"""
    print("🧪 Testing Ghostwriter Feedback System")
    print("=" * 50)
    
    # Test 1: Initialize feedback store
    print("\n1️⃣ Testing feedback store initialization...")
    try:
        feedback_store = FeedbackMemoryStore("profiles")
        print("✅ Feedback store initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize feedback store: {e}")
        return False
    
    # Test 2: Create a test feedback entry
    print("\n2️⃣ Testing feedback entry creation...")
    try:
        feedback_entry = create_feedback_entry(
            profile_name="test_profile",
            context="I failed a coding interview but learned something",
            instruction="Make it vulnerable but hopeful",
            generated_post="today i failed my interview.\n\nbut i learned something important.\n\nfailure teaches what success cannot.",
            feedback_type="positive",
            feedback_text="Perfect vulnerability and tone! This sounds exactly like me.",
            refinement_instruction="",
            approved_version=""
        )
        print("✅ Feedback entry created successfully")
        print(f"   - Profile: {feedback_entry.profile_name}")
        print(f"   - Type: {feedback_entry.feedback_type}")
        print(f"   - Feedback: {feedback_entry.feedback_text}")
    except Exception as e:
        print(f"❌ Failed to create feedback entry: {e}")
        return False
    
    # Test 3: Store feedback
    print("\n3️⃣ Testing feedback storage...")
    try:
        success = feedback_store.store_feedback(feedback_entry)
        if success:
            print("✅ Feedback stored successfully")
        else:
            print("❌ Failed to store feedback")
            return False
    except Exception as e:
        print(f"❌ Error storing feedback: {e}")
        return False
    
    # Test 4: Retrieve feedback summary
    print("\n4️⃣ Testing feedback summary retrieval...")
    try:
        summary = feedback_store.get_profile_feedback_summary("test_profile")
        print("✅ Feedback summary retrieved successfully")
        print(f"   - Total feedback: {summary['total_feedback']}")
        print(f"   - Positive: {summary['positive']}")
        print(f"   - Negative: {summary['negative']}")
        print(f"   - Refinements: {summary['refinements']}")
    except Exception as e:
        print(f"❌ Error retrieving feedback summary: {e}")
        return False
    
    # Test 5: Add more diverse feedback
    print("\n5️⃣ Testing diverse feedback storage...")
    try:
        # Add negative feedback
        negative_feedback = create_feedback_entry(
            profile_name="test_profile",
            context="I got promoted at work",
            instruction="Make it celebratory",
            generated_post="I'm thrilled to announce my promotion to Senior Developer!",
            feedback_type="negative",
            feedback_text="Too corporate and formal. Not my authentic voice at all.",
        )
        feedback_store.store_feedback(negative_feedback)
        
        # Add refinement feedback
        refinement_feedback = create_feedback_entry(
            profile_name="test_profile",
            context="Launched my side project",
            instruction="Share the journey",
            generated_post="after 6 months of coding nights, my project is live.",
            feedback_type="refinement",
            feedback_text="Good start but needs more emotion",
            refinement_instruction="Add more personal struggle and emotions"
        )
        feedback_store.store_feedback(refinement_feedback)
        
        print("✅ Diverse feedback stored successfully")
    except Exception as e:
        print(f"❌ Error storing diverse feedback: {e}")
        return False
    
    # Test 6: Retrieve relevant feedback
    print("\n6️⃣ Testing relevant feedback retrieval...")
    try:
        relevant_feedback = feedback_store.get_relevant_feedback(
            "test_profile", 
            "I failed at something but learned from it", 
            k=2
        )
        print("✅ Relevant feedback retrieved successfully")
        print(f"   - Found {len(relevant_feedback)} relevant feedback entries")
        for i, feedback in enumerate(relevant_feedback):
            print(f"   - Feedback {i+1}: {feedback['metadata']['feedback_type']}")
    except Exception as e:
        print(f"❌ Error retrieving relevant feedback: {e}")
        return False
    
    # Test 7: Initialize feedback-enhanced generator
    print("\n7️⃣ Testing feedback-enhanced generator...")
    try:
        feedback_generator = FeedbackEnhancedGenerator(feedback_store)
        print("✅ Feedback-enhanced generator initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize feedback generator: {e}")
        return False
    
    # Test 8: Test feedback summary after multiple entries
    print("\n8️⃣ Testing updated feedback summary...")
    try:
        updated_summary = feedback_store.get_profile_feedback_summary("test_profile")
        print("✅ Updated feedback summary retrieved successfully")
        print(f"   - Total feedback: {updated_summary['total_feedback']}")
        print(f"   - Positive: {updated_summary['positive']}")
        print(f"   - Negative: {updated_summary['negative']}")
        print(f"   - Refinements: {updated_summary['refinements']}")
        print(f"   - Recent patterns: {len(updated_summary['recent_patterns'])}")
    except Exception as e:
        print(f"❌ Error retrieving updated feedback summary: {e}")
        return False
    
    # Test 9: Test file persistence
    print("\n9️⃣ Testing file persistence...")
    try:
        feedback_dir = os.path.join("profiles", "feedback")
        feedback_file = os.path.join(feedback_dir, "test_profile_feedback.json")
        
        if os.path.exists(feedback_file):
            with open(feedback_file, 'r', encoding='utf-8') as f:
                stored_data = json.load(f)
            print("✅ Feedback file persistence working")
            print(f"   - File location: {feedback_file}")
            print(f"   - Stored entries: {len(stored_data)}")
        else:
            print("❌ Feedback file not found")
            return False
    except Exception as e:
        print(f"❌ Error checking file persistence: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All feedback system tests passed successfully!")
    print("\n📋 Test Summary:")
    print(f"   ✅ Feedback store initialization")
    print(f"   ✅ Feedback entry creation")
    print(f"   ✅ Feedback storage")
    print(f"   ✅ Summary retrieval")
    print(f"   ✅ Diverse feedback types")
    print(f"   ✅ Relevant feedback search")
    print(f"   ✅ Enhanced generator initialization")
    print(f"   ✅ Updated summaries")
    print(f"   ✅ File persistence")
    
    return True

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    try:
        feedback_dir = os.path.join("profiles", "feedback")
        test_files = [
            os.path.join(feedback_dir, "test_profile_feedback.json"),
            os.path.join(feedback_dir, "test_profile_feedback_vectors.faiss"),
            os.path.join(feedback_dir, "test_profile_feedback_vectors.pkl")
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"   ✅ Removed {file_path}")
        
        print("✅ Test data cleanup completed")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    print("🚀 Starting Ghostwriter Feedback System Tests")
    
    try:
        # Run tests
        success = test_feedback_system()
        
        if success:
            print("\n🎊 All tests completed successfully!")
            print("\n🔥 Your feedback system is ready to learn!")
            print("\n💡 Next steps:")
            print("   1. Start the API: python -m uvicorn api:app --reload")
            print("   2. Start Streamlit: streamlit run app.py")
            print("   3. Or start React frontend: cd project && npm run dev")
            
        else:
            print("\n❌ Some tests failed. Please check the error messages above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        sys.exit(1)
    finally:
        # Always cleanup test data
        cleanup_test_data()
        
    print("\n👋 Thanks for testing the Ghostwriter feedback system!") 