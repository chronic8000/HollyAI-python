# Holly AI Avatar - Installation Guide

## For Windows Local Installation

1. **Install Python 3.11** (if not already installed)
   - Download from https://python.org

2. **Install Required Libraries**
   ```cmd
   pip install google-genai pygame SpeechRecognition pyttsx3 opencv-python numpy
   ```
   
   **For Audio Support (Optional):**
   ```cmd
   pip install pyaudio
   ```
   If pyaudio fails on Windows:
   ```cmd
   pip install pipwin
   pipwin install pyaudio
   ```

3. **Set up API Key**
   - Get a free Gemini API key from https://aistudio.google.com/app/apikey
   - Create a `.env` file in the project folder:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run Holly**
   ```cmd
   python main.py
   ```

## Controls
- **T** - Test Holly's AI response
- **SPACE** - Manual speech trigger
- **R** - Reset Holly to neutral
- **ESC** - Exit

## Troubleshooting

### ImportError: cannot import name 'genai'
Install the correct Google AI library:
```cmd
pip install google-genai
```

### Audio Issues
If you get audio errors, install these:
```cmd
pip install pyaudio
# On Windows, you might need:
pip install pipwin
pipwin install pyaudio
```

### API Quota Exceeded
- The free Gemini API has a daily limit of 250 requests
- Wait 24 hours for quota reset, or upgrade to paid plan
- Holly will still display and animate without AI responses