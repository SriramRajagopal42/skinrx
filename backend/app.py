import os
from flask import Flask, request, jsonify, send_from_directory
from fastai.vision.all import load_learner, PILImage
import pandas as pd

# ————————————————————————————————————————————————
#  Configuration
# ————————————————————————————————————————————————
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH   = os.path.join(BASE_DIR, 'export.pkl')
RECO_PATH    = os.path.join(BASE_DIR, 'recommendation.xlsx')
DIST_DIR     = os.path.normpath(os.path.join(BASE_DIR, '../frontend/skinrx/dist'))

# Create Flask app, pointing static_folder to your React build output
app = Flask(
    __name__,
    static_folder=DIST_DIR,
    static_url_path=''     # serve JS/CSS/assets from /
)

# ————————————————————————————————————————————————
#  Load model and data
# ————————————————————————————————————————————————
learner = load_learner(MODEL_PATH)
df      = pd.read_excel(RECO_PATH)

# ————————————————————————————————————————————————
#  Inference endpoint
# ————————————————————————————————————————————————
@app.route('/predict', methods=['POST'])
def predict():
    img_file = request.files.get('file')
    if not img_file:
        return jsonify({'error': 'No file uploaded.'}), 400

    # Run FastAI prediction
    img        = PILImage.create(img_file.read())
    pred, idx, probs = learner.predict(img)
    label      = str(pred)
    confidence = float(probs[idx])

    # Lookup recommendations for this label
    recs = []
    for _, row in df[df['class'] == label].iterrows():
        recs.append({
            'link':  row['profit_link'],
            'image': row['product_image']
        })

    return jsonify({
        'label':           label,
        'confidence':      round(confidence, 4),
        'recommendations': recs
    })

# ————————————————————————————————————————————————
#  Serve React app
# ————————————————————————————————————————————————
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """
    If the requested file exists in the dist folder, serve it.
    Otherwise fall back to index.html (for client-side routing).
    """
    if path and os.path.exists(os.path.join(DIST_DIR, path)):
        return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, 'index.html')

# ————————————————————————————————————————————————
#  Entry point
# ————————————————————————————————————————————————
if __name__ == '__main__':
    # In production, use Gunicorn/Uvicorn instead of this dev server
    app.run(host='0.0.0.0', port=5000, debug=True)
