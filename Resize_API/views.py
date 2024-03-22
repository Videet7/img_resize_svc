from django.http import HttpResponse

def ready_home(request):
    return HttpResponse("This is Home Page")

