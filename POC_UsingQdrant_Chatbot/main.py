import os
from langchain_core.documents import Document
from dotenv import load_dotenv
from retriever_setup import (
    get_rag_chain,
    fallback_web_search,
    get_moderated_conversation_chain
)
from embed_docs import embed_and_store_documents
from memory_utils import InMemoryChatSession, InMemoryChatSessionManager
from qdrant_utils import get_vector_store, create_qdrant_collection

load_dotenv()

# Acceptance policy
acceptance_policy = """
ACCEPTANCE POLICY (DECISION TREE FORMAT):

This assistant is responsible for both user engagement and content moderation. Follow the steps below to evaluate any user message.

==================================
STEP 1: MODERATION CHECK
==================================
Scan the input for any content or words used that fall under *banned categories* in any language. If **any** of the following are detected:
    - Defamatory, obscene, pornographic, vulgar, offensive
    - Unlawful, libelous, indecent, lewd, suggestive
    - Abusive, inflammatory, harassing, hateful
    - Mentions of addictive or controlled substances such as:
        > alcohol, beer, wine, whiskey, vodka, drugs, weed, marijuana, cocaine, etc.
    - Promotes: discrimination, racism, violence, threats, illegal activities
    - Spam, advertising, political campaigning, or solicitation

**ACTION**:  
Immediately respond with:

"MODERATION_ALERT: This message violates Sherpal's Acceptable Use Policy. Continued violations may lead to account suspension and parental notification, as stated in our Terms of Service."

==================================
STEP 2: TOPIC CLASSIFICATION
==================================

**TECHNOLOGY TOPICS**  
If the content is related to technology, learning tools, or programming:  
**Action**: Proceed with full engagement.

**OUT-OF-SCOPE TOPICS**
Includes:
    - Celebrity or pop culture (unless user-declared AND relevant)
    - Politics, religion, ideology
    - Dating or relationships
    - Non-technical rants/debates
    - Stock trading, side hustles, business ideas
    - Anything violating the Acceptable Use Policy

**Action**:
    - Respectfully redirect away from this topic.
    - Remind the user that this topic is not part of the supported scope.

**NOT PART OF FOCUS AREA**
If the topic is technical but off-topic from the current session:  
**Action**:
    - Issue a respectful redirection to stay on track.
    - Encourage saving off-topic questions for later.

==================================
FINAL STEP: RETURN TO MODULE
==================================
After handling any case (except moderation alert), conclude with:
    "Let's get back to our focus area."
"""

# Session & memory
session_id = "user_session"
chat_memory = InMemoryChatSession()
session_manager = InMemoryChatSessionManager()
chat_chain = get_moderated_conversation_chain(acceptance_policy, session_manager)

def save_chat_to_qdrant():
    if not chat_memory.messages:
        return
    create_qdrant_collection("chat_history")
    vectorstore = get_vector_store("chat_history")

    docs = [
        Document(page_content=m["content"], metadata={"role": m["role"]})
        for m in chat_memory.messages
    ]

    vectorstore.add_documents(docs)
    print("💾 Chat history saved to Qdrant.")

def main():
    embed_and_store_documents()
    qa_chain = get_rag_chain()
    print("\n🤖 ChatBot is ready! Type 'exit' to end.\n")

    while True:
        query = input("You: ")
        if query.strip().lower() == "exit":
            save_chat_to_qdrant()
            print("👋 Session ended and chat saved.")
            break

        chat_memory.add_message("user", query)
        session_manager.add_message(session_id, "user", query)

        try:
            response = chat_chain(query, session_id=session_id)
        except Exception as e:
            print("⚠️ Error with contextual chain. Falling back to web search.\n", e)
            response = fallback_web_search(query)

        print("Bot:", response)
        chat_memory.add_message("bot", response)
        session_manager.add_message(session_id, "bot", response)

if __name__ == "__main__":
    main()
