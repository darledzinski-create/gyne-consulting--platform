from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def send_emergency_sms(full_name, phone, concern):
    print("🚨 EMERGENCY ALERT")
    print("Name:", full_name)
    print("Phone:", phone)
    print("Concern:", concern)
    
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/first-consultation")
def first_consultation():
    return render_template("first-consultation.html")

@app.route("/intake", methods=["GET", "POST"])
def intake():

    # ✅ ALWAYS handle GET first
    if request.method == "GET":
        return render_template("intake.html")

    # ✅ POST logic starts here
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
                concern=intake_data["concern"],
            )
        except Exception as e:
            print("! Emergency SMS failed:", e)

        # Emergency path always exits
        return redirect(url_for("emergency_notice"))

    # Non-emergency path
    print("INTAKE RECEIVED:", intake_data)
    return redirect(url_for("thank_you"))
    
@app.route("/emergency")
def emergency_notice():
    return render_template("emergency.html")

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run(debug=True)
