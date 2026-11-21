#!/usr/bin/env python3
"""Independent exact, record-weighted audit of the Mortensen released decisions.

This implementation does not import or read the parent implementation. Raw files
are read-only. All policies are retrospective transformations of the same votes.
"""
import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

INPUT = Path(__file__).resolve().parent / 'sources'
OUTPUT = Path(__file__).resolve().parent / 'independent-output'
REVIEWS = ('Appendicitis', 'DST', 'Omega3')
POLICIES = ('single', 'AND', 'OR', 'perfect_reference_correction_on_disagreement')


def criterion_answer(review, question, raw):
    """Return 1, 0, or None. Only recognized answers imply a decision."""
    if review == 'Appendicitis' and question == 'Question2':
        if raw == 'NoInfo':
            return 1
        try:
            number = float(raw)
        except (TypeError, ValueError):
            return None
        if math.isfinite(number) and number >= 0:
            return int(number >= 10)
        return None
    if raw in ('Yes', 'CantTell'):
        return 1
    if raw == 'No':
        return 0
    return None


def worker_decision(review, row):
    answers = [criterion_answer(review, q, row[q])
               for q in row if q.startswith('Question')]
    if 0 in answers:
        return 0
    if all(answer == 1 for answer in answers):
        return 1
    return None


def empty_matrix():
    return {key: Fraction(0) for key in ('TP', 'FP', 'FN', 'TN')}


def add_prediction(matrix, positive_probability, gold):
    if gold:
        matrix['TP'] += positive_probability
        matrix['FN'] += 1 - positive_probability
    else:
        matrix['FP'] += positive_probability
        matrix['TN'] += 1 - positive_probability


def fraction_json(value):
    if isinstance(value, Fraction):
        return {'fraction': str(value), 'decimal': float(value)}
    if isinstance(value, dict):
        return {key: fraction_json(val) for key, val in value.items()}
    if isinstance(value, (tuple, list)):
        return [fraction_json(val) for val in value]
    return value


def ratios(matrix):
    tp, fp, fn, tn = [matrix[key] for key in ('TP', 'FP', 'FN', 'TN')]
    def divide(a, b):
        return a / b if b else None
    return {
        'precision': divide(tp, tp + fp),
        'recall': divide(tp, tp + fn),
        'specificity': divide(tn, tn + fp),
        'accuracy': divide(tp + tn, tp + fp + fn + tn),
        'selected_mass': tp + fp,
        'selected_fraction': divide(tp + fp, tp + fp + fn + tn),
        'F1': divide(2 * tp, 2 * tp + fp + fn),
    }


def source_rows(review):
    with (INPUT / f'{review}.csv').open(newline='') as handle:
        raw = list(csv.DictReader(handle))
    source_r = (INPUT / f'{review}_processing.r').read_text()
    blacklist = set(re.findall(r'"(A[A-Z0-9]+)"', source_r))
    return raw, blacklist


def audit(review, unknown_policy='omit', blacklist_enabled=True):
    raw, blacklist = source_rows(review)
    non_honeypot = [row for row in raw if row.get('Honeypot', '0') == '0']
    rows = [row for row in non_honeypot
            if not blacklist_enabled or row['WorkerId'] not in blacklist]
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['AbstractId']].append(row)
    matrices = {policy: empty_matrix() for policy in POLICIES}
    disagreement = {'all': Fraction(0), 'gold_positive': Fraction(0),
                    'gold_negative': Fraction(0)}
    unanimous = {'FN_ids': [], 'FP_ids': []}
    rejected = []
    unknown_rows = []
    items = []
    eligible_gold = Counter()
    pair_count = 0
    vote_count = 0
    distinct_workers = set()
    for item_id, item_rows in sorted(grouped.items(), key=lambda item: int(item[0])):
        gold_values = {row['Relevant'] for row in item_rows}
        assert len(gold_values) == 1, (review, item_id, 'inconsistent gold')
        gold = int(next(iter(gold_values)))
        assert gold in (0, 1)
        assert len({row['WorkerId'] for row in item_rows}) == len(item_rows), (
            review, item_id, 'duplicate worker')
        pmids = {row['PMID'] for row in item_rows}
        assert len(pmids) == 1, (review, item_id, 'multiple PMIDs')
        decisions = []
        had_unknown = False
        for row in item_rows:
            vote = worker_decision(review, row)
            if vote is None:
                had_unknown = True
                unknown_rows.append({'AbstractId': item_id,
                                     'AssignmentId': row['AssignmentId'],
                                     'gold': gold,
                                     'questions': {q: row[q] for q in row
                                                   if q.startswith('Question')}})
                if unknown_policy == 'omit':
                    continue
                vote = int(unknown_policy)
            decisions.append(vote)
            distinct_workers.add(row['WorkerId'])
        m = len(decisions)
        if m < 2:
            rejected.append({'AbstractId': item_id, 'votes': m, 'gold': gold})
            continue
        k = sum(decisions)
        n_pairs = math.comb(m, 2)
        both_positive = Fraction(math.comb(k, 2), n_pairs)
        both_negative = Fraction(math.comb(m - k, 2), n_pairs)
        discordant = Fraction(k * (m - k), n_pairs)
        assert both_positive + both_negative + discordant == 1
        probs = {
            'single': Fraction(k, m),
            'AND': both_positive,
            'OR': 1 - both_negative,
            'perfect_reference_correction_on_disagreement': both_positive + gold * discordant,
        }
        assert probs['single'] == (probs['AND'] + probs['OR']) / 2
        for policy, probability in probs.items():
            add_prediction(matrices[policy], probability, gold)
        disagreement['all'] += discordant
        disagreement['gold_positive' if gold else 'gold_negative'] += discordant
        eligible_gold[gold] += 1
        pair_count += n_pairs
        vote_count += m
        if not had_unknown:
            if k == 0 and gold:
                unanimous['FN_ids'].append(item_id)
            if k == m and not gold:
                unanimous['FP_ids'].append(item_id)
        items.append({'review': review, 'AbstractId': item_id,
                      'PMID': next(iter(pmids)), 'gold': gold, 'm': m, 'k': k,
                      'unordered_pair_count': n_pairs,
                      'had_unresolved_source_vote': had_unknown,
                      'disagreement_probability': discordant,
                      'positive_probabilities': probs})
    assert all(sum(matrix.values()) == len(items) for matrix in matrices.values())
    return {
        'review': review,
        'unknown_policy': unknown_policy,
        'blacklist_enabled': blacklist_enabled,
        'raw_rows': len(raw),
        'non_honeypot_rows': len(non_honeypot),
        'source_blacklist_size': len(blacklist),
        'excluded_blacklisted_rows': len(non_honeypot) - len(rows),
        'retained_source_rows': len(rows),
        'unresolved_source_rows': len(unknown_rows),
        'unresolved_rows': unknown_rows,
        'eligible_votes': vote_count,
        'distinct_workers_in_valid_votes': len(distinct_workers),
        'eligible_records': len(items),
        'gold_positive': eligible_gold[1],
        'gold_negative': eligible_gold[0],
        'raw_unordered_pair_count': pair_count,
        'rejected_records': rejected,
        'valid_votes_per_record': dict(Counter(item['m'] for item in items)),
        'matrices': matrices,
        'metrics': {policy: ratios(matrix) for policy, matrix in matrices.items()},
        'disagreement_mass': disagreement,
        'disagreement_fraction': disagreement['all'] / len(items),
        'unanimous_with_no_unknown': {
            'FN_count': len(unanimous['FN_ids']),
            'FP_count': len(unanimous['FP_ids']),
            **unanimous,
        },
        'items': items,
    }


def pool(reviews):
    matrices = {policy: empty_matrix() for policy in POLICIES}
    for review in reviews:
        for policy in POLICIES:
            for cell, value in review['matrices'][policy].items():
                matrices[policy][cell] += value
    disagreement = {
        key: sum((review['disagreement_mass'][key] for review in reviews), Fraction(0))
        for key in ('all', 'gold_positive', 'gold_negative')
    }
    record_count = sum(review['eligible_records'] for review in reviews)
    return {
        'eligible_records': record_count,
        'eligible_votes': sum(review['eligible_votes'] for review in reviews),
        'unresolved_source_rows': sum(review['unresolved_source_rows'] for review in reviews),
        'raw_unordered_pair_count': sum(review['raw_unordered_pair_count'] for review in reviews),
        'gold_positive': sum(review['gold_positive'] for review in reviews),
        'gold_negative': sum(review['gold_negative'] for review in reviews),
        'matrices': matrices,
        'metrics': {policy: ratios(matrix) for policy, matrix in matrices.items()},
        'disagreement_mass': disagreement,
        'disagreement_fraction': disagreement['all'] / record_count,
        'unanimous_with_no_unknown': {
            'FN_count': sum(review['unanimous_with_no_unknown']['FN_count'] for review in reviews),
            'FP_count': sum(review['unanimous_with_no_unknown']['FP_count'] for review in reviews),
        },
    }


def main():
    global INPUT, OUTPUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, default=INPUT,
                        help='Directory containing the source CSV and R files (default: sources beside this script).')
    parser.add_argument('--out-dir', type=Path, default=OUTPUT,
                        help='Output directory (default: independent-output beside this script).')
    parser.add_argument('--item-details', action='store_true',
                        help='Include record-level identifiers and write item probability details.')
    args = parser.parse_args()
    INPUT, OUTPUT = args.source_dir, args.out_dir
    OUTPUT.mkdir(parents=True, exist_ok=True)
    result = {
        'method': 'Exact expectation over every unordered pair of distinct observed workers; each record total weight 1.',
        'reference': 'Main CSV Relevant, source expert title/abstract/keyword screening decision. No _Lvl2 decisions used.',
        'decision_rule': 'Any explicit criterion failure -> exclude; all required criteria Yes/CantTell or numeric>=10/NoInfo -> include; otherwise unresolved.',
        'oracle_caveat': 'Perfect reference correction is a hypothetical upper bound restricted to disagreements, not observed adjudication.',
        'variants': {},
    }
    settings = [('primary', 'omit', True), ('unknown_as_0', '0', True),
                ('unknown_as_1', '1', True), ('no_blacklist', 'omit', False)]
    for label, unknown_policy, blacklist in settings:
        reviews = [audit(review, unknown_policy, blacklist) for review in REVIEWS]
        pooled = pool(reviews)
        if label == 'primary' and args.item_details:
            items = [item for review in reviews for item in review['items']]
            (OUTPUT / 'independent_mortensen_item_probabilities.json').write_text(
                json.dumps(fraction_json(items), ensure_ascii=False, indent=2) + '\n')
        for review in reviews:
            del review['items']
            if not args.item_details:
                del review['unresolved_rows']
                del review['unanimous_with_no_unknown']['FN_ids']
                del review['unanimous_with_no_unknown']['FP_ids']
        result['variants'][label] = {'reviews': reviews, 'pooled': pooled}
    destination = OUTPUT / 'independent_mortensen_audit_results.json'
    destination.write_text(json.dumps(fraction_json(result), ensure_ascii=False, indent=2) + '\n')
    print(destination)
    for label, variant in result['variants'].items():
        pooled = variant['pooled']
        print(label, 'records=', pooled['eligible_records'], 'votes=', pooled['eligible_votes'],
              'pairs=', pooled['raw_unordered_pair_count'])
        for policy, matrix in pooled['matrices'].items():
            print(policy, {key: str(value) for key, value in matrix.items()},
                  {key: round(float(pooled['metrics'][policy][key]), 9)
                   for key in ('precision', 'recall', 'specificity')})
        print('disagreement=', {key: str(value) for key, value in pooled['disagreement_mass'].items()},
              'unanimous=', pooled['unanimous_with_no_unknown'])


if __name__ == '__main__':
    main()
