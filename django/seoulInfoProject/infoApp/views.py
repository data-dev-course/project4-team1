from django.shortcuts import render
from django.core.paginator import Paginator
from infoApp.models import Place

PATH = ""


# Create your views here.
def placeList(request):
    template_name = ""
    place = Place.objects.all()
    paginator = Paginator(place, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}
    return render(request, PATH + "infoPages/placeList.html", context)


def population(request):
    return render(request, PATH + "infoPages/population.html")


def weather(request):
    return render(request, PATH + "infoPages/weather.html")


def restaurant(request):
    return render(request, PATH + "infoPages/restaurant.html")


def news(request):
    return render(request, PATH + "infoPages/news.html")
