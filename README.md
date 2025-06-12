# AI Dev Challenge

This project implements a multi-stage pipeline that takes a user prompt, expands it via a local LLM (optional), generates an image via Openfabric Text→Image, converts that image into a 3D model via Openfabric Image→3D, and stores memory for future remixing.

---

## Requirements

- **Python**: 3.11.x (recommended) or 3.10.x
- **Virtual environment** (venv)
- **Poetry** (optional, for dependency & environment management)
- (Optional) **CUDA-capable GPU** & matching PyTorch

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/dragonous102/Openfabric
cd Openfabric
```

### 2. Create & activate a virtual environment (venv)

**Using Python 3.11+**:

```powershell
# Create venv with Python 3.11
py -3.11 -m venv .venv

# Activate in ubuntu (first time only: allow scripts)
source venv/bin/activate

# OR in windows
.venv\Scripts\activate.bat
```

### 3. Upgrade pip

```bash
pip install --upgrade pip
```

### 4. Install core dependencies

```bash
pip install openfabric-pysdk
```

> **Tip:** If you see a `gevent` build error (on Python 3.13), switch to Python 3.11 or 3.10 so pip can install a pre-built wheel.

### 5. (Optional) Install local LLM support

Provides prompt interpretation & creative expansion:

```bash
pip install torch transformers accelerate bitsandbytes
```

Or, for a lightweight Llama CPP backend:

```bash
pip install llama-cpp-python
```

### 6. (Optional) Poetry workflow

```bash
pip install poetry
poetry install
# Then run commands via:
poetry run python ignite.py
```

---

## Configuration

Set your Openfabric App IDs before starting the server. Replace with your actual IDs:

```bash
export APP_IDS='{"super-user":["<text2img-app-id>","<img2obj-app-id>"]}'
```

On PowerShell:

```powershell
$env:APP_IDS = '{"super-user":["<text2img-app-id>","<img2obj-app-id>"]}'
```

---

## Running the App

### Via `start.sh` (Git Bash / WSL)

```bash
./start.sh
```

### Direct Python

```bash
python ignite.py
```

This will start a FastAPI server at `http://localhost:8888`.

### Swagger UI

Open in your browser:

```
http://localhost:8888/swagger-ui/#/App/post_execution
```

POST an example payload:

```json
{
  "prompt": "A glowing dragon on a cliff at sunset"
}
```

You should receive back a confirmation message and see:

- `output_<timestamp>.png` in your project folder
- `model_<timestamp>.obj` in your project folder

---

## Memory & Persistence

- **Session memory** saved to `model.state["last_interaction"]`
- **Long-term memory** appended to `memory.json`

---

## Troubleshooting

- Ensure your venv is activated and `pip install openfabric-pysdk` succeeded.

- compile errors: Use Python 3.11 or install via Conda to get prebuilt binaries.

- The `Resource` class was removed from `openfabric_pysdk.fields` in recent SDK versions. Remove any `from openfabric_pysdk.fields import Resource` lines. If you need to set up API endpoints, use `Starter` from `openfabric_pysdk.starter` combined with Flask’s routing/decorators.

- Ensure your venv is activated and `pip install openfabric-pysdk` succeeded.

- Compile errors: Use Python 3.11 or install via Conda to get prebuilt binaries.

---

## Optional Enhancements

- Add a GUI with Streamlit or Gradio
- Integrate semantic memory (FAISS, ChromaDB)
- Build a voice-to-text interface
- Create a local 3D model viewer for your outputs

---

Happy coding! Feel free to contribute improvements or file issues.")

