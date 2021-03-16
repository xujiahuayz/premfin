VBT_UNISMOKE_URL = "https://www.soa.org/globalassets/assets/files/research/exp-study/2015-vbt-unismoke-alb-anb.xlsx"
VBT_SMOKEDISTINCT_URL = "https://www.soa.org/globalassets/assets/files/research/exp-study/2015-vbt-smoker-distinct-alb-anb.xlsx"
PERSIST_URL = "https://www.soa.org/globalassets/assets/files/resources/research-report/2019/2009-13-us-ind-life-persistency-excel.xlsx"

MORT_URL = "http://cdn-files.soa.org/research/2009-15_Data_20180601.zip"
YIELD_URL = "https://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData"
DATA_FOLDER = "data/"

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
