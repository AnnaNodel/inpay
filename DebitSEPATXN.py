import datetime
import json
import logging
import random
from time import sleep, gmtime, strftime, time
import requests

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG,  # If smth wrong, change to 'DEBUG'
                    filename="inpay_flow.log")  # Name of log file
logger = logging.getLogger("INPAY")
timeout = 15  # Timeout for APIs check (login not included!), in seconds
loop_time = 60  # Time between every loop, in second

# log in credentials
GetAuthTokenAPI = "https://api-stage.wallter.com/api/v2/auth/token"
authPayload = {
    "client_id": "aIhaP0NjIQFgKPPb35iWmIijgl3owE1D",
    "client_secret": "LO1O3uBGUXBQWzmI91NftM3nd2mSQZJ80WDqxGVvMFgonkG05OJUAw0PgRUOCGUI"
}

# payment credentials
CreateDebitPaymentAPI = "https://api-stage.wallter.com/api/v2/payments/debit"


def main_flow():
    # getting token
    with requests.Session() as s:
        try:
            GetAuthTokenResponse = s.post(GetAuthTokenAPI, json=authPayload)
            loginToken = GetAuthTokenResponse.json().get("access_token")

            if GetAuthTokenResponse.status_code in (200, 201, 202, 204):
                logger.info("Successfully logged in to Wallter!")
            else:
                logger.info(GetAuthTokenResponse.status_code)

        except requests.exceptions.RequestException as e:
            logger.exception(e)

        # create DEBIT SEPA transaction
        amount = random.uniform(1, 10)
        SEPAPayload = {"creditor": "instantv",
                       "reason": "api testing",
                       "currency": "EUR",
                       "type": "SEPA",
                       "amount": amount
                        }

        try:
            CreateDebitPaymentResponse = s.post(CreateDebitPaymentAPI,
                                                headers={'Authorization': "Bearer " + loginToken},
                                                json=SEPAPayload, verify=False)

            paymentID = CreateDebitPaymentResponse.json().get("paymentId")
            paymentStatus = CreateDebitPaymentResponse.json().get("status")
            paymentType = CreateDebitPaymentResponse.json().get("type")

            if (CreateDebitPaymentResponse.status_code in (200, 201, 202, 204)) and (paymentID is not None):
                logger.info("SEPA DEBIT transaction is created")
                logger.info(paymentID)
                logger.info(paymentType)
                logger.info(amount)
                logger.info(paymentStatus)
            else:
                logger.info(CreateDebitPaymentResponse.status_code)
        except requests.exceptions.RequestException as e:
            logger.exception(e)


main_flow()