# Gemini Chat Application

A simple command-line chat application that uses Google's Gemini API.

## Setup

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Set up your Google AI API key:
   - Get an API key from [Google AI Studio](https://ai.google.dev/)
   - Either set it as an environment variable:
     ```
     export GOOGLE_API_KEY="your-api-key"
     ```
   - Or pass it as an argument when running the script

## Usage

Run the script with:

```bash
python gemini_chat.py
```

Optional arguments:
- `--api-key YOUR_API_KEY`: Provide your Google AI API key directly
- `--model MODEL_NAME`: Choose which Gemini model to use:
  - `gemini-1.5-flash`: Faster, more efficient model
  - `gemini-1.5-pro`: More capable but slower model
  - `gemini-2.0-flash`: Latest fast model (default)
  - `gemini-2.0-pro`: Latest most capable model

Example:
```bash
python gemini_chat.py --model gemini-2.0-pro
```

Type your messages and press Enter to send them to Gemini.
Type 'exit' or 'quit' to end the conversation. 