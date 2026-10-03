# Blood Work Analyzer

A Streamlit app that reads a blood test report and gives a plain-language
health summary and a suggested diet plan, using a local Ollama model (llama3.2).

![Blood Work Analyzer](screenshot.png)

## Run it
```bash
pip install -r requirements.txt
ollama pull llama3.2
streamlit run app.py
```

*For information only. This is not medical advice.*
