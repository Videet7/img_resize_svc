import os 
import requests

from Resize_API import const, settings

def revert(request, nation=None, sendNumber=None, message=None, type=None):
    try:
        auth = {
            "Authorization" : os.getenv('TOKEN', settings.TOKEN)
        }
        number = None
        if nation and len(sendNumber) == 10:
            number = const.NATION[nation] + str(sendNumber)
        if type and type == 'text':
            payload = {
                "messaging_product" : "whatsapp",
                "to": int(number) if number else sendNumber,
                "type" : "template",
                "template": { 
                "name": "welcome",
                "language": { "code": "en_US" }, 
                "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": message
                        }
                    ]
                }
                ]
            } }

        if type and type == 'image':
            payload = {
                "messaging_product" : "whatsapp",
                "to": int(number) if number else sendNumber,
                "type": "template",
                "template": {
                        "name": "updated_image",
                        "language": {
                            "code": "en_US"
                            },
                        "components": [
                            {
                            "type": "header",
                            "parameters": [
                                    {
                                        "type": "image",
                                        "image": {
                                        "link": message
                                        }
                                    }
                                ]
                        }
                    ]
                }
            }
        response = requests.post(os.getenv('WA_URL', settings.WA_URL), headers=auth, json=payload)
        ans = response.json()
        return ans
    except Exception as e:
        if isinstance(e, KeyError):
            revert(request=None,nation='ind',sendNumber= os.getenv('PH_NO'), message=f'Error occurred due to {str(e)}')


def if_type_text(request, entry, data):
    try:
        if 'messages' in entry['changes'][0]['value'] and 'text' in entry['changes'][0]['value']['messages'][0]['type']:
            revert(request,'ind', os.getenv('PH_NO'), str(data), "text")
            ph_no = entry['changes'][0]['value']['messages'][0]['from']
            text = entry['changes'][0]['value']['messages'][0]['text']['body']
            if text:
                reply = f"Thank You for your message -- {text}"
            revert(request,'ind', ph_no, text, 'text')
    except Exception as e:
        revert(request=None,nation='ind',sendNumber= os.getenv('PH_NO'), message=f'Error occurred due to {str(e)}')

def if_type_image(request, entry, data):
    try:
        if 'messages' in entry['changes'][0]['value'] and 'image' in entry['changes'][0]['value']['messages'][0]['type']:
            revert(request,'ind', os.getenv('PH_NO'), str(data), "image")
            ph_no = entry['changes'][0]['value']['messages'][0]['from']
            image_id = entry['changes'][0]['value']['messages'][0]['image']['id']
            if image_id:
                auth = {
                    "Authorization" : os.getenv('TOKEN')
                    }
                img_url = f'https://graph.facebook.com/v19.0/{image_id}'
                response = requests.get(img_url,headers=auth)
                res_json = response.json()
                img_url = res_json.get("url",None)
                revert(request,'ind', ph_no, img_url, 'image')
    except Exception as e:
        revert(request=None,nation='ind',sendNumber= os.getenv('PH_NO'), message=f'Error occurred due to {str(e)}')