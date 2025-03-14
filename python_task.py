# -*- coding: utf-8 -*-
"""Python_Task.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18mPQQpQJmlFc-xc9U-qgS20IrxuAEOJR
"""

!pip install PyMuPDF

!pip install pymupdf transformers torch spacy
!python -m spacy download en_core_web_sm

import fitz  # PyMuPDF for PDF text extraction
import re
import spacy
import pandas as pd
from collections import defaultdict
from transformers import pipeline
from IPython.display import display
from google.colab import files

# Load the SpaCy NLP model
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])
    return text

def clean_text(text):
    """Clean extracted text by removing extra whitespace and newlines."""
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_key_sections(text):
    """Extracts key financial insights using broader regex patterns."""
    sections = defaultdict(str)

    # Debug: Print the first 1000 characters to check if the text is extracted correctly
    print("\n===== DEBUG: First 1000 characters of Extracted Text =====\n")
    print(text[:1000])
    print("\n==========================================================\n")

    patterns = {
        "Growth Prospects": r"(?i)(growth prospects|future outlook|expansion strategy).*?(?=\n[A-Z]|\Z)",
        "Key Triggers": r"(?i)(key triggers|catalysts|drivers of growth).*?(?=\n[A-Z]|\Z)",
        "Business Changes": r"(?i)(business changes|strategic shifts|operational changes).*?(?=\n[A-Z]|\Z)",
        "Material Effects": r"(?i)(material effects|earnings impact|risks and uncertainties).*?(?=\n[A-Z]|\Z)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL)
        if match:
            sections[key] = match.group(0)  # Capture the full matched text
        else:
            # If no match, fallback to a larger portion of the text
            sections[key] = text[:3000]  # Extract the first 3000 characters for context

    return sections

def summarize_text(section_text):
    """Summarizes extracted sections using Hugging Face's BART model."""
    if section_text.startswith("No relevant information found."):
        return section_text

    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(section_text, max_length=400, min_length=200, do_sample=False)[0]['summary_text']
    return summary

def main(pdf_path):
    """Main function to process PDF and extract insights."""
    print("Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)

    if not text:
        print("Error: No text extracted. Please check the file.")
        return

    print("Cleaning text...")
    cleaned_text = clean_text(text)

    print("Extracting key sections...")
    key_sections = extract_key_sections(cleaned_text)

    print("Summarizing extracted information...")
    insights = {key: summarize_text(key_sections[key]) for key in key_sections}

    # Create a DataFrame for tabular display
    df = pd.DataFrame(list(insights.items()), columns=["Section", "Summary"])

    # Display the table in Colab
    print("\n===== Extracted Key Investor Information =====\n")
    display(df)  # Google Colab-friendly display

    # Save the table as a CSV file (Optional)
    df.to_csv("/content/extracted_info.csv", index=False)
    print("\n✅ Extracted insights saved as 'extracted_info.csv' in /content/")

# Upload PDF manually in Google Colab before running the script
uploaded = files.upload()  # Prompts user to upload a PDF
pdf_file = list(uploaded.keys())[0]  # Get the uploaded file name
main(f"/content/{pdf_file}")  # Run the main function with uploaded file path