# AI Security Research Portfolio

Three runnable research prototypes using publicly documented scientific and cybersecurity datasets. **Source code is published; no model training or benchmark runs have been performed yet.**

| Project | Data | Research question | Status |
| --- | --- | --- | --- |
| [SatelliteShield](satelliteshield/) | EuroSAT RGB / Sentinel-2-derived | How robust is a land-cover classifier to FGSM and PGD pixel attacks? | Implementation |
| [AdversarialSOC](adversarialsoc/) | CIC-IDS2017 labeled research traffic | How does intrusion detection respond to feature corruption? | Implementation; no validated evasion |
| [ThreatGraph AI](threatgraph/) | MITRE ATT&CK Enterprise STIX | Can we build a provenance-preserving threat-technique graph? | Implementation |

## Reproducibility and ethics

- Follow each project README for commands, source attribution, and limitations.
- Dataset files, trained weights, and generated results are excluded from version control.
- Do not mistake simulated or testbed observations for operational incident data.
- No attack on live satellites, networks, or third-party infrastructure.
- Do not infer performance from code alone; publish measured results after running experiments.
- Cloud deployment is not configured; no cloud credit has been spent.

## Next milestones

1. Execute and verify each pipeline and record environment/dependency versions.
2. Improve SatelliteShield with geographic splits and multispectral Sentinel-2 Level-2A experiments.
3. Add realistic feasibility constraints and time-separated evaluation to AdversarialSOC.
4. Add grounded retrieval, adversarial prompt-injection evaluation and citations to ThreatGraph AI.
5. Add CI unit tests, dataset integrity manifests, dependency pinning, and experiment cards.
