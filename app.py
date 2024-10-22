from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from twilio.rest import Client
import requests
import os

load_dotenv()

app = Flask(__name__)

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')


client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

user_state = {}

@app.route('/receive', methods=['POST'])
def receive_images():
    
    user_id = request.values.get("From")
    num_media = int(request.values.get("NumMedia", 0))

    if user_id not in user_state:
        user_state[user_id] = {"person_image": None, "dress_image": None}

    if num_media == 0:
        response = MessagingResponse()
        response.message("Please send the person's image first.")
        return str(response)

    if not user_state[user_id]["person_image"]:
        user_state[user_id]["person_image"] = request.values.get('MediaUrl0')
        response = MessagingResponse()
        response.message("Got the person's image! Now, please send the dress image.")
        return str(response)
    elif not user_state[user_id]["dress_image"]:
        user_state[user_id]["dress_image"] = request.values.get('MediaUrl0')
        person_image = user_state[user_id]["person_image"]
        dress_image = user_state[user_id]["dress_image"]
        
        result = Hfapi(person_image, dress_image)

        if result:
            send_response(user_id, result)
            user_state[user_id] = {"person_image": None, "dress_image": None}
            return jsonify({"status": "Success"})
        else:
            return jsonify({"status": "Failed to generate try-on result"})

def Hfapi(person_image, dress_image):
    url = "https://huggingface.co/spaces/Kwai-Kolors/Kolors-Virtual-Try-On"
    response = requests.post(url, json={'person_image': person_image, 'dress_image': dress_image})
    if response.status_code == 200:
        return response.json().get('result_image')
    else:
        return None

def send_response(user_id, image_url):
    message = client.messages.create(
        media_url=[image_url],
        from_=TWILIO_WHATSAPP_NUMBER,
        to=user_id
    )
    print(f"Message SID: {message.sid}")

if __name__ == '__main__':
    app.run(debug=True)
