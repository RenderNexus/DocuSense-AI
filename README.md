# 📄 DocuSense AI

A smart document parser and feedback tool that analyzes PDF documents using AI-powered insights. DocuSense AI provides comprehensive feedback for student essays, resumes, and invoices with detailed scoring and improvement suggestions.

## ✨ Features

### 🎯 Multi-Document Support
- **Student Essays**: Grammar check, content quality assessment, structure analysis
- **Resumes**: Content relevance, formatting quality, impact assessment, keyword analysis
- **Invoices**: Completeness check, clarity assessment, professional standards review

### 🤖 AI-Powered Analysis
- OpenAI GPT-3.5 Turbo integration for intelligent feedback
- Customized prompts for each document type
- Comprehensive scoring system (0-100 scale)
- Detailed improvement suggestions

### 📊 Rich Feedback System
- Overall and category-specific scores
- Detailed feedback sections
- Strengths identification
- Areas for improvement
- Actionable suggestions

### 📄 Export Capabilities
- PDF report generation with detailed analysis
- Professional formatting with ReportLab
- Downloadable results for offline review

### 🎨 Clean User Interface
- Modern, responsive Streamlit interface
- Intuitive sidebar navigation
- Real-time feedback display
- Tabbed results organization

## 🚀 Quick Start

### For Users (Streamlit Cloud)
1. **Visit the app**: [DocuSense AI on Streamlit Cloud](your-streamlit-url-here)
2. **Get your API key**: [OpenAI Platform](https://platform.openai.com/api-keys)
3. **Start analyzing**: Upload your PDF and get instant feedback!

### For Developers (Local Setup)

#### Prerequisites
- Python 3.8 or higher
- OpenAI API key

#### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DocuSense-AI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install spaCy model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Set up environment variables (Optional)**
   For local development, you can create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   **Note**: For Streamlit Cloud deployment, users will enter their API key directly in the app.

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

The application will open in your default browser at `http://localhost:8501`

### 📖 User Guide
For detailed instructions on how to use the app, check out our **[Quick Start Guide](QUICKSTART.md)**!

## 📖 Usage Guide

### 1. Select Document Type
Choose from three analysis modes:
- **Student Essay**: For academic writing analysis
- **Resume**: For professional resume review
- **Invoice**: For business document assessment

### 2. Upload PDF
- Click "Browse files" to upload your PDF document
- The system will extract text and show a preview
- Supported format: PDF only

### 3. Configure API
- Enter your OpenAI API key in the sidebar
- The key is required for AI-powered analysis
- Your API key is stored locally and never shared
- Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

### 4. Analyze Document
- Click "Analyze Document" to start the AI analysis
- Wait for the processing to complete
- Review the comprehensive feedback

### 5. Export Results
- Generate a PDF report with detailed analysis
- Download the report for offline review
- Start a new analysis when ready

## 🔧 Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **PyMuPDF (fitz)**: PDF text extraction
- **spaCy**: Natural language processing
- **OpenAI**: AI-powered analysis
- **ReportLab**: PDF report generation
- **python-dotenv**: Environment variable management

### Architecture
```
DocuSense AI/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── README.md          # Documentation
└── .env               # Environment variables (create this)
```

### API Integration
The application uses OpenAI's GPT-3.5 Turbo model with custom prompts for each document type:

- **Student Essay**: Focuses on grammar, content quality, and structure
- **Resume**: Emphasizes content relevance, formatting, and impact
- **Invoice**: Checks completeness, clarity, and professional standards

## 🎯 Analysis Features

### Student Essay Analysis
- **Grammar Score**: Spelling, punctuation, and syntax
- **Content Score**: Argument quality, evidence, and ideas
- **Structure Score**: Organization, flow, and coherence
- **Detailed Feedback**: Specific improvement areas

### Resume Analysis
- **Content Score**: Skills, experience, and achievements
- **Formatting Score**: Layout, design, and presentation
- **Impact Score**: Compelling nature and effectiveness
- **Keyword Analysis**: Missing relevant terms

### Invoice Analysis
- **Completeness Score**: Required elements presence
- **Clarity Score**: Readability and understanding
- **Professionalism Score**: Presentation standards
- **Missing Elements**: Identified gaps

## 🚀 Deployment

### ✅ Ready for Production
This app is **production-ready** and can be deployed immediately to Streamlit Cloud!

### Streamlit Cloud Deployment
1. **Push your code to GitHub**
2. **Connect your repository** to [Streamlit Cloud](https://streamlit.io/cloud)
3. **Deploy the app** - No additional configuration needed!
4. **Share the URL** - Users will enter their own OpenAI API keys

### Security Features
- ✅ **No hardcoded API keys** - Each user provides their own
- ✅ **Session-based storage** - API keys stored only in user's browser
- ✅ **No data persistence** - Documents processed in memory only
- ✅ **Privacy compliant** - No user data shared or stored

### Local Deployment
1. Follow the installation instructions above
2. Create a `.env` file with your API key (optional)
3. Run `streamlit run app.py`

## 🔒 Security & Privacy

- **User API Keys**: Each user provides their own OpenAI API key
- **No Shared Keys**: Your API key is never exposed or shared
- **Local Storage**: API keys are stored only in the user's session
- **No Document Storage**: No documents are stored permanently
- **Memory Processing**: All processing is done in memory
- **No Third-Party Sharing**: No data is shared with third parties

## 🛠️ Customization

### Adding New Document Types
1. Add the new type to the mode selection
2. Create a custom prompt in the `get_openai_feedback` function
3. Update the scoring display logic
4. Modify the PDF report generation

### Customizing Prompts
Edit the prompts in the `get_openai_feedback` function to adjust the analysis focus and feedback style.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check the documentation
- Review the troubleshooting section

## 🔄 Updates

Stay updated with the latest features and improvements by:
- Following the repository
- Checking release notes
- Updating dependencies regularly

---

**DocuSense AI** - Making document analysis smarter and more accessible! 📄✨ 