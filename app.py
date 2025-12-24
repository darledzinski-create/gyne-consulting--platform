from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask")
def ask():
    return render_template("ask.html")

@app.route("/submit_question", methods=["POST"])
def submit_question():
    return redirect(url_for("thank_you"))

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run()
