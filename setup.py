#!/usr/bin/env python3
"""
DocuSense AI Setup Script
Automates the installation and setup process for DocuSense AI
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def install_spacy_model():
    """Install spaCy English model"""
    return run_command("python -m spacy download en_core_web_sm", "Installing spaCy English model")

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file...")
    try:
        with open(".env", "w") as f:
            f.write("# OpenAI API Configuration\n")
            f.write("# Get your API key from: https://platform.openai.com/api-keys\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n\n")
            f.write("# Optional: Custom OpenAI Model (default: gpt-3.5-turbo)\n")
            f.write("# OPENAI_MODEL=gpt-4\n\n")
            f.write("# Optional: Custom temperature for AI responses (default: 0.3)\n")
            f.write("# OPENAI_TEMPERATURE=0.3\n\n")
            f.write("# Optional: Custom max tokens for AI responses (default: 2000)\n")
            f.write("# OPENAI_MAX_TOKENS=2000\n")
        print("✅ .env file created successfully")
        print("⚠️  Please edit .env file and add your OpenAI API key")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 DocuSense AI Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Install spaCy model
    if not install_spacy_model():
        print("❌ Setup failed at spaCy model installation")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("❌ Setup failed at .env file creation")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: streamlit run app.py")
    print("3. Open http://localhost:8501 in your browser")
    print("\n📖 For more information, see README.md")

if __name__ == "__main__":
    main() 