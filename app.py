import streamlit as st
from pypdf import PdfReader
import requests

# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(
    page_title="Chat with Your PDF",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Chat with Your PDF")
st.write("Upload a PDF and ask questions about it.")

# -----------------------------
# Extract PDF Text
# -----------------------------
def extract_text(pdf_file):
    reader = PdfReader(pdf_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# -----------------------------
# Split Text
# -----------------------------
def split_text(text, chunk_size=3000):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    return chunks


# -----------------------------
# Ask Ollama
# -----------------------------
def ask_ai(question, context):

    prompt = f"""
You are a helpful PDF assistant.

Answer the question using the PDF content below.

If the answer is not available in the PDF,
say: "I could not find the answer in the PDF."

PDF CONTENT:
{context}

QUESTION:
{question}

ANSWER:
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        if response.status_code == 200:
            return response.json()["response"]

        return "Error communicating with Ollama."

    except requests.exceptions.ConnectionError:
        return """
        ❌ Ollama is not running.

        Open Ollama and make sure it is running.
        Then try again.
        """

    except Exception as e:
        return f"Error: {e}"


# -----------------------------
# Upload PDF
# -----------------------------
pdf_file = st.file_uploader(
    "📄 Upload your PDF",
    type=["pdf"]
)


if pdf_file:

    st.success(
        f"PDF uploaded: {pdf_file.name}"
    )

    with st.spinner("Reading your PDF..."):

        pdf_text = extract_text(pdf_file)

    if not pdf_text.strip():

        st.error(
            "❌ Could not extract text from this PDF."
        )

        st.stop()

    chunks = split_text(pdf_text)

    st.success(
        f"PDF successfully processed! "
        f"{len(chunks)} sections found."
    )

    st.divider()

    # -----------------------------
    # Question Box
    # -----------------------------

    st.subheader("💬 Ask Your PDF")

    question = st.text_input(
        "Enter your question:"
    )

    if question:

        with st.spinner("🤖 Thinking..."):

            # Use the first few relevant sections
            context = "\n\n".join(
                chunks[:5]
            )

            answer = ask_ai(
                question,
                context
            )

        st.subheader("🤖 Answer")

        st.write(answer)

        # -----------------------------
        # PDF Text
        # -----------------------------

        with st.expander("📖 View PDF Text"):

            st.write(pdf_text)

else:

    st.info(
        "👆 Please upload a PDF to start chatting."
    )

    st.markdown("""
    ### How it works

    1. 📄 Upload your PDF
    2. 🔍 The application reads the PDF
    3. 💬 Ask a question
    4. 🤖 AI generates an answer
    """)
