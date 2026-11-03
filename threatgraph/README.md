# ThreatGraph AI

Build a local, inspectable threat-intelligence technique graph from [MITRE ATT&CK STIX data](https://github.com/mitre-attack/attack-stix-data).

```bash
python threatgraph/run.py
```

The script fetches the public Enterprise ATT&CK STIX 2.1 JSON and writes an evidence-preserving graph summary to `results/threatgraph.json`. It tracks technique identifiers, names, descriptions and relationship edges, while excluding revoked and deprecated objects.

**No language model is used in v0.1.** This is a provenance-aware foundation for future grounded threat reasoning and prompt-injection evaluation, not an automated incident attribution engine. The ATT&CK knowledge base documents observed behaviors and is not a labeled incident ground truth.
