from datetime import datetime

import streamlit as st,string,secrets
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import base64
import email, smtplib, ssl,os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
def send_email(subject, body, receiver,files=None):
    with open('pass.txt') as f:
        password = f.read()
    sender='khanuka1912@gmail.com'
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = subject
    message["Bcc"] = receiver  # Recommended for mass emails
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    if files:
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

def make_pass():
    letters = string.ascii_letters
    digits = string.digits
    special_chars = string.punctuation
    alphabet = letters + digits + special_chars
    pwd_length = 8
    pwd = ''
    for i in range(pwd_length):
        pwd += ''.join(secrets.choice(alphabet))

    return pwd

def send_pass(receiver):
    subject='Password for ITL'
    pswrd=make_pass()
    body=f'Please enter this password: {pswrd}'
    send_email(subject,body,receiver)
    return pswrd


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

def make_student_list(path):
    df = pd.read_csv(path, header=0)
    skiprows = df.index[df['Groups'] == u'רישום לשלשות מעבדה - 01'].values[0]
    tmp = df.index[df['Grouping name'] == 'Not in a grouping'].values[0]
    df = df.iloc[skiprows:tmp]
    # df = df[[df.columns[1], df.columns[2]]]
    df=df[['Group members','Groups',"Email address"]]
    pd.set_option('display.max_columns', None)
    # return df
    df['Groups'] = df['Groups'].str.split('-')
    # return  df
    stam = pd.DataFrame(df['Groups'].tolist(), columns=['Group', 'num'])
    # return  stam['num']
    df = df.reset_index()
    final = df.join(stam)
    groups = final[['Group members', 'num','Email address']]
    return groups

def find_members(group):
    groups=make_student_list('auth.csv')
    return groups[groups['num'].str.strip()==group]

def fbwrite(*args,**kwards):
    # print(f,created_os,start,created,processed,station,group,lab)
    year,semester,lab,group,student=args
    ref = db.reference(f'/{year}/{semester}/{lab}/{group}/{student}/')
    for k,v in kwards.items():
        ref.set({f'{k}':f'{v}'})

def load(what,f,year,semester,lab,group):
    ds=storage.bucket()
    bob=ds.blob(f.name)
    bob.upload_from_file(f)
    ds.rename_blob(bob,'{}/{}/{}/{}/{}_{}'.format(what,year,semester,lab,group,f.name))
@st.cache(allow_output_mutation=True)
def displayPDF(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # base64_pdf = base64.b64encode(file).decode('utf-8')
    # Embedding PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    return pdf_display
    # Displaying File

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
    base_path=os.path.abspath(os.curdir)
    options = range(1, 21)
    group = st.sidebar.select_slider('Please choose group number', options)
    location = st.sidebar.radio('Please choose location', ['None','Home', 'Lab'])
    if location !='None':
        df_group=find_members(f'{group:02}')
        members=df_group['Group members']
        if location=='Home':
            end=1
        else:
            end=len(members)
            # home=st.sidebar.radio('Mark yourself',members)
        for i in range(end):
            with st.sidebar.form(f'Location{i}'):
                member=st.radio('Who R U?',members)
                reciver=df_group[df_group['Group members'].str.strip()==member]['Email address'].values
                submitted = st.form_submit_button("Send password")
                if submitted:
                    st_pass = send_pass(reciver[0].strip())
                    if st_pass not in st.session_state:
                        st.session_state['st_pass']=st_pass
                    st.write('Password was sent to your email')
                    st.text_input('Write password',max_chars=8,type="password",key="user_pass")
                second_button=st.form_submit_button("Verify password")
                if second_button:
                    if st.session_state.user_pass==st.session_state.st_pass:
                        if end==1:
                            param='start read'
                        else:
                            param='start lab'
                        fbwrite(year,semester,lab,group,member,param=datetime.now())
                        st.session_state.counter+=1
                    else:
                        st.error('Wrong password',icon="🚨")
                missing = st.form_submit_button('Missing')
                if missing:
                    st.write(member[:-1])
                    fbwrite(year,semester,lab,group,member[:-1], missing=datetime.now().strftime("%d/%m/%y"))
                    st.session_state.counter += 1
        if st.session_state.counter==end and lab!='Choose':
            base_path = base_path + f'/{lab}'
            # st.write(os.path.dirname(base_path))
            for f in (os.listdir(os.path.dirname(base_path + '/%s' % lab))):
                # st.write(f)
                if f.endswith('pdf'):
                    # st.write(f)
                    # st.write(base_path+f'/{f}')
                    pdf = displayPDF(base_path + f'/{f}')
                    st.markdown(pdf, unsafe_allow_html=True)
            session_end=st.button('Done close application')
            if session_end:
                if end==1:
                    param='end read'
                    fbwrite(year,semester,lab,group,member,param=datetime.now())
                else:
                    param='finish lab'
                    for m in members:
                        fbwrite(year,semester,lab,group,m,param=datetime.now())

        if 'st_pass' in st.session_state:
            st.write('st_pass',st.session_state.st_pass)
        if 'user_pass' in st.session_state:
            st.write('user_pass',st.session_state.user_pass)
        if location=='Lab':
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