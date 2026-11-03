"""Threshold report from a verified cumulative credit-consumption snapshot.

This does not query Cloud Billing, send email, or enforce a cloud-wide cap.
"""
import argparse
import json
import math
from pathlib import Path


def status(initial_credit, consumed):
    if not all(math.isfinite(v) for v in (initial_credit, consumed)) or initial_credit <= 0 or consumed < 0:
        raise ValueError('Credit must be positive and consumed amount nonnegative and finite')
    fraction = consumed / initial_credit
    return {'initial_credit_usd': initial_credit, 'consumed_credit_usd': consumed,
            'remaining_credit_usd': max(0, initial_credit - consumed),
            'used_percent': round(100 * fraction, 2),
            'crossed_thresholds_percent': [t for t in (30, 50, 75, 90, 100) if fraction >= t / 100],
            'exhausted': consumed >= initial_credit}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', type=Path, required=True)
    args = parser.parse_args()
    snapshot = json.loads(args.snapshot.read_text())
    for key in ('source', 'verified_at', 'initial_credit_usd', 'consumed_credit_usd'):
        if key not in snapshot:
            raise ValueError(f'Missing snapshot field: {key}')
    report = status(snapshot['initial_credit_usd'], snapshot['consumed_credit_usd'])
    report.update({'source': snapshot['source'], 'verified_at': snapshot['verified_at'],
                   'email_alerts_configured': False, 'live_billing_connected': False})
    print(json.dumps(report, indent=2))
