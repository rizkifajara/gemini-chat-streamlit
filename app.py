import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Default system prompts
DEFAULT_SYSTEM_PROMPTS = {
    "default": "You are a helpful AI assistant. Provide clear, concise, and accurate responses.",
    "analyst": "You are an analytical AI assistant. Focus on data-driven insights and detailed analysis.",
    "summarizer": "You are a summarization AI. Provide concise summaries while maintaining key information.",
    "comparator": "You are a comparison AI. Focus on identifying similarities and differences between documents.",
    "retrieval": """You are a helpful and factual legal document assistant.

You will be given a **Question** and context retrieved from one or more sources in the **Knowledge Base**.

You must:

- Answer the Question **only using the information provided in the Knowledge Base**.
- When retrieving sections (like BAB III), provide the **complete section** including all subsections (like Pasal 4, 5, 6, etc.) until the next major section.
- If the answer cannot be found on the Knowledge Base or not relevant, answer with "None" only.

Formatting Rules:
- Use **Markdown**.
- Use **numbered lists** for steps.
- Use **bullets (*)** for unordered information.
- Do not add or infer content that is not in the Knowledge Base.
- When presenting sections, maintain the hierarchical structure (BAB, Pasal, ayat, etc.).

Answer only in Bahasa Indonesia."""
}

def setup_gemini_client():
    """Set up the Gemini API client."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("API key not found. Please set the GOOGLE_API_KEY environment variable or add it to your .env file.")
        st.stop()
    return genai.Client(api_key=api_key)

def upload_file(client, uploaded_file):
    """Upload a file to Gemini API."""
    try:
        # Save the uploaded file temporarily
        temp_path = Path(f"temp_{uploaded_file.name}")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Check file size
        file_size = temp_path.stat().st_size
        if file_size > 20 * 1024 * 1024:  # 20MB limit
            st.error(f"File too large. Maximum size is 20MB, got {file_size/1024/1024:.2f}MB")
            temp_path.unlink()
            return None
        
        # Upload the file
        uploaded = client.files.upload(file=temp_path)
        temp_path.unlink()  # Clean up temp file
        return uploaded
    except Exception as e:
        st.error(f"Error uploading file: {str(e)}")
        return None

def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPTS["default"]

def main():
    st.set_page_config(
        page_title="Gemini Chat",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Gemini Chat")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")
        
        # Model selection
        model_name = st.selectbox(
            "Select Model",
            ["gemini-2.5-flash-preview-05-20", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash", "gemini-2.0-pro"],
            index=0
        )
        
        # System prompt selection
        prompt_choice = st.selectbox(
            "System Prompt",
            list(DEFAULT_SYSTEM_PROMPTS.keys()),
            index=0
        )
        st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPTS[prompt_choice]
        
        # File upload
        st.header("Upload Files")
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"])
        if uploaded_file:
            client = setup_gemini_client()
            new_file = upload_file(client, uploaded_file)
            if new_file:
                st.session_state.uploaded_files.append(new_file)
                st.success(f"File uploaded successfully! Total files: {len(st.session_state.uploaded_files)}")
        
        # Display uploaded files
        if st.session_state.uploaded_files:
            st.header("Uploaded Files")
            for i, file in enumerate(st.session_state.uploaded_files):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{i+1}. {file.name if hasattr(file, 'name') else 'Unnamed file'}")
                with col2:
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.uploaded_files.pop(i)
                        st.rerun()
        
        # Clear all files
        if st.session_state.uploaded_files:
            if st.button("Clear All Files"):
                st.session_state.uploaded_files = []
                st.rerun()
    
    # Main chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response from Gemini
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    client = setup_gemini_client()
                    
                    # Prepare input context
                    input_context = [st.session_state.system_prompt]
                    if st.session_state.uploaded_files:
                        input_context.extend(st.session_state.uploaded_files)
                    input_context.append(prompt)
                    
                    # Generate response
                    response = client.models.generate_content(
                        model=model_name,
                        contents=input_context,
                        config=types.GenerateContentConfig(
                            max_output_tokens=32768,
                            temperature=0.1,
                            top_p=0.95,
                            top_k=40
                        )
                    )
                    
                    # Display response
                    st.markdown(response.text)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    if st.session_state.uploaded_files:
                        st.warning("There might be an issue with the file processing. Try uploading the files again.")

if __name__ == "__main__":
    main() 