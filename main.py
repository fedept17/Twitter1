from crypt import methods

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
current_piechart_type = "nationwide"
tweets = []
gmail = "incidenthubweek9@gmail.com"
password = "mikv iudj fwqh dobp" # app password
# real = 'utwenteproject2024!'
current_region_calls_count = {'nationwide': {"Brandweer": 0, "Politie":0, "Ambulance":0, "Other":0}}

#pie chart

def count_calls_region(data):
    if data['region'] not in current_region_calls_count:
        current_region_calls_count[data['region']] = {"Brandweer": 0, "Politie":0, "Ambulance":0, "Other":0}

    if data['service'] in ["Brandweer", "Politie", "Ambulance"]:
        current_region_calls_count[data['region']][data['service']] += 1
        current_region_calls_count['nationwide'][data['service']] += 1

    else:
        current_region_calls_count[data['region']]['Other'] += 1
        current_region_calls_count['nationwide']['Other'] += 1

def add_nationwide_pie_chart():
    emit("piecharts", {"action": "set",
                       "value": ["Brandweer", current_region_calls_count['nationwide'].get('Brandweer')]})
    emit("piecharts",
         {"action": "set", "value": ["Politie", current_region_calls_count['nationwide'].get('Politie')]})
    emit("piecharts", {"action": "set",
                       "value": ["Ambulance", current_region_calls_count['nationwide'].get('Ambulance')]})
    emit("piecharts",
         {"action": "set", "value": ["Other", current_region_calls_count['nationwide'].get('Other')]})

def add_regional_pie_chart():
    global selected_region
    if selected_region not in current_region_calls_count:
        emit("piecharts", {"action": "set",
                           "value": ["Brandweer", 0]})
        emit("piecharts",
             {"action": "set", "value": ["Politie", 0]})
        emit("piecharts", {"action": "set",
                           "value": ["Ambulance", 0]})
        emit("piecharts",
             {"action": "set", "value": ["Other", 0]})
    else:
        emit("piecharts", {"action": "set",
                           "value": ["Brandweer", current_region_calls_count[selected_region].get('Brandweer')]})
        emit("piecharts",
             {"action": "set", "value": ["Politie", current_region_calls_count[selected_region].get('Politie')]})
        emit("piecharts", {"action": "set",
                           "value": ["Ambulance", current_region_calls_count[selected_region].get('Ambulance')]})
        emit("piecharts",
             {"action": "set", "value": ["Other", current_region_calls_count[selected_region].get('Other')]})

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
    print(data)
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
    global current_piechart_type
    current_piechart_type = type

    if current_piechart_type == "nationwide":
        add_nationwide_pie_chart()
    else:
        add_regional_pie_chart()



# filter priority
@socket.on("filter")
def filter(data):
    global selected_region, selected_priorities
    if current_piechart_type == "region":
        add_regional_pie_chart()


    selected_region, selected_priorities = data
    
    #Need of the function to identify priority to filter only the ones with the input priority and region
    filtered_data = [entry for entry in tweets if (entry["priority"] in selected_priorities and entry["region"] == selected_region)]

    emit("filtered_region", filtered_data)

@event("tweet")
def tweet_event(context, data):
    extract_priority(data)
    add_nationwide_data(data)
    add_region_data(data)
    check_location_email(data)
    tweets.append(data)
    count_calls_region(data)

    if current_piechart_type == "nationwide":
        add_nationwide_pie_chart()
    else:
        add_regional_pie_chart()

generate_data('p2000_incidents.json',
              time_scale=3,
              event_name='tweet',
              limit=10000)

# starts the server and prevents the program from exiting
neca.start(port=3200)
