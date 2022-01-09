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
    print(f" Number: {number}, Message Body: {message_body}")
    resp = MessagingResponse()
    resp.message(f"/sms_recieve worked!  Number: {number}, Message Body: {message_body}")
    return (str(resp),204)


@app.route("/send", methods=['GET'])
def send_message():
    """EX: https://ekpert.deta.dev/send"""

    message = client.messages.create(
                              from_='whatsapp:+14155238886',
                              body='#1-back,#2-more info: 2015 Honda accord sport low miles - $18,500 (sacramento)',
                              to=myphonenumber,
                              status_callback='https://ekpert.deta.dev/status',
                              media_url=['https://ekpert.deta.dev/static/car_v1.jpg'],
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
