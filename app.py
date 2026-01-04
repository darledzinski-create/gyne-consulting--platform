from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --------------------
# ROUTES
# --------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask")
def ask_page():
    return render_template("ask.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/intake", methods=["GET", "POST"])
def intake():
    if request.method == "POST":
        return redirect(url_for("intake_submitted"))
    return render_template("intake.html")


@app.route("/intake-submitted")
def intake_submitted():
    return render_template("intake_submitted.html")
