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
PHONENUMBER = os.environ['PHONENUMBER']
DATABASE_NAME = os.environ["DATABASE_NAME"]
PROJECT_KEY = os.environ["PROJECT_KEY"]
client = Client(account_sid, auth_token)

deta = Deta(PROJECT_KEY)
db = deta.Base(DATABASE_NAME)


app = Flask(__name__, static_url_path='')


def format_options(options):
    options_with_text_formating = [
                f"{str(item_number+1)}) - {option}"
                for item_number, option  in enumerate( options)
              ]
    return "\n".join(options_with_text_formating)
welcome_text ="""Text to buy: 
#1 - latest posts
#2 - free stuff
#3 - for sale
Type 1, 2, or 3"""

welcome_options = [
 "latest posts",
 "free stuff",
 "for sale"
]
menu_options = [
"back",
# "photo",
# "more details",
# "message",
]
latest_posts = [
    "$185 Commencal ebike 2021(Pa lo Alto)",
    "$30  snow tire chains (gilroy)",
    # "$10  Yard chairs (alameda)",
    "$35  Wheelchair (santa cruz)",
]


listings = {
    "1":"""
Commencal ebike 2021 - $185 (Palo Alto)
With wireless charging case. Can be used through Bluetooth. top quality earbuds. Sealed.....
""",
    "2":"""
snow tire chains - $30 (Santa Cruz)
New Volt snow tire chains. Never been used, these don’t fit my current vehicle. Looking up QV339 will give you a list of compatible tire sizes
""",
  "3":"""
Wheelchair - $35 (sunnyvale)
Wheelchair for sale.
Good condition, sturdy, comfy!
$35 come and get it!
"""
}

pages = {
    "main_page": lambda options: f"""
Text To Buy: 
Easiest way to buy&sell stuff via Text or Whatsapp!
{format_options(options)}""",
    "latest_posts": lambda options: f"""
Latest stuff:
{format_options(options)}
{len(options)+1}) - More...
""",
    "listing": lambda listing_id, menu_options=[]: f"{listings[listing_id]}{format_options(menu_options)}",
    "try_again":lambda _=None,__=None: "Sorry please try again"
}

def send_message(message, 
                 from_number = 'whatsapp:+14155238886',
                 status_callback = 'https://ekpert.deta.dev/status', 
                 media_url = [], ## ['https://ekpert.deta.dev/static/car_v1.jpg']
                 to_number = PHONENUMBER):
    return client.messages.create(
                            from_ = from_number,
                            to = to_number,
                            body=message,
                            status_callback = status_callback,
                            media_url = media_url,
                        )

formate_input = lambda text: text.strip()
def db_put(data,phonenumber=PHONENUMBER):
    db_response = db.put(data, PHONENUMBER)
    print(f"put: {db_response}")

def db_insert(data,phonenumber=PHONENUMBER):
    db_response = db.insert(data, PHONENUMBER)
    print(f"insert: {db_response}")
    

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    print("/sms")
    resp = MessagingResponse()

    # Add a message
    resp.message("The Robots are coming! Head for the hills!")
    print(resp)
    return str(resp)
@app.route("/sms_recieve", methods=["POST"])
def sms_recieve():
    print("/sms_recieve")
    number = request.form["From"]
    message_body = request.form["Body"]
    
    from_number = 'whatsapp:+14155238886' 
    status_callback = 'https://ekpert.deta.dev/status'
    media_url = []
    menu_selection = formate_input(message_body)
    
    user_state = db.get(PHONENUMBER)
    print(f"get: {user_state}")
    if not user_state:
        # note "menu_selection": menu_selection is a db hackable point please sanitize input
        db_insert({"page": "main_page", "page_id": None,"prev_page":None, "menu_selection": menu_selection })
        send_message(pages['main_page'](welcome_options))
        
    elif user_state["page"] == "main_page":
        db_put({"page": "latest_posts", "page_id": None , "prev_page":"main_page", "menu_selection": menu_selection })
        send_message(pages["latest_posts"](latest_posts))
        
    elif user_state["page"] == "latest_posts":
        page = ""
        if menu_selection == "1":
            page = user_state["main_page"] # which actually directs to latest_posts
        else:
            page = "try_again"
        db_put({"page": page, "page_id": None , "prev_page":"latest_posts", "menu_selection": menu_selection })
        send_message(pages["listing"](menu_selection, menu_options))
    elif user_state["page"] == "try_again":
        db_put({"page": user_state["prev_page"] , "page_id": None , "prev_page":"try_again", "menu_selection": menu_selection })
        send_message(pages["try_again"]())
    else:
        send_message("Please type a number, ex: '1','2','3'")

        
    print(f" Number: {number}, Message Body: {message_body}")
    
    resp = MessagingResponse()
    resp.message(f"/sms_recieve worked!  Number: {number}, Message Body: {message_body}")
    
    return (str(resp),204)


@app.route("/send", methods=['GET'])
def send_page():
    """EX: https://ekpert.deta.dev/send"""
    print("/send")
    
    db_put({"page": "main_page", "page_id": None,"prev_page": None, "menu_selection": None  })
    
  
    message = send_message(pages['main_page'](welcome_options))
    user_state = db.get(PHONENUMBER)
    print(f"After Update: {user_state}")
    
    print(message.sid)
    return f"{message.sid}"
@app.route('/static/<path:path>')
def send_files(path):
    """EX: https://ekpert.deta.dev/static/car_v1.jpg"""
    print(path)
    return send_from_directory("./static",path)
@app.route('/status',methods=["POST","GET"])
def status():
    print("/status")
    message_sid = request.values.get('MessageSid', None)
    message_status = request.values.get('MessageStatus', None)
    sms_status = request.values.get('SmsStatus', None)
    logging.info('SID: {}, Status: {}'.format(message_sid, message_status))

    print(f'SID: {message_sid}, Status: {message_status}' )
    return ('please use post request on /static, or look at application logs', 204)
    
if __name__ == "__main__":
    app.run(debug=True)
