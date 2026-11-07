"""Conditional interpretation gates for LLM-screening audit claims.

This module validates categorical evidence flags supplied by the user. It does
not automatically validate their factual truth, independence or study quality.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Evidence:
    matched_human_time: bool = False
    full_human_overhead_observed: bool = False
    modeled_rates_disclosed: bool = False
    decision_counts_observed: bool = False
    human_oversight_executed_and_timed: bool = False
    policy_simulated_only: bool = False
    complete_eligibility_reference: bool = False
    cohort_independence_verified: bool = False
    comprehensive_search_logged: bool = False
    independent_human_adjudication: bool = False


def evaluate(rule: str, ev: Evidence) -> str:
    """Return highest permitted *wording category* conditional on evidence flags."""
    if rule == 'E01':
        return ('OBSERVED_NET_PERSON_TIME_COMPONENT' if
                (ev.matched_human_time and ev.full_human_overhead_observed)
                else 'TASK_TIME_ONLY_OR_UNIDENTIFIED')
    if rule == 'E02':
        return 'MODELED_SCENARIO_WITH_ASSUMPTIONS' if ev.modeled_rates_disclosed else 'MODELED_CLAIM_HOLD'
    if rule == 'E03':
        return 'DECISION_WORKLOAD_ONLY' if ev.decision_counts_observed else 'DECISION_COUNT_UNVERIFIED'
    if rule == 'E04':
        return ('EXECUTED_HUMAN_OVERSIGHT_TIMED' if ev.human_oversight_executed_and_timed
                else ('SIMULATED_ROUTING_ONLY' if ev.policy_simulated_only else 'HUMAN_OVERSIGHT_UNVERIFIED'))
    if rule == 'E05':
        return 'FULL_REFERENCE_RETENTION' if ev.complete_eligibility_reference else 'VERIFIED_SUBSET_ONLY'
    if rule == 'E06':
        return 'COHORT_INDEPENDENCE_SUPPORTED' if ev.cohort_independence_verified else 'CLUSTER_LINKED_OR_HOLD'
    if rule == 'E07':
        return ('SYSTEMATIC_REVIEW_MINIMUM_PROCESS_GATES' if
                (ev.comprehensive_search_logged and ev.independent_human_adjudication)
                else 'CRITICAL_REVIEW_ONLY')
    raise ValueError(f'Unknown gate: {rule}')
