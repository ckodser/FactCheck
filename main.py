from TFIDF import search_tfidf
from reasoner import reasoner

def fact_checker_pipeline(query):
    print("Running TF-IDF Search...")
    search_results = search_tfidf(query)

    print("\nAssessing Results with the Reasoner...")
    overall_assessment = reasoner(query, search_results)

    print("\nOverall Assessment:", overall_assessment)

if __name__ == "__main__":
    query_input = "سپاه اسنپ را خرید."
    fact_checker_pipeline(query_input)
