import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Model pricing information (per 1M tokens)
MODEL_PRICING = {
    "gemini-2.5-flash-preview-05-20": {"input": 0.15, "output": 0.60},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    "gemini-2.0-pro": {"input": 1.25, "output": 5.00}
}

def count_tokens(client, model_name, content):
    """Count tokens using Gemini's API."""
    try:
        response = client.models.count_tokens(
            model=model_name,
            contents=[content]
        )
        return response.total_tokens
    except Exception as e:
        st.warning(f"Error counting tokens: {str(e)}")
        return 0

def calculate_cost(model_name, input_tokens, output_tokens):
    """Calculate the cost for a request based on token counts."""
    if model_name not in MODEL_PRICING:
        return 0, 0
    
    pricing = MODEL_PRICING[model_name]
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost, output_cost

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
        
        # Process the file with Gemini API
        if uploaded:
            # Clear the file context to ensure it's reprocessed
            st.session_state.file_context = []
            return uploaded
        return None
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
        st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPTS["retrieval"]
    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = {"input": 0, "output": 0}
    if "total_cost" not in st.session_state:
        st.session_state.total_cost = {"input": 0, "output": 0}
    if "file_context" not in st.session_state:
        st.session_state.file_context = []
    if "upload_key" not in st.session_state:
        st.session_state.upload_key = 0

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
            list(MODEL_PRICING.keys()),
            index=0
        )
        
        # Display token usage and cost
        st.header("Token Usage & Cost")
        st.write(f"Total Input Tokens: {st.session_state.total_tokens['input']:,}")
        st.write(f"Total Output Tokens: {st.session_state.total_tokens['output']:,}")
        st.write(f"Total Input Cost: ${st.session_state.total_cost['input']:.6f}")
        st.write(f"Total Output Cost: ${st.session_state.total_cost['output']:.6f}")
        st.write(f"Total Cost: ${st.session_state.total_cost['input'] + st.session_state.total_cost['output']:.6f}")
        
        # Reset usage button
        if st.button("Reset Usage"):
            st.session_state.total_tokens = {"input": 0, "output": 0}
            st.session_state.total_cost = {"input": 0, "output": 0}
            st.rerun()
        
        # System prompt selection
        prompt_choice = st.selectbox(
            "System Prompt",
            list(DEFAULT_SYSTEM_PROMPTS.keys()),
            index=list(DEFAULT_SYSTEM_PROMPTS.keys()).index("retrieval")
        )
        st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPTS[prompt_choice]
        
        # File upload
        st.header("Upload Files")
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"], key=f"file_uploader_{st.session_state.upload_key}")
        if uploaded_file:
            client = setup_gemini_client()
            new_file = upload_file(client, uploaded_file)
            if new_file:
                st.session_state.uploaded_files.append(new_file)
                st.success(f"File uploaded successfully! Total files: {len(st.session_state.uploaded_files)}")
                # Increment the upload key to force a new uploader instance
                st.session_state.upload_key += 1
                # Rerun to clear the uploader
                st.rerun()
        
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
                        st.session_state.file_context = []  # Clear file context when files are removed
                        st.rerun()
        
        # Clear all files
        if st.session_state.uploaded_files:
            if st.button("Clear All Files"):
                st.session_state.uploaded_files = []
                st.session_state.file_context = []  # Clear file context when files are removed
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
                    
                    # Count system prompt tokens
                    input_tokens = count_tokens(client, model_name, st.session_state.system_prompt)
                    
                    # Add file context only if it's not already in the messages
                    if st.session_state.uploaded_files and not st.session_state.file_context:
                        st.session_state.file_context = st.session_state.uploaded_files.copy()
                    
                    # Count uploaded files tokens
                    if st.session_state.file_context:
                        for file in st.session_state.file_context:
                            file_tokens = count_tokens(client, model_name, file)
                            input_tokens += file_tokens
                            st.info(f"File '{file.name if hasattr(file, 'name') else 'Unnamed'}' tokens: {file_tokens:,}")
                        input_context.extend(st.session_state.file_context)
                        # Clear file context after processing
                        st.session_state.file_context = []
                    
                    # Add user prompt tokens
                    prompt_tokens = count_tokens(client, model_name, prompt)
                    input_tokens += prompt_tokens
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
                    
                    # Count output tokens
                    output_tokens = count_tokens(client, model_name, response.text)
                    
                    # Calculate costs
                    input_cost, output_cost = calculate_cost(model_name, input_tokens, output_tokens)
                    
                    # Update session state
                    st.session_state.total_tokens["input"] += input_tokens
                    st.session_state.total_tokens["output"] += output_tokens
                    st.session_state.total_cost["input"] += input_cost
                    st.session_state.total_cost["output"] += output_cost
                    
                    # Display token usage for this request
                    st.info(f"Request Tokens: {input_tokens:,} input, {output_tokens:,} output")
                    st.info(f"Request Cost: ${input_cost + output_cost:.6f}")
                    
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