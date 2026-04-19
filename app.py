from flask import Flask, render_template, request, redirect, url_for
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
        print("FORM SUBMITTED")

        # --- Get form data ---
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        symptoms = request.form.get("symptoms")
        duration = request.form.get("duration")
        urgency = request.form.get("urgency")
       
        try:
            print("CONNECTING TO EMAIL SERVER")

            mailjet = Client(
                auth=(
                    os.environ.get("MAILJET_API_KEY"),
                    os.environ.get("MAILJET_SECRET_KEY")
                ),
                version="v3.1"
            )

            urgency_clean = (urgency or "").strip().lower()
            print("CLEAN URGENCY:", urgency_clean)

            if urgency_clean == "urgent":
                print("ENTERED URGENT BRANCH")
                confirmation_body = "<html><body><h2>URGENT</h2>,</body></html>"
            else:
                print("ENTERED NON-URGENT BRANCH")
                confirmation_body = "<html><body><h2>NORMAL</h2></body></html>"
             
            data = {
                "Messages": [
                    {
                        "From": {
                            "Email": "contact@drdariuszconsults.com",
                            "Name": "Dr Dariusz"
                        },
                        "To": [
                            {
                                "Email": email,
                                "Name": name
                            }
                        ],
                        "Subject": "Consultation",
                        "HTMLPart": confirmation_body
                    },

                ]

            }

            result = mailjet.send.create(data=data)

        except Exception as e:
            print("❌ ERROR:", repr(e))
            return f"ERROR: {repr(e)}", 500

        return redirect(url_for("thank_you"))

    return render_template("consultation.html")

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")
