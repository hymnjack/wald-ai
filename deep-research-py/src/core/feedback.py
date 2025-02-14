from langchain_openai import ChatOpenAI

async def generate_feedback(query: str) -> list[str]:
    """Generate follow-up questions to better understand research needs."""
    llm = ChatOpenAI(temperature=0.7)
    response = await llm.ainvoke(
        "You are a research assistant helping to understand a user's research needs. "
        "Generate 3 follow-up questions to better understand what the user wants to learn. "
        "The questions should help clarify the scope, depth, and specific aspects of interest. "
        f"Here is their query: {query}\n\n"
        "Return only the questions, one per line, starting with a dash (-)"
    )
    
    questions = []
    for line in response.content.split("\n"):
        if line.strip() and line.strip().startswith("-"):
            questions.append(line.strip()[2:])
    return questions
