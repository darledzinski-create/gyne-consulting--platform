from mailjet_rest import Client

import os

mailjet = Client(

    auth=(

        os.environ.get("MAILJET_API_KEY"),

        os.environ.get("MAILJET_SECRET_KEY")

    ),

    version="v3.1"

)
