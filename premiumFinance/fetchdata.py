# %%
import csv
import xml.etree.ElementTree as ET
from io import BytesIO, TextIOWrapper
from pathlib import Path
from pprint import pprint
from typing import Iterable, Optional
from zipfile import ZipFile

# must build from source with mac M1
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from nelson_siegel_svensson.calibrate import calibrate_ns_ols
from scipy.interpolate import interp1d

from premiumFinance.constants import (
    DATA_FOLDER,
    MORT_URL,
    TREASURY_YIELD_URL,
    VBT_TABLES,
    YIELD_DURATION,
)
from premiumFinance.settings import PROJECT_ROOT

# %%

# need to `pip install openpyxl`
pers_file = DATA_FOLDER / "persistency.xlsx"
# read lapse rates
lapse_tbl = pd.read_excel(
    pers_file,
    sheet_name="Universal Life",
    index_col=0,
    skiprows=8,
    skipfooter=71,
    usecols="J:K,O",
)


def get_vbt_data(
    vbt: str = "VBT15",
    is_male: bool = True,
    is_smoker: Optional[bool] = None,
    issue_age: float = 50,
    current_age: float = 70,
) -> pd.Series:
    """
    get 1-year conditional mortality rates from VBT
    """

    tbl_index = VBT_TABLES[vbt]["m" if is_male else "f"][
        "unism" if is_smoker is None else "smoke" if is_smoker else "nonsm"
    ]

    tbl_file = PROJECT_ROOT / DATA_FOLDER / f"VBTXML/t{tbl_index}.xml"

    vbt_tbl = ET.parse(tbl_file)
    root = vbt_tbl.getroot()
    [sel, ult] = root.findall("Table/Values")
    ult_mort = pd.Series(
        {m.get("t"): float(m.text) for m in ult.find("Axis").findall("Y")}
    )

    start_age = int(sel.find("Axis").get("t"))
    sel_mort = (
        pd.Series(
            {
                m.get("t"): m.text
                for m in sel[issue_age - start_age].find("Axis").findall("Y")
            }
        )
        .dropna()
        .astype(float)
    )
    ult_start = issue_age + int(sel_mort.index[-1])

    if ult_start <= int(ult_mort.index[-1]):
        curv = pd.concat([sel_mort, ult_mort[str(ult_start) :]], ignore_index=True)
        # sel_mort.append(ult_mort[str(ult_start) :], ignore_index=True)
    else:
        curv = sel_mort.reset_index(drop=True)

    mort = pd.concat(
        [pd.Series([0]), curv[(current_age - issue_age) :]], ignore_index=True
    )
    # pd.Series([0]).append(curv[(currentage - issueage) :], ignore_index=True)

    return mort


def get_soa_data(url: str, filename: str):
    """
    download excel data from SOA
    """
    request_result = requests.get(url)
    vbt_path = PROJECT_ROOT / DATA_FOLDER / f"{filename}.xlsx"
    with open(vbt_path, "wb") as f:
        f.write(request_result.content)


def fetch_treasury_yield(
    rooturl: str = TREASURY_YIELD_URL,
    date: str = "02",
    month: str = "01",
    year: int = 2025,
) -> pd.DataFrame:
    r_yield = requests.get(f"{rooturl}&field_tdr_date_value={year}")
    content = r_yield.content.decode("utf-8")
    root = ET.fromstring(content)
    dat = f"{year}-{month}-{date}T00:00:00"
    for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
        if (
            entry.find(
                ".//{http://schemas.microsoft.com/ado/2007/08/dataservices}NEW_DATE"
            ).text
            == dat
        ):
            rates = {
                child.tag.split("}")[1]: child.text
                for child in entry.find(
                    ".//{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}properties"
                )
            }

    yieldTable = [{"duration": 0, "rate": 0}]

    yieldTable.extend(
        {"duration": YIELD_DURATION[key[3:]], "rate": float(value) / 100}
        for key, value in rates.items()
        if key.startswith("BC_") and (key.endswith("YEAR") or key.endswith("MONTH"))
    )
    # entry = "{http://www.w3.org/2005/Atom}entry"

    # entry_set = root.findall(entry)
    # for rate in entry_set:
    #     if rate[6][0][1].text == dat:
    #         root = rate
    # yieldTable.extend(
    #     {"duration": YIELD_DURATION[w.tag[58:]], "rate": float(w.text) / 100}
    #     for w in root[6][0][2:-1]
    # )
    return pd.DataFrame(yieldTable[1:])


def get_annual_yield(durange: Iterable = range(150), **kwargs):
    yield_table = fetch_treasury_yield(**kwargs)
    curve, status = calibrate_ns_ols(
        np.array(yield_table["duration"]), np.array(yield_table["rate"]), tau0=1.0
    )  # starting value of 1.0 for the optimization of tau
    assert status.success
    return curve(np.array(durange))


# kind has to be one of ‘linear’, ‘nearest’, ‘nearest-up’, ‘zero’, ‘slinear’, ‘quadratic’, ‘cubic’, ‘previous’,
# or ‘next’. ‘zero’, ‘slinear’, ‘quadratic’ and ‘cubic’ refer to a spline interpolation of zeroth, first, second or third order;
# ‘previous’ and ‘next’ simply return the previous or next value of the point;
# ‘nearest-up’ and ‘nearest’ differ when interpolating half-integers (e.g. 0.5, 1.5) in that ‘nearest-up’ rounds up and ‘nearest’ rounds down.
# def get_annual_yield_linear(
#     yieldTable=None, durange=range(150), intertype: str = "linear"
# ):
#     if yieldTable is None:
#         yieldTable = get_yield_data()
#     f = interp1d(
#         yieldTable["duration"],
#         yieldTable["rate"],
#         kind=intertype,
#         fill_value=tuple(yieldTable.iloc[[0, -1]]["rate"]),
#         bounds_error=False,
#     )
#     return f(durange)


# amount in dollar
def get_market_size(year: int = 2024) -> float:
    tbl = pd.read_excel(
        DATA_FOLDER / 'SP'/ "Life Fraternal Five Year Histo Data.xlsx",
        index_col=0,
        skiprows=8,
        # skipfooter=37,
        usecols="A:AD",
        # choose the right tab
        sheet_name="Life Fraternal Five Year Histo",
    ).T
    market_size = (
        1000 * tbl["Ordinary Contracts: Whole Life & Endowment Amount"][f"{year}-12-31"]
    )
    return market_size


# retrieve the huge mortality data set from the SOA
def get_mort_data(url: str = MORT_URL):
    r_mort = requests.get(url)

    zip_ref = ZipFile(BytesIO(r_mort.content))

    for i, name in enumerate(zip_ref.namelist()):
        # to make sure there is only one file in the zip
        print(str(i) + name)
        with zip_ref.open(name) as file_contents:
            reader = csv.DictReader(TextIOWrapper(file_contents), delimiter="\t")
            for j, item in enumerate(reader):
                # try a few rows
                if j > 1:
                    break
                print(str(j) + "=========")
                pprint(item)
                # {'Age Basis': '0',
                #  'Amount Exposed': '2742585.841000',
                #  'Attained Age': '52',
                #  'Common Company Indicator 57': '1',
                #  'Death Claim Amount': '.000000',
                #  'Duration': '9',
                #  'Expected Death QX2001VBT by Amount': '5978.8371333800014',
                #  'Expected Death QX2001VBT by Policy': '4.4306527100000007E-2',
                #  'Expected Death QX2008VBT by Amount': '3675.0650269400003',
                #  'Expected Death QX2008VBT by Policy': '2.7234287300000003E-2',
                #  'Expected Death QX2008VBTLU by Amount': '6582.2060183999984',
                #  'Expected Death QX2008VBTLU by Policy': '4.8777828000000002E-2',
                #  'Expected Death QX2015VBT by Amount': '2989.4185666900007',
                #  'Expected Death QX2015VBT by Policy': '2.2153263550000003E-2',
                #  'Expected Death QX7580E by Amount': '8803.700549610001',
                #  'Expected Death QX7580E by Policy': '6.5240344949999973E-2',
                #  'Face Amount Band': '  100000-249999',
                #  'Gender': 'Female',
                #  'Insurance Plan': ' Term',
                #  'Issue Age': '44',
                #  'Issue Year': '2000',
                #  'Number of Deaths': '0',
                #  'Number of Preferred Classes': '2',
                #  'Observation Year': '2009',
                #  'Policies Exposed': '20.324095',
                #  'Preferred Class': '2',
                #  'Preferred Indicator': '1',
                #  'SOA Anticipated Level Term Period': 'Unknown',
                #  'SOA Guaranteed Level Term Period': ' 5 yr guaranteed',
                #  'SOA Post level term indicator': 'Post Level Term',
                #  'Select_Ultimate_Indicator': 'Select',
                #  'Smoker Status': 'NonSmoker'}


if __name__ == "__main__":
    print(get_market_size())
# getYieldData(entryindex=7790)
# getSOAdata(url=constants.VBT_UNISMOKE_URL, filename="unismoke")
# getSOAdata(url=constants.VBT_SMOKEDISTINCT_URL, filename="smokedistinct")
# getSOAdata(url=constants.PERSIST_URL, filename="persistency")
# durange = range(40)
# plt.plot(durange, getAnnualYield(durange=durange, intertype="linear"))
# plt.plot(durange, getAnnualYield(durange=durange, intertype="quadratic"))
