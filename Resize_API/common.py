import os 
import requests
from Resize_API import const, settings
from .wa_utils import Whatsapp
from PIL import Image 

def revert(request, nation=None, payload=None, type=None):
    try:
        auth = {
            "Authorization" : os.getenv('TOKEN', settings.TOKEN)
        }
        number = None
        if nation and "ph_no" in payload and len(str(payload['ph_no'])) == 10:
            number = const.NATION[nation] + str(payload['ph_no'])
        if type and type == 'text':
            payload = {
                "messaging_product" : "whatsapp",
                "to": int(number) if number else payload['ph_no'],
                "type" : "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": f"Hi {payload['name']}, \nWelcome to Whatsapp Image."
                    },
                    "action": {
                    "buttons": [
                        {
                        "type": "reply",
                        "reply": {
                            "id": "5687687",
                            "title": "Image Resize"
                        }
                        },
                        {
                        "type": "reply",
                        "reply": {
                            "id": "8687901",
                            "title": "Food Suggestions"
                        }
                        }
                    ]
                    }
                }
            }

        if type and type == 'image':
            payload = {
                "messaging_product" : "whatsapp",
                "to": int(number) if number else payload['ph_no'],
                "type": "document",
                "document": {
                "id": payload['upload_img_id'] if 'upload_img_id' in payload else payload['image_id']
                }
            }

        if type and type == 'reply':
            payload = {
                "messaging_product" : "whatsapp",
                "to": int(number) if number else payload['ph_no'] if "ph_no" in payload else os.getenv("PH_NO"),
                "type" : "text",
                "text": {'body':payload['reply']}
                }
        
        if type and type == 'body': 
            payload = {
                "messaging_product" : "whatsapp",
                "to": os.getenv("PH_NO"),
                "type" : "text",
                "text": {'body':payload}
                }
            
        response = Whatsapp().send_message(payload)
        ans = response.json()
        return ans
    except Exception as e:
        if isinstance(e, KeyError):
            revert(request=None,nation='ind', payload={'ph_no': os.getenv('PH_NO'), 'text':f'Error occurred due to {str(e)}'})
        raise e

def if_type_text(request, entry, data):
    try:
        if 'messages' in entry['changes'][0]['value'] and 'text' in entry['changes'][0]['value']['messages'][0]['type']:
            payload  = {}
            payload['ph_no'] = entry['changes'][0]['value']['messages'][0]['from'] or None
            payload['text'] = entry['changes'][0]['value']['messages'][0]['text']['body'] or None
            payload['name'] = entry['changes'][0]['value']['contacts'][0]['profile']['name'] or None
            if "*" in payload['text']:
                #_ = mongo_obj.save_to_mongo(data, "image_resolution")
                return resize_image(request, payload)
            #_ = mongo_obj.save_to_mongo(data, "wa_text")
            revert(request,'ind', payload, 'text')
    except Exception as e:
        revert(request=None,nation='ind',payload={'ph_no': os.getenv('PH_NO'), 'text':f'Error occurred due to {str(e)}'})
        raise e
    
def if_type_button(request, entry, data):
    try:
        if 'messages' in entry['changes'][0]['value'] and entry['changes'][0]['value']['messages'][0]['type'] in ['button', 'interactive']:
            #_ = mongo_obj.save_to_mongo(data, "wa_button")
            payload = {}
            payload['ph_no'] = entry['changes'][0]['value']['messages'][0]['from'] or None
            try:
                payload['text'] = entry['changes'][0]['value']['messages'][0]['button']['text']
            except:
                payload['text'] = entry['changes'][0]['value']['messages'][0]['interactive']['button_reply']['title']
            reply_message(request, payload)
    except Exception as e:
        revert(request=None,nation='ind',payload={'ph_no': os.getenv('PH_NO'), 'text':f'Error occurred due to {str(e)}'})
        raise e

def reply_message(request, payload):
    try:
        if "food" in str(payload['text']).lower():
            payload["reply"] = "Please upload the food related image."
            return revert(request,'ind', payload, 'reply')
        if "exit" in str(payload['text']).lower():
            payload["reply"] = "Thank You and Good Bye"
            return revert(request,'ind', payload, 'reply')
        payload["reply"] = "Please send us the image to be resized"
        return revert(request,'ind', payload, 'reply')
    except Exception as e:
        revert(request=None,nation='ind',payload={'ph_no': os.getenv('PH_NO'), 'text':f'Error occurred due to {str(e)}'})
        raise e

def if_type_image(request, entry, data):
    try:
        if 'messages' in entry['changes'][0]['value'] and 'image' in entry['changes'][0]['value']['messages'][0]['type']:
           # _ = mongo_obj.save_to_mongo(data, "wa_image")  #Save incoming image object into mongo
            payload  = {}
            payload['ph_no'] = entry['changes'][0]['value']['messages'][0]['from'] or None
            payload['image_id'] = entry['changes'][0]['value']['messages'][0]['image']['id'] or None
            
            if payload['image_id']:
                res_json = Whatsapp().fetch_image_details(payload['image_id']) #Fetch image details based on image id
                mongo_data = {
                    'image_id' : Whatsapp().get_image(res_json.get("url",None))
                }
               # _ = mongo_obj.save_to_mongo(mongo_data, "saved_images") #Save image into mongo

                #Saving fetched image to local temporarily
                with open(const.FILE_NAME, 'wb') as handler:
                    handler.write(mongo_data['image_id'])
                
                payload["reply"] = "Please share the dimensions in following format -- \nLength * Width"
                return revert(request,'ind', payload, 'reply')
            
    except Exception as e:
        revert(request=None,nation='ind',payload={'ph_no': os.getenv('PH_NO'), 'text':f'Error occurred due to {str(e)}'})
        raise e
    
def resize_image(request, payload):
    try:
        img_obj = Image.open(const.FILE_NAME)
        os.remove(const.FILE_NAME)
        resolution = tuple(map(int,payload['text'].split('*')))
        img_obj = img_obj.resize(resolution)
        img_obj.save(const.NEW_FILE_NAME)
        payload['updated_image_id'] = Whatsapp().upload_media(const.NEW_FILE_NAME)
        os.remove(const.NEW_FILE_NAME)

        #Fetch uploaded image id using updated image id
        res_json = Whatsapp().fetch_image_details(payload['updated_image_id'])
        payload['upload_img_id'] = res_json.get('id', None)

        revert(request,'ind', payload, 'image')

    except Exception as e:
        revert(request=None,nation='ind',payload={'ph_no': os.getenv('PH_NO'), 'text':f'Error occurred due to {str(e)}'})
        raise e   