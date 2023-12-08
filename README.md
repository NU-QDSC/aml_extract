# Setup
1. Setup and activate python environment
   - `python -m venv venv`
   - `source venv/bin/activate`
2. Install Ollama and llama2 model
   - Install Ollama from https://ollama.ai/
   - Use instructions to create a Modelfile https://github.com/jmorganca/ollama?tab=readme-ov-file#import-from-gguf
   - `ollama create hermes -f Modelfile`
3. Install other tools
   - `pip install langchain`
   - Extract nmslib-master.zip into `./venv/lib/python3.11/site-packages`
   - `pip install --no-cache-dir venv/lib/python3.11/site-packages/nmslib-master/python_bindings`
   - `pip install scispacy`
   - `pip install 'spacy[apple]'`
   - `pip install sentence-transformers`
   - Install 'en_core_sci_lg' model from https://github.com/allenai/scispacy#available-models
4. Use the following command and prompt format with this specific model
   - `cat report.txt | llm -m llama2-hermes -s 'This is a prompt related to the piped in file'`
```text
Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{prompt}

### Response:
```