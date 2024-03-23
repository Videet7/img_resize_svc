from django.http import HttpResponse
import requests
from Resize_API import settings
import json

def ready_home(request):
    return HttpResponse("This is Home Page")

def send_msg(sendNumber, message):
    try:
        auth = {
            "Authorization" : settings.TOKEN
        }
        payload = {
            "messaging_product" : "whatsapp",
            "to": sendNumber,
            "type" : "text",
            "text" : {"body" : message}
        }
        response = requests.post(settings.WA_URL, headers=auth, json=payload)
        ans = response.json()
        return ans
    except Exception as e:
        HttpResponse(f"Failed due to {e}")

def whatsAppWebhook(request):
    try:
        if request.method == "GET":
            mode = request.GET['hub.mode']
            token = request.GET['hub.verify_token']
            challenge = request.GET['hub.challenge']

            if token == settings.BASE_TOKEN and mode == "subscribe":
                return HttpResponse(challenge, status=200)
            else:
                return HttpResponse('error', status=400)
            
        if request.method == "POST":
            data = json.loads(request.body)


    except Exception as e:
        HttpResponse(f"Failed due to {e}")   

        
