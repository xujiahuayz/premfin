import requests
from pandas import read_excel
from scipy.integrate import quad
from scipy.integrate import nquad

VBT_URL = 'https://www.soa.org/globalassets/assets/files/research/exp-study/2015-vbt-unismoke-alb-anb.xlsx'


def premium_integrand(pr, r_free: float = 0.1) -> float:


def pv_premium(pr, r_free: float = 0.1) -> float:
    # entry = nquad(entryint, [
    #     lambda phi, tee: [lstar(tee, phi), np.inf],
    #     [0, upperbound],
    #     [0, np.inf]
    # ], opts=[quadoptions, quadoptions, quadoptions])[0]

    # return dict(plotdata=df, entrydata=entry)


if if __name__ == "__main__":
    r = requests.get(VBT_URL)
    # need to `pip install openpyxl`
    malevbt = read_excel(
        r.content, sheet_name='2015 Male Unismoke ANB', header=2, index_col=0
    )
    femavbt = read_excel(
        r.content, sheet_name='2015 Female Unismoke ANB', header=2, index_col=0
    )
