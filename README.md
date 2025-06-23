# 🤖 Ghostwriter - AI LinkedIn Post Generator

**Ghostwriter** is an AI-powered application that learns your authentic writing style and generates personalized LinkedIn posts. Built with React, FastAPI, and Ollama's Llama3:8B model - everything runs locally for complete privacy.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)

## ✨ What It Does

- **🎯 Learns Your Voice**: Analyzes your writing samples to match your authentic style
- **🧠 Gets Smarter**: Improves with feedback - give thumbs up/down and watch it learn
- **🔒 Completely Private**: Runs locally using Ollama - your data never leaves your machine
- **⚡ Fast & Modern**: React UI with real-time feedback and instant regeneration

## 🚀 Quick Start

### 1. Install Ollama & Model
```bash
# Install Ollama from https://ollama.ai
# Then download the model:
ollama pull llama3:8b
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
cd project && npm install
```

### 3. Start the Application
```bash
# Start API server
python start_app.py

# In a new terminal, start React frontend
cd project
npm run dev
```

### 4. Open in Browser
- **React UI**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

## 🎯 How to Use

1. **Select a voice profile** (or create a new one with your writing samples)
2. **Enter context** - describe what you want to write about
3. **Generate post** - AI creates content in your style
4. **Give feedback** - help the AI learn your preferences
5. **Regenerate** - see immediate improvements from your feedback

## 📁 What You Need

- **Python 3.8+**
- **Node.js 16+** 
- **Ollama** with llama3:8b model
- **4GB+ RAM** (for the AI model)

## 💡 Key Features

- **Voice Profiles**: Create multiple writing personas
- **Learning System**: AI improves with every piece of feedback
- **Real-time Regeneration**: Instantly see improvements
- **Vector Memory**: Stores feedback patterns for smart learning
- **Local Privacy**: Everything runs on your machine

---

**Ready to start writing?** 🚀

```bash
python start_app.py
```

For detailed documentation, performance optimizations, and advanced features, see [DETAILED_DOCS.md](DETAILED_DOCS.md). 