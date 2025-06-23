#!/usr/bin/env python3
"""
Ghostwriter Application Starter
Runs the API server and instructions for the React frontend.
No more Streamlit - Pure React UI for faster performance!
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_ollama():
    """Check if Ollama is running"""
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            if 'llama3:8b' in result.stdout:
                print("✅ Ollama is running with llama3:8b model")
                return True
            else:
                print("❌ llama3:8b model not found. Please run: ollama pull llama3:8b")
                return False
        else:
            print("❌ Ollama not responding. Please start Ollama service.")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Ollama not found. Please install Ollama from https://ollama.ai")
        return False

def check_node_dependencies():
    """Check if Node.js dependencies are installed"""
    project_dir = Path("project")
    if not project_dir.exists():
        print("❌ React project directory not found")
        return False
    
    node_modules = project_dir / "node_modules"
    if not node_modules.exists():
        print("❌ Node dependencies not installed. Please run: cd project && npm install")
        return False
    
    print("✅ Node.js dependencies are installed")
    return True

def start_api_server():
    """Start the FastAPI server"""
    try:
        print("🚀 Starting FastAPI server on http://localhost:8000...")
        # Start API server in background
        api_process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'api:app', 
            '--host', '0.0.0.0', '--port', '8000', '--reload'
        ])
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Check if server started successfully
        try:
            import requests
            response = requests.get('http://localhost:8000/profiles', timeout=5)
            if response.status_code == 200:
                print("✅ API server started successfully!")
                return api_process
            else:
                print("❌ API server started but not responding correctly")
                return None
        except requests.exceptions.RequestException:
            print("⚠️ API server starting... (this may take a moment)")
            return api_process
            
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def main():
    print("🤖 Ghostwriter - AI LinkedIn Post Generator")
    print("=" * 50)
    print("🎯 Optimized for React-only UI with feedback learning")
    print()
    
    # Check prerequisites
    print("📋 Checking prerequisites...")
    
    if not check_ollama():
        print("\n❌ Ollama setup required. Please:")
        print("   1. Install Ollama: https://ollama.ai")
        print("   2. Run: ollama pull llama3:8b")
        print("   3. Start Ollama service")
        return
    
    if not check_node_dependencies():
        print("\n❌ Node.js setup required. Please:")
        print("   1. cd project")
        print("   2. npm install")
        return
    
    print("\n🚀 Starting Ghostwriter...")
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        print("❌ Failed to start API server")
        return
    
    # Instructions for React frontend
    print("\n📱 React Frontend Setup:")
    print("   1. Open a new terminal")
    print("   2. cd project")
    print("   3. npm run dev")
    print("   4. Open http://localhost:5173")
    
    print("\n🌐 Application URLs:")
    print("   • React UI: http://localhost:5173")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • API Health: http://localhost:8000/profiles")
    
    print("\n💡 Features Available:")
    print("   ✅ Voice profile management")
    print("   ✅ AI post generation with feedback learning")
    print("   ✅ Real-time feedback and regeneration")
    print("   ✅ Vector-based memory storage")
    print("   ✅ Profile-specific learning")
    
    print("\n🎯 Optimizations Applied:")
    print("   ✅ Removed Streamlit dependency")
    print("   ✅ Cached API components for faster response")
    print("   ✅ Lazy loading of AI models")
    print("   ✅ Optimized feedback vector retrieval")
    
    try:
        print("\n⏹️ Press Ctrl+C to stop the API server")
        api_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping API server...")
        api_process.terminate()
        try:
            api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api_process.kill()
        print("✅ API server stopped")

if __name__ == "__main__":
    main() 