<div align="center">

# ◒ LumaLab
### Homomorphic Illumination Correction

A hands-on **Digital Image Processing** lab for correcting uneven illumination and enhancing image details.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.11-5C3EE8?logo=opencv)](https://opencv.org/)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel-black?logo=vercel)](https://vercel.com/)

[Live application](https://homomorphic-filtering.vercel.app) · [Report a bug](https://github.com/gudla0098-arch/homomorphic-filtering/issues)

</div>

---

## Overview

LumaLab demonstrates **homomorphic filtering**, a frequency-domain image enhancement technique. It reduces slowly varying illumination while emphasizing reflectance details.

Upload an image, tune the filter parameters, compare the original and corrected versions, and download the result.

## Features

- Responsive, editorial-style interface for desktop and mobile.
- PNG, JPG, WEBP, BMP and TIFF image upload.
- Python + OpenCV processing on the LAB luminance channel to help preserve colour.
- Four adjustable parameters: low-frequency gain, high-frequency gain, cutoff frequency and transition sharpness.
- Before/after comparison and corrected JPEG download.
- Educational sections explaining the model, filter families, pipeline and limitations.
- Uploads are processed in memory and are not intentionally saved.

## How it works

An image is approximated as the product of illumination and reflectance:

`f(x,y) = i(x,y) × r(x,y)`

The logarithm converts this product into a sum. The app then applies a frequency-domain emphasis filter and reconstructs the enhanced image:

1. Convert RGB input to LAB and isolate luminance.
2. Apply the logarithmic transform.
3. Compute the centered 2D Fourier transform.
4. Apply the smooth high-pass emphasis transfer function.
5. Perform the inverse Fourier transform and exponential reconstruction.
6. Normalize luminance and merge it with the original chroma channels.

The transfer function used by the interactive demo is:

`H(u,v) = (γH − γL) × (1 − exp(−cD² / D₀²)) + γL`

- **γL / γH:** low- and high-frequency gains.
- **D₀:** cutoff frequency.
- **c:** transition sharpness.
- **D:** distance from the frequency origin.

### Filter families

| Filter | Main characteristic | Consideration |
|---|---|---|
| Ideal | Abrupt frequency cutoff | Can introduce ringing |
| Butterworth | Order-controlled roll-off | Transition depends on order |
| Gaussian | Smooth exponential response | Gradual transition |

*The interactive engine uses the smooth exponential emphasis response. The other filter families are included as learning concepts.*

## Run locally

**Recommended:** Python 3.12.

```bash
git clone https://github.com/gudla0098-arch/homomorphic-filtering.git
cd homomorphic-filtering

python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS / Linux: source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000.

## API

### `GET /health`
Returns a JSON health response.

### `POST /api/process`
Send multipart form data containing an `image` file and optional numeric settings:

| Parameter | Default | Allowed range |
|---|---:|---:|
| `gamma_l` | 0.65 | 0–1 |
| `gamma_h` | 1.65 | 1–3 |
| `cutoff` | 42 | 5–120 |
| `sharpness` | 1.8 | 0.5–4 |

A successful response includes original and processed JPEG data URLs, output filename, dimensions and selected parameters. Invalid input returns a JSON error and an appropriate HTTP status.

## Repository structure

```text
homomorphic-filtering/
├── app.py                 # Flask routes and OpenCV algorithm
├── requirements.txt       # Runtime dependencies
├── requirements-dev.txt   # Test dependencies
├── runtime.txt            # Python runtime hint
├── vercel.json            # Vercel build and routing
├── templates/
│   └── index.html         # Main application interface
├── static/
│   ├── styles.css         # Responsive visual system
│   └── app.js             # Upload and interaction logic
├── tests/
│   └── test_app.py        # API smoke tests
└── CONTRIBUTING.md        # Contribution guidelines
```

## Deploy to Vercel

1. Import this GitHub repository into Vercel.
2. Keep the project root directory at the repository root.
3. Deploy from the `main` branch.
4. Check `/health`, then upload a sample image to verify the processing endpoint.

The repository includes `vercel.json` for Vercel's Python runtime. Build success confirms packaging; always test a real image upload after deployment.

## Limits and privacy

- Maximum upload size: **12 MB**.
- Maximum decoded image size: **24 megapixels**.
- Filtering cannot recover clipped highlights or information lost in deep shadows.
- Strong high-frequency gain can amplify sensor noise and compression artifacts.
- Results depend on image content and parameter choices.
- Avoid uploading private or sensitive images to public demos.

## Development and tests

Install test dependencies and run the suite:

```bash
pip install -r requirements.txt
pip install pytest
pytest -q
```

See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

---

<div align="center">

Built as a Digital Image Processing academic project · **LumaLab**

</div>
