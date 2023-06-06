import datetime
import logging
import requests
# import app

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG,  # If smth wrong, change to 'DEBUG'
                    filename="inpay_test.log")  # Name of log file
logger = logging.getLogger("INPAY")
timeout = 15  # Timeout for APIs check (login not included!), in seconds
loop_time = 60  # Time between every loop, in second

# log in credentials
GetAuthTokenAPI = "https://api-stage.wallter.com/api/v2/auth/token"
authPayload = {
    "client_id": "aIhaP0NjIQFgKPPb35iWmIijgl3owE1D",
    "client_secret": "LO1O3uBGUXBQWzmI91NftM3nd2mSQZJ80WDqxGVvMFgonkG05OJUAw0PgRUOCGUI"
}

GetPaymentsByDateAPI = "https://api-stage.wallter.com/api/v2/payments?" # start=2023-05-22T11:00:00Z&end=2023-05-23T11:00:00Z&page=1&itemPerPage=1000"

now = datetime.datetime.now()
endDate = now.strftime("%Y-%m-%dT%H:%M:%SZ")
then = datetime.datetime.now() - datetime.timedelta(days=7)
startDate = then.strftime("%Y-%m-%dT%H:%M:%SZ")
Npage = 1
a = 1000


def main_flow():
    # getting token
    with requests.Session() as s:
        try:
            GetAuthTokenResponse = s.post(GetAuthTokenAPI, json=authPayload)
            loginToken = GetAuthTokenResponse.json().get("access_token")

            if GetAuthTokenResponse.status_code in (200, 201, 202, 203, 204):
                logger.info("Successfully logged in to Wallter!")
            else:
                logger.info(GetAuthTokenResponse.status_code)

        except requests.exceptions.RequestException as e:
            logger.exception(e)

        try:
            # app.run(debug=True, use_reloader=False)
            PaymentsByDateResponse = s.get(GetPaymentsByDateAPI, params={'end': endDate,'start': startDate,'page': Npage,'itemsPerPage': a}, headers={'Authorization': "Bearer " + loginToken},
                                           verify=False)
            if PaymentsByDateResponse.status_code in (200, 201, 202, 203, 204):
                logger.info(startDate)
                logger.info(endDate)
                amount_of_txn = (PaymentsByDateResponse.text.count("id")/2)
                logger.info(amount_of_txn)
            else:
                logger.info(PaymentsByDateResponse.status_code)

        except requests.exceptions.RequestException as e:
            logger.exception(e)


main_flow()
