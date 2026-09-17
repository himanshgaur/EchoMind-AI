# from langchain_mistralai import ChatMistralAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# import os

# def get_llm():
#     return ChatMistralAI(model = "mistral-small-latest",mistral_api_key = os.getenv("MISTRAL_API_KEY"),temperature=0.3)


# def split_transcript(transcript: str) -> list:
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size = 3000,
#         chunk_overlap = 200
#     )

#     return splitter.split_text(transcript)

# def summarize(transcript: str) -> str:
#     llm = get_llm()

#     map_prompt = ChatPromptTemplate.from_messages(
#         [
#             ("system", "Summarize this portion of a meeting transcript concisely")
#         ]
#     )

#     map_chain = map_prompt | llm | StrOutputParser()

#     chunks = split_transcript(transcript)

#     chunk_summaries = [map_chain.invoke({"text" : chunk}) for chunk in chunks]

#     combined = "\n\n".join(chunk_summaries)

#     combined_prompt = ChatPromptTemplate.from_messages(
#         [
#             {
#                 "system",
#                 "You are an expert meeting summarizer. Combine these partial summaries"
#                 "into one final professional meeting summary in bullet points.",
#             },
#             ("human", "{text}"),
#         ]
#     )

#     combined_chain= (
#         RunnablePassthrough() | RunnableLambda(lambda x: {"text":x}) | combined_prompt | llm | StrOutputParser
#     )
#     return combined_chain.invoke(combined)

# def generate_title(transcript: str) -> str:
#     llm = get_llm()

#     title_chain = (
#         RunnablePassthrough() | RunnableLambda(lambda x:{"text": x}) | 
#         ChatPromptTemplate.from_messages([
#             {
#                 "system",
#                 "Based on the meeting transcript, generate a short professional meeting title"
#                 "{max 8 words}. Only return the title, nothing else.",

#             },
#             ("human","{text}"),
#         ])
#         | llm
#         | StrOutputParser()
#     )

#     return title_chain.invoke(transcript[:2000])
import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import time

def get_llm():
    model = os.getenv("MISTRAL_MODEL", "ministral-3b-latest")
    return ChatMistralAI(
        model=model,
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.3,
        max_retries=5,
    )


def split_transcript(transcript: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200
    )
    return splitter.split_text(transcript)


def summarize(transcript: str) -> str:
    if not transcript or not transcript.strip():
        return "No spoken content detected to summarize."

    llm = get_llm()

    map_prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize this portion of a meeting transcript concisely."),
        ("human", "{text}"),
    ])
    map_chain = map_prompt | llm | StrOutputParser()

    chunks = split_transcript(transcript)
    chunk_summaries = []
    for chunk in chunks:
        try:
            chunk_summaries.append(map_chain.invoke({"text": chunk}))
            time.sleep(0.5)  # Avoid bursting rate limits
        except Exception as e:
            print(f"Summary chunk failed: {e}")
            chunk_summaries.append(chunk[:300])

    combined = "\n\n".join(chunk_summaries)

    combined_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert meeting summarizer. Combine these partial summaries "
            "into one final professional meeting summary in bullet points.",
        ),
        ("human", "{text}"),
    ])
    combined_chain = (
        RunnablePassthrough() | RunnableLambda(lambda x: {"text": x}) | combined_prompt | llm | StrOutputParser()
    )

    try:
        return combined_chain.invoke(combined)
    except Exception as e:
        print(f"Combined summary fallback due to: {e}")
        return combined


def generate_title(transcript: str) -> str:
    if not transcript or not transcript.strip():
        return "Untitled Meeting Recording"

    llm = get_llm()

    title_chain = (
        RunnablePassthrough() | RunnableLambda(lambda x: {"text": x}) | 
        ChatPromptTemplate.from_messages([
            (
                "system",
                "Based on the meeting transcript, generate a short professional meeting title "
                "(max 8 words). Only return the title, nothing else.",
            ),
            ("human", "{text}"),
        ])
        | llm
        | StrOutputParser()
    )

    try:
        return title_chain.invoke(transcript[:2000]).strip('"\n ')
    except Exception as e:
        print(f"Title generation fallback due to: {e}")
        return "Meeting Intelligence Digest"
