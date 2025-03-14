from premiumFinance.constants import YIELD_CURVE_YEAR
from premiumFinance.fetchdata import get_annual_yield

yield_curve = get_annual_yield(year=YIELD_CURVE_YEAR)
