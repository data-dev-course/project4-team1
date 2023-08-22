from django.shortcuts import render
from django.core.paginator import Paginator
from info_app.models import Place

PATH = ""
# Create your views here.
def placeList(request):
    template_name = ''
    place = Place.objects.all()
    paginator = Paginator(place, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj" : page_obj,
    }
    return render(request, PATH + 'infoPages/placeList.html', context)

def population(request):

    q = [
            { 'dt' : '2023-08-20 14:00', 'pplt':'3000~4000'},
            { 'dt' : '2023-08-20 15:00', 'pplt':'5000~6000'},
            { 'dt' : '2023-08-20 16:00', 'pplt':'4000~5000'},
        ]
    q2 = [1,2,3,4,5]

    context = {'q_set' : q}
    return render(request, PATH + 'infoPages/population.html', context)

def weather(request):
    return render(request, PATH + 'infoPages/weather.html')

def restaurant(request):
    return render(request, PATH + 'infoPages/restaurant.html')

def news(request):
    return render(request, PATH + 'infoPages/news.html')