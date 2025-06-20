import os
from dotenv import load_dotenv

load_dotenv()

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_qdrant import Qdrant
from langchain_tavily import TavilySearch

from qdrant_utils import get_vector_store
from memory_utils import InMemoryChatSessionManager


def get_rag_chain():
    retriever = get_vector_store("docs_index").as_retriever()
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7
    )
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever)


def fallback_web_search(query: str) -> str:
    try:
        tool = TavilySearch(k=2)
        results = tool.invoke({"query": query})
        texts = []

        for res in results:
            content = res.get("content", "")
            # Clean markdown and hyperlinks
            content = content.replace("**", "")
            content = content.replace("[", "").replace("]", "")
            content = content.split("http")[0]  # truncate long links
            texts.append(content.strip())

        return "\n\n".join(texts) if texts else "Sorry, I couldn’t find relevant information right now."
    except Exception as e:
        return f"Web search failed: {str(e)}"


def get_moderated_conversation_chain(acceptance_policy: str, session_manager: InMemoryChatSessionManager):
    prompt_template = PromptTemplate(
        input_variables=["input", "history"],
        template=f"""You are a helpful and safe AI assistant.

First, follow this policy:

{acceptance_policy}

Here is the chat history:
{{history}}

User: {{input}}
Assistant:"""
    )

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.3
    )

    def invoke_chain(input_text: str, session_id: str) -> str:
        history_msgs = session_manager.get_history(session_id)
        history = ""
        for msg in history_msgs:
            if msg["role"] == "user":
                history += f"User: {msg['content']}\n"
            elif msg["role"] == "bot":
                history += f"Assistant: {msg['content']}\n"

        # Format prompt
        prompt = prompt_template.format(input=input_text, history=history)
        ai_response = llm.invoke(prompt)

        if isinstance(ai_response, AIMessage):
            return ai_response.content.strip()
        return str(ai_response).strip()

    return invoke_chain
