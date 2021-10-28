from os import path
import requests

from premiumFinance.constants import PROJECT_ROOT, DATA_FOLDER

AGE_BIN = [
    "< 25",
    "25-34",
    "35-44",
    "45-54",
    "55-64",
    "65-74",
    ">= 75",
]

DATE_ID = {
    "Expenditures_Healthcare": {
        AGE_BIN[0]: "CXUHEALTHLB0402M",
        AGE_BIN[1]: "CXUHEALTHLB0403M",
        AGE_BIN[2]: "CXUHEALTHLB0404M",
        AGE_BIN[3]: "CXUHEALTHLB0405M",
        AGE_BIN[4]: "CXUHEALTHLB0406M",
        # "65_or_Over": "CXUHEALTHLB0407M",
        AGE_BIN[5]: "CXUHEALTHLB0408M",
        AGE_BIN[6]: "CXUHEALTHLB0409M",
    },
    "Income_After_Taxes": {
        AGE_BIN[0]: "CXUINCAFTAXLB0402M",
        AGE_BIN[1]: "CXUINCAFTAXLB0403M",
        AGE_BIN[2]: "CXUINCAFTAXLB0404M",
        AGE_BIN[3]: "CXUINCAFTAXLB0405M",
        AGE_BIN[4]: "CXUINCAFTAXLB0406M",
        # "65_or_Over": "CXUINCAFTAXLB0407M",
        AGE_BIN[5]: "CXUINCAFTAXLB0408M",
        AGE_BIN[6]: "CXUINCAFTAXLB0409M",
    },
}

FRED_URL_ROOT = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="

if __name__ == "__main__":
    for _, account_name in DATE_ID.items():
        for _, w in account_name.items():
            request_result = requests.get(FRED_URL_ROOT + w)
            with open(path.join(PROJECT_ROOT, DATA_FOLDER, w + ".csv"), "wb") as f:
                f.write(request_result.content)
                print(w)
