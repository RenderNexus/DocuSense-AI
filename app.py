import streamlit as st

# Page configuration
st.set_page_config(
    page_title="DocuSense AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

import fitz  # PyMuPDF
import spacy
import openai
import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import base64
import json
from datetime import datetime

# Load environment variables
load_dotenv()

from spacy.util import is_package
import subprocess


MODEL_NAME = "en_core_web_sm"

# Download spaCy model if not already installed
if not is_package(MODEL_NAME):
    subprocess.run(["python", "-m", "spacy", "download", MODEL_NAME], check=True)

# Cached spaCy model loader for Streamlit
@st.cache_resource
def load_spacy_model():
    try:
        return spacy.load(MODEL_NAME)
    except OSError:
        st.error(f"spaCy model '{MODEL_NAME}' not found. Please run:\n\npython -m spacy download {MODEL_NAME}")
        return None

# Initialize spaCy
nlp = load_spacy_model()

# Custom CSS for clean UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .mode-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        margin: 1rem 0;
    }
    .mode-card:hover {
        border-color: #1f77b4;
        background-color: #f0f8ff;
    }
    .feedback-section {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    .score-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        color: white;
    }
    .score-excellent { background-color: #28a745; }
    .score-good { background-color: #17a2b8; }
    .score-average { background-color: #ffc107; color: #212529; }
    .score-poor { background-color: #dc3545; }
    
    .metric-card {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 1.5rem;
        overflow: hidden;
        position: relative;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        border-color: #ff6b9d;
    }
    
    .metric-card h4 {
        margin: 0 0 0.5rem 0;
        color: #333333;
        font-weight: 600;
    }
    
    .metric-card p {
        margin: 0;
        color: #666666;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

def get_openai_feedback(text, mode):
    """Get feedback from OpenAI based on the selected mode"""
    
    # Define prompts for different modes
    prompts = {
        "Student Essay": f"""
        Analyze the following student essay and provide comprehensive feedback:
        
        ESSAY:
        {text}
        
        Please provide feedback in the following JSON format:
        {{
            "overall_score": <score out of 100>,
            "grammar_score": <score out of 100>,
            "content_score": <score out of 100>,
            "structure_score": <score out of 100>,
            "grammar_issues": [<list of grammar errors with corrections>],
            "content_feedback": "<detailed feedback on content quality, arguments, and ideas>",
            "structure_feedback": "<feedback on essay structure, flow, and organization>",
            "suggestions": [<list of specific improvement suggestions>],
            "strengths": [<list of essay strengths>],
            "areas_for_improvement": [<list of areas that need work>]
        }}
        """,
        
        "Resume": f"""
        Analyze the following resume and provide professional feedback:
        
        RESUME:
        {text}
        
        Please provide feedback in the following JSON format:
        {{
            "overall_score": <score out of 100>,
            "content_score": <score out of 100>,
            "formatting_score": <score out of 100>,
            "impact_score": <score out of 100>,
            "content_feedback": "<detailed feedback on resume content, skills, and experience>",
            "formatting_feedback": "<feedback on layout, structure, and presentation>",
            "impact_feedback": "<feedback on how compelling and impactful the resume is>",
            "suggestions": [<list of specific improvement suggestions>],
            "strengths": [<list of resume strengths>],
            "areas_for_improvement": [<list of areas that need work>],
            "keywords_missing": [<list of relevant keywords that could be added>]
        }}
        """,
        
        "Invoice": f"""
        Analyze the following invoice document and provide feedback:
        
        INVOICE:
        {text}
        
        Please provide feedback in the following JSON format:
        {{
            "overall_score": <score out of 100>,
            "completeness_score": <score out of 100>,
            "clarity_score": <score out of 100>,
            "professionalism_score": <score out of 100>,
            "completeness_feedback": "<feedback on whether all required invoice elements are present>",
            "clarity_feedback": "<feedback on clarity and readability of the invoice>",
            "professionalism_feedback": "<feedback on professional presentation and formatting>",
            "suggestions": [<list of specific improvement suggestions>],
            "strengths": [<list of invoice strengths>],
            "areas_for_improvement": [<list of areas that need work>],
            "missing_elements": [<list of missing invoice elements>]
        }}
        """
    }
    
    try:
        # Get API key from session state (user input)
        api_key = st.session_state.get('openai_api_key')
        if not api_key:
            st.error("OpenAI API key not found. Please enter your API key in the sidebar.")
            return None
            
        # Create OpenAI client with user's API key
        client = openai.OpenAI(api_key=api_key)
        
        # Use the latest API syntax
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert document analyzer providing detailed, constructive feedback."},
                {"role": "user", "content": prompts[mode]}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        feedback_text = response.choices[0].message.content
        # Try to parse JSON response
        try:
            feedback_json = json.loads(feedback_text)
            return feedback_json
        except json.JSONDecodeError:
            # If JSON parsing fails, return structured text
            return {
                "overall_score": 75,
                "feedback": feedback_text,
                "suggestions": ["Review the document for improvements"],
                "strengths": ["Document submitted for review"],
                "areas_for_improvement": ["See detailed feedback above"]
            }
            
    except Exception as e:
        st.error(f"Error getting OpenAI feedback: {str(e)}")
        return None

def get_score_class(score):
    """Get CSS class for score display"""
    if score >= 90:
        return "score-excellent"
    elif score >= 80:
        return "score-good"
    elif score >= 70:
        return "score-average"
    else:
        return "score-poor"

def create_pdf_report(feedback, mode, original_text):
    """Create a PDF report of the feedback"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("DocuSense AI - Document Analysis Report", title_style))
    story.append(Spacer(1, 20))
    
    # Report details
    story.append(Paragraph(f"<b>Document Type:</b> {mode}", styles['Normal']))
    story.append(Paragraph(f"<b>Analysis Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Overall score
    overall_score = feedback.get('overall_score', 0)
    story.append(Paragraph(f"<b>Overall Score:</b> {overall_score}/100", styles['Heading2']))
    story.append(Spacer(1, 15))
    
    # Detailed scores
    if 'grammar_score' in feedback:
        story.append(Paragraph("<b>Detailed Scores:</b>", styles['Heading3']))
        scores_data = [
            ['Category', 'Score'],
            ['Grammar', f"{feedback.get('grammar_score', 0)}/100"],
            ['Content', f"{feedback.get('content_score', 0)}/100"],
            ['Structure', f"{feedback.get('structure_score', 0)}/100"]
        ]
    elif 'content_score' in feedback:
        story.append(Paragraph("<b>Detailed Scores:</b>", styles['Heading3']))
        scores_data = [
            ['Category', 'Score'],
            ['Content', f"{feedback.get('content_score', 0)}/100"],
            ['Formatting', f"{feedback.get('formatting_score', 0)}/100"],
            ['Impact', f"{feedback.get('impact_score', 0)}/100"]
        ]
    else:
        scores_data = [['Category', 'Score'], ['Overall', f"{overall_score}/100"]]
    
    scores_table = Table(scores_data)
    scores_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(scores_table)
    story.append(Spacer(1, 20))
    
    # Feedback sections
    feedback_sections = [
        ('Content Feedback', 'content_feedback'),
        ('Grammar Feedback', 'grammar_feedback'),
        ('Structure Feedback', 'structure_feedback'),
        ('Formatting Feedback', 'formatting_feedback'),
        ('Impact Feedback', 'impact_feedback'),
        ('Completeness Feedback', 'completeness_feedback'),
        ('Clarity Feedback', 'clarity_feedback'),
        ('Professionalism Feedback', 'professionalism_feedback')
    ]
    
    for section_title, key in feedback_sections:
        if key in feedback and feedback[key]:
            story.append(Paragraph(f"<b>{section_title}:</b>", styles['Heading3']))
            story.append(Paragraph(feedback[key], styles['Normal']))
            story.append(Spacer(1, 15))
    
    # Lists
    for list_title, key in [('Strengths', 'strengths'), ('Areas for Improvement', 'areas_for_improvement'), ('Suggestions', 'suggestions')]:
        if key in feedback and feedback[key]:
            story.append(Paragraph(f"<b>{list_title}:</b>", styles['Heading3']))
            for item in feedback[key]:
                story.append(Paragraph(f"• {item}", styles['Normal']))
            story.append(Spacer(1, 15))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def main():
    # Header
    st.markdown('<h1 class="main-header">📄 DocuSense AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Smart Document Parser & Feedback Tool</p>', unsafe_allow_html=True)
    
    # Sidebar for mode selection
    with st.sidebar:
        st.markdown('<h3 class="sub-header">📋 Document Mode</h3>', unsafe_allow_html=True)
        
        mode = st.selectbox(
            "Select document type:",
            ["Student Essay", "Resume", "Invoice"],
            help="Choose the type of document you're uploading for appropriate analysis"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Analysis Features")
        
        if mode == "Student Essay":
            st.markdown("""
            - **Grammar & Style Check**
            - **Content Quality Assessment**
            - **Structure Analysis**
            - **Writing Suggestions**
            - **Overall Scoring**
            """)
        elif mode == "Resume":
            st.markdown("""
            - **Content Relevance**
            - **Formatting Quality**
            - **Impact Assessment**
            - **Keyword Analysis**
            - **Professional Feedback**
            """)
        else:  # Invoice
            st.markdown("""
            - **Completeness Check**
            - **Clarity Assessment**
            - **Professional Standards**
            - **Missing Elements**
            - **Formatting Review**
            """)
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        
        # OpenAI API Key input
        api_key = st.text_input(
            "🔐 OpenAI API Key",
            help="Enter your OpenAI API key to enable AI-powered analysis. Your key is stored locally and not shared."
        )
        
        if api_key:
            st.session_state.openai_api_key = api_key
            st.success("✅ API key saved!")
        elif 'openai_api_key' in st.session_state:
            st.info("🔑 API key already saved")
        
        st.markdown("---")
        st.markdown("### 🔑 Get Your API Key")
        st.markdown("""
        To use this app, you need your own OpenAI API key:
        
        1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
        2. Sign up or log in
        3. Create a new API key
        4. Copy and paste it above
        
        **Note:** Your API key is stored locally and never shared.
        """)
        
        st.markdown("---")
        st.markdown("### 📖 Instructions")
        st.markdown("""
        1. Enter your OpenAI API key
        2. Select your document type
        3. Upload a PDF file
        4. Click 'Analyze Document'
        5. Review the feedback
        6. Export results as PDF
        """)
    
    # Main content area
    st.markdown('<h2 class="sub-header">📤 Upload Document</h2>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF document for analysis"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Extract text
        with st.spinner("Extracting text from PDF..."):
            extracted_text = extract_text_from_pdf(uploaded_file)
        
        if extracted_text:
            st.markdown('<h3 class="sub-header">📝 Extracted Text Preview</h3>', unsafe_allow_html=True)
            with st.expander("View extracted text", expanded=False):
                st.text_area("Extracted Text", extracted_text, height=200, disabled=True)
            
            # Analysis button
            if st.button("🔍 Analyze Document", type="primary", use_container_width=True):
                if not st.session_state.get('openai_api_key'):
                    st.error("❌ Please enter your OpenAI API key in the sidebar to proceed with analysis.")
                else:
                    with st.spinner("🤖 Analyzing document with AI..."):
                        feedback = get_openai_feedback(extracted_text, mode)
                    
                    if feedback:
                        # Store feedback in session state
                        st.session_state.feedback = feedback
                        st.session_state.extracted_text = extracted_text
                        st.session_state.mode = mode
                        st.success("✅ Analysis complete!")
                        st.rerun()
    
    # Quick Stats Section - Display after analysis
    if 'feedback' in st.session_state:
        st.markdown('<h2 class="sub-header">📊 Quick Stats</h2>', unsafe_allow_html=True)
        
        feedback = st.session_state.feedback
        overall_score = feedback.get('overall_score', 0)
        
        # Create horizontal layout for stats
        if mode == "Student Essay":
            scores = [
                ("Overall", overall_score),
                ("Grammar", feedback.get('grammar_score', 0)),
                ("Content", feedback.get('content_score', 0)),
                ("Structure", feedback.get('structure_score', 0))
            ]
        elif mode == "Resume":
            scores = [
                ("Overall", overall_score),
                ("Content", feedback.get('content_score', 0)),
                ("Formatting", feedback.get('formatting_score', 0)),
                ("Impact", feedback.get('impact_score', 0))
            ]
        else:  # Invoice
            scores = [
                ("Overall", overall_score),
                ("Completeness", feedback.get('completeness_score', 0)),
                ("Clarity", feedback.get('clarity_score', 0)),
                ("Professionalism", feedback.get('professionalism_score', 0))
            ]
        
        # Create columns for horizontal layout
        cols = st.columns(len(scores))
        
        for i, (score_name, score_value) in enumerate(scores):
            with cols[i]:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{score_name}</h4>
                    <div class="score-badge {get_score_class(score_value)}">
                        {score_value}/100
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Display detailed feedback
    if 'feedback' in st.session_state:
        st.markdown('<h2 class="sub-header">📋 Detailed Feedback</h2>', unsafe_allow_html=True)
        
        feedback = st.session_state.feedback
        
        # Create tabs for different feedback sections
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Feedback", "✅ Strengths", "🔧 Improvements", "💡 Suggestions"])
        
        with tab1:
            st.markdown('<h3>Detailed Analysis</h3>', unsafe_allow_html=True)
            
            # Display feedback based on mode
            if mode == "Student Essay":
                if 'content_feedback' in feedback:
                    st.markdown("**Content Feedback:**")
                    st.write(feedback['content_feedback'])
                
                if 'grammar_feedback' in feedback:
                    st.markdown("**Grammar Feedback:**")
                    st.write(feedback['grammar_feedback'])
                
                if 'structure_feedback' in feedback:
                    st.markdown("**Structure Feedback:**")
                    st.write(feedback['structure_feedback'])
                    
            elif mode == "Resume":
                if 'content_feedback' in feedback:
                    st.markdown("**Content Feedback:**")
                    st.write(feedback['content_feedback'])
                
                if 'formatting_feedback' in feedback:
                    st.markdown("**Formatting Feedback:**")
                    st.write(feedback['formatting_feedback'])
                
                if 'impact_feedback' in feedback:
                    st.markdown("**Impact Feedback:**")
                    st.write(feedback['impact_feedback'])
                    
            else:  # Invoice
                if 'completeness_feedback' in feedback:
                    st.markdown("**Completeness Feedback:**")
                    st.write(feedback['completeness_feedback'])
                
                if 'clarity_feedback' in feedback:
                    st.markdown("**Clarity Feedback:**")
                    st.write(feedback['clarity_feedback'])
                
                if 'professionalism_feedback' in feedback:
                    st.markdown("**Professionalism Feedback:**")
                    st.write(feedback['professionalism_feedback'])
        
        with tab2:
            st.markdown('<h3>Document Strengths</h3>', unsafe_allow_html=True)
            if 'strengths' in feedback and feedback['strengths']:
                for i, strength in enumerate(feedback['strengths'], 1):
                    st.markdown(f"**{i}.** {strength}")
            else:
                st.info("No specific strengths identified in this analysis.")
        
        with tab3:
            st.markdown('<h3>Areas for Improvement</h3>', unsafe_allow_html=True)
            if 'areas_for_improvement' in feedback and feedback['areas_for_improvement']:
                for i, area in enumerate(feedback['areas_for_improvement'], 1):
                    st.markdown(f"**{i}.** {area}")
            else:
                st.info("No specific areas for improvement identified.")
        
        with tab4:
            st.markdown('<h3>Suggestions</h3>', unsafe_allow_html=True)
            if 'suggestions' in feedback and feedback['suggestions']:
                for i, suggestion in enumerate(feedback['suggestions'], 1):
                    st.markdown(f"**{i}.** {suggestion}")
            else:
                st.info("No specific suggestions provided in this analysis.")
        
        # Export section
        st.markdown("---")
        st.markdown('<h2 class="sub-header">📄 Export Report</h2>', unsafe_allow_html=True)
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            if st.button("📊 Export PDF Report", use_container_width=True):
                if 'feedback' in st.session_state:
                    with st.spinner("Generating PDF report..."):
                        pdf_buffer = create_pdf_report(
                            st.session_state.feedback,
                            st.session_state.mode,
                            st.session_state.extracted_text
                        )
                    
                    # Create download button
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_buffer.getvalue(),
                        file_name=f"DocuSense_AI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
        
        with col_export2:
            if st.button("🔄 New Analysis", use_container_width=True):
                # Clear session state
                for key in ['feedback', 'extracted_text', 'mode']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

if __name__ == "__main__":
    main() 
    
    
    