import requests
from pandas import read_excel

vbt_url = 'https://www.soa.org/globalassets/assets/files/research/exp-study/2015-vbt-unismoke-alb-anb.xlsx'
r = requests.get(vbt_url)

# need to `pip install openpyxl`
malevbt = read_excel(
    r.content, sheet_name='2015 Male Unismoke ANB', header=2, index_col=0)
femavbt = read_excel(
    r.content, sheet_name='2015 Female Unismoke ANB', header=2, index_col=0)
