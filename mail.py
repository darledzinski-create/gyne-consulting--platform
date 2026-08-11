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
    result = mailjet.send.create(data=data)

    print("Status:", result.status_code)
    print("Response:", result.json())

    return result

    return mailjet.send.create(data=data)

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

def create_patient_email(name, urgency):
    if urgency == "urgent":
        subject = "CONSULTATION REQUEST"
        text = f"""
Your urgent consultation request has been received.
    
This platform is not suitable for medical emergencies.

Please seek immediate in-person medical care if necessary.

Dr Dariusz
"""
    else:

        subject = "STANDARD CONSULTATION"

        text = f"""
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

    def send_email(data):
        result = mailjet.send.create(data=data)

    print("Status:", result.status_code)
    print("Response:", result.json())

    return result

    return mailjet.send.create(data=data)

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

def create_patient_email(name, urgency):
    if urgency == "urgent":
        subject = "CONSULTATION REQUEST"
        text = f"""
Your urgent consultation request has been received.
    
This platform is not suitable for medical emergencies.

Please seek immediate in-person medical care if necessary.

Dr Dariusz
"""
    else:

        subject = "STANDARD CONSULTATION"

        text = f"""
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
   
   def send_appoimtment_confirmation_email(
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
       
   
   
