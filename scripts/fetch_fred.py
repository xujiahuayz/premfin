from os import path
import requests

from premiumFinance.constants import PROJECT_ROOT, DATA_FOLDER, DATE_ID, FRED_URL_ROOT


if __name__ == "__main__":
    for _, account_name in DATE_ID.items():
        for _, w in account_name.items():
            request_result = requests.get(FRED_URL_ROOT + w)
            with open(path.join(PROJECT_ROOT, DATA_FOLDER, w + ".csv"), "wb") as f:
                f.write(request_result.content)
                print(w)
