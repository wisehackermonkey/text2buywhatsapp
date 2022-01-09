import os
import logging
from deta import Deta
from twilio.rest import Client
from flask import Flask, request, redirect, send_from_directory
from twilio.twiml.messaging_response import Message, MessagingResponse
from twilio import twiml

logging.basicConfig(level=logging.INFO)

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
myphonenumber = os.environ['PHONENUMBER']
DATABASE_NAME = os.environ["DATABASE_NAME"]
PROJECT_KEY = os.environ["PROJECT_KEY"]
client = Client(account_sid, auth_token)

deta = Deta(PROJECT_KEY)
db = deta.Base(DATABASE_NAME)


app = Flask(__name__, static_url_path='')

welcome_text ="""Text to buy: 
#1 - latest posts
#2 - free stuff
#3 - for sale
Type 1, 2, or 3"""



def send_message(message, from_number, to_number, status_callback, media_url):
    """send_message

    Args:
        message ([str]): [description]
        from_number ([str]): [description]
        to_number ([str]): [description]
        status_callback ([str]): [description]
        media_url ([List]): [description]
    """
    message = client.messages.create(
                            from_=from_number,
                            to=to_number,
                            body=message,
                            status_callback=status_callback,
                            media_url=media_url,
                        )
    return message

formate_input = lambda text: text.strip()

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    resp = MessagingResponse()

    # Add a message
    resp.message("The Robots are coming! Head for the hills!")
    print(resp)
    return str(resp)
@app.route("/sms_recieve", methods=["POST"])
def sms_recieve():
    number = request.form["From"]
    message_body = request.form["Body"]
    
    from_number = 'whatsapp:+14155238886' 
    status_callback = 'https://ekpert.deta.dev/status'
    media_url = []
    option = formate_input(message_body)
    
    if option == "1":
        message = """
Latest stuff:
1) $185 AirPod Pro  (Santa Clara)
2) $30  snow tire chains (gilroy)
3) $10  Yard chairs (alameda)
4) $35  Wheelchair (santa cruz)
5) More...
"""
        message = client.messages.create(
                                from_=from_number,
                                to=myphonenumber,
                                body=message,
                                status_callback=status_callback,
                                media_url=media_url,
                            )
        # send_message(message, from_number, myphonenumber, status_callback, media_url)
    else:
        message = """
Please type "1","2","3"
"""
        send_message(message, from_number, myphonenumber, status_callback, media_url)

        
    print(f" Number: {number}, Message Body: {message_body}")
    
    resp = MessagingResponse()
    resp.message(f"/sms_recieve worked!  Number: {number}, Message Body: {message_body}")
    
    return (str(resp),204)


@app.route("/send", methods=['GET'])
def send_message():
    """EX: https://ekpert.deta.dev/send"""
    # message = send_message(welcome_text,
    #     'whatsapp:+14155238886',
    #     myphonenumber,
    #     'https://ekpert.deta.dev/status',
    #     ['https://ekpert.deta.dev/static/car_v1.jpg']
    # )
    
    message = client.messages.create(
                        from_='whatsapp:+14155238886',
                        to=myphonenumber,
                        body=welcome_text,
                        status_callback='https://ekpert.deta.dev/status',
                 )

    print(message.sid)
    return str(message.sid)
@app.route('/static/<path:path>')
def send_files(path):
    """EX: https://ekpert.deta.dev/static/car_v1.jpg"""
    print(path)
    return send_from_directory("./static",path)
@app.route('/status',methods=["POST","GET"])
def status():
    message_sid = request.values.get('MessageSid', None)
    message_status = request.values.get('MessageStatus', None)
    sms_status = request.values.get('SmsStatus', None)
    logging.info('SID: {}, Status: {}'.format(message_sid, message_status))

    print(f'SID: {message_sid}, Status: {message_status}' )
    return ('please use post request on /static, or look at application logs', 204)
    
if __name__ == "__main__":
    app.run(debug=True)
