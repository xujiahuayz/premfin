import requests
from pandas import read_excel

VBT_URL = 'https://www.soa.org/globalassets/assets/files/research/exp-study/2015-vbt-unismoke-alb-anb.xlsx'


def pv_premium(pr, r_free: float = 0.1) -> float:


if if __name__ == "__main__":
    r = requests.get(VBT_URL)
    # need to `pip install openpyxl`
    malevbt = read_excel(
        r.content, sheet_name='2015 Male Unismoke ANB', header=2, index_col=0
    )
    femavbt = read_excel(
        r.content, sheet_name='2015 Female Unismoke ANB', header=2, index_col=0
    )
