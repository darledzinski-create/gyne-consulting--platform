


      },
                "To": [
                        {
                    "Email": os.environ.get("MAILJET_TO_EMAIL"),
                        "Name": "Dr Dariusz Ledzinski"
                }
                ],
                "Subject": "New Consultation Request",
                "TextPart": email_body
            }
        ]
    }

    try:
        result = requests.post(
            "https://api.mailjet.com/v3.1/send",
            auth=(
                os.environ.get("MAILJET_API_KEY"),
                os.environ.get("MAILJET_SECRET_KEY")
        ),
        json=payload
        )

        if result.status_code not in (200, 201):
            return "Email delivery failed.", 500

        return render_template("thankyou.html")

        except Exception as e:
        return f"Unexpected error: {e}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
