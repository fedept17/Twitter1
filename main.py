import neca
from neca.generators import print_object, generate_data
from neca.events import *
from neca.settings import app, socket
from flask import Flask, request
import smtplib
import socketio


## default values
send_email_user = {}
selected_region = ""
selected_priorities = {"p1", "p2", "p3", "non-priority"}
piechart_type = "nationwide"
tweets = []
gmail = "incidenthubweek9@gmail.com"
password = "mikv iudj fwqh dobp" # app password
# real = 'utwenteproject2024!'
5

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
            connection.starttls()  # Start TLS for security5
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

def add_region_data(data):
    if data['region'] == selected_region and data['priority'] in selected_priorities:
        emit("region", data)


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

def extract_priority(data):
    if data['description'][:1] in ['1', '2', '3']:
        data["priority"] = "p"+data['description'][0]
        data["description"] = data['description'][1:]
    elif data['description'][:2].lower() in ['a1', 'a2', 'a3']:
        data["priority"] = "p"+data['description'][1]
        data["description"] = data['description'][2:]
    elif data['description'][:3].lower() in ['p 1', 'p 2', 'p 3']:
        data["priority"] = "p"+data['description'][2]
        data["description"] = data['description'][3:]
    elif data['description'][:6].lower() in ['prio 1', 'prio 2', 'prio 3']:
        data["priority"] = "p"+data['description'][5]
        data["description"] = data['description'][6:]
    else:
        data["priority"] = "non-priority"

@socket.on("piechart-type")
def piechart(type):
    # type = "nationwide" or "region"
    # change pie chart
    pass

# filter priority
@socket.on("filter")
def filter(data):
    global selected_region, selected_priorities

    if piechart_type == "region" and data[0] != selected_region:
        # change pie chart
        pass

    selected_region, selected_priorities = data
    
    #Need of the function to identify priority to filter only the ones with the input priority and region
    filtered_data = [entry for entry in tweets if (entry["priority"] in selected_priorities and entry["region"] == selected_region)]

    emit("filtered_region", filtered_data)

@event("tweet")
def tweet_event(context, data):
    extract_priority(data)

    add_nationwide_data(data)
    add_region_data(data)
    add_data_pie_chart(data)
    check_location_email(data)
    tweets.append(data)
    # get_alert_priority(data)

generate_data('p2000_incidents.json',
              time_scale=10,
              event_name='tweet',
              limit=10000)

# starts the server and prevents the program from exiting
neca.start(port=3100)
