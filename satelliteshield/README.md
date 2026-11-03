# SatelliteShield

**Status: runnable research prototype; no benchmark results claimed.**

Reproducible white-box adversarial robustness evaluation of land-cover classification on real Sentinel-2-derived [EuroSAT RGB](https://github.com/phelber/EuroSAT) images (27,000 samples; 10 classes).

## Setup
Python 3.11 recommended.

```bash
pip install torch torchvision numpy
python satelliteshield/run.py --epochs 5 --epsilon 0.0156862745
```

The script downloads EuroSAT via torchvision, trains a small convolutional neural network, and evaluates clean, FGSM and PGD accuracy on a fixed held-out split. Metrics are saved to `results/satelliteshield.json` (not committed).

**Threat model:** untargeted white-box pixel-space L-infinity perturbations in [0,1], epsilon 4/255. These do **not** establish physically feasible attacks on satellite sensors.

**Limitations:** random rather than geographic split; RGB rather than 13-band imagery; no physical radiometry; baseline network only. Do not publish benchmark performance before executing experiments. Original imagery is not redistributed.

Data: https://github.com/phelber/EuroSAT ; https://documentation.dataspace.copernicus.eu/APIs/STAC.html
