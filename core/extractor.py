#Actionableitem, decision, questions

# from langchain_mistralai import ChatMistralAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import RunnablePassthrough, RunnableLambda
# import os

# def get_llm():
#     return ChatMistralAI(model = "mistral-small-latest",mistral_api_key = os.getenv("MISTRAL_API_KEY"),temperature=0.2)

# def build_chain(system_prompt : str):
#     llm = get_llm()
#     return (RunnablePassthrough() | RunnableLambda(lambda x : {"text" : x}) | ChatPromptTemplate.from_messages([
#         ("system", system_prompt),
#         ("human","{text}"),

#     ]) | llm | StrOutputParser()
#     )

# def extract_action_items(transcript:str)->str:
#     chain = build_chain(
#         "You are an expert meeting analyst. From the meeting transcript,"
#         "extract all action items. For each provide:\n"
#         "- Task description\n"
#         "-Owner (who is responsible)\n"
#         "-Deadline(if mentioned, else write 'Not specified')\n\n"
#         "Format as a numbered list. If none found say 'No action found."
#     )

#     return chain.invoke(transcript)


# def extract_key_decisions(transcript: str) -> str:
#     chain = build_chain(
#         "You are an expert meeting analyst. From the meeting trnscript,"
#         "extract all key decisions made. Format as a numbered list."
#         "If none found say 'No key decisions found."
#     )
#     return chain.invoke(transcript)

# def extract_questions(transcript: str) -> str:
#     chain = build_chain(
#         "From the meeting transcript, extract all unresolved questions"
#         "or topics needing follow-up.Format as a numbered list."
#         "If none found say 'No open questions found."
#     )
#     return chain.invoke(transcript)


from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_llm():
    model = os.getenv("MISTRAL_MODEL", "ministral-3b-latest")
    return ChatMistralAI(
        model=model,
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.2,
        max_retries=5,
    )


def build_chain(system_prompt: str):
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{text}")
    ])

    return (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | prompt
        | llm
        | StrOutputParser()
    )


def extract_action_items(transcript: str) -> str:
    if not transcript or not transcript.strip():
        return "No action items found (transcript is empty)."

    chain = build_chain(
        "You are an expert meeting analyst. "
        "From the meeting transcript, extract all action items. "
        "For each action item provide:\n"
        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, otherwise write 'Not specified')\n\n"
        "Format as a numbered list. "
        "If none are found, say 'No action items found.'"
    )

    try:
        return chain.invoke(transcript)
    except Exception as e:
        print(f"Action items extraction fallback: {e}")
        return "Could not extract action items due to AI rate limits. Please try again in a moment."


def extract_key_decisions(transcript: str) -> str:
    if not transcript or not transcript.strip():
        return "No key decisions found (transcript is empty)."

    chain = build_chain(
        "You are an expert meeting analyst. "
        "From the meeting transcript, extract all key decisions made. "
        "Format as a numbered list. "
        "If none are found, say 'No key decisions found.'"
    )

    try:
        return chain.invoke(transcript)
    except Exception as e:
        print(f"Key decisions extraction fallback: {e}")
        return "Could not extract key decisions due to AI rate limits. Please try again in a moment."


def extract_questions(transcript: str) -> str:
    if not transcript or not transcript.strip():
        return "No open questions found (transcript is empty)."

    chain = build_chain(
        "From the meeting transcript, extract all unresolved questions "
        "or topics needing follow-up. "
        "Format as a numbered list. "
        "If none are found, say 'No open questions found.'"
    )

    try:
        return chain.invoke(transcript)
    except Exception as e:
        print(f"Open questions extraction fallback: {e}")
        return "Could not extract open questions due to AI rate limits. Please try again in a moment."


