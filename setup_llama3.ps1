#!/usr/bin/env pwsh
# Setup script for Ghostwriter - ensures Llama3:8B model is available

Write-Host "🚀 Setting up Ghostwriter with Llama3:8B..." -ForegroundColor Green

# Check if Ollama is installed
try {
    $ollamaVersion = ollama --version
    Write-Host "✅ Ollama is installed: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama is not installed or not in PATH" -ForegroundColor Red
    Write-Host "📥 Please install Ollama from: https://ollama.ai" -ForegroundColor Yellow
    exit 1
}

# Check if llama3:8b model is available
Write-Host "🔍 Checking for Llama3:8B model..." -ForegroundColor Blue
$models = ollama list
if ($models -match "llama3:8b") {
    Write-Host "✅ Llama3:8B model is already installed" -ForegroundColor Green
} else {
    Write-Host "📥 Downloading Llama3:8B model (this may take a while)..." -ForegroundColor Yellow
    ollama pull llama3:8b
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Llama3:8B model installed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install Llama3:8B model" -ForegroundColor Red
        exit 1
    }
}

Write-Host "🎉 Setup complete! You can now run Ghostwriter." -ForegroundColor Green
Write-Host "📝 Start the Streamlit app: streamlit run app.py" -ForegroundColor Cyan
Write-Host "🚀 Start the FastAPI backend: uvicorn api:app --reload" -ForegroundColor Cyan
Write-Host "⚛️  Start the React frontend: cd project && npm run dev" -ForegroundColor Cyan 