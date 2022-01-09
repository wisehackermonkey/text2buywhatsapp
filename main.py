# from flask import Flask
# from twilio.twiml.messaging_response import Body, Message, Redirect, MessagingResponse


# app = Flask(__name__)

# @app.route('/', methods=["GET"])
# def hello_world():
#     return "Hello World"

# @app.route("/oran", methods=["get"])
# def text_oran
# response = MessagingResponse()
# message = Message()
# message.body('Hello World!')
# response.append(message)
# response.redirect('https://demo.twilio.com/welcome/sms/')

# print(response)

from flask import Flask, request, redirect, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
import os
from twilio.rest import Client
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
myphonenumber = os.environ['PHONENUMBER']
client = Client(account_sid, auth_token)


app = Flask(__name__, static_url_path='')

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    resp = MessagingResponse()

    # Add a message
    resp.message("The Robots are coming! Head for the hills!")
    print()
    return str(resp)
@app.route("/send", methods=['GET'])
def send_message():
    message = client.messages.create(
                              from_='whatsapp:+14155238886',
                              body='Your {{1}} code is {{2}}',
                              to=myphonenumber,
                                media_url=['https://demo.twilio.com/owl.png'],


                          )

    print(message.sid)
    return str(message.sid)
@app.route('/static/<path:path')
def send_files(path):
    return send_from_directory("static",path)
if __name__ == "__main__":
    app.run(debug=True)
