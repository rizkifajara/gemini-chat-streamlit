# Gemini Chat Application

A modern web-based chat application using Google's Gemini API, built with Streamlit.

## Features

- Modern web interface with Streamlit
- Multiple Gemini model support
- File upload and processing
- Customizable system prompts
- Docker support for easy deployment

## Setup

### Local Development

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your Google AI API key:
   - Get an API key from [Google AI Studio](https://ai.google.dev/)
   - Create a `.env` file in the project root:
     ```
     GOOGLE_API_KEY="your-api-key"
     ```

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t gemini-chat .
   ```

2. Run the container:
   ```bash
   docker run -p 40050:40050 --env-file .env gemini-chat
   ```

The application will be available at `http://localhost:40050`

## Usage

### Web Interface

1. Open your browser and navigate to `http://localhost:40050`
2. Select your preferred Gemini model from the sidebar
3. Choose a system prompt or use the default
4. Upload files if needed (PDF, TXT, DOCX)
5. Start chatting with Gemini!

### Available Models

- `gemini-2.5-flash-preview-05-20`: Latest preview model
- `gemini-1.5-flash`: Faster, more efficient model
- `gemini-1.5-pro`: More capable but slower model
- `gemini-2.0-flash`: Latest fast model
- `gemini-2.0-pro`: Latest most capable model

### System Prompts

The application includes several pre-configured system prompts:
- Default: General-purpose assistant
- Analyst: Data-driven insights
- Summarizer: Document summarization
- Comparator: Document comparison
- Retrieval: Legal document analysis

## Development

### Project Structure

```
.
├── app.py              # Streamlit web application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── .env              # Environment variables (not in git)
└── README.md         # This file
```

### Environment Variables

- `GOOGLE_API_KEY`: Your Google AI API key
- `STREAMLIT_SERVER_PORT`: Port for the Streamlit server (default: 40050)
- `STREAMLIT_SERVER_ADDRESS`: Server address (default: 0.0.0.0)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 