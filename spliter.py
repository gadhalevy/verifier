import streamlit as st,os
from pypdf import PdfReader,PdfWriter
import base64,os
def split_pdfs(input_file_path,lab):
    inputpdf = PdfReader(open(input_file_path, "rb"))

    out_paths = []
    if not os.path.exists(f"splitted/{lab}"):
        os.makedirs(f"splitted/{lab}")

    for i, page in enumerate(inputpdf.pages):
        output = PdfWriter()
        output.add_page(page)

        out_file_path = f"splitted/{lab}/{lab}_{i}.pdf"
        with open(out_file_path, "wb") as output_stream:
            output.write(output_stream)

        out_paths.append(out_file_path)
    return out_paths
# split_pdfs('PreVision/preVision.pdf')
def main():
    labs = ('Robotica', 'PreVision', 'Vision', 'Robolego', 'Yetsur', 'HMI', 'Android', 'IOT', 'Auto car 1','Social networks')
    for lab in labs:
        st.write(os.listdir(f'splitted/{lab}'))
        # for l in os.listdir(lab):
        #     if l.endswith('pdf'):
        #         split_pdfs(f'{lab}/{l}',lab)

main()
