import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import base64
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
def send_email(subject, body, sender, receiver,files):
    with open('pass.txt') as f:
        password = f.read()

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = subject
    message["Bcc"] = receiver  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))
    for i,filename in enumerate(files):

        # Open PDF file in binary mode

        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            part = MIMEBase("application", "octet-stream")
            # Email client can usually download this automatically as attachment
            part.set_payload(attachment.read())

            # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
        part.add_header(
            f"Content-Disposition" ,
            f"attachment; filename= {filename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, text)

@st.cache(allow_output_mutation=True)
def init():
    try:
        firebase_admin.delete_app(firebase_admin.get_app())
    except ValueError:
        pass
    # tmp = platform.platform()
    # # print(tmp)
    # if 'Windows' in tmp:
    #     cred = credentials.Certificate("H:/Gibui260318/pythonStuff/verifier/apikey.json")
    #     ocr.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    # else:
    cred = credentials.Certificate('apikey.json')
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://Lab9-c9743.firebaseio.com/',
                                             'storageBucket' :'lab9-c9743.appspot.com'})


def load(what,f,year,semester,lab,group):
    ds=storage.bucket()
    bob=ds.blob(f.name)
    bob.upload_from_file(f)
    ds.rename_blob(bob,'{}/{}/{}/{}/{}_{}'.format(what,year,semester,lab,group,f.name))

def displayPDF(file):
    # Opening file from file path
    # with open(file, "rb") as f:
    #     base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    base64_pdf = base64.b64encode(file).decode('utf-8')
    # Embedding PDF in HTML
    pdf_display = pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)
def main():
    init()
    st.header("Verifier")
    st.subheader('Assist you with your submissions')
    if not 'counter' in st.session_state:
        st.session_state['counter']=0
#     path = st.sidebar.file_uploader("Find the Overview.csv file of students groups")
#     year=st.sidebar.selectbox('Please choose year',['תשפג','תשפד','תשפה','תשפו','תשפז','תשפח','Tashpag'])
    year=st.sidebar.selectbox('Please choose year',['Tashpad','Tashpah','Tashpav'])
    labs=('Choose', 'Robotica', 'Vision', 'Robolego', 'Yetsur', 'Android', 'IOT','Auto car 1','Auto car 2')
    semester=st.sidebar.selectbox("Please choose semester",('A','B'))
    lab = st.sidebar.selectbox('Please select maabada',labs)
    options=range(1,21)
    group=st.sidebar.select_slider('Please choose group number',options)
    movies=st.file_uploader("Please select your movies",accept_multiple_files=True)
    for m in movies:
        if m.name.lower().endswith('mp4'):
            load('Movies',m,year,semester,lab,group)
        else:
            st.error('Must be mp4',icon="🚨")
    files=st.file_uploader("Please select your code submission files",accept_multiple_files=True)
    for f in files:
        if f.name.lower().endswith('py') or f.name.lower().endswith('kv'):
            load('Code',f,year,semester,lab,group)
        else:
            st.error('Must be py or kv',icon="🚨")
    tadrikh=st.sidebar.file_uploader('Select instruction set')
    if tadrikh:
        displayPDF(tadrikh.read1())


main()