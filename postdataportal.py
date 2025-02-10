import streamlit as st
import pandas as pd
import json
import requests

def process_excel(file):
    # Membaca file Excel
    df = pd.read_excel(file)
    
    # Ganti semua NaN dengan None untuk memastikan JSON valid
    df = df.applymap(lambda x: None if pd.isna(x) else x)

    # Deteksi dan ubah kolom yang berisi data numerik (misalnya integer) menjadi tipe data integer
    for col in df.select_dtypes(include=['float64']).columns:
        # Cek apakah kolom tersebut hanya berisi angka bulat (tanpa desimal)
        if df[col].dropna().apply(lambda x: x.is_integer()).all():
            df[col] = df[col].astype('Int64', errors='ignore')  # Ubah menjadi Int64 jika memungkinkan

    # Ubah data menjadi list of dicts
    data_list = df.to_dict(orient='records')
    return data_list  # Mengembalikan list of dicts

def send_to_api(json_data, api_url, bearer_token):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {bearer_token}'
    }
    try:
        response = requests.post(api_url, json=json_data, headers=headers)
        response.raise_for_status()  # Menangani error HTTP
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        return "Error", str(e)

st.title("Alat Bantu Upload Data Ke Portal Data")

# Upload file
uploaded_file = st.file_uploader("Unggah file Excel", type=["xls", "xlsx"])
api_url = st.text_input("Masukkan URL API tujuan")
data_id = st.text_input("Masukkan Data ID")
tahun_data = st.text_input("Masukkan Tahun Data")
bearer_token = st.text_input("Masukkan Bearer Token", type="password")

if uploaded_file is not None:
    st.success("File berhasil diunggah!")
    data_list = process_excel(uploaded_file)
    json_payload = {
        "data_id": data_id,
        "tahun_data": tahun_data,
        "data": data_list
    }
    json_data = json.dumps(json_payload, indent=4)
    st.subheader("Format JSON yang Akan Dikirim")
    st.code(json_data, language='json')
    
    if st.button("Konfirmasi dan Kirim ke API"):
        if api_url and bearer_token:
            status, response_text = send_to_api(json_payload, api_url, bearer_token)
            st.write(f"Status Code: {status}")
            st.write("Response:", response_text)
            
            # Debugging tambahan
            if status != 200:
                st.error("Terjadi kesalahan saat mengirim data. Periksa kembali API tujuan dan format JSON.")
        else:
            st.error("Harap masukkan URL API tujuan dan Bearer Token")
