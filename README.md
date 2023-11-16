# Setup
1. Setup and activate python environment
   - `python -m venv venv`
   - `source venv/bin/activate`
2. Install langchain and ollama
   - `pip install langchain`
   - Monkey patch ollama.py:135 in langchain.llms to `json={"prompt": prompt, "format": "json", **params},` and multiple places, where appropriate, to allow for system prompts:
   ```python
   system: Optional[str] = None
   
   "system": self.system,
   
   return {**{"model": self.model, "system": self.system}, **self._default_params}
   
   params = {**self._default_params, "stop": stop, "system": self.system, **kwargs}
   ```
   - https://github.com/jmorganca/ollama
3. Install other tools
   - Extract nmslib-master.zip into `./venv/lib/python3.11/site-packages`
   - `pip install --no-cache-dir venv/lib/python3.11/site-packages/nmslib-master/python_bindings`
   - `pip install scispacy`
   - `pip install 'spacy[apple]'`
   - `pip install sentence-transformers`
   - `pip install pandas`
   - `pip install openpyxl`
   - Install 'en_core_sci_lg' model from https://github.com/allenai/scispacy#available-models