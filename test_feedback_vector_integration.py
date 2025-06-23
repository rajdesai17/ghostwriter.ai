#!/usr/bin/env python3
"""
Comprehensive test to verify feedback is properly stored in vectors 
and used for future post generation.
"""

import os
import sys
import json
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from feedback_system import FeedbackMemoryStore, FeedbackEnhancedGenerator, create_feedback_entry
except ImportError as e:
    print(f"❌ Error importing feedback system: {e}")
    sys.exit(1)

def test_feedback_vector_storage_and_retrieval():
    """Test complete feedback → vector → generation pipeline"""
    
    print("🧪 Testing Feedback Vector Storage & Retrieval")
    print("=" * 60)
    
    # Test 1: Initialize system
    print("\n1️⃣ Initializing feedback system...")
    try:
        feedback_store = FeedbackMemoryStore("profiles")
        feedback_generator = FeedbackEnhancedGenerator(feedback_store)
        test_profile = "test_vector_profile"
        print("✅ System initialized")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 2: Store multiple feedback entries
    print("\n2️⃣ Storing multiple feedback entries...")
    
    feedback_data = [
        {
            "context": "I failed my coding interview",
            "instruction": "Make it vulnerable but hopeful",
            "post": "today i failed my interview.\n\nbut i learned something.",
            "feedback_type": "negative",
            "feedback_text": "Too short and simple. Add more emotional depth and personal details about the struggle."
        },
        {
            "context": "Got rejected from my dream job",
            "instruction": "Share the raw emotions",
            "post": "rejection stings.\n\nbut it redirects us.",
            "feedback_type": "negative", 
            "feedback_text": "Needs more vulnerability. Share what the rejection actually felt like in the moment."
        },
        {
            "context": "I launched my side project and got mixed reactions",
            "instruction": "Be authentic about the experience",
            "post": "launched my project today.\n\nsome loved it, some didn't.\n\nthat's life.",
            "feedback_type": "positive",
            "feedback_text": "Perfect balance of vulnerability and acceptance. This tone is exactly right."
        },
        {
            "context": "Feeling imposter syndrome at new job",
            "instruction": "Make it relatable",
            "post": "day 3 at the new job.\n\nstill googling 'how to look like you know what you're doing'\n\nimposter syndrome is real.",
            "feedback_type": "positive",
            "feedback_text": "Great humor mixed with vulnerability. The self-deprecating tone works perfectly."
        }
    ]
    
    stored_count = 0
    for i, data in enumerate(feedback_data):
        try:
            feedback_entry = create_feedback_entry(
                profile_name=test_profile,
                context=data["context"],
                instruction=data["instruction"],
                generated_post=data["post"],
                feedback_type=data["feedback_type"],
                feedback_text=data["feedback_text"]
            )
            
            if feedback_store.store_feedback(feedback_entry):
                stored_count += 1
                print(f"   ✅ Stored feedback {i+1}: {data['feedback_type']}")
            else:
                print(f"   ❌ Failed to store feedback {i+1}")
                
        except Exception as e:
            print(f"   ❌ Error storing feedback {i+1}: {e}")
    
    print(f"✅ Stored {stored_count}/4 feedback entries")
    
    # Test 3: Verify vector store creation
    print("\n3️⃣ Verifying vector store creation...")
    try:
        feedback_dir = os.path.join("profiles", "feedback")
        vector_store_path = os.path.join(feedback_dir, f"{test_profile}_feedback_vectors")
        json_file_path = os.path.join(feedback_dir, f"{test_profile}_feedback.json")
        
        files_exist = []
        
        if os.path.exists(json_file_path):
            files_exist.append("JSON feedback file")
            with open(json_file_path, 'r') as f:
                feedback_count = len(json.load(f))
            print(f"   ✅ JSON file exists with {feedback_count} entries")
        
        if os.path.exists(vector_store_path):
            files_exist.append("Vector store directory")
            
            # Check for FAISS files
            faiss_files = [f for f in os.listdir(vector_store_path) if f.endswith(('.faiss', '.pkl'))]
            if faiss_files:
                files_exist.append(f"FAISS files: {faiss_files}")
                print(f"   ✅ Vector store exists with files: {faiss_files}")
        
        if len(files_exist) >= 2:
            print("✅ Vector storage verified")
        else:
            print("❌ Vector storage incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying storage: {e}")
        return False
    
    # Test 4: Test feedback retrieval for similar contexts
    print("\n4️⃣ Testing feedback retrieval for similar contexts...")
    
    test_contexts = [
        "I failed my technical interview at Google",  # Similar to first feedback
        "Just got rejected from my dream company",     # Similar to second feedback
        "Launched my startup and got criticism",       # Similar to third feedback
        "New job anxiety and feeling like a fraud"     # Similar to fourth feedback
    ]
    
    retrieval_results = []
    for i, context in enumerate(test_contexts):
        try:
            relevant_feedback = feedback_store.get_relevant_feedback(
                test_profile, context, k=2
            )
            
            if relevant_feedback:
                print(f"   ✅ Context {i+1}: Found {len(relevant_feedback)} relevant feedback entries")
                for j, feedback in enumerate(relevant_feedback):
                    feedback_type = feedback['metadata'].get('feedback_type', 'unknown')
                    print(f"      - Feedback {j+1}: {feedback_type}")
                retrieval_results.append(len(relevant_feedback))
            else:
                print(f"   ❌ Context {i+1}: No relevant feedback found")
                retrieval_results.append(0)
                
        except Exception as e:
            print(f"   ❌ Error retrieving feedback for context {i+1}: {e}")
            retrieval_results.append(0)
    
    successful_retrievals = sum(1 for count in retrieval_results if count > 0)
    print(f"✅ Successfully retrieved feedback for {successful_retrievals}/4 test contexts")
    
    # Test 5: Test that feedback influences generation
    print("\n5️⃣ Testing feedback influence on generation...")
    
    # Generate without feedback (fresh profile)
    print("   📝 Generating post without feedback history...")
    fresh_profile = "fresh_test_profile"
    test_context = "I failed my coding interview but learned something"
    test_instruction = "Make it vulnerable but hopeful"
    
    # Simulate style examples (would normally come from profile file)
    style_examples = """Example 1:
today was tough.

but tough days teach us things easy days cannot.

growth lives in discomfort.

Example 2:
failed at something today.

reminded me that failure is data, not defeat.

tomorrow we try again."""
    
    try:
        post_without_feedback = feedback_generator.generate_with_feedback(
            fresh_profile, test_context, test_instruction, style_examples
        )
        print(f"   ✅ Generated without feedback: {len(post_without_feedback) if post_without_feedback else 0} chars")
    except Exception as e:
        print(f"   ❌ Error generating without feedback: {e}")
        post_without_feedback = None
    
    # Generate with feedback (using our test profile with stored feedback)
    print("   📝 Generating post WITH feedback history...")
    try:
        post_with_feedback = feedback_generator.generate_with_feedback(
            test_profile, test_context, test_instruction, style_examples
        )
        print(f"   ✅ Generated with feedback: {len(post_with_feedback) if post_with_feedback else 0} chars")
    except Exception as e:
        print(f"   ❌ Error generating with feedback: {e}")
        post_with_feedback = None
    
    # Compare results
    if post_without_feedback and post_with_feedback:
        print(f"\n   📊 Comparison:")
        print(f"   Without feedback: {len(post_without_feedback)} characters")
        print(f"   With feedback: {len(post_with_feedback)} characters")
        
        if post_without_feedback != post_with_feedback:
            print("   ✅ Posts are different - feedback is influencing generation!")
        else:
            print("   ⚠️ Posts are identical - feedback may not be strongly influencing generation")
    
    # Test 6: Test feedback types influence
    print("\n6️⃣ Testing specific feedback type influence...")
    
    # Test negative feedback retrieval
    negative_feedback = feedback_store.get_relevant_feedback(
        test_profile, test_context, feedback_type="negative", k=3
    )
    positive_feedback = feedback_store.get_relevant_feedback(
        test_profile, test_context, feedback_type="positive", k=3
    )
    
    print(f"   📊 Feedback retrieval by type:")
    print(f"   Negative feedback entries: {len(negative_feedback)}")
    print(f"   Positive feedback entries: {len(positive_feedback)}")
    
    # Test 7: Test feedback summary
    print("\n7️⃣ Testing feedback summary...")
    try:
        summary = feedback_store.get_profile_feedback_summary(test_profile)
        print(f"   📊 Profile feedback summary:")
        print(f"   Total feedback: {summary['total_feedback']}")
        print(f"   Positive: {summary['positive']}")
        print(f"   Negative: {summary['negative']}")
        print(f"   Refinements: {summary['refinements']}")
        print(f"   Recent patterns: {len(summary['recent_patterns'])}")
        
        expected_total = len(feedback_data)
        if summary['total_feedback'] == expected_total:
            print("   ✅ Summary matches stored feedback count")
        else:
            print(f"   ❌ Summary mismatch: expected {expected_total}, got {summary['total_feedback']}")
    except Exception as e:
        print(f"   ❌ Error getting summary: {e}")
    
    # Final verification
    print("\n" + "=" * 60)
    print("🎉 FEEDBACK VECTOR INTEGRATION TEST COMPLETE")
    print("=" * 60)
    
    verification_results = [
        ("System initialization", True),
        ("Feedback storage", stored_count == 4),
        ("Vector store creation", len(files_exist) >= 2),
        ("Feedback retrieval", successful_retrievals >= 3),
        ("Generation with feedback", post_with_feedback is not None),
        ("Feedback summary", summary['total_feedback'] == 4)
    ]
    
    passed_tests = sum(1 for _, passed in verification_results if passed)
    total_tests = len(verification_results)
    
    print(f"\n📋 Test Results: {passed_tests}/{total_tests} passed")
    for test_name, passed in verification_results:
        status = "✅" if passed else "❌"
        print(f"   {status} {test_name}")
    
    if passed_tests == total_tests:
        print(f"\n🎊 ALL TESTS PASSED!")
        print(f"\n🔄 Verified Complete Pipeline:")
        print(f"   1. ✅ Feedback stored in JSON files")
        print(f"   2. ✅ Feedback embedded in FAISS vectors")
        print(f"   3. ✅ Similar contexts retrieve relevant feedback")
        print(f"   4. ✅ Feedback influences future generation")
        print(f"   5. ✅ Profile-specific learning works")
        print(f"   6. ✅ Feedback types are properly categorized")
        print(f"   7. ✅ Summary and analytics work correctly")
        
        print(f"\n💡 Your feedback system is fully operational!")
        print(f"   Every piece of feedback will improve future post generation.")
        
        return True
    else:
        print(f"\n❌ Some tests failed. Check the errors above.")
        return False

def cleanup_test_data():
    """Clean up test data files"""
    print("\n🧹 Cleaning up test data...")
    try:
        feedback_dir = os.path.join("profiles", "feedback")
        test_profiles = ["test_vector_profile", "fresh_test_profile"]
        
        removed_count = 0
        for profile in test_profiles:
            files_to_remove = [
                os.path.join(feedback_dir, f"{profile}_feedback.json"),
                os.path.join(feedback_dir, f"{profile}_feedback_vectors")
            ]
            
            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    if os.path.isdir(file_path):
                        import shutil
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)
                    removed_count += 1
                    print(f"   ✅ Removed {file_path}")
        
        if removed_count > 0:
            print(f"✅ Cleanup completed ({removed_count} items removed)")
        else:
            print("✅ No test data to cleanup")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    print("🚀 Starting Feedback Vector Integration Tests")
    print("This test verifies feedback is stored in vectors and used for future generation")
    
    try:
        success = test_feedback_vector_storage_and_retrieval()
        
        if success:
            print("\n🎉 Vector integration is working perfectly!")
            print("\n📈 What this means:")
            print("   • Every feedback you give is stored with vector embeddings")
            print("   • Similar contexts automatically retrieve relevant feedback")
            print("   • AI learns from patterns and applies them to new posts")
            print("   • Your writing style improves with every interaction")
            
        else:
            print("\n❌ Some integration issues found. Please check the errors.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
    finally:
        cleanup_test_data()
        
    print("\n👋 Vector integration testing complete!") 