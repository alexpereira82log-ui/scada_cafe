import io
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive']


def conectar_drive():
    creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

    service = build('drive', 'v3', credentials=creds)
    return service


def listar_arquivos(service, folder_id):
    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name)"
    ).execute()

    return results.get('files', [])


def baixar_arquivo(service, file_id):
    request = service.files().get_media(fileId=file_id)
    file = io.BytesIO()

    downloader = MediaIoBaseDownload(file, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    file.seek(0)
    return file.read().decode("utf-8")