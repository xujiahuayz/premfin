from os import path
from premiumFinance.settings import PROJECT_ROOT

VBT_UNISMOKE_URL = "https://www.soa.org/globalassets/assets/files/research/exp-study/2015-vbt-unismoke-alb-anb.xlsx"
VBT_SMOKEDISTINCT_URL = "https://www.soa.org/globalassets/assets/files/research/exp-study/2015-vbt-smoker-distinct-alb-anb.xlsx"
PERSIST_URL = "https://www.soa.org/globalassets/assets/files/resources/research-report/2019/2009-13-us-ind-life-persistency-excel.xlsx"

MORT_URL = "http://cdn-files.soa.org/research/2009-15_Data_20180601.zip"
YIELD_URL = "https://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData"
YIELD_URL_cdt = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value=2021"
DATA_FOLDER = path.join(PROJECT_ROOT, "data")
FIGURE_FOLDER = path.join(PROJECT_ROOT, "figures")

MORTALITY_TABLE_CLEANED_PATH = path.join(DATA_FOLDER, "mortality_experience_clean.xlsx")
PROCESSED_PROFITABILITY_PATH = path.join(DATA_FOLDER, "profitability.json")
UNTAPPED_PROFIT_PATH = path.join(DATA_FOLDER, "untappedprofit.xlsx")

NAIC_PATH = path.join(DATA_FOLDER, "NAIC_1996_2020_SPGlobalofficeworkbook.xls")

YIELD_DURATION = {
    "1MONTH": 1 / 12,
    "2MONTH": 2 / 12,
    "3MONTH": 3 / 12,
    "6MONTH": 6 / 12,
    "1YEAR": 1,
    "2YEAR": 2,
    "3YEAR": 3,
    "5YEAR": 5,
    "7YEAR": 7,
    "10YEAR": 10,
    "20YEAR": 20,
    "30YEAR": 30,
}

FIN_OPTIONS = ["lapse", "nonrecourse", "fullrecourse", "sale"]

VBT_TABLES = {
    "VBT01": {
        "m": {"unism": 1148, "nonsm": 1149, "smoke": 1150},
        "f": {"unism": 1151, "nonsm": 1152, "smoke": 1153},
    },
    "VBT08": {"m": {"nonsm": 1003, "smoke": 1005}, "f": {"nonsm": 997, "smoke": 999}},
    "VBT15": {
        "m": {"unism": 3273, "nonsm": 3265, "smoke": 3267},
        "f": {"unism": 3274, "nonsm": 3266, "smoke": 3268},
    },
}


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

# 2009-2013 Individual Life Insurance Mortality Experience Report
# https://www.soa.org/resources/experience-studies/2017/2009-13-indiv-life-ins-mort-exp/
