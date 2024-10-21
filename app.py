from flask import Flask,request,jsonify
from twilio.rest import client
import requests
import os

app=Flask(__name__)

TWILIO_ACCOUNT_SID=os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN=os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER=os.getenv('TWILIO_WHATSAPP_NUMBER')

@app.route('/receive',methods=['POST'])

def receive_images():
    data=request.get_json()
    person_image=data['person_image_url']
    dress_image=data['dress_image_url']

    result=Hfapi(person_image,dress_image)
    send_response(data['from'],result)

    return jsonify({"status":"Success"})

def Hfapi(person_image,dress_image):
    url="https://huggingface.co/spaces/Kwai-Kolors/Kolors-Virtual-Try-On"
    response=requests.post(url,json={'person_image':person_image,
                                     'dress_image':dress_image})
    return response.json()['result_image']

def send_response(user_id,image_url):

    if(image_url):
        message_body=f"Here is the virtual try-on result:{image_url}"
    else :
        message_body=f"Try-on failed.Please try again "
    
    message=client.messages.create(
        body=message_body,
        from_=TWILIO_WHATSAPP_NUMBER,
        to=f'Whatsapp:{user_id}'
    )

if __name__=='__main__':
    app.run(debug=True)