import neca
from neca.generators import print_object, generate_data
from neca.events import *
from neca.settings import app, socket
from flask import Flask, request
import smtplib

# your code here

#pie chart
def add_data_pie_chart(data):
    if data['service'] in ["Brandweer", "Politie", "Ambulance"]:
        emit("piecharts", {"action": "add","value": [f"{data['service']}", 1]})
    else:
        emit("piecharts", {"action": "add","value": [f"Other", 1]})

@event("tweet")
def tweet_event(context, data):
    add_data_pie_chart(data)
    
generate_data('p2000_incidents.json',
              time_scale=100,
              event_name='tweet',
              limit=1000)


def send_email(user_data):
    receiver_email = user_data['email']
    try:
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()  # Start TLS for security
            connection.login(user=gmail, password=password)  # Log in with your email and password

            subject = "[ALERT]"
            message = "You good?"
            full_message = f"Subject: {subject}\n\n{message}"

            connection.sendmail(
                from_addr=gmail,
                to_addrs=receiver_email,
                msg=full_message
            )
            print("Email sent successfully!")

            connection.quit()

    except Exception as e:
        print(f"An error occurred: {e}")


gmail = "incidenthubweek9@gmail.com"
password = "mikv iudj fwqh dobp" # app password
# real = 'utwenteproject2024!'

@app.route("/api/form", methods=["POST"])
def form():
    # Extract JSON data from the request
    data = request.json

    # Convert email and location to lowercase
    email = data['email'].lower()
    location = data['location'].lower()

    # Prepare the data to be sent to the event
    lowercased_data = {'email': email, 'location': location}

    send_email(lowercased_data)
    # Fire the global event with the modified data

    return "ok", 200


# starts the server and prevents the program from exiting
neca.start()
