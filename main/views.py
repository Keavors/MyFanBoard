from django.shortcuts import render

def home(request):
    # Очень простое представление, которое просто рендерит шаблон
    return render(request, 'main/home.html', {})