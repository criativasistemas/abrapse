import os
from flask import Flask, request, jsonify
from google.cloud import storage, vision
import base64
import io

app = Flask(__name__)

# Configurar as credenciais do Google Cloud
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/google-cloud-key.json'
bucket_name = 'your-bucket-name'  # Substitua pelo nome do bucket

# Inicializar a Google Cloud Vision API
vision_client = vision.ImageAnnotatorClient()

def upload_image_to_gcs(image_data, image_name):
    """Faz o upload de uma imagem base64 para o Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(image_name)

    # Converter base64 para bytes
    img_bytes = base64.b64decode(image_data.split(',')[1])
    
    # Fazer upload da imagem
    blob.upload_from_string(img_bytes, content_type='image/png')
    return image_name

def analyze_image_with_vision(image_data):
    """Analisa a imagem usando Google Cloud Vision para extrair características que ajudam na análise PASI."""
    # Decodificar base64 para bytes
    img_bytes = base64.b64decode(image_data.split(',')[1])

    # Criar a imagem a partir dos bytes
    image = vision.Image(content=img_bytes)

    # Usar detecção de rótulos (label detection) como exemplo para obter informações sobre a pele
    response = vision_client.label_detection(image=image)
    labels = response.label_annotations
    
    # Processar a resposta para identificar características relevantes
    analysis = {
        'eritema': 0,  # Eritema (vermelhidão)
        'induracao': 0,  # Induração (espessura)
        'descamacao': 0  # Descamação (escamas)
    }
    
    # Interpretar as labels retornadas para associar com as características do PASI
    for label in labels:
        description = label.description.lower()
        if 'redness' in description or 'rash' in description:
            analysis['eritema'] += label.score  # Eritema detectado
        if 'thick' in description or 'skin' in description:
            analysis['induracao'] += label.score  # Induração detectada
        if 'scaly' in description or 'scale' in description:
            analysis['descamacao'] += label.score  # Descamação detectada
    
    return analysis

def calculate_pasi(analysis_results):
    """Cálculo simples do índice PASI com base nas características das imagens."""
    # Para simplificação, estamos usando os valores dos escores como fatores no cálculo do PASI
    pasi_score = 0
    total_area_score = 1  # Neste exemplo, vamos assumir que cada área tem o mesmo peso
    
    # Somamos as características analisadas
    for area, analysis in analysis_results.items():
        eritema = analysis['eritema']
        induracao = analysis['induracao']
        descamacao = analysis['descamacao']
        
        # O índice PASI é calculado com base nas médias de cada área do corpo
        pasi_score += total_area_score * (eritema + induracao + descamacao)
    
    return round(pasi_score, 2)

@app.route('/upload', methods=['POST'])
def upload_images():
    data = request.get_json()
    images = data.get('images', [])
    
    analysis_results = {}
    
    # Fazer upload de cada imagem capturada e analisar cada uma
    for idx, image in enumerate(images):
        image_name = f'teste_pasi_image_{idx+1}.png'
        upload_image_to_gcs(image, image_name)
        
        # Analisar a imagem com a Google Vision API
        analysis = analyze_image_with_vision(image)
        analysis_results[f'area_{idx+1}'] = analysis
    
    # Calcular o índice PASI com base nas análises
    pasi_score = calculate_pasi(analysis_results)

    return jsonify({
        'message': 'Imagens enviadas e analisadas com sucesso',
        'pasi_score': pasi_score,
        'analysis_results': analysis_results
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
