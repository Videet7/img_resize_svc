from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .common import revert, if_type_text, if_type_button, if_type_image

import requests
import json
import os

def ready_home(request):
    return HttpResponse("This is Home Page")

def send_msg(request, nation=None, sendNumber=None, message=None):
    try:
        ans = revert(request, nation, sendNumber, message, 'text')
        return HttpResponse(f"Response {ans}")
    except Exception as e:
        HttpResponse(f"Failed due to {e}")

@csrf_exempt
def whatsAppWebhook(request):
    try:
        if request.method == "GET":
            mode = request.GET['hub.mode']
            token = request.GET['hub.verify_token']
            challenge = request.GET['hub.challenge']

            if token == os.getenv('BASE_TOKEN') and mode == "subscribe":
                print("Success")
                return HttpResponse(challenge, status=200)
            else:
                return HttpResponse('error', status=400)
            
        if request.method == "POST":
            data = json.loads(request.body)
            try:
                if data['object'] == 'whatsapp_business_account':
                    for entry in data['entry']:
                        if_type_text(request, entry, data)
                        if_type_button(request, entry , data)
                        if_type_image(request, entry, data)
                return HttpResponse("Success", status=200)
            except Exception as err:
                return HttpResponse(f"Failed due to {err}")

    except Exception as e:
        HttpResponse(f"Failed due to {e}")       
