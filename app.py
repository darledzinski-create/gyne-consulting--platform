from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Home OK</h1><a href='/intake'>Go to intake</a>"

@app.route("/intake", methods=["GET", "POST"])
def intake():
    if request.method == "POST":
        intake_data = {
            "full_name = request.form.get("full_name")
            "email = request.form.get("email")
            "phone = request.form.get("phone")
            "concern = request.form.get("concern")

        }

        print("INTAKE RECEIVED:", intake_data)

        return render_templat("thank_you.html")

    return render_template("intake.html")

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run(debug=True)
