import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

def get_embedding_model():
    return OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

def get_llm():
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
        max_tokens=1000,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
    )

def invoke_llm(prompt: str):
    llm = get_llm()
    response = llm.invoke(prompt)
    return response.content