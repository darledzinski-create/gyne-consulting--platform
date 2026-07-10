from mailjet_rest import Client

from config import MAILJET_API_KEY, MAILJET_SECRET_KEY

mailjet = Client(

    auth=(MAILJET_API_KEY, MAILJET_SECRET_KEY),

    version="v3.1"

)
