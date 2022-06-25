import pandas as pd

# Read a Stata dta file
df = pd.read_stata("pu2020.dta")

# Read in the primary data file schema to get data-type information for each variable.
rd_schema = pd.read_json("pu2020_schema.json")

# Read in the replicate weight data file schema to get data-type information for each variable.
rw_schema = pd.read_json("rw2020_schema.json")

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
    header=colmname,
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
