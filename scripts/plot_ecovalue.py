#%%
import pandas as pd
from os import path
import numpy as np
import matplotlib.pyplot as plt
from premiumFinance.constants import (
    DATA_FOLDER,
    FIGURE_FOLDER,
)

#%%
organize_path = path.join(DATA_FOLDER, "sub_organize.xlsx")
profit_path = path.join(DATA_FOLDER, "untappedprofit.xlsx")
wealth_path = path.join(DATA_FOLDER, "pu2020.dta")

#%%
def transCon(row):
    if len(row["Issue Age Group"]) < 4:
        row["Issue Age Group"] = int(row["Issue Age Group"][0:2])
    else:
        row["Issue Age Group"] = int(
            (int(row["Issue Age Group"][0:2]) + int(row["Issue Age Group"][-2:])) / 2
        )
    if len(row["Attained Age Group"]) < 4:
        row["Attained Age Group"] = int(row["Attained Age Group"][0:2])
    else:
        row["Attained Age Group"] = int(
            (int(row["Attained Age Group"][0:2]) + int(row["Attained Age Group"][-2:]))
            / 2
        )
    return row


# %%
def findPV(row, profit_tb):
    condition = [
        row["Gender"],
        row["Smoker Status"],
        row["Issue Age Group"],
        row["Attained Age Group"],
    ]
    data = profit_tb[profit_tb["issueage"] == condition[2]][
        profit_tb["currentage"] == condition[3]
    ][profit_tb["isMale"] == condition[0]][profit_tb["isSmoker"] == condition[1]]
    return float(data["Excess_Policy_PV_yield_curve"])


#%%
organize_tb = pd.read_excel(organize_path)
organize_tb = organize_tb.dropna()
organize_tb = organize_tb[organize_tb["Smoker Status"] != "Unknown"]
organize_tb = organize_tb.replace("Smoker", 1).replace("NonSmoker", 0)
organize_tb = organize_tb.replace("Female", False).replace("Male", True)
organize_tb = organize_tb.apply(lambda row: transCon(row), axis=1)
#%%
profit_tb = pd.read_excel(profit_path)
organize_tb["pv_curve"] = organize_tb.apply(lambda row: findPV(row, profit_tb), axis=1)

# %%
X_label = list(set(organize_tb["Face Amount Band"].values))
sum_dict = dict()
for i in range(len(X_label)):
    sum_dict[X_label[i]] = organize_tb[organize_tb["Face Amount Band"] == X_label[i]][
        "Policies Exposed "
    ].sum()
organize_tb["weight"] = organize_tb.apply(
    lambda row: row["Policies Exposed "] / sum_dict[row["Face Amount Band"]],
    axis=1,
)
organize_tb["weight_value"] = organize_tb.apply(
    lambda row: row["pv_curve"] * row["weight"],
    axis=1,
)
avr = list(
    organize_tb["weight_value"]
    .groupby(organize_tb["Face Amount Band"])
    .sum()
    .iteritems()
)
#%%
wealth_tb = pd.DataFrame()
chunk_reader = pd.read_stata(wealth_path, chunksize=1000)
for i in range(10):
    chunk = chunk_reader.get_chunk(1000)
    chunk = chunk.loc[:, ["TNETWORTH", "WPFINWGT", "TLIFE_FVAL"]].dropna()
    wealth_tb = wealth_tb.append(chunk)

# %%
bins = np.array(
    [
        1,
        9999,
        24999,
        49999,
        99999,
        249999,
        499999,
        999999,
        2499999,
        4999999,
        9999999,
        1e13,
    ]
)


def findPV_2(row, avr_dict):
    return avr_dict[key_map[row["Face Amount Band"]]]


# %%
wealth_tb["Face Amount Band"] = pd.cut(wealth_tb["TLIFE_FVAL"], bins).astype(str)
wealth_tb = wealth_tb[wealth_tb["Face Amount Band"] != "nan"]
key_map = dict()
values = []
for i in range(len(avr)):
    values.append(avr[i][0])
keys = sorted(
    set(wealth_tb["Face Amount Band"]), key=lambda x: float(x.split(",")[0][1:])
)
for i in range(len(keys)):
    key_map[keys[i]] = values[i]
avr_dict = dict()
for i in range(len(avr)):
    avr_dict[avr[i][0]] = avr[i][1]
# %%
wealth_tb["pv_curve"] = wealth_tb.apply(lambda row: findPV_2(row, avr_dict), axis=1)
bins_2 = np.array(
    [
        1,
        4999,
        9999,
        24999,
        49999,
        99999,
        249999,
        499999,
        1e10,
    ]
)
# %%
wealth_tb["Net Worth Band"] = pd.cut(wealth_tb["TNETWORTH"], bins_2).astype(str)
wealth_tb = wealth_tb[wealth_tb["Net Worth Band"] != "nan"]
X_label_2 = list(set(wealth_tb["Net Worth Band"].values))
sum_dict_2 = dict()
for i in range(len(X_label_2)):
    sum_dict_2[X_label_2[i]] = wealth_tb[wealth_tb["Net Worth Band"] == X_label_2[i]][
        "WPFINWGT"
    ].sum()
wealth_tb["weight"] = wealth_tb.apply(
    lambda row: row["WPFINWGT"] / sum_dict_2[row["Net Worth Band"]],
    axis=1,
)
wealth_tb["weight_value"] = wealth_tb.apply(
    lambda row: row["pv_curve"] * row["weight"] * row["TLIFE_FVAL"] / row["TNETWORTH"],
    axis=1,
)
avr_2 = list(
    wealth_tb["weight_value"].groupby(wealth_tb["Net Worth Band"]).sum().iteritems()
)
avr_2.sort(key=lambda x: -x[1])
#%%
X = np.array(avr_2)[:, 0]
heights = np.array(avr_2)[:, 1].astype(float)
plt.bar(x=X, height=heights, width=0.7, color="royalblue", label="value")
for x, y in enumerate(heights):
    plt.text(x, y, "%s" % round(y, 2), ha="center", va="bottom", fontsize=8)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(path.join(FIGURE_FOLDER, "eco_wealth_distr.pdf"))
plt.show()
#%%
conditions = list(
    organize_tb.groupby(
        ["Face Amount Band", "Gender", "Attained Age Group"]
    ).groups.keys()
)
sum_dict_3 = dict()
for con in conditions:
    sum_dict_3[con] = organize_tb[organize_tb["Face Amount Band"] == con[0]][
        organize_tb["Gender"] == con[1]
    ][organize_tb["Attained Age Group"] == con[2]]["Policies Exposed "].sum()
organize_tb["weight"] = organize_tb.apply(
    lambda row: row["Policies Exposed "]
    / sum_dict_3[row["Face Amount Band"], row["Gender"], row["Attained Age Group"]],
    axis=1,
)
organize_tb["weight_value"] = organize_tb.apply(
    lambda row: row["pv_curve"] * row["weight"],
    axis=1,
)
avr_3 = list(
    organize_tb["weight_value"]
    .groupby(
        [
            organize_tb["Face Amount Band"],
            organize_tb["Gender"],
            organize_tb["Attained Age Group"],
        ]
    )
    .sum()
    .iteritems()
)
# %%
wealth_tb = pd.DataFrame()
chunk_reader = pd.read_stata(wealth_path, chunksize=1000)
for i in range(600):
    chunk = chunk_reader.get_chunk(1000)
    chunk = chunk.loc[
        :, ["TNETWORTH", "WPFINWGT", "TLIFE_FVAL", "ESEX", "TAGE"]
    ].dropna()
    wealth_tb = wealth_tb.append(chunk)
wealth_tb["Face Amount Band"] = pd.cut(wealth_tb["TLIFE_FVAL"], bins).astype(str)
# %%
sub_organize_tb = pd.read_excel(organize_path)
sub_organize_tb = sub_organize_tb.dropna()
age_set = set(sub_organize_tb["Attained Age Group"])
age_bins = []
for i, age in enumerate(age_set):
    age_bins.append(int(age[0:2]))
age_bins = sorted(age_bins)
#%%
wealth_tb["Age Band"] = pd.cut(wealth_tb["TAGE"], age_bins).astype(str)
wealth_tb = wealth_tb[wealth_tb["Age Band"] != "nan"]
wealth_tb = wealth_tb[wealth_tb["Face Amount Band"] != "nan"]
wealth_tb["Age Band"] = wealth_tb.apply(
    lambda row: (int(int(row["Age Band"][1:3]) + int(row["Age Band"][-3:-1]) - 1) / 2),
    axis=1,
)
wealth_tb["ESEX"] = wealth_tb["ESEX"].replace(1, True).replace(2, False)
#%%
def findPV_3(row, avr_dict_3):
    key = (
        key_map_3[row["Face Amount Band"]],
        row["ESEX"],
        row["Age Band"],
    )
    data = avr_dict_3[key]
    return data


# %%
key_map_3 = dict()
values = []
for i in range(len(avr)):
    values.append(avr[i][0])
keys = sorted(
    set(wealth_tb["Face Amount Band"]), key=lambda x: float(x.split(",")[0][1:])
)
for i in range(len(keys)):
    key_map_3[keys[i]] = values[i]
#%%
avr_dict_3 = dict()
for i in range(len(avr_3)):
    avr_dict_3[avr_3[i][0]] = avr_3[i][1]
wealth_tb["pv_curve"] = wealth_tb.apply(lambda row: findPV_3(row, avr_dict_3), axis=1)
# %%
wealth_tb["Net Worth Band"] = pd.cut(wealth_tb["TNETWORTH"], bins_2).astype(str)
wealth_tb = wealth_tb[wealth_tb["Net Worth Band"] != "nan"]
con_networth = list(set(wealth_tb["Net Worth Band"].values))
sum_dict_4 = dict()
for i in range(len(con_networth)):
    sum_dict_4[con_networth[i]] = wealth_tb[
        wealth_tb["Net Worth Band"] == con_networth[i]
    ]["WPFINWGT"].sum()
wealth_tb["weight"] = wealth_tb.apply(
    lambda row: row["WPFINWGT"] / sum_dict_4[row["Net Worth Band"]],
    axis=1,
)
wealth_tb["eco_value"] = wealth_tb.apply(
    lambda row: row["pv_curve"] * row["TLIFE_FVAL"] / row["TNETWORTH"], axis=1
)
eco_path = path.join(DATA_FOLDER, "eco_value.xlsx")
wealth_tb.to_excel(eco_path)
wealth_tb["weight_value"] = wealth_tb["weight"] * wealth_tb["eco_value"]
avr_4 = list(
    wealth_tb["weight_value"].groupby(wealth_tb["Net Worth Band"]).sum().iteritems()
)
avr_4.sort(key=lambda x: -x[1])
#%%
X = np.array(avr_4)[:, 0]
heights = np.array(avr_4)[:, 1].astype(float)
plt.bar(x=X, height=heights, width=0.7, color="royalblue", label="value")
for x, y in enumerate(heights):
    plt.text(x, y, "%s" % round(y, 2), ha="center", va="bottom", fontsize=8)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(path.join(FIGURE_FOLDER, "eco_wealth_gender_age_distr_.pdf"))
plt.show()

# %%
