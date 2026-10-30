
from mailjet_rest import Client
import os
import base64


mailjet = Client(
    auth=(
        os.environ.get("MAILJET_API_KEY"),
        os.environ.get("MAILJET_SECRET_KEY")
    ),
    version="v3.1"
)


def send_email(data):

    result = mailjet.send.create(data=data)

    print("Status:", result.status_code)
    print("Response:", result.json())

    return result

def send_consultation_email(
    to_email,
    from_name,
    subject,
    message
):
    import html

    email_message = {
        "From": {
            "Email": "contact@drdariuszconsults.com",
            "Name": from_name
        },
        "To": [
            {
                "Email": to_email
            }
        ],
        "Subject": subject,
        "TextPart": message
    }

    # Add the branded HTML version only to patient emails.
    if from_name == "Dr Dariusz":

        safe_message = html.escape(message).replace("\n", "<br>")

        email_message["HTMLPart"] = f"""
        <html>
        <body style="margin:0; padding:30px 15px;
                     background-color:#f4f7f9;">

            <div style="max-width:600px; margin:0 auto;
                        padding:35px 25px;
                        background-color:#ffffff;
                        border-radius:12px;">

                <div style="text-align:center;
                            margin-bottom:30px;">

                    <img
                        src="https://drdariuszconsults.com/static/Dr%20Dariusz%20Consulting%20Medical%20Logo.png"
                        alt="Dr Dariusz Consulting"
                        width="280"
                        style="max-width:100%; height:auto;"
                    >

                </div>

                <div style="font-family:Arial,sans-serif;
                            font-size:16px;
                            line-height:1.8;
                            color:#263746;">

                    {safe_message}

                </div>

            </div>

        </body>
        </html>
        """

    data = {
        "Messages": [
            email_message
        ]
    }

    return send_email(data)
    return send_email(data)


def create_patient_email(name, urgency):
    if urgency == "urgent":
        subject = "CONSULTATION REQUEST"

        text = f"""
Dear {name},

Your urgent consultation request has been received.

This platform is not suitable for medical emergencies.

Please seek immediate in-person medical care if necessary.

Dr Dariusz
"""

    else:
        subject = "STANDARD CONSULTATION"

        text = f"""
Dear {name},

Thank you for your consultation request.

Your message has been received and will be reviewed carefully.

Dr Dariusz
"""

    return subject, text


def send_appointment_email(
    patient_email,
    patient_name,
    practice,
    date,
    time,
    reason
):
    patient_text = f"""
Dear {patient_name},

Your appointment has been offered.

Practice: {practice}
Date: {date}
Time: {time}

Reason:
{reason}

CONSULTATION FEE: R 500

PAYMENT BY EFT
Bank: GoTyme
Account holder: Dariusz Ledzinski
Account number: 510 1312 9386

Please make payment by EFT and reply to this email with your proof of payment.

Your appointment will be confirmed once payment has been received and verified.

If you need any changes to the appointment, please contact us.

Dr Dariusz Ledzinski
"""

    data = {
        "Messages": [
            {
                "From": {
                    "Email": "contact@drdariuszconsults.com",
                    "Name": "Dr Dariusz"
                },
                "To": [
                    {
                        "Email": patient_email
                    }
                ],
                "Subject": "Appointment Offer",
                "TextPart": patient_text
            }
        ]
    }

    return send_email(data)

def send_appointment_confirmation_email(
    patient_email,
    patient_name,
    practice,
    date,
    time,
    reason
):
    patient_text = f"""
Dear {patient_name},

Your appointment has been confirmed.

Practice: {practice}
Date: {date}
Time: {time}

Reason:
{reason}

Payment has been received and verified.

We look forward to seeing you.

Dr Dariusz Ledzinski
"""

    data = {
        "Messages": [
            {
                "From": {
                    "Email": "contact@drdariuszconsults.com",
                    "Name": "Dr Dariusz"
                },
                "To": [
                    {
                        "Email": patient_email
                    }
                ],
                "Subject": "Appointment Confirmed",
                "TextPart": patient_text
            }
        ]
    }

    return send_email(data)


def send_pdf_email(
    patient_email,
    patient_name,
    subject,
    message,
    pdf_bytes,
    filename
):
    encoded_pdf = base64.b64encode(
        pdf_bytes
    ).decode("utf-8")

    data = {
        "Messages": [
            {
                "From": {
                    "Email": "contact@drdariuszconsults.com",
                    "Name": "Dr Dariusz"
                },
                "To": [
                    {
                        "Email": patient_email,
                        "Name": patient_name
                    }
                ],
                "Subject": subject,
                "TextPart": message,
                "Attachments": [
                    {
                        "ContentType": "application/pdf",
                        "Filename": filename,
                        "Base64Content": encoded_pdf
                    }
                ]
            }
        ]
    }

    return send_email(data)
