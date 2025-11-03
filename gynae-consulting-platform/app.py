from flask import Flask, render_template_string

app = Flask(__name__)

@app.route("/")
def home():
    return render_template_string("""
    <html>
        <head><title>Dr. Dariusz Ledzinski - Online Gynaecological Consultation</title></head>
        <body style="font-family: Arial; margin: 2em;">
            <h2>Welcome to Dr. Dariusz Ledzinski’s Online Consulting Platform</h2>
            <p>This is a prototype version deployed via Render.</p>
            <p>Stay tuned as we expand this into a full online consultation system.</p>
        </body>
    </html>
    """)
