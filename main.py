import logging
import os
import json
from datetime import datetime
from typing import Dict

from transformers import pipeline

from ontology_dc8f06af066e4a7880a5938933236037.config import ConfigClass
from ontology_dc8f06af066e4a7880a5938933236037.input import InputClass
from ontology_dc8f06af066e4a7880a5938933236037.output import OutputClass
from openfabric_pysdk.context import AppModel, State
from core.stub import Stub

import torch

# If you have a GPU, this will put the model on cuda; otherwise -1 = CPU
device = 0 if torch.cuda.is_available() else -1

# -------------------------------------------------------------------
# Module-level LLM setup (local GPT-2 used here as an example)
# -------------------------------------------------------------------
try:
    llm = pipeline("text-generation", model="gpt2", device=device, max_length=100)
    logging.info("Local LLM pipeline loaded")
except Exception:
    llm = None
    logging.warning("Couldn't load local LLM pipeline; proceeding without expansion")



# Configurations for the app
configurations: Dict[str, ConfigClass] = dict()

############################################################
# Config callback function
############################################################
def config(configuration: Dict[str, ConfigClass], state: State) -> None:
    """
    Stores user-specific configuration data.

    Args:
        configuration (Dict[str, ConfigClass]): A mapping of user IDs to configuration objects.
        state (State): The current state of the application (not used in this implementation).
    """
    for uid, conf in configuration.items():
        logging.info(f"Saving new config for user with id:'{uid}'")
        configurations[uid] = conf


############################################################
# Execution callback function
############################################################
def execute(model: AppModel) -> None:
    """
    Main execution entry point for handling a model pass.
      1. Expand the user prompt via local LLM
      2. Call Text→Image Openfabric app
      3. Call Image→3D Openfabric app
      4. Save outputs
      5. Record short- and long-term memory

    Args:
        model (AppModel): The model object containing request and response structures.
        
    """

    # 1) Get request & config & Retrieve input
    request: InputClass = model.request
    user_id = "super-user"
    # Retrieve user config
    user_config: ConfigClass = configurations.get(user_id, None)
    logging.info(f"{configurations}")

    # Initialize the Stub with app IDs
    app_ids = user_config.app_ids if user_config else []
    stub = Stub(app_ids)

    logging.info(f"Received prompt: {request.prompt}")

    # 2) Optionally expand prompt via local LLM
    if llm:
        try:
            gen = llm(request.prompt)[0]["generated_text"]
            expanded = gen.strip()
            logging.info(f"Expanded prompt: {expanded}")
        except Exception as e:
            logging.warning("LLM expansion failed, using original prompt", exc_info=e)
            expanded = request.prompt
    else:
        expanded = request.prompt

    # 3) Text → Image
    #    (uses first app_id in the list)
    text2img_id = app_ids[0]
    img_result = stub.call(text2img_id, {"prompt": expanded}, user_id)
    image_bytes = img_result.get("result")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_filename = f"output_{timestamp}.png"
    with open(img_filename, "wb") as f:
        f.write(image_bytes)
    logging.info(f"Saved generated image to {img_filename}")

    # 4) Image → 3D
    #    (uses second app_id in the list)
    img2obj_id = app_ids[1]
    obj_result = stub.call(img2obj_id, {"image": image_bytes}, user_id)
    model_bytes = obj_result.get("result")
    obj_filename = f"model_{timestamp}.obj"
    with open(obj_filename, "wb") as f:
        f.write(model_bytes)
    logging.info(f"Saved 3D model to {obj_filename}")

    # 5) Short-term memory (session)
    model.state["last_interaction"] = {
        "prompt": request.prompt,
        "expanded": expanded,
        "image_file": img_filename,
        "model_file": obj_filename
    }

    # 6) Long-term memory (append to JSON)
    mem_file = "memory.json"
    try:
        memories = json.load(open(mem_file, "r"))
    except (FileNotFoundError, json.JSONDecodeError):
        memories = []
    memories.append(model.state["last_interaction"])
    with open(mem_file, "w") as f:
        json.dump(memories, f, indent=2)
    logging.info(f"Appended interaction to {mem_file}")

    # 7) Prepare response
    response: OutputClass = model.response
    response.message = (
        f"✅ 3D model generation complete!\n"
        f"- Image: `{img_filename}`\n"
        f"- 3D model: `{obj_filename}`\n"
        f"(Memory stored for remixing later.)"
    )

