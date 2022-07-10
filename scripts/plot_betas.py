from premiumFinance.constants import DATA_FOLDER, FIGURE_FOLDER
import pandas as pd
import numpy as np
from os import path
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt


DATE_RANGE = pd.date_range("2011-06-30", "2021-07-01", freq="1D")
LOG_RETURN_COLUMN = "log_return"

SPGURLROOT = "https://www.spglobal.com/spdji/en/idsexport/file.xls?selectedModule=PerformanceGraphView&yearFlag=tenYearFlag&indexId="

INDEX_DICT = {
    "filename": [
        "USTMIIndex",
        "USconsumerfinanceIndex",
        "USRealEstateIndex",
        "USREITIndex",
        "USoilgasIndex",
        "USutilityIndex",
        "UShealthcareIndex",
        "USinsuranceIndex",
    ],
    "indexid": [
        2762,
        5458463,
        91882099,
        5552915,
        101116869,
        100003020,
        101117012,
        57092,
    ],
    "labelname": [
        "TMI",
        "Consumer finance",
        "Real estate",
        "REIT",
        "Oil & gas",
        "Utility",
        "Healthcare",
        "Insurance",
        "Life settlement index",
    ],
}


def get_index_log_return(index_file_name: str) -> pd.DataFrame:

    index_file = path.join(DATA_FOLDER, index_file_name + ".xls")

    index_table = pd.read_excel(
        index_file,
        index_col=0,
        skiprows=6,
        skipfooter=4,
        usecols="A:B",
    )

    index_table_interpolated = index_table.reindex(DATE_RANGE).interpolate()

    index_table_interpolated[LOG_RETURN_COLUMN] = np.log(
        1 + index_table_interpolated.iloc[:, 0].pct_change()
    )

    return index_table_interpolated.iloc[1:, :]


USTreasury = get_index_log_return("USTreasuryIndex")
USTMI = get_index_log_return("USTMIIndex")
market_excess = USTMI[LOG_RETURN_COLUMN] - USTreasury[LOG_RETURN_COLUMN]


def get_coefficients(index_file_name: str) -> pd.Series:

    index_table = get_index_log_return(index_file_name)

    regression_table = (
        index_table[LOG_RETURN_COLUMN] - USTreasury[LOG_RETURN_COLUMN]
    ).to_frame()
    regression_table["market_excess"] = market_excess
    lm = smf.ols(formula=LOG_RETURN_COLUMN + "~ market_excess", data=regression_table)
    lm_results = lm.fit()
    return lm_results.params


if __name__ == "__main__":
    # utilities / REIT / Finance / Insurance

    index_betas = pd.Series(
        [
            get_coefficients("USTMIIndex")[1],
            # get_coefficients("USbondIndex")[1],
            get_coefficients("USconsumerfinanceIndex")[1],
            get_coefficients("USRealEstateIndex")[1],
            get_coefficients("USREITIndex")[1],
            get_coefficients("USoilgasIndex")[1],
            get_coefficients("USutilityIndex")[1],
            get_coefficients("UShealthcareIndex")[1],
            get_coefficients("USinsuranceIndex")[1],
            0.067,
        ]
    )

    print(index_betas)

    x_pos = range(len(index_betas))
    barlist = plt.bar(x=x_pos, height=index_betas)
    barlist[-1].set_color("green")

    plt.axhline(y=1, c="gray", linestyle="--")

    plt.xticks(
        x_pos,
        INDEX_DICT["labelname"],
        rotation=90,
    )
    plt.ylabel("beta")

    plt.tight_layout()

    plt.savefig(path.join(FIGURE_FOLDER, "betas.pdf"))

    #need to download statsmodel.
    