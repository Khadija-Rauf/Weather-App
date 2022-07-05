from unicodedata import name
from django.shortcuts import redirect, render
import requests
from .models import City
from .forms import CityForm

def index(request):
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=bbf0aeef1e7951e0b14668448e7c31b9'

    error_message = ''
    warning_message = ''
    message = ''
    message_class = ''

    if request.method == 'POST':
        form = CityForm(request.POST)

        if form.is_valid():
            new_city = form.cleaned_data['name']
            existing_city_count = City.objects.filter(name=new_city).count()

        if existing_city_count == 0:
            r = requests.get(url.format(new_city)).json()

            if r['cod'] == 200:
                form.save()
            else:
                error_message = "City doesn't exist in real!"
        else:
            warning_message = 'City already exists in the database!'

    if error_message:
        message = error_message
        message_class = 'is-danger'
    elif warning_message:
        message = warning_message
        message_class = 'is-warning'                
    else:
        message = 'City added successfully'
        message_class = 'is-success'

    form = CityForm()    

    cities = City.objects.all()

    weather_data = []

    for city in cities:
        r = requests.get(url.format(city)).json()

        t = r['main']['temp']           #converting Farenhite to Centigrade
        c = 0.55 * (t - 32)
        cen = "{:.1f}".format(c)

        city_weather = {
            'city' : city.name,
            'temperature': t,
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
        }

        weather_data.append(city_weather)
        
    context = {
        'weather_data':weather_data,
        'form':form,
        'message':message,
        'message_class':message_class}
    return render(request, 'weatherapp/index.html',context)

def delete_city(request, city_name):
    City.objects.get(name=city_name).delete()
    return redirect('home')