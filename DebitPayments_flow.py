import datetime
import json
import logging
import random
from time import sleep, gmtime, strftime, time
import requests
from hashids import Hashids
from mongo_client import MongoClient
import subprocess

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
# settle credentials
SettleDebitPaymentAPI = "https://api-stage.wallter.com/api/transaction/"
# cancel credentials
CancelDebitPaymentAPI = "https://api-stage.wallter.com/api/v2/payments/"


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

            a = "ssh -i wlt-test-20230104.pem ec2-user@13.41.160.110"
            b = '"mongo --eval \'db.transactions.find'
            c = '({ \"id\": '
            e = f"{paymentID}"
            f = "})"
            d = ".projection ({_id: 1})' wallter --quiet\""
            command = f"{a} {b} {c} {e} {f} {d}"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            k = result.stdout.split('{ "_id" : ObjectId("')[1]
            _id = k.split('") }\n')[0]

            if (CreateDebitPaymentResponse.status_code in (200, 201, 202, 204)) and (paymentID is not None):
                logger.info("SEPA DEBIT transaction is created")
                logger.info(paymentID)
                logger.info(paymentType)
                logger.info(amount)
                logger.info(paymentStatus)
                # approve debit txn with wallter token
                wallterTokenAPI = "https://test-wallter.eu.auth0.com/oauth/token"
                wallterTokenPayload = {"grant_type": "password",
                                       "client_id": "IZR8D7mTqHKZudqaSUfuWleoQ6mSKeie",
                                       "username": "Annak@wallter.com",
                                       "password": "Wallter@23",
                                       "audience": "https://api.wallter.services",
                                       "scope": "openid profile email offline_access"}

                wallterTokenResponse = s.post(wallterTokenAPI, data=wallterTokenPayload)
                wallter_token = wallterTokenResponse.json().get("access_token")
                settlePayload = {"status": "COMPLETED"}
                settleDebitPaymentResponse = s.patch(SettleDebitPaymentAPI + _id,
                                                     headers={'Authorization': "Bearer " + wallter_token},
                                                     json=settlePayload, verify=False)
                if settleDebitPaymentResponse.status_code in (200, 201, 202, 204):
                    logger.info(_id)
                    logger.info("Transaction is completed!")
                else:
                    logger.info(settleDebitPaymentResponse.status_code)

            else:
                logger.info(CreateDebitPaymentResponse.status_code)
        except requests.exceptions.RequestException as e:
            logger.exception(e)

        # create DEBIT Internal transaction
        amount = random.uniform(1, 25)
        InternalPayload = {"creditor": "MONEY FLOW OU",
                           "reason": "api testing",
                           "currency": "EUR",
                           "type": "INTERNAL",
                           "amount": amount
                           }

        try:
            CreateDebitPaymentResponse = s.post(CreateDebitPaymentAPI,
                                                headers={'Authorization': "Bearer " + loginToken},
                                                json=InternalPayload, verify=False)

            paymentID = CreateDebitPaymentResponse.json().get("paymentId")
            paymentStatus = CreateDebitPaymentResponse.json().get("status")
            paymentType = CreateDebitPaymentResponse.json().get("type")

            if (CreateDebitPaymentResponse.status_code in (200, 201, 202, 204)) and (paymentID is not None):
                logger.info("Internal DEBIT transaction is created")
                logger.info(paymentID)
                logger.info(paymentType)
                logger.info(amount)
                logger.info(paymentStatus)
                # cancel Debit internal transaction
                try:
                    CancelDebitPaymentResponse = s.delete(CancelDebitPaymentAPI + str(paymentID),
                                                          headers={'Authorization': "Bearer " + loginToken},
                                                          verify=False)
                    payment_ID = CancelDebitPaymentResponse.json().get("payment_id")
                    payment_Status = CancelDebitPaymentResponse.json().get("payment_status")
                    if (CreateDebitPaymentResponse.status_code in (200, 201, 203, 204)) and (payment_ID is not None):
                        logger.info("Internal DEBIT transaction is canceled")
                        logger.info(payment_ID)
                        logger.info(payment_Status)
                    else:
                        logger.info(CancelDebitPaymentResponse.status_code)
                        logger.info(CancelDebitPaymentResponse.text)
                except requests.exceptions.RequestException as e:
                    logger.info(e)

            else:
                logger.info(CreateDebitPaymentResponse.status_code)
        except requests.exceptions.RequestException as e:
            logger.exception(e)

        # create Instant SEPA transaction
        amount = random.uniform(1, 5)
        InternalPayload = {"creditor": "instantvit",
                           "reason": "api test",
                           "currency": "EUR",
                           "type": "INST",
                           "amount": amount
                          }
        try:
            CreateDebitPaymentResponse = s.post(CreateDebitPaymentAPI,
                                                headers={'Authorization': "Bearer " + loginToken},
                                                json=InternalPayload, verify=False)

            paymentID = CreateDebitPaymentResponse.json().get("paymentId")
            paymentStatus = CreateDebitPaymentResponse.json().get("status")
            paymentType = CreateDebitPaymentResponse.json().get("type")

            if (CreateDebitPaymentResponse.status_code in (200, 201, 202, 204)) and (paymentID is not None):
                logger.info("Instant transaction is created")
                logger.info(paymentID)
                logger.info(paymentType)
                logger.info(amount)
                logger.info(paymentStatus)
            else:
                logger.info(CreateDebitPaymentResponse.status_code)
                logger.info(CreateDebitPaymentResponse.text)
        except requests.exceptions.RequestException as e:
            logger.exception(e)


main_flow()
