from dataclasses import dataclass
from scipy import optimize

from premiumFinance.inspolicy import InsurancePolicy, extendarray
from typing import Any, Optional, Union, List


@dataclass
class PolicyFinancingScheme:
    policy: InsurancePolicy

    def PV_pr(
        self,
        pr: Any = None,
        levelPr: Optional[bool] = None,
    ):
        if pr is None:
            if levelPr is None:
                pr = self.policy.pr
            else:
                pr = (
                    self.policy.getLevelpr() if levelPr else self.policy.getVariablePr()
                )
        return self.policy.PV_pr(
            pr=pr,
            issuerPerspective=False,
            atIssue=False,
            assumeLapse=False,
        )

    def PV_db(self) -> float:
        return self.policy.PV_db(
            issuerPerspective=False, atIssue=False, assumeLapse=False
        )

    def unpaid_pr(self, pr=None, levelPr: bool = None):
        if pr is None:
            if levelPr is None:
                pr = self.policy.pr
            else:
                starting_period = (
                    self.policy.insrd.currentage - self.policy.insrd.issueage
                )

                pr = (
                    self.policy.getLevelpr()
                    if levelPr
                    else self.policy.getVariablePr()[starting_period:]
                )
        pr = extendarray(pr)
        return pr

    def PV_repay(
        self,
        loanrate: float,
        pr: Any = None,
        levelPr: Optional[bool] = None,
        oneperiod_mort: Any = None,
    ) -> float:
        pr = self.unpaid_pr(pr=pr, levelPr=levelPr)

        if oneperiod_mort is None:
            oneperiod_mort = self.policy.dbPayRate(assumeLapse=False, atIssue=False)

        discount_rate = self.policy.policyholder_rate

        cf = 0.0

        for i in range(len(oneperiod_mort) - 1):
            debt = 0
            for j in range(i):
                debt += pr[j] * (1 + loanrate) ** (i + 1 - j)
            debt *= oneperiod_mort[i + 1]

            cf += debt / (1 + discount_rate[i + 1]) ** (i + 1)

        return cf

    def PV_borrower(
        self,
        loanrate: float,
        pr: Any = None,
        levelPr: Optional[bool] = None,
        fullrecourse: bool = True,
        pv_deathben: Optional[float] = None,
        oneperiod_mort: Any = None,
    ) -> float:
        if pv_deathben is None:
            pv_deathben = self.PV_db()
        pv = pv_deathben - self.PV_repay(
            pr=pr, levelPr=levelPr, loanrate=loanrate, oneperiod_mort=oneperiod_mort
        )
        if fullrecourse:
            pv = max(0, pv)
        return pv

    def PV_lender(
        self,
        loanrate: float,
        pr: Any = None,
        levelPr: Optional[bool] = None,
        fullrecourse: bool = True,
        pv_deathben: Optional[float] = None,
    ) -> float:
        in_flow = self.PV_repay(pr=pr, levelPr=levelPr, loanrate=loanrate)
        if fullrecourse:
            if pv_deathben is None:
                pv_deathben = self.PV_db()
            in_flow = min(pv_deathben, in_flow)
        pv = in_flow - self.PV_pr(pr=pr, levelPr=levelPr)
        return pv

    def PV_lender_maxed(
        self,
        pr: Any = None,
        levelPr: Optional[bool] = None,
        fullrecourse: bool = True,
        pv_deathben: Optional[float] = None,
        surPenalty: Optional[float] = None,
    ) -> float:
        loanrate = self.breakevenLoanRate(
            pr=pr, levelPr=levelPr, surPenalty=surPenalty, fullrecourse=fullrecourse
        )
        pv = self.PV_lender(
            loanrate=loanrate,
            pr=pr,
            levelPr=levelPr,
            fullrecourse=fullrecourse,
            pv_deathben=pv_deathben,
        )
        return pv

    def surrender_value(
        self, pr=None, levelPr: bool = None, surPenalty: Optional[float] = None
    ) -> float:
        if pr is None:
            if levelPr is None:
                pr = self.policy.pr
            elif levelPr:
                pr = self.policy.getLevelpr()
            else:  # if policyholder has been paying variable premium, then cash value is 0
                return 0

        variablepr = self.policy.getVariablePr()
        pr = extendarray(pr)
        sv = 0
        obs_period = self.policy.insrd.currentage - self.policy.insrd.issueage
        for i, vp in enumerate(variablepr[:obs_period]):
            sv += (pr[i] - vp) / (1 + self.policy.cash_interest) ** i
        sv *= 1 - (
            self.policy.surrender_penalty_rate if surPenalty is None else surPenalty
        )
        return sv

    def breakevenLoanRate(
        self,
        pr: Any = None,
        levelPr: Optional[bool] = None,
        surPenalty: Optional[float] = None,
        fullrecourse: bool = True,
    ) -> float:
        sv = self.surrender_value(pr=pr, levelPr=levelPr, surPenalty=surPenalty)
        unpaidpr = self.unpaid_pr(pr=pr, levelPr=levelPr)
        oneperiod_mort = self.policy.dbPayRate(assumeLapse=False, atIssue=False)
        pv_deathben = self.PV_db()
        sol = optimize.root_scalar(
            lambda r: self.PV_borrower(
                pr=unpaidpr,
                loanrate=r,
                fullrecourse=fullrecourse,
                pv_deathben=pv_deathben,
                oneperiod_mort=oneperiod_mort,
            )
            - sv,
            x0=0.001,
            bracket=[-0.5, 3],
            method="brentq",
        )
        return sol.root