from premiumFinance.settings import PROJECT_ROOT
import numpy as np

VBT_UNISMOKE_URL = "https://www.soa.org/globalassets/assets/files/research/exp-study/2015-vbt-unismoke-alb-anb.xlsx"
VBT_SMOKEDISTINCT_URL = "https://www.soa.org/globalassets/assets/files/research/exp-study/2015-vbt-smoker-distinct-alb-anb.xlsx"
PERSIST_URL = "https://www.soa.org/globalassets/assets/files/resources/research-report/2019/2009-13-us-ind-life-persistency-excel.xlsx"

MORT_URL = "http://cdn-files.soa.org/research/2009-15_Data_20180601.zip"
YIELD_URL = "https://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData"
TREASURY_YIELD_URL = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve"
DATA_FOLDER = PROJECT_ROOT / "data"
FIGURE_FOLDER = PROJECT_ROOT / "figures"

MORTALITY_TABLE_CLEANED_PATH = DATA_FOLDER / "mortality_experience_clean.xlsx"
PROCESSED_PROFITABILITY_PATH = DATA_FOLDER / "profitability.json"

NAIC_PATH = DATA_FOLDER / "NAIC_1996_2020_SPGlobalofficeworkbook.xls"

YIELD_DURATION = {
    "1MONTH": 1 / 12,
    "2MONTH": 2 / 12,
    "3MONTH": 3 / 12,
    "4MONTH": 4 / 12,
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

AGE_BREAKPOINTS_MID = np.arange(25, 85, 10)
AGE_BREAKPOINTS = np.append(AGE_BREAKPOINTS_MID, 200)

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


LIFE_SETTLEMENTS_SIZE = {
    "secondary_volume": {
        "aap": {
            "2001": 1.7,
            "2002": 3.1,
            "2003": 4.9,
            "2004": 7.1,
            "2005": 11.2,
            "2006": 13.7,
            "2007": 15.8,
            "2008": 12.7,
            "2009": 7.1,
            "2010": 4.9,
            "2011": 5.4,
            "2012": 2.4,
            "2013": 2.7,
            "2014": 2.2,
            "2015": 2.5,
        },
        "thedeal": {
            "2011": 5.06,
            "2012": 2.12,
            "2013": 2.57,
            "2014": 1.65,
            "2015": 1.65,
            "2016": 0.488,
            "2017": 0.61282,
            "2018": 0.64048,
            "2019": 0.83956,
            "2020": 0.84813,
            "2021": 0.71501,
        },
        "conning": {
            "2002": 2,
            "2003": 2.6,
            "2004": 3.3,
            "2005": 5.5,
            "2006": 6.1,
            "2007": 12.2,
            "2008": 11.8,
            "2009": 7.6,
            "2010": 3.8,
            "2011": 1.3,
            "2012": 2,
            "2013": 2.6,
            "2014": 1.7,
            "2015": 1.7,
            "2016": 2.1,
            "2017": 2.5,
        },
        "roland": {
            "2001": 2.124304,
            "2002": 3.239994,
            "2003": 9.224147,
            "2004": 11.354099,
            "2005": 18.961073,
            "2006": 36.4064,
            "2007": 55.528331,
            "2008": 60.352221,
            "2009": 37.090352,
            "2010": 23.476263,
            "2011": 9.969372,
            "2012": 5.359877,
            "2013": 3.323124,
            "2014": 3.001531,
            "2015": 1.929556,
            "2016": 3.001531,
        },
    },
    "secondary_count": {
        "thedeal": {
            "2016": 1707,
            "2017": 2027,
            "2018": 2587,
            "2019": 2878,
            "2020": 3241,
            "2021": 2937,
        },
    },
    "tertiary_volume": {
        "aap": {
            "2009": 0.5,
            "2010": 7.1,
            "2011": 2.1,
            "2012": 2.3,
            "2013": 3.7,
            "2014": 8.1,
            "2015": 6.5,
        },
        "roland": {
            "2007": 0.554775,
            "2008": 1.005053,
            "2009": 3.068822,
            "2010": 10.901611,
            "2011": 11.628785,
            "2012": 7.819896,
            "2013": 4.075349,
            "2014": 9.062552,
            "2015": 7.294591,
            "2016": 5.0055,
        },
    },
    "inforce_face": {
        "aap": {
            "2001": 5,
            "2002": 8,
            "2003": 13,
            "2004": 20,
            "2005": 32,
            "2006": 45,
            "2007": 61,
            "2008": 74,
            "2009": 81,
            "2010": 84,
            "2011": 87,
            "2012": 88,
            "2013": 90,
            "2014": 91,
            "2015": 92,
        },
        "conning": {
            "2002": 1,
            "2003": 4.2,
            "2004": 6.7,
            "2005": 10.8,
            "2006": 14.5,
            "2007": 23.5,
            "2008": 31.8,
            "2009": 35.6,
            "2010": 36.0,
            "2011": 35.1,
            "2012": 34.6,
            "2013": 34.6,
            "2014": 32.5,
            "2015": 29.3,
            "2016": 25.2,
            "2017": 21.8,
        },
        "tockytot": {
            "2001": 2.124304,
            "2002": 3.239994,
            "2003": 9.224147,
            "2004": 11.354099,
            "2005": 18.961073,
            "2006": 36.4064,
            "2007": 56.083106,
            "2008": 61.357274,
            "2009": 40.159174,
            "2010": 34.377874,
            "2011": 21.598157,
            "2012": 13.179773,
            "2013": 7.398473,
            "2014": 12.064083,
            "2015": 9.224147,
            "2016": 8.007031,
        },
    },
}
# 2009-2013 Individual Life Insurance Mortality Experience Report
# https://www.soa.org/resources/experience-studies/2017/2009-13-indiv-life-ins-mort-exp/

DOLLAR_MAGNITUDES = {
    6: "million",
    9: "billion",
    12: "trillion",
}
