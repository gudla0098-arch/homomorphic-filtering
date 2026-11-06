from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import cv2
import numpy as np
import io
import base64

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 12 * 1024 * 1024
ALLOWED = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tif', 'tiff'}

def homomorphic_filter(image, gamma_l=0.65, gamma_h=1.65, cutoff=42.0, sharpness=1.8):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    luminance, a, b = cv2.split(lab)
    src = np.log1p(luminance.astype(np.float32))
    rows, cols = src.shape
    pr, pc = cv2.getOptimalDFTSize(rows), cv2.getOptimalDFTSize(cols)
    padded = np.zeros((pr, pc), np.float32)
    padded[:rows, :cols] = src
    spectrum = np.fft.fftshift(np.fft.fft2(padded))
    y, x = np.ogrid[:pr, :pc]
    d2 = (x - pc // 2) ** 2 + (y - pr // 2) ** 2
    denom = np.maximum(d2 / max(cutoff * cutoff, 1e-6), 1e-8)
    transfer = (gamma_h - gamma_l) * (1 - np.exp(-sharpness * denom)) + gamma_l
    filtered = np.real(np.fft.ifft2(np.fft.ifftshift(spectrum * transfer)))[:rows, :cols]
    restored = np.nan_to_num(np.expm1(filtered), nan=0.0, posinf=255.0, neginf=0.0)
    low, high = np.percentile(restored, (1, 99))
    if high <= low: high = low + 1.0
    enhanced = np.clip((restored - low) * (255.0 / (high - low)), 0, 255).astype(np.uint8)
    return cv2.cvtColor(cv2.merge([enhanced, a, b]), cv2.COLOR_LAB2BGR)

def data_url(image):
    ok, encoded = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if not ok: raise RuntimeError('Could not encode result')
    return 'data:image/jpeg;base64,' + base64.b64encode(encoded.tobytes()).decode('ascii')

@app.get('/')
def index(): return render_template('index.html')

@app.get('/health')
def health(): return jsonify({'status':'ok','engine':'OpenCV homomorphic filter'})

@app.post('/api/process')
def process_image():
    if 'image' not in request.files: return jsonify({'error':'Choose an image before processing.'}), 400
    file = request.files['image']
    if not file.filename or '.' not in file.filename or file.filename.rsplit('.',1)[1].lower() not in ALLOWED:
        return jsonify({'error':'Unsupported image type.'}), 415
    try:
        pil = ImageOps.exif_transpose(Image.open(io.BytesIO(file.read()))).convert('RGB')
        if pil.width * pil.height > 24_000_000: return jsonify({'error':'Image exceeds 24 megapixels.'}), 413
        rgb = np.asarray(pil)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        gl = float(request.form.get('gamma_l', .65)); gh = float(request.form.get('gamma_h', 1.65))
        cutoff = float(request.form.get('cutoff', 42)); sharpness = float(request.form.get('sharpness', 1.8))
        if not (0 <= gl <= 1 and 1 <= gh <= 3 and 5 <= cutoff <= 120 and .5 <= sharpness <= 4):
            return jsonify({'error':'Filter settings are outside the supported range.'}), 400
        result = homomorphic_filter(bgr, gl, gh, cutoff, sharpness)
        return jsonify({'success':True,'filename':secure_filename(file.filename.rsplit('.',1)[0])+'-corrected.jpg','original':data_url(bgr),'processed':data_url(result),'width':pil.width,'height':pil.height,'parameters':{'gamma_l':gl,'gamma_h':gh,'cutoff':cutoff,'sharpness':sharpness}})
    except (OSError, ValueError): return jsonify({'error':'The selected file could not be read as an image.'}), 400
    except Exception:
        app.logger.exception('Image processing failed')
        return jsonify({'error':'Image processing failed. Please try another image.'}), 500

if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, debug=True)
