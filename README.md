# Setup
1. Setup and activate python environment
   - `python -m venv venv`
   - `source venv/bin/activate`
2. Install llm and llama2 model
   - `pip install llm`
   - `CMAKE_ARGS="-DLLAMA_METAL=on" FORCE_CMAKE=1 llm install llama-cpp-python`
   - `llm install llm-llama-cpp`
   - `llm llama-cpp download-model 'https://huggingface.co/TheBloke/Speechless-Llama2-Hermes-Orca-Platypus-WizardLM-13B-GGUF/resolve/main/speechless-llama2-hermes-orca-platypus-wizardlm-13b.Q5_K_M.gguf' -a llama2-hermes`
3. Install other tools
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