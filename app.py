from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return "LOCAL TEST WORKING"
    print("REQUEST METHOD:", request.method)

    if request.method == "POST":
        print("POST DETECTED ✅")

        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        print("DATA:", name, email, message)
        return render_template("index.html", success=True)

    return render_template("index.html", success=False)


if __name__ == "__main__":
    app.run(debug=True)
