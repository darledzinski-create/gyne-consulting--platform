from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.debug = True   # ADD THIS LINE

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
    print("=== INTAKE ROUTE HIT ===")
    print("METHOD:", request.method)
    print("FORM DATA:", request.form)
   
    if request.method == "GET":
        return render_template("intake.html")
       
    emergency = request.form.get("emergency")

    print("EMERGENCY VALUE:", emergency)

    if emergency == "yes":
        return redirect(url_for("emergency_notice"))
    return redirect(url_for("thank_you"))
    
@app.route("/emergency")
def emergency_notice():
    return render_template("emergency.html")

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run(debug=True)
