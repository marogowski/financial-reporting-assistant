import streamlit as st
import pandas as pd
import PyPDF2
from openai import OpenAI

st.set_page_config(page_title="Financial Reporting Assistant", layout="wide")
st.title("📊 Financial Reporting Assistant (Prototype)")

# OpenAI API Key input
api_key = st.text_input("Enter your OpenAI API key", type="password")

# File uploaders
pdf_file = st.file_uploader("Upload a PDF financial report", type=["pdf"])
excel_file = st.file_uploader("Upload an Excel financial report", type=["xlsx", "xls"])

# Function to extract text from uploaded PDF file
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

# Function to query GPT-4o with financial context
def ask_gpt4o(question, context, api_key):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a financial reporting assistant. Answer based only on the document content."},
            {"role": "user", "content": f"{context}\n\nQuestion: {question}"}
        ]
    )
    return response.choices[0].message.content

# Main logic
if pdf_file or excel_file:
    context = ""

    if pdf_file:
        with st.spinner("Extracting text from PDF..."):
            context += extract_text_from_pdf(pdf_file)

    if excel_file:
        with st.spinner("Reading Excel file..."):
            try:
                excel_data = pd.read_excel(excel_file, sheet_name=None)
                for sheet, df in excel_data.items():
                    context += f"\n\nSheet: {sheet}\n"
                    context += df.to_string(index=False)
            except Exception as e:
                st.error(f"Error reading Excel: {e}")

    if context:
        question = st.text_area("Enter your question about the financials:", height=100)
        if question and api_key:
            with st.spinner("Thinking..."):
                try:
                    answer = ask_gpt4o(question, context, api_key)
                    st.success("Answer:")
                    st.write(answer)
                except Exception as e:
                    st.error(f"OpenAI error: {e}")
        elif question:
            st.warning("Please enter your OpenAI API key to get answers.")
