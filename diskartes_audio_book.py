import streamlit as st
import os
import whisper
import pandas as pd
from streamlit.components.v1 import html
import streamlit_scrollable_textbox as stx

from whisper.utils import (
    exact_div,
    format_timestamp,
    get_writer,
    make_safe,
    optional_float,
    optional_int,
    str2bool,
)

writer = get_writer("tsv", "temp/")
writer_args = {"highlight_words":False,
               "max_line_count":None,
               "max_line_width":None}

def create_paragraphs(data):

    paragraphs = []
    paragraph = ""
    time_interval = 60 * 1000  # 1 minutes in milliseconds
    current_time = 0
    
    for index, row in data.iterrows():

        start_time = int(row['start'])
        end_time = int(row['end'])
        text = row['text']

        if current_time + (end_time - start_time) <= time_interval:
            paragraph += text
            current_time += (end_time - start_time)

        else:
            paragraphs.append(paragraph.strip())
            paragraph = text
            current_time = end_time - start_time
        
    if paragraphs:
        paragraphs.append(paragraph.strip())
        
    return paragraphs
 

def main():

    # memanggil whisper dulu
    model = whisper.load_model("small")

    # Header dari halaman
    st.title("Diskartes Audio Book")

    # sedikit description ttg website ini
    st.subheader("sebuah aplikasi web sederhana "+
                 "untuk mengubah file audio podcast dalam format MP3 " +
                 "menjadi teks. Web app ini menggunakan " 
                 "Whisper dari OpenAI.")

    # file Mp3 default dari folder mp3, ini gunakan file paling pertama saja
    file_list = os.listdir("diskartes_mp3/")
    selected_file = st.selectbox("Pilih topik podcast Diskartes", file_list)

    if st.button("Start Podcast"):
        with st.spinner("Processing the file...."):
            # get filenames from selectbox
            fname = "diskartes_mp3/" + selected_file

            # audio display
            audio_file = open(fname, 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/ogg')
            
            # memanggil whisper untuk extraksi text dari audio
            response = model.transcribe(fname, language="id", task="transcribe")
            # html(response['text'], height=300, scrolling=True)

            # menampilkan text dari audio, bagi teks menjadi paragraf untuk tiap 2 menit
            subfile = selected_file[:-4] + ".tsv"
            writer(response, subfile, writer_args)

            data=pd.read_csv("temp/"+subfile, sep="\t", header=0)
            paragraphs = create_paragraphs(data)
            
            long_text = "" 
            for paragraph in paragraphs:
                # st.write(paragraph)
                long_text =long_text +  paragraph + "\n\n"

            stx.scrollableTextbox(long_text,height = 300)


    
if __name__ == '__main__':
    main()