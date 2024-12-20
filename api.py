from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer

app = Flask(__name__)

# Загрузка модели
model = joblib.load('ridge_model.pkl')

imputer = SimpleImputer(strategy='mean')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    post_text = data.get('post_text')
    post_date = data.get('post_date')
    hashtags = data.get('hashtags')

    # Преобразование данных в формат, пригодный для модели
    input_data = pd.DataFrame({
    "наличие эмодзи": [1 if '#' in post_text else 0],
    "количество текста": [len(post_text)],
    "reposts": [0],  
    "comments": [0], 
    })

    input_data_imputed = imputer.fit_transform(input_data)

    # Прогнозирование
    prediction = model.predict(input_data_imputed)

    rounded_prediction = int(round(prediction[0]))

    return jsonify({'prediction': rounded_prediction})

if __name__ == '__main__':
    app.run(debug=True)
