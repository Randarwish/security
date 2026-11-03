# AdversarialSOC

Research prototype for intrusion-detection evaluation using the [CIC-IDS2017 dataset](https://www.unb.ca/cic/datasets/ids-2017.html), generated in a controlled research testbed.

Download the official **MachineLearningCSV** flow files from the source and extract them into `data/cicids2017/` (do not commit the CSV files).

```bash
pip install pandas numpy scikit-learn
python adversarialsoc/run.py --data-dir data/cicids2017
```

Outputs `results/adversarialsoc.json`: held-out clean metrics and a **feature-corruption stress test**, not a validated evasion attack. The corruption is an intentionally simplistic noise model; many network flow features cannot be manipulated independently by a real attacker. Treat random-split results as an exploratory baseline, not evidence of operational effectiveness.

Future work: day-separated evaluation, feasible traffic transformations, false-positive analysis, and calibrated detection.
