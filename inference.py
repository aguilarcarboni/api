# Please install transformers & llama-cpp-python to run this script
# This script is an example of inference using llama-cpp-python + HF tokenizer
from llama_cpp import Llama

from functionary.prompt_template import get_prompt_template_from_tokenizer

from transformers import AutoTokenizer

tools = [
    {
        "name": "get_info_from_database",
        "description": "Get info from my database when Athena doesn't know the answer to a personal question and thinks it should be in the database.",
        "parameters": {
            "type": "object",
            "properties": {
            "output": {
                "type": "array",
                "description": "An array containing objects with one key and one value each. Each element in the array is one field in the table the function is querying. Returned keys should match the schema in the database-schema.json file in Memory to see all paths.",
                "items":{
                "type":"object",
                "properties":{
                    "generic_key":{
                    "type":"string",
                    "description":"A table field containing one key and one value representing one field of the data being queried. The name, generic key, is supposed to be replaced with whatever the database returned. Also, you can see what key to use in the database-schema.json fle in your Memory."
                    }
                }
                }
            },
            "path": {
                "type": "string",
                "description": "The path in my database where Athena thinks the relevant data should be gotten from. Use database-schema.json file in Memory to see all paths. Use only the paths in that file under each schema."
            },
            "query": {
                "type": "string",
                "description": "The query Athena thinks should be made to my database to retrieve the data. Should always have format that can be used to query a MongoDB database. Use database-schema.json file in Memory to see all keys and paths."
            }
            },
            "required": [
            "path",
            "query"
            ]
        }
    },
    {
        "name": "save_info_to_database",
        "description": "Save info to outside database when the user inputs a personal fact Athena doesn't know about and thinks should be stored.",
        "parameters": {
            "type": "object",
            "properties": {
            "path": {
                "type": "string",
                "description": "The path in my database where Athena thinks the relevant data should be stored. Returned paths should match the schema in the database-schema.json file in Memory to see all paths. Use only the paths in that file under each schema."
            },
            "data": {
                "type": "string",
                "description": "The data Athena thinks should be saved in the database. Must have dictionary format enclosed by brackets {} and use relevant key names."
            },
            "query": {
                "type": "string",
                "description": "The query Athena thinks should be run to query the data in the database. Should always have format that can be used to query a MongoDB database. Use the string NONE if no query will be made, for example when inserting a document. Use database-schema.json file in Memory to see all keys and paths."
            }
            },
            "required": [
            "path",
            "data",
            "query"
            ]
        }
    }
]

# You can download gguf files from https://huggingface.co/meetkai/functionary-small-v2.5-GGUF
PATH_TO_GGUF_FILE = "athena.gguf"
llm = Llama(model_path=PATH_TO_GGUF_FILE, n_ctx=8192, n_gpu_layers=-1)

# Create tokenizer from HF. We should use tokenizer from HF to make sure that tokenizing is correct
# Because there might be a mismatch between llama-cpp tokenizer and HF tokenizer and the model was trained using HF tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    "meetkai/functionary-small-v2.5-GGUF", legacy=True
)

# prompt_template will be used for creating the prompt
prompt_template = get_prompt_template_from_tokenizer(tokenizer)

# Start messages
messages = [
    {
        "role": "system", 
        "content":  """
                    You are Athena, a powerful and advanced virtual personal assistant application.
                    """
    }
]

while True:
    message = input('Enter a message:')
    messages.append({"role": "user", "content": message})

    # Before inference, we need to add an empty assistant (message without content or function_call)
    messages.append({"role": "assistant"})

    # Create the prompt to use for inference
    prompt_str = prompt_template.get_prompt_from_messages(messages, tools)
    token_ids = tokenizer.encode(prompt_str)

    gen_tokens = []
    # Get list of stop_tokens
    stop_token_ids = [
        tokenizer.encode(token)[-1]
        for token in prompt_template.get_stop_tokens_for_generation()
    ]

    print('Generating result...')
    index = 1

    # We use function generate (instead of __call__) so we can pass in list of token_ids
    for token_id in llm.generate(token_ids, temp=0):
        if token_id in stop_token_ids:
            break
        gen_tokens.append(token_id)
        index += 1

    #print('Decoding...')
    llm_output = tokenizer.decode(gen_tokens)

    # parse the message from llm_output
    #print('Parsing...')
    result = prompt_template.parse_assistant_response(llm_output)
    print('Athena:', result)

"""
import base64

def image_to_base64_data_uri(file_path):
    with open(file_path, "rb") as img_file:
        base64_data = base64.b64encode(img_file.read()).decode('utf-8')
        return f"data:image/png;base64,{base64_data}"

# Replace 'file_path.png' with the actual path to your PNG file
file_path = 'file_path.png'
data_uri = image_to_base64_data_uri(file_path)

messages = [
    {
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": data_uri }},
            {"type" : "text", "text": "Describe this image in detail please."}
        ]
    }
]
"""