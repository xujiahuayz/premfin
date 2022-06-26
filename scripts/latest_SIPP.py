import pandas as pd
import numpy as np

# Read in the primary data file schema to get data-type information for each variable.
rd_schema = pd.read_json("pu2020_schema.json", orient="split")

# Read in the replicate weight data file schema to get data-type information for each variable.
rw_schema = pd.read_json("rw2020_schema.json", orient="split")

# Define Pandas data types based on the schema data-type information for both schema dataframes
rd_schema["dtype"] = [
    "Int64"
    if x == "integer"
    else "object"
    if x == "string"
    else "Float64"
    if x == "float"
    else "ERROR"
    for x in rd_schema["dtype"]
]

rw_schema["dtype"] = [
    "Int64"
    if x == "integer"
    else "object"
    if x == "string"
    else "Float64"
    if x == "float"
    else "ERROR"
    for x in rw_schema["dtype"]
]

# Read in the primary data
df_data = pd.read_csv(
    "pu2020.csv",
    names=rd_schema["name"],  # dtype expects a dictionary of key:values
    dtype=dict(
        [(i, v) for i, v in zip(rd_schema["name"], rd_schema["dtype"])]
    ),  # files are pipe-delimited
    sep="|",
    header=(),
    usecols=[
        "ssuid",
        "swave",
        "erelrpe",
        "wpfinwgt",
        "tirakeoval",
        "tthr401val",
        "tlife_fval",
        "tlife_cval",
        "tannval",
        "tinc_bank",
        "tval_bank",
        "tinc_stmf",
        "tval_stmf",
        "tinc_bond",
        "tval_bond",
        "tinc_rent",
        "tinc_rent",
        "teq_rent",
        "tval_re",
        "teq_re",
        "tinc_oth",
        "tval_oth",
        "tinc_ast",
        "tval_ret",
        "tval_bus",
        "teq_bus",
        "tval_home",
        "teq_home",
        "tval_veh",
        "teq_veh",
        "tval_esav",
        "tval_rmu",
        "tval_ast",
        "tnetworth",
    ],
)

# preview the data
print(df_data.head())

# check some unweighted means against the validation xls file to help ensure that the data were read in correctly.
print("TPTOTINC mean:" + str(df_data.TPTOTINC.mean()))

# Read in the replicate-weight data.
df_rw = pd.read_csv(
    "rw2020.csv",
    dtype=dict([(i, v) for i, v in zip(rw_schema["name"], rw_schema["dtype"])]),
    sep="|",
    header=0,
    names=rw_schema["name"],
)

# preview the data
print(df_rw.head())

# check some unweighted means against the validation xls file.
print("REPWT100 mean:" + str(df_rw.REPWGT100.mean()))

# Merge data and replicate weights on SSUID, PNUM, MONTHCODE
df = df_data.merge(
    df_rw,
    left_on=["SSUID", "PNUM", "MONTHCODE"],
    right_on=["SSUID", "PNUM", "MONTHCODE"],
)

# preview the merged data
print(df.head())

# Example of using the replicate weights to estimate the standard error of a weighted mean
# Requires the NumPy package
df_est = df.loc[df.TPTOTINC.isna() != True]
point_estimate = np.nansum(df_est.TPTOTINC * df_est["WPFINWGT"]) / np.nansum(
    df_est["WPFINWGT"]
)
rep_means = [
    np.nansum(df_est.TPTOTINC * df_est["REPWGT" + str(i)])
    / np.nansum(df_est["REPWGT" + str(i)])
    for i in range(1, 241)
]
variance = (1 / (240 * 0.5**2)) * sum((rep_means - point_estimate) ** 2)
print(
    "Point estimate:{:.2f} , Standard error:{:.2f}".format(
        point_estimate, variance**0.5
    )
)
