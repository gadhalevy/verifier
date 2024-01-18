import streamlit as st,os
from pypdf import PdfReader,PdfWriter
import base64,os
def split_pdfs(input_file_path):
    inputpdf = PdfReader(open(input_file_path, "rb"))

    out_paths = []
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    for i, page in enumerate(inputpdf.pages):
        output = PdfWriter()
        output.add_page(page)

        out_file_path = f"outputs/preVision_{i}.pdf"
        with open(out_file_path, "wb") as output_stream:
            output.write(output_stream)

        out_paths.append(out_file_path)
    return out_paths
# split_pdfs('PreVision/preVision.pdf')
def main():
    labs = ('Robotica', 'PreVision', 'Vision', 'Robolego', 'Yetsur', 'HMI', 'Android', 'IOT', 'Auto car 1','Social networks')
    for l in labs:
        st.write(os.listdir(l))
main()
