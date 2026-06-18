import io
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive']

@st.cache_resource
def conectar_drive():

    try:
        # 🔐 Produção (Streamlit Cloud)
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=SCOPES
        )

    except Exception:
        # 💻 Ambiente local
        creds = service_account.Credentials.from_service_account_file(
            "credentials.json",
            scopes=SCOPES
        )

    service = build('drive', 'v3', credentials=creds)
    return service

@st.cache_data(ttl=300)
def listar_arquivos(_service, folder_id):
    results = _service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name)"
    ).execute()

    return results.get('files', [])

@st.cache_data(ttl=300)
def baixar_arquivo(_service, file_id):
    request = _service.files().get_media(fileId=file_id)
    file = io.BytesIO()

    downloader = MediaIoBaseDownload(file, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    file.seek(0)
    conteudo = file.read()

    try:
        return conteudo.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return conteudo.decode("latin-1")
        except:
            return conteudo.decode("cp1252")