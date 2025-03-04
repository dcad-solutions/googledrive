from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import werkzeug

app = Flask(__name__)

# Configuração da API do Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'credentials.json'

# Autenticação com a conta de serviço
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

# ID da pasta principal no Google Drive (configurar no Railway)
PARENT_FOLDER_ID = os.getenv('PARENT_FOLDER_ID')

@app.route('/upload', methods=['POST'])
def upload():
    dentista = request.form.get('dentista')
    paciente = request.form.get('paciente')

    if not dentista or not paciente:
        return jsonify({'error': 'Nome do dentista e paciente são obrigatórios'}), 400

    # Criar uma pasta para armazenar os arquivos no Google Drive
    folder_metadata = {
        'name': f"{dentista} - {paciente}",
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [PARENT_FOLDER_ID]
    }
    folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
    folder_id = folder.get('id')

    # Upload dos arquivos
    for file_key in request.files:
        for file in request.files.getlist(file_key):
            filename = werkzeug.utils.secure_filename(file.filename)
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            media = file.read()
            drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    return jsonify({'message': 'Arquivos enviados com sucesso'}), 200

if __name__ == '__main__':
    app.run(debug=True)
