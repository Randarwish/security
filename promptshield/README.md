# PromptShield: Gemini prompt-injection detection benchmark

Compare a fixed regular-expression baseline with a Gemini classifier on a held-out, real public dataset. Record classification quality, malformed answers, request latency and provider token metadata. This measures **detection**, not successful attacks against an agent.

## Dataset and provenance

- Source: https://huggingface.co/datasets/deepset/prompt-injections
- Immutable revision: `b4218bf21defc7780bfca76d7048fd23f165977a`
- Published splits: 546 train / 116 test; columns `text` and `label` (0 benign, 1 injection).
- Dataset card declares Apache-2.0 at the top level but also contains a conflicting nested CC-BY-4.0 field. Preserve source attribution and review upstream terms before redistributing. Raw data is downloaded locally, not committed.
- `prepare.py` saves hashes, row counts and revision. `run.py` verifies the hash before evaluation.
- Test prompts are never used as few-shot examples. The baseline is intentionally weak; this small dataset is not a comprehensive or independent safety certification. Model pretraining contamination cannot be ruled out.

## Run without cloud spending

From the repository root, using Python 3.11 or later:

```bash
python -m pip install -r promptshield/requirements.txt
python -m promptshield.prepare
python -m promptshield.run --provider baseline --limit 116 --output results/promptshield-baseline
python -m unittest promptshield.test_promptshield -v
```

Download requires Hugging Face access. If your environment uses a SOCKS proxy, install `httpx[socks]`. The runner rejects an existing output file to preserve earlier experiments; use a new output directory for each run.

## Connect Google Cloud together

Browser sign-in to Gemini or AI Studio **does not authenticate Python**. Cloud project `ai-governance-assessor` is a candidate only: its billing linkage and credit eligibility have not been verified. Do not assume the Default Gemini Project uses Cloud trial credit.

Before the first API request:

1. Verify the project billing account, remaining promotional credit, expiry and eligibility for the selected model/service in Cloud billing. No prepay activation or paid upgrade is part of this repository.
2. Configure a provider-native budget and email notification at 30% consumed ($90 of an original $300), then 50%, 75%, 90% and 100%. Scope and credit treatment must match eligible credit consumption across all projects. A normal monthly net-cost budget is not automatically equivalent to a cumulative trial-credit monitor.
3. Authenticate locally using `gcloud auth application-default login`. For hosted automation, prefer workload identity federation rather than exported service-account keys.
4. Confirm that the required service and model are available in the verified project and region. Do not enable services blindly.
5. Set `GOOGLE_CLOUD_PROJECT` and optionally `GOOGLE_CLOUD_LOCATION` (default `global`). Select an available model explicitly; there is no default moving model alias.

Then begin with **one** request:

```bash
python -m promptshield.run --provider gemini --live --model YOUR_VERIFIED_MODEL_ID --limit 1 --output results/promptshield-gemini-smoke
```

The client uses Google Gen AI SDK with Cloud credentials, no tool execution, a JSON schema, a 256-token output limit and one attempt per request. Dataset text is untrusted and is placed in a JSON value under a separate system instruction; this boundary is a defense, not a guarantee. Prompt and completion bodies are omitted from logs; hashes identify public test cases. API failures stop the run and do not trigger retry loops. A failed request may still incur a cost and may not return token counts.

## Usage and credit monitoring: distinct sources

| Evidence | What it establishes |
| --- | --- |
| `events.jsonl` | Requests attempted by this runner, returned tokens, latency and response validity |
| Cloud billing / credit records | Actual account-wide credit consumption, other services and delayed charges |
| Provider email alerts | Notifications independent of whether this experiment is running |

Token metadata is **not** an authoritative dollar balance. Pricing can vary by model, context length, thinking tokens and discounts. Billing records may lag. The runner limits requests per invocation (at most 116), not cumulative account spend, and is not a hard $300 cap. Stopping exactly at zero credit cannot be guaranteed from delayed usage data.

To check thresholds from a manually verified credit snapshot, save this structure outside Git:

```json
{
  "source": "Cloud billing promotional credit record",
  "verified_at": "REPLACE_WITH_ACTUAL_ISO_TIMESTAMP",
  "initial_credit_usd": 300,
  "consumed_credit_usd": 90
}
```

```bash
python -m promptshield.budget --snapshot data/credit-snapshot.json
```

The numbers above are an **example**, not the account balance. This command reports crossed thresholds only. It does not fetch billing data, send email or run on a schedule. **Live billing monitoring and email alerts remain unconfigured until Cloud access is available.** Never commit API keys, credentials, billing exports or snapshots. Use the existing ignored `data/` and `results/` directories.

## Outputs and interpretation

`summary.json` reports coverage, accuracy counting invalid predictions as errors, precision/recall/F1 on valid predictions, and a confusion matrix. Inspect coverage alongside valid-only metrics. `events.jsonl` is flushed after each request. A partial run retains its observations and records the requested count separately from the evaluated count. Do not describe baseline results as Gemini performance.

### Measured first baseline: November 3, 2026

The fixed regex baseline was executed on all 116 held-out examples: **48.28% accuracy, 0% injection recall** (0 true positives, 60 false negatives, 56 true negatives, 0 false positives). This baseline is inadequate. No Gemini inference was performed. The dataset includes broad role/task redirections, so labels require context and are not equivalent to malicious intent. Do not tune the regex against these test results and then present it as an untouched test evaluation.

Summary and dataset hashes are committed under `reports/`; raw prompts and generated events stay outside version control. Tested with Python 3.12, datasets 4.8.5 and google-genai 2.34.0. Four offline unit tests pass. Live Cloud authentication, model availability, inference and billing notifications remain unverified.

Official SDK: https://github.com/googleapis/python-genai
