from django.shortcuts import render

# Create your views here.
def home(request):
    template_name = ''
    return render(request, './infoPages/placeList.html')

def population(request):
    return render(request, './infoPages/population.html')

def weather(request):
    return render(request, './infoPages/weather.html')

def restaurant(request):
    return render(request, './infoPages/restaurant.html')

def news(request):
    return render(request, './infoPages/news.html')