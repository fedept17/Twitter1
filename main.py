import neca
from neca.generators import print_object, generate_data
from neca.events import *
from neca.settings import app, socket
from flask import Flask, request
import smtplib

import socketio

send_email_user = {}
selected_location = ""
selected_priorities = {}
tweets = []

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
        

@event("tweet")
def tweet_event(context, data):
    tweets.append(data)
    emit("nationwide", data)
    add_data_pie_chart(data)
    check_location_email(data)
    print(data['region'])
    
generate_data('p2000_incidents.json',
              time_scale=50,
              event_name='tweet',
              limit=1000)

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


gmail = "incidenthubweek9@gmail.com"
password = "mikv iudj fwqh dobp" # app password
# real = 'utwenteproject2024!'

@app.route("/filter", methods=["POST"])
def filter():
    filter_priorities = request.json
    print('received json: ' + str(filter_priorities))

    # process data
    emit("location", "data")

@app.route("/api/form", methods=["POST"])
def form():
    # Extract JSON data from the request
    data = request.json

    # Convert email and location to lowercase
    email = data['email'].lower()
    location = data['location'].lower()
    if location not in send_email_user:
        send_email_user[location] = []
    send_email_user[f'{location}'].append(email)
    # Prepare the data to be sent to the event
    lowercased_data = {'email': email, 'location': location}
    print(send_email_user)
    # Fire the global event with the modified data

    return "ok", 200


# starts the server and prevents the program from exiting
neca.start()
