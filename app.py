from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from twilio.rest import Client
from gradio_client import Client as GradioClient, handle_file
import os

load_dotenv()

app = Flask(__name__)

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

user_state = {}
gradio_client = GradioClient("Nymbo/Virtual-Try-On")

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
    try:
        result = gradio_client.predict(
            dict={"background": handle_file(person_image), "layers": [], "composite": None},
            garm_img=handle_file(dress_image),
            garment_des="Generated with AI",
            is_checked=True,
            is_checked_crop=False,
            denoise_steps=30,
            seed=42,
            api_name="/tryon"
        )
        return result
    except Exception as e:
        print(f"Error calling Gradio API: {e}")
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

