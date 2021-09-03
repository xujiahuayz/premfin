import requests
import csv
from os import path
import pandas as pd
from io import TextIOWrapper, BytesIO
from zipfile import ZipFile
from pprint import pprint
import xml.etree.ElementTree as ET
from scipy.interpolate import interp1d
import numpy as np

from nelson_siegel_svensson.calibrate import calibrate_ns_ols


# must build from source with mac M1
import matplotlib.pyplot as plt
from typing import Optional
from premiumFinance import constants
from premiumFinance.settings import PROJECT_ROOT


# need to `pip install openpyxl`
pers_file = path.join(constants.DATA_FOLDER, "persistency.xlsx")
# read lapse rates
lapse_tbl = pd.read_excel(
    pers_file,
    sheet_name="Universal Life",
    index_col=0,
    skiprows=8,
    skipfooter=71,
    usecols="J:K,O",
)


def getVBTdata(
    vbt: str = "VBT15",
    isMale: bool = True,
    isSmoker: Optional[bool] = False,
    issueage: int = 50,
    currentage: Optional[int] = 70,
) -> pd.Series:

    tbl_index = constants.VBT_TABLES[vbt]["m" if isMale else "f"][
        "unism" if isSmoker is None else "smoke" if isSmoker else "nonsm"
    ]

    tbl_file = path.join(
        PROJECT_ROOT, constants.DATA_FOLDER, f"VBTXML/t{tbl_index}.xml"
    )
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
                for m in sel[issueage - start_age].find("Axis").findall("Y")
            }
        )
        .dropna()
        .astype(float)
    )
    ult_start = issueage + int(sel_mort.index[-1])

    if ult_start <= int(ult_mort.index[-1]):
        curv = sel_mort.append(ult_mort[str(ult_start) :], ignore_index=True)
    else:
        curv = sel_mort.reset_index(drop=True)

    mort = pd.Series([0]).append(curv[(currentage - issueage) :], ignore_index=True)

    return mort


# retrieve SOA data
def getSOAdata(url: str, filename: str):
    request_result = requests.get(url)
    vbt_path = path.join(PROJECT_ROOT, constants.DATA_FOLDER, filename + ".xlsx")
    with open(vbt_path, "wb") as f:
        f.write(request_result.content)


def getYieldData(
    rooturl: str = constants.YIELD_URL,
    entryindex: int = 7782,
    month: int = 2,
    year: int = 2021,
):
    if entryindex is None:
        url = (
            f"{rooturl}?$filter=month(NEW_DATE) eq {month} and year(NEW_DATE) eq {year}"
        )
    else:
        url = f"{rooturl}({entryindex})"
    r_yield = requests.get(url)
    content = r_yield.content.decode("utf-8")
    root = ET.fromstring(content)
    yieldTable = [{"duration": 0, "rate": 0}]

    yieldTable.extend(
        {"duration": constants.YIELD_DURATION[w.tag[58:]], "rate": float(w.text) / 100}
        for w in root[6][0][2:-1]
    )

    return pd.DataFrame(yieldTable)


def getAnnualYield(yieldTable=None, durange=range(150)):
    if yieldTable is None:
        yieldTable = getYieldData()
    curve, status = calibrate_ns_ols(
        np.array(yieldTable["duration"]), np.array(yieldTable["rate"]), tau0=1.0
    )  # starting value of 1.0 for the optimization of tau
    assert status.success
    return curve(np.array(durange))


# kind has to be one of ‘linear’, ‘nearest’, ‘nearest-up’, ‘zero’, ‘slinear’, ‘quadratic’, ‘cubic’, ‘previous’,
# or ‘next’. ‘zero’, ‘slinear’, ‘quadratic’ and ‘cubic’ refer to a spline interpolation of zeroth, first, second or third order;
# ‘previous’ and ‘next’ simply return the previous or next value of the point;
# ‘nearest-up’ and ‘nearest’ differ when interpolating half-integers (e.g. 0.5, 1.5) in that ‘nearest-up’ rounds up and ‘nearest’ rounds down.
def getAnnualYield_linear(
    yieldTable=None, durange=range(150), intertype: str = "linear"
):
    if yieldTable is None:
        yieldTable = getYieldData()
    f = interp1d(
        yieldTable["duration"],
        yieldTable["rate"],
        kind=intertype,
        fill_value=tuple(yieldTable.iloc[[0, -1]]["rate"]),
        bounds_error=False,
    )
    return f(durange)


def getMarketSize(naic_path: str = constants.NAIC_PATH, year: int = 2020) -> float:
    lapse_tbl = pd.read_excel(
        naic_path,
        index_col=0,
        skiprows=8,
        skipfooter=21,
        usecols="A:Z",
    ).T
    market_size = (
        1000 * lapse_tbl["Face Amount of In Force  - Ordinary Life"][f"{year}-12-31"]
    )
    return market_size


# retrieve the huge mortality data set from the SOA
def getMortData(url: str = constants.MORT_URL):
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


# if __name__ == "__main__":
# getYieldData(entryindex=7790)
# getSOAdata(url=constants.VBT_UNISMOKE_URL, filename="unismoke")
# getSOAdata(url=constants.VBT_SMOKEDISTINCT_URL, filename="smokedistinct")
# getSOAdata(url=constants.PERSIST_URL, filename="persistency")
# durange = range(40)
# plt.plot(durange, getAnnualYield(durange=durange, intertype="linear"))
# plt.plot(durange, getAnnualYield(durange=durange, intertype="quadratic"))
