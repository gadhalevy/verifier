# import streamlit as st,os
# from pypdf import PdfReader,PdfWriter
# import base64,os
# def split_pdfs(input_file_path,lab):
#     inputpdf = PdfReader(open(input_file_path, "rb"))
#
#     out_paths = []
#     if not os.path.exists("splitted"):
#         os.makedirs("splitted")
#
#     for i, page in enumerate(inputpdf.pages):
#         output = PdfWriter()
#         output.add_page(page)
#
#         out_file_path = f"splitted/{lab}/{lab}_{i}.pdf"
#         with open(out_file_path, "wb") as output_stream:
#             output.write(output_stream)
#
#         out_paths.append(out_file_path)
#     return out_paths
# # split_pdfs('PreVision/preVision.pdf')
# def main():
#     labs = ('Robotica', 'PreVision', 'Vision', 'Robolego', 'Yetsur', 'HMI', 'Android', 'IOT', 'Auto car 1','Social networks')
#     for lab in labs:
#         for l in os.listdir(lab):
#             if l.endswith('pdf'):
#                 split_pdfs(f'{lab}/l',lab)
#
# main()
import streamlit as st
import pandas as pd
st.header("Verifier decoder")
st.subheader('Tries to find incorrect submissions')
year = st.sidebar.selectbox('Please choose year', ['Tashpag', 'Tashpad', 'Tashpah','Demo'],1)
labs = ('Choose', 'Robotica', 'PreVision','Vision', 'Robolego', 'Yetsur','HMI', 'Android', 'IOT', 'Auto car 1', 'Auto car 2','Social networks')
semester = st.sidebar.selectbox("Please choose semester", ('A', 'B'),1)
maabada = st.sidebar.selectbox('Please select maabada', labs)
kvutsot = pd.read_csv('groups.csv', header=0)
st.write(kvutsot)
num=len(kvutsot)
remarks = [l + '_rem' for l in labs[1:]]
rem_data = {r: ['Lo nivdak'] * num for r in remarks}
data={l:[100]*num for l in labs[1:]}
data.update(rem_data)
temp=list(zip(labs[1:],remarks))
new_cols=[item for sublist in temp for item in sublist]
grades=pd.DataFrame(columns=new_cols,data=data)
concated=pd.concat([kvutsot,grades],axis=1)
st.write(concated)
concated.to_csv('grades.csv')
