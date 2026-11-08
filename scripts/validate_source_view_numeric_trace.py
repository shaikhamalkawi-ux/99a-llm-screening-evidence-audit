#!/usr/bin/env python3
"""Audit two published-source numeric views. No external research data is imputed."""
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import csv, json
P=Path(__file__).resolve().parents[1] / 'data/source_view_numeric_trace_2.csv'

def audit():
    with P.open(encoding='utf-8',newline='') as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==2 and {r['audit_id'] for r in rows}=={'LEADS_2025_VERSION_AND_RATIO','HUOTALA_2024_PRINTED_MEANS'}
    assert all(r['published_url'].startswith('https://') and r['doi'] for r in rows)
    d={r['audit_id']:r for r in rows}
    leads=d['LEADS_2025_VERSION_AND_RATIO']
    assert leads['early_version_kind'].find('preprint')>=0
    assert (leads['early_baseline_recall'],leads['early_assisted_recall'],leads['early_time_saving_pct'])==('0.77','0.81','22.6')
    assert (leads['published_baseline_recall'],leads['published_assisted_recall'],leads['published_time_saving_pct'])==('0.78','0.81','20.8')
    start=Decimal(leads['published_baseline_task_seconds']);end=Decimal(leads['published_assisted_task_seconds'])
    displayed_means_ratio_pct=(start-end)/start*100
    one_decimal=displayed_means_ratio_pct.quantize(Decimal('0.1'),rounding=ROUND_HALF_UP)
    assert one_decimal==Decimal('22.6')
    # Crucial: do NOT assert 22.6 equals journal's 20.8. Different aggregation or report version is unresolved.
    assert one_decimal!=Decimal(leads['published_time_saving_pct'])
    h=d['HUOTALA_2024_PRINTED_MEANS']
    displayed_difference=Decimal(h['published_original_abstract_seconds'])-Decimal(h['published_simplified_abstract_seconds'])
    assert displayed_difference==Decimal('9.69')
    assert displayed_difference!=Decimal(h['published_narrative_difference_seconds'])
    return {'ok':True, 'certificate_rows':len(rows),
        'leads_earlier_preprint_saving_pct':str(leads['early_time_saving_pct']),
        'leads_final_reported_saving_pct':str(leads['published_time_saving_pct']),
        'leads_ratio_of_final_printed_means_pct_to_1dp':str(one_decimal),
        'huotala_difference_of_printed_means_s':str(displayed_difference),
        'huotala_narrative_difference_s':h['published_narrative_difference_seconds'],
        'limits':'Source-view comparison; no re-estimation of individual-level experimental effects'}

if __name__=='__main__':print(json.dumps(audit(),indent=2))
