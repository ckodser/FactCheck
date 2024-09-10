from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def main_view(request):
    context = {}
    return render(request, 'news.html', context)


def results(request):
    text = request.POST.get('news_text')  # getting the text from the form

    context={'text':text, 'stocks':[{'name':'وآیند', 'growth':True}, {'name':'افق', 'growth':True},{'name':'کاما', 'growth':False}]}
    return render(request, 'results.html', context)
