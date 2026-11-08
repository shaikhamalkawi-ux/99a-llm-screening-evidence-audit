"""Sharp finite-universe recall bounds under unresolved exclusion eligibility.

Pure algebra, not an empirical estimate or sampling confidence interval.
Applicability must be checked from an original study; no counts are imputed.
"""
from dataclasses import dataclass
from fractions import Fraction

@dataclass(frozen=True)
class RetentionInterval:
    lower: Fraction
    upper: Fraction
    known_retained_eligible: int
    known_excluded_eligible: int
    unresolved_excluded: int


def bound_full_reference_recall(known_retained_eligible: int,
                                known_excluded_eligible: int,
                                unresolved_excluded: int) -> RetentionInterval:
    """Compute logical sharp bounds conditional on a *complete finite candidate universe*.

    Precondition external to this function: eligibility is settled for all retained
    candidates, all excluded records except `unresolved_excluded` are adjudicated,
    and counts refer to one identical review stage, candidate set, and reference.

    k: known eligible retained; f: verified eligible excluded (false negatives);
    u: excluded with genuinely unresolved eligibility. Unknown eligible excluded
    z may be any integer from zero to u. Observed reference sensitivity k/(k+f)
    is an upper bound, not the full-corpus quantity unless z=0 is established.
    """
    vals=(known_retained_eligible,known_excluded_eligible,unresolved_excluded)
    if any(type(v) is not int or v < 0 for v in vals):
        raise ValueError('Counts must be nonnegative exact integers')
    k,f,u=vals
    if k+f==0:
        raise ValueError('At least one adjudicated eligible record is required')
    lo=Fraction(k,k+f+u)
    hi=Fraction(k,k+f)
    assert lo<=hi
    return RetentionInterval(lo,hi,k,f,u)
