from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime   # ✅ MOVE THIS TO THE TOP

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        print(name, email, message)  # debug

        # ✅ SAVE DATA (correct indentation)
        with open("submissions.txt", "a") as f:
            f.write(f"{datetime.now()} | {name} | {email} | {message}\n")

        return redirect(url_for("thank_you"))

    return render_template("index.html")


@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")


if __name__ == "__main__":
    app.run(debug=True)
