import requests, os
from Resize_API import settings


class Whatsapp():
    def __init__(self):
        self.auth = {
                    "Authorization" : os.getenv('TOKEN', settings.TOKEN)
                    }
        
    def fetch_image_details(self, image_id):
        try:
            img_url = f'https://graph.facebook.com/v19.0/{image_id}'
            response = requests.get(img_url,headers=self.auth)
            res_json = response.json()
            return res_json
        except Exception as e:
            raise e
                
    def get_image(self, url):
        return requests.get(url ,headers=self.auth).content
    
    def send_message(self, payload):
        url = f'https://graph.facebook.com/v19.0/{os.getenv("PHONE_ID")}/messages'
        return requests.post(url, headers=self.auth, json=payload)
        
    def upload_media(self, path):
        try:
            url = f'https://graph.facebook.com/v19.0/{os.getenv("PHONE_ID")}/media'
            files = {
                'file' : ("file.jpg", open(path, 'rb'), 'image/jpeg')
            }
            data={
                'messaging_product':"whatsapp"
            }
            
            response = requests.post(url, headers=self.auth, files=files, data=data)
            res_id = response.json()
            return res_id['id']
        except Exception as e:
            raise e