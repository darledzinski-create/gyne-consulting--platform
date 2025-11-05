from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gynae Consulting Platform</title>
        <style>
            body {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(to bottom right, #f7f8fc, #e8edf5);
                color: #333;
                margin: 0;
                padding: 0;
            }
            header {
                background-color: #4a6fa5;
                color: white;
                padding: 2rem 1rem;
                text-align: center;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            }
            main {
                max-width: 800px;
                margin: 3rem auto;
                padding: 2rem;
                background-color: white;
                border-radius: 12px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.1);
            }
            h1 {
                margin-top: 0;
                color: #4a6fa5;
                text-align: center;
            }
            p {
                font-size: 1.15rem;
                line-height: 1.7;
                text-align: center;
                color: #555;
            }
            footer {
                text-align: center;
                font-size: 0.9rem;
                color: #777;
                margin: 3rem 0 1rem 0;
            }
            .button {
                display: inline-block;
                margin-top: 1.5rem;
                background-color: #4a6fa5;
                color: white;
                padding: 0.8rem 1.6rem;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 500;
                transition: background-color 0.3s;
            }
            .button:hover {
                background-color: #395780;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Gynae Consulting Platform</h1>
        </header>
        <main>
            <p>Welcome to the <strong>Gynae Consulting Platform</strong>.</p>
            <p>This service will soon provide <em>secure, expert gynaecological consultations</em> online — combining professionalism, discretion, and compassion.</p>
            <a class="button" href="#">Learn More</a>
        </main>
        <footer>
            &copy; 2025 Gynae Consulting Platform | Designed with care and expertise
        </footer>
    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
