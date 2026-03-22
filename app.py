from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.debug = True


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


@app.route("/intake", methods=["POST"])
def intake():

    full_name = request.form.get("full_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    concern = request.form.get("concern")
    emergency = request.form.get("emergency")

    print("NEW CONSULTATION")
    print("Name:", full_name)
    print("Email:", email)
    print("Phone:", phone)
    print("Concern:", concern)
    print("Emergency:", emergency)

    if emergency == "yes":
        send_emergency_sms(full_name, phone, concern)

    return redirect(url_for("thank_you"))


@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")


if __name__ == "__main__":
    app.run(debug=True)
