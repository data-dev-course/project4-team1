from django.shortcuts import render
PATH = ""

# Create your views here.
def home(request):
    template_name = ''
    return render(request, PATH + 'infoPages/placeList.html')

def population(request):
    return render(request, PATH + 'infoPages/population.html')

def weather(request):
    return render(request, PATH + 'infoPages/weather.html')

def restaurant(request):
    return render(request, PATH + 'infoPages/restaurant.html')

def news(request):
    return render(request, PATH + 'infoPages/news.html')