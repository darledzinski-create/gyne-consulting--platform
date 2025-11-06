from flask import Flask, render_template_string

app = Flask(__name__)

@app.route("/")
def home():
    return render_template_string("""
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dr. Dariusz Ledzinski – Online Gynaecological Consultation</title>
        <style>
            body {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                background: #fff9f9;
                color: #333;
                margin: 0;
                padding: 0;
            }
            header {
                background-color: #f8d7da;
                color: #7a1c29;
                padding: 2em 1em;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                margin: 0;
                font-size: 1.8em;
            }
            main {
                max-width: 700px;
                margin: 2em auto;
                background: #fff;
                padding: 2em;
                border-radius: 12px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            }
            h2 {
                color: #b04154;
            }
            p {
                line-height: 1.6;
                margin-bottom: 1em;
            }
            footer {
                text-align: center;
                padding: 1em;
                font-size: 0.9em;
                color: #777;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Welcome to Dr. Dariusz Ledzinski’s Gynaecological Consulting Platform</h1>
        </header>
        <main>
            <h2>Warm, Confidential, and Professional Care</h2>
            <p>Thank you for visiting my online consultation platform. Here, you will soon be able to book secure, private gynaecological consultations from the comfort of your home.</p>
            <p>My goal is to offer you compassionate, evidence-based medical advice in a safe and understanding environment.</p>
            <p>This service is currently in development — but soon, it will open its doors to women seeking professional guidance with sensitivity and care.</p>
        </main>
        <footer>
            <p>© 2025 Dr. Dariusz Ledzinski | All rights reserved</p>
        </footer>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


