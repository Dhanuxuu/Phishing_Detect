# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from phishing_predict import predict_url  # your Python script functions

# app = Flask(__name__)
# CORS(app)  # Allow all origins (for development)

# @app.route('/')
# def home():
#     return "PhishGuard AI Backend Running!"

# @app.route('/predict', methods=['POST'])
# def predict():
#     data = request.json
#     url = data.get('url')
#     if not url:
#         return jsonify({"error": "No URL provided"}), 400
    
#     verdict, probability, reasons = predict_url(url)
    
#     return jsonify({
#         "url": url,
#         "verdict": verdict,
#         "probability": probability,
#         "reasons": reasons
#     })

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, jsonify
from phishing_predict import predict_url  # your script

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    url = request.json.get('url')
    verdict, probability, reasons = predict_url(url)
    return jsonify({
        'verdict': verdict,
        'probability': float(probability),  # convert to native float
        'reasons': reasons
    })

    # verdict, probability, reasons = predict_url(url)
    # return jsonify({
    #     'verdict': verdict,
    #     'probability': probability,
    #     'reasons': reasons
    # })

if __name__ == '__main__':
    app.run(debug=True)
