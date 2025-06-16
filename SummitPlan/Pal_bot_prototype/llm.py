from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI


# Load .env environment variables
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

def invoke_llm(prompt):
    llm = ChatOpenAI(
            model= os.getenv("OPENAI_MODEL"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.1,
            max_tokens=10000,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
        )
    response = llm.invoke(prompt)
    return response.content