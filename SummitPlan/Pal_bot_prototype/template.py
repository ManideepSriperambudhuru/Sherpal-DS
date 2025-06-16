from llm import invoke_llm
from prompts import prompt

def generate_prompt_template(**kwargs):
    return prompt.format(**kwargs)

def gen_pal_output(data):
    prompt =  generate_prompt_template(**data)
    return invoke_llm(prompt)