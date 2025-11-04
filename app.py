from flask import Flask, render_template_string

app = Flask(__name__)

@app.route("/")
def home():
    return render_template_string("""
        <html>
            <head><title>Gynae Consulting Platform</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
                <h1>Welcome to the Gynae Consulting Platform</h1>
                <p>This service will soon provide secure, expert gynaecological consultations online.</p>
            </body>
        </html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
