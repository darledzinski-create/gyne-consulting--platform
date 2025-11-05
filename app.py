from flask import Flask, render_template_string

app = Flask(__name__)

@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dr. Dariusz Ledzinski - Online Gynaecological Consultation</title>
        <style>
            body {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                background-color: #f8f9fa;
                color: #333;
                margin: 0;
                padding: 0;
                line-height: 1.6;
            }
            header {
                background-color: #004080;
                color: white;
                padding: 1.5em 0;
                text-align: center;
                font-size: 1.4em;
                letter-spacing: 0.5px;
            }
            main {
                max-width: 800px;
                margin: 2em auto;
                background: white;
                padding: 2em;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
            h2 {
                color: #004080;
                border-bottom: 2px solid #e0e0e0;
                padding-bottom: 0.4em;
            }
            footer {
                text-align: center;
                padding: 1em;
                background: #f0f0f0;
                color: #555;
                font-size: 0.9em;
                position: fixed;
                bottom: 0;
                width: 100%;
            }
            @media (max-width: 600px) {
                main {
                    margin: 1em;
                    padding: 1.5em;
                }
                header {
                    font-size: 1.2em;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <strong>Dr. Dariusz Ledzinski</strong><br>
            Online Gynaecological Consultation Platform
        </header>
        <main>
            <h2>Welcome</h2>
            <p>
                This is the secure online consulting platform of 
                <strong>Dr. Dariusz Ledzinski</strong>, dedicated to providing 
                expert gynaecological guidance and compassionate care through a 
                digital interface designed for privacy and trust.
            </p>
            <p>
                The platform will soon allow patients to book virtual consultations,
                review consent forms, and receive confidential advice.
            </p>
            <p><em>“Where expertise meets empathy.”</em></p>
        </main>
        <footer>
            © 2025 Dr. Dariusz Ledzinski — All rights reserved.
        </footer>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)