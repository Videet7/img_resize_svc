from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from Resize_API import settings, const
import json

def ready_home(request):
    return HttpResponse("This is Home Page")

def send_msg(request, nation=None, sendNumber=None, message=None):
    try:
        auth = {
            "Authorization" : settings.TOKEN
        }
        if nation:
            number = const.NATION[nation] + str(sendNumber)
        payload = {
            "messaging_product" : "whatsapp",
            "to": int(number) if number else sendNumber,
            "type" : "text",
            "text" : {"body" : message}
        }
        response = requests.post(settings.WA_URL, headers=auth, json=payload)
        ans = response.json()
        return HttpResponse(f"Response {ans}")
    except Exception as e:
        if isinstance(e, KeyError):
            send_msg(request=None,nation='ind',sendNumber='9307103565', message=f'Error occurred due to {str(e)}')
        HttpResponse(f"Failed due to {e}")

@csrf_exempt
def whatsAppWebhook(request):
    try:
        if request.method == "GET":
            mode = request.GET['hub.mode']
            token = request.GET['hub.verify_token']
            challenge = request.GET['hub.challenge']

            if token == settings.BASE_TOKEN and mode == "subscribe":
                print("Success")
                return HttpResponse(challenge, status=200)
            else:
                return HttpResponse('error', status=400)
            
        if request.method in ["PUT", "POST"]:
            data = json.loads(request.body)
            send_msg(request,'ind', ph_no, str(data))
            if 'object' in data and 'entry' in data and  data['object'] == 'whatsapp_business_account':
                try:
                    for entry in data['entry']:
                        ph_no = entry['changes'][0]['value']['metadata']['display_phone_number']
                        text = entry['changes'][0]['value']['messages'][0]['text']['body']

                        revert = f"Thank You for you message -- {text}"
                        send_msg(request,'ind', ph_no, revert)
                except Exception as e:
                    send_msg(request,'ind','9307103565', f'Error occurred due to {str(e)}')
                    return HttpResponse("Falied", status=403)
            return HttpResponse("Success", status=200)

    except Exception as e:
        HttpResponse(f"Failed due to {e}")   

        
