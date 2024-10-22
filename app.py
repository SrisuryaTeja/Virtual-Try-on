from flask import Flask,request,jsonify
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from twilio.rest import Client
import requests
import os

load_dotenv()

app=Flask(__name__)

TWILIO_ACCOUNT_SID=os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN=os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER=os.getenv('TWILIO_WHATSAPP_NUMBER')
TO_NUMBER=os.getenv('TO_NUMBER')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
@app.route('/receive',methods=['POST'])

def receive_images():
    try :
        num_media=int(request.values.get("NumMedia"))
    except (ValueError,TypeError):
        return "Invalid request: invalid or missing NumMedia parameter", 400
    
    if num_media <2 :
        response=MessagingResponse()
        response.message("Please send both the person's image and the dress image.")
        return str(response)
    

    person_image=request.values.get('MediaUrl0')
    dress_image=request.values.get['MediaUrl1']

    result=Hfapi(person_image,dress_image)
    if result:
        send_response(request.values.get("From"),result)
        return jsonify({"status":"Success"})
    else :
        return jsonify({"status":"Failed to generate try-on result"})
    

def Hfapi(person_image,dress_image):
    url="https://huggingface.co/spaces/Kwai-Kolors/Kolors-Virtual-Try-On"
    response=requests.post(url,json={'person_image':person_image,
                                     'dress_image':dress_image})
    if response.status_code ==200:
        return response.json().get('result_image')
    else :
        return None

def send_response(user_id,image_url):
    message=client.messages.create(
        # body=message_body,
        media_url=[image_url],
        from_=TWILIO_WHATSAPP_NUMBER,
        to=user_id
    )
    print(message.sid)

if __name__=='__main__':
    app.run(debug=True)