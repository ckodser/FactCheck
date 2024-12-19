from TFIDF import search_tfidf  # Import the function from your TF-IDF file
from reasoner import reasoner
from django.shortcuts import render


def main_page(request):
    if request.method == "POST":
        text = request.POST.get('news_text')  # Get the text from the form
        top_matches = search_tfidf(text)  # Use the search_tfidf function to get results

        context = {
            'text': text,
            'reasoner_outcome': reasoner(text, top_matches),
            'top_matches': top_matches  # Pass the results to the template
        }
        return render(request, 'news_results.html', context)
    return render(request, 'news_results.html')  # Return the empty page if GET request
