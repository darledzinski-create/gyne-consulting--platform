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
