# gender-prediction-api

## LLM configuration

When using `?model=llm` the service will call an Ollama server. Set the
`OLLAMA_API_URL` and `OLLAMA_MODEL` environment variables to point at your
deployment. Example:

```bash
export OLLAMA_API_URL="http://146.148.125.199:11434/api/generate"
export OLLAMA_MODEL="llama3.2:1b"
```