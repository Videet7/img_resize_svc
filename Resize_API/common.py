import os 
import requests, random
from Resize_API import const, settings

def revert(request, nation=None, payload=None, type=None):
    try:
        auth = {
            "Authorization" : os.getenv('TOKEN', settings.TOKEN)
        }
        number = None
        if nation and len(str(payload['ph_no'])) == 10:
            number = const.NATION[nation] + str(payload['ph_no'])
        if type and type == 'text':
            payload = {
                "messaging_product" : "whatsapp",
                "to": int(number) if number else payload['ph_no'],
                "type" : "template",
                "template": { 
                "name": "resizer",
                "language": { "code": "en_US" }, 
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "text",
                                "text": payload['name'] if payload['name'] else payload['text']
                            }
                        ]
                    }
                ]
            } }

        if type and type == 'image':
            payload = {
                "messaging_product" : "whatsapp",
                "to": int(number) if number else payload['ph_no'],
                "type": "template",
                "template": {
                        "name": "test_reply",
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
                                        "id": payload['image_id']
                                        }
                                    }
                                ]
                        }
                    ]
                }
            }
        if type and type == 'reply':
            payload = {
                "messaging_product" : "whatsapp",
                "to": int(number) if number else payload['ph_no'],
                "type" : "text",
                "text": {'body':payload['reply']}
                }
        response = requests.post(os.getenv('WA_URL', settings.WA_URL), headers=auth, json=payload)
        ans = response.json()
        return ans
    except Exception as e:
        if isinstance(e, KeyError):
            revert(request=None,nation='ind', payload={'ph_no': os.getenv('PH_NO'), 'text':f'Error occurred due to {str(e)}'})


def if_type_text(request, entry, data):
    try:
        if 'messages' in entry['changes'][0]['value'] and 'text' in entry['changes'][0]['value']['messages'][0]['type']:
            payload  = {}
            payload["reply"] = str(data)
            revert(request,'ind', payload, 'reply')
            payload['ph_no'] = entry['changes'][0]['value']['messages'][0]['from'] or None
            payload['text'] = entry['changes'][0]['value']['messages'][0]['text']['body'] or None
            payload['name'] = entry['changes'][0]['value']['contacts'][0]['profile']['name'] or None
            if payload['text'] == 'Image Resize' or "*" in payload['text']:
                return image_resize(request, payload)
            revert(request,'ind', payload, 'text')
    except Exception as e:
        revert(request=None,nation='ind',payload={'ph_no': os.getenv('PH_NO'), 'text':f'Error occurred due to {str(e)}'})

def image_resize(request, payload):
    if "*" in payload['text']:
        payload["reply"] = "Please upload the image to be resized"
        return revert(request,'ind', payload, 'reply')
    payload["reply"] = "Please entry the new dimensions in following format \nLenght * Width"
    return revert(request,'ind', payload, 'reply')

def if_type_image(request, entry, data):
    try:
        if 'messages' in entry['changes'][0]['value'] and 'image' in entry['changes'][0]['value']['messages'][0]['type']:
            payload  = {}
            payload['ph_no'] = entry['changes'][0]['value']['messages'][0]['from'] or None
            payload['image_id'] = entry['changes'][0]['value']['messages'][0]['image']['id'] or None
            if payload['image_id']:
                auth = {
                    "Authorization" : os.getenv('TOKEN', settings.TOKEN)
                    }
                img_url = f'https://graph.facebook.com/v19.0/{payload["image_id"]}'
                response = requests.get(img_url,headers=auth)
                res_json = response.json()
                download_url = res_json.get("url",None)
                res = requests.get(download_url,headers=auth).content
                filename = "Image/whatsapps_image_" + str(random.randrange(1,10000)) + '.jpg'
                with open(filename, 'wb') as handler:
                    handler.write(res)
                revert(request,'ind', payload, 'image')
    except Exception as e:
        revert(request=None,nation='ind',payload={'ph_no': os.getenv('PH_NO'), 'text':f'Error occurred due to {str(e)}'})