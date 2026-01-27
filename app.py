from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/first-consultation")
def first_consultation():
    return render_template("first-consultation.html")

@app.route("/intake", methods=["GET", "POST"])
def intake():
    if request.method == "POST":
        intake_data = {
            "full_name": request.form.get("full_name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "concern": request.form.get("concern"),
        }

        emergency = request.form.get("emergency")

       if emergency:
    try:
        send_emergency_sms(
            full_name=intake_data["full_name"],
            phone=intake_data["phone"],
            concern=intake_data["concern"]
        )
    except Exception as e:
        print("⚠️ Emergency SMS failed:", e)

    return redirect(url_for("emergency_notice"))
    
        # Non-emergency flow
        print("INTAKE RECEIVED:", intake_data)
        return redirect(url_for("thank_you"))
    # Get request
    return render_template("intake.html")

@app.route("/emergency")
def emergency_notice():
    return render_template("emergency.html")

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run(debug=True)
