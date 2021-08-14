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

get untapped profit from the perspective of policyholder when their cost of capital is at various levels:

```zsh
python get_untappedprofit_policyholder.py
```

plot money left of the table from the perspective of policyholder in comparison with real estate value loss during the financial crisis:

```zsh
python plot_moneyleft.py
```

get untapped profit from the perspective of lender when their cost of capital is at various levels:

```zsh
python get_lenderprofit.py
```
