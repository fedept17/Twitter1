import neca
from neca.generators import print_object, generate_data
from neca.events import *
from neca.settings import app, socket
from flask import Flask, request
import smtplib
import socketio


## default values
send_email_user = {}
selected_location = ""
selected_priorities = {}
tweets = []
gmail = "incidenthubweek9@gmail.com"
password = "mikv iudj fwqh dobp" # app password
# real = 'utwenteproject2024!'


#pie chart
def add_data_pie_chart(data):
    if data['service'] in ["Brandweer", "Politie", "Ambulance"]:
        emit("piecharts", {"action": "add","value": [f"{data['service']}", 1]})
    else:
        emit("piecharts", {"action": "add","value": [f"Other", 1]})

#send email
def check_location_email(data):
    if data['region'].lower() in send_email_user:
        for email in send_email_user[data['region'].lower()]:
            send_email(email, data)
def send_email(receiver_email, data):
    try:
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()  # Start TLS for security
            connection.login(user=gmail, password=password)  # Log in with your email and password

            subject = "[ALERT]"
            message = f"{data['description']}\n{data['related_messages']}"
            full_message = f"Subject: {subject}\n\n{message}"

            connection.sendmail(
                from_addr=gmail,
                to_addrs=receiver_email,
                msg=full_message
            )
            print("Email sent successfully!")
            print (send_email_user)
            connection.quit()

    except Exception as e:
        print(f"An error occurred: {e}")


@app.route("/api/form", methods=["POST"])
def form():
    # Extract JSON data from the request
    data = request.json

    email = data['email'].lower()
    location = data['location'].lower()
    if location not in send_email_user:
        send_email_user[location] = []
    send_email_user[f'{location}'].append(email)

    return "ok", 200

# add nationwide
def add_nationwide_data(data):
    emit("nationwide", data)


# append tweets with priority
def get_alert_priority(data):
    if data['description'][:1] in ['1', '2', '3']:
        tweets.append([data, data['description'][:1]])
    elif data['description'][:2] in ['A1', 'A2', 'A3']:
        tweets.append([data, data['description'][:2].replace("A", "")])
    elif data['description'][:3] in ['P 1', 'P 2', 'P 3']:
        tweets.append([data, data['description'][:3].replace("P ", "")])
    elif data['description'][:6] in ['Prio 1', 'Prio 2', 'Prio 3']:
        tweets.append([data, data['description'][:6].replace("Prio ", "")])
    else:
        tweets.append([data, "non-priority"])


# filter priority
@app.route("/filter_priority", methods=["POST"])
def filter_priority(data):
    filter_priorities = request.json
    print('received json: ' + str(filter_priorities))

    #Need of the function to identify priority to filter only the ones with the input priority
    filtered_data = [entry for entry in data if entry["priority"] in filter_priorities]
    
    socketio.emit("location", {"data": filtered_data})



@event("tweet")
def tweet_event(context, data):
    add_nationwide_data(data)
    add_data_pie_chart(data)
    check_location_email(data)
    get_alert_priority(data)

generate_data('p2000_incidents.json',
              time_scale=10,
              event_name='tweet',
              limit=1000)

# starts the server and prevents the program from exiting
neca.start(port=3100)
