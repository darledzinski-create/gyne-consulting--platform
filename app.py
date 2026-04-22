from flask import Flask, request, redirect, url_for, render_template
from datetime import datetime
import os
from mailjet_rest import Client

app = Flask(__name__)

@app.route("/")
def homepage():
    return render_template("home.html")


@app.route("/consultation", methods=["GET", "POST"])
def consultation():

    if request.method == "POST":
        try:
            print("🔥 POST RECEIVED")

            name = request.form.get("name")
            email = request.form.get("email")
            urgency = request.form.get("urgency")

            print("NAME:", repr(name))
            print("EMAIL:", repr(email))
            print("URGENCY:", repr(urgency))

            urgency_clean = (urgency or "").strip().lower()

            if urgency_clean == "urgent":
                text_message = f"URGENT CASE\n{name}\n{email}"
            else:
                text_message = f"NON-URGENT CASE\n{name}\n{mail}"
           
            data = {
                "Messages": [
                    {
                        "From": {
                            "Email": "contact@drdariuszconsults.com",
                            "Name": "Consultation System"
                        },
                        "To": [
                            {
                                "Email": "22mozorro@gmail.com",
                                "Name": "Dr Dariusz"
                            }
                        ],
                        "Subject": "New Consultation",
                        "TextPart": text_message
                    }
                ]
            }
         
            try:
                result = mailjet.send.create(data=data)
                print("STATUS:", result.status_code)
                print("BODY:", result.json())
            except Exception as e:
                print("❌ MAIL ERROR:", e)

            return redirect(url_for("thank_you"))

        except Exception as e:
            print("ERROR:", e)
            return "Something went wrong", 500

    return render_template("consultation.html")

    @app.route("/thank-you")
    def thank_you():
        return render_template("thank_you.html")
