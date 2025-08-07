#!/usr/bin/env python3
"""
Sample PDF Creator for DocuSense AI
Converts sample text files to PDF format for testing the application
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

def create_pdf_from_text(text_file, pdf_file):
    """Convert a text file to PDF format"""
    try:
        # Read the text file
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        
        for para in paragraphs:
            if para.strip():  # Skip empty paragraphs
                # Use different styles for headers and body text
                if para.isupper() and len(para) < 100:  # Likely a header
                    story.append(Paragraph(para, styles['Heading1']))
                elif para.startswith('•') or para.startswith('-'):  # List items
                    story.append(Paragraph(para, styles['Normal']))
                else:  # Regular paragraph
                    story.append(Paragraph(para, styles['Normal']))
                story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        print(f"✅ Created {pdf_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating {pdf_file}: {e}")
        return False

def main():
    """Main function to create sample PDFs"""
    print("📄 Creating sample PDFs for DocuSense AI testing...")
    print("=" * 50)
    
    # Define the sample files to convert
    samples = [
        ("sample_essay.txt", "sample_essay.pdf"),
        ("sample_resume.txt", "sample_resume.pdf"),
        ("sample_invoice.txt", "sample_invoice.pdf")
    ]
    
    success_count = 0
    
    for text_file, pdf_file in samples:
        if os.path.exists(text_file):
            if create_pdf_from_text(text_file, pdf_file):
                success_count += 1
        else:
            print(f"⚠️  {text_file} not found, skipping...")
    
    print("=" * 50)
    print(f"🎉 Created {success_count} sample PDF files!")
    print("\n📋 Sample PDFs created:")
    for _, pdf_file in samples:
        if os.path.exists(pdf_file):
            print(f"   • {pdf_file}")
    
    print("\n💡 You can now use these PDFs to test DocuSense AI:")
    print("   1. Run: streamlit run app.py")
    print("   2. Upload any of the sample PDFs")
    print("   3. Select the appropriate document type")
    print("   4. Enter your OpenAI API key")
    print("   5. Click 'Analyze Document'")

if __name__ == "__main__":
    main() 