import streamlit as st,os
from pypdf import PdfReader,PdfWriter
import base64,os
def new_lab():
    st.session_state.numpage = 0
    
def next_page():
    st.session_state.numpage+=1
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
    if 'numpage' not in st.session_state:
        st.session_state['numpage'] = 0
    labs = ('Robotica', 'PreVision', 'Vision', 'Robolego', 'Yetsur', 'HMI', 'Android', 'IOT', 'Auto car 1','Social networks')
    lab = st.sidebar.selectbox('Please select maabada', options=labs,on_change=new_lab())
    lstdir = os.listdir(f'splitted/{lab}')
    read = st.button('Press to read a page',on_click=next_page())
    if read:
        st.write(st.session_state)
        # st.session_state['numpage']+=1
        # if st.session_state.numpage>=len(lstdir):
        #     st.error('No more pages!',icon="🚨")
        # else:
        #     st.write(st.session_state.numpage)
        #     with open(f'splitted/{lab}/{lab}_{st.session_state.numpage}.pdf', "rb") as file:
        #         base64_pdf = base64.b64encode(file.read()).decode('utf-8')
        #     pdf = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        #     st.markdown(pdf, unsafe_allow_html=True)
        #     st.session_state.numpage+=1
    # for lab in labs:
    #     st.write(os.listdir(f'splitted/{lab}'))
        # for l in os.listdir(lab):
        #     if l.endswith('pdf'):
        #         split_pdfs(f'{lab}/{l}',lab)

main()
