from langchain_openai import ChatOpenAI  # pip install -U langchain_openai

# OpenAI API setup
llm = ChatOpenAI(
    model="gpt-4o-mini",
    base_url="https://api.avalai.ir/v1",
    api_key="aa-dsqM6ozL9gSMLfpnPPeDhMv73APgRDcTfzjiY7nvKpTunawG"
)


def reasoner(query, search_results):
    """
    Assess the relationship between the query and multiple search results,
    producing a single outcome: FACT, FALSE, or UNRELATED.

    Args:
        query (str): The user-provided query.
        search_results (list): A list of search results where each result contains:
                               (index, similarity_score, text, key, persian_date, url)

    Returns:
        str: One of "FACT", "FALSE", or "UNRELATED".
    """
    # Prepare the texts for the prompt
    news_texts = '\n'.join([f"Text {i + 1}: {result[2]}" for i, result in enumerate(search_results)])

    # Construct the prompt
    reasoning_prompt = f"""
    You are a fact-checking assistant. A user provides a query and multiple news texts. 
    Your task is to analyze all the news texts and assess their overall relationship to the query.

    Query:
    "{query}"

    News Texts:
    {news_texts}

    Based on the news texts and query, determine one of the following:
    - FACT: The news collectively confirms the query as true.
    - FALSE: The news collectively disproves the query.
    - UNRELATED: The news is unrelated to the query.

    Respond with only one word: FACT, FALSE, or UNRELATED.
    """

    # Invoke the OpenAI model and get the response
    response = llm.invoke(reasoning_prompt).content.strip().upper()
    print(response)
    # Validate and return the response
    if response in {"FACT", "FALSE", "UNRELATED"}:
        return response
    else:
        return "UNAVAILABLE"  # Fallback if the API response is unexpected