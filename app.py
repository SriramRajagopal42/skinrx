from flask import Flask, request, render_template, jsonify
from fastai.vision.all import load_learner, PILImage
import pandas as pd

# 1) Initialize
app = Flask(__name__)

# 2) Load your model once at startup
learner = load_learner('export.pkl')
classes  = learner.dls.vocab

# 3) (Optional) Load recommendations if you want to mirror your Gradio “accordion”:
df = pd.read_excel('recommendation.xlsx')

@app.route('/', methods=['GET'])
def home():
    # Render upload form
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # 1) grab the uploaded file
    img_file = request.files.get('file')
    if not img_file:
        return jsonify({'error': 'no file uploaded'}), 400

    # 2) run inference
    img = PILImage.create(img_file.read())
    pred, idx, probs = learner.predict(img)

    # 3) prepare top-result
    top_label = str(pred)
    top_conf  = float(probs[idx])
    
    # 4) (Optional) lookup recommendation links
    recs = []
    for _, row in df[df['class'] == top_label].iterrows():
        recs.append({
            'link': row['profit_link'],
            'image': row['product_image']
        })

    # 5) return JSON
    return jsonify({
        'label': top_label,
        'confidence': round(top_conf, 4),
        'recommendations': recs
    })

if __name__ == '__main__':
    # In production, run under gunicorn or uvicorn; debug=False for prod.
    app.run(host='0.0.0.0', port=5000, debug=True)
