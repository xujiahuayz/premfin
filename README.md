# Premium financing for life insurance policies

Clone this repository

```bash
git clone https://github.com/xujiahuayz/premfin.git
```

Navigate to the directory of the cloned repo

```bash
cd premfin
```

## Set up the repo

### Give execute permission to your script and then run `setup_repo.sh`

```
chmod +x setup_repo.sh
./setup_repo.sh
```

or follow the step-by-step instructions below

### Create a python virtual environment

- iOS

```zsh
python3 -m venv venv
```

- Windows

```
python -m venv venv
```

### Activate the virtual environment

- iOS

```zsh
. venv/bin/activate
```

- Windows (in Command Prompt, NOT Powershell)

```zsh
venv\Scripts\activate.bat
```

## Install the project in editable mode

```
pip install -e ".[dev]"
```

## Git Large File Storage (Git LFS)

All files in [`data/`](data/) are stored with `lfs`.

To initialize Git LFS:

```
git lfs install
```

```
git lfs track data/**/*
```

To pull data files, use

```
git lfs pull
```
(Could run first if error show when running)

## Run scripts

```zsh
cd scripts
```

plot betas

```zsh
python plot_betas.py
```

create a clean `mortality_experience_clean.xlsx`:

```zsh
python process_empirical_table.py
```

get surrender value, max loan rate acceptable by policyholder, lender profit at max loan rate in one go:

```zsh
python get_surrendervalue_maxloanrate_lenderprofit.py
```

get different untapped profit based on different VBT tables and mortality rates from the perspective of policyholder when their cost of capital is at various levels:

```zsh
python get_untappedprofit_policyholder.py
```

1. plot money left based on different VBT on the table from the perspective of policyholder in comparison with real estate value loss during the financial crisis:
2. plot distribution of life insurance value to policyhodlers on gender and age:
3. plot avearge value to policy holders of different face value amount:

```zsh
python plot_moneyleft.py
```

get untapped profit from the perspective of lender when their cost of capital is at various levels:

```zsh
python get_lenderprofit.py
```

1. get median value loss from common household mistakes
2. And its distribution on age and gender:

```zsh
python get_median.py
```

plot value to policy holders of different net worth band:

```zsh
python plot_wealth_distr.py
```

1. plot economic value to policy holders of different net worth based on Face Amount Band:
2. plot economic value to policy holders of different net worth based on Face Amount Band, Attainedage and Gender:

```zsh
python plot_ecovalue.py
```

1. plot lapsed life inusrance economic value and Food stamp, Medicare and Medicaid.
2. Break down the life insurance economic value and see its distribution on gender and age

```zsh
python plot_wealthtransferprogram.py
```

## Synchronize with the repo

Always pull latest code first

```bash
git pull
```

Make changes locally, save. And then add, commit and push

```bash
git add [file-to-add]
git commit -m "update message"
git push
```

# Best practice

## Coding Style

We follow [PEP8](https://www.python.org/dev/peps/pep-0008/) coding format.
The most important rules above all:

1. Keep code lines length below 80 characters. Maximum 120. Long code lines are NOT readable.
1. We use snake_case to name function, variables. CamelCase for classes.
1. We make our code as DRY (Don't repeat yourself) as possible.
1. We give a description to classes, methods and functions.
1. Variables should be self explaining and just right long:
   - `implied_volatility` is preferred over `impl_v`
   - `implied_volatility` is preferred over `implied_volatility_from_broker_name`

## Do not

1. Do not place .py files at root level (besides setup.py)!
1. Do not upload big files > 100 MB.
1. Do not upload log files.
1. Do not declare constant variables in the MIDDLE of a function
