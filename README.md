# LumaLab — Homomorphic Illumination Correction

A responsive educational Digital Image Processing web app using Flask, NumPy and OpenCV.

## Features
- Image upload, adjustable filter parameters, before/after comparison and JPEG download.
- Homomorphic filtering on LAB luminance to preserve chroma.
- Supports PNG, JPG, WEBP, BMP and TIFF; 12 MB upload and 24 MP image limits.
- Uploaded images are processed in memory and not stored.

## Algorithm
Model the image as illumination multiplied by reflectance. Apply log transform, 2D FFT, a smooth high-pass emphasis transfer function, inverse FFT and exponential reconstruction. Percentile normalization maps output to 8-bit luminance.

`H(u,v) = (gamma_h - gamma_l) * (1 - exp(-sharpness * D² / cutoff²)) + gamma_l`

## Run locally
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000.

## Deploy
Import this repository into Vercel; `vercel.json` configures the Python runtime. Use a container host for sustained large-image workloads.

## API
- `GET /health`
- `POST /api/process` multipart form: `image`, optional `gamma_l`, `gamma_h`, `cutoff`, `sharpness`.

## Limitations
Filtering cannot recover clipped highlights or lost shadow detail. Strong high-frequency gain can amplify noise; results depend on image content and parameters.
