from mailjet_rest import Client

import os

mailjet = Client(

    auth=(

        os.environ.get("MAILJET_API_KEY"),

        os.environ.get("MAILJET_SECRET_KEY")

    ),

    version="v3.1"

)

def send_email(data):

    """

    Send an email using Mailjet.

    Returns the Mailjet response.

    """

    return mailjet.send.create(data=data)

def send_appointment_email(

    patient_email,

    patient_name,

    practice,

    date,

    time,

    reason

):

def send_consultation_email(

    to_email,

    from_name,

    subject,

    message

):

    data = {

        "Messages": [

            {

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

        ]

    }

    return send_email(data)

    patient_text = f"""

Dear {patient_name},

Your appointment has been offered.

Practice: {practice}

Date: {date}

Time: {time}

Reason:

{reason}

Please contact us if you need any changes.

Dr Dariusz Consulting

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
