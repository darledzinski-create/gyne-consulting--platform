from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# -----------------------------
# Pages
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask")
def ask_page():
    return render_template("ask.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/consent")
def consent_page():
    return render_template("consent.html")


@app.route("/thankyou")
def thankyou_page():
    return render_template("thankyou.html")


# -----------------------------
# Form submission (NO email yet)
# -----------------------------

@app.route("/submit_question", methods=["POST"])
def submit_question():
    name = request.form.get("name")
    email = request.form.get("email")
    question = request.form.get("question")

    # We intentionally do NOTHING with the data yet
    # This confirms the form → route → redirect flow works

    return redirect(url_for("thankyou_page"))


# -----------------------------
# Run locally (Render ignores this)
# -----------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
