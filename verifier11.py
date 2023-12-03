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
    # with open('passtxt') as f:
    #     password = f.read()
    password=st.secrets.sisma
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
    # Unmark line below in production
    send_email(subject,body,receiver)
    return pswrd


@st.cache_resource()
def init():
    # try:
    #     firebase_admin.delete_app(firebase_admin.get_app())
    # except ValueError:
    #     pass
    cred = credentials.Certificate(dict(st.secrets['fb']))
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://Lab9-c9743.firebaseio.com/',
                                             'storageBucket' :'lab9-c9743.appspot.com'})
@st.cache_data()
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
    st.write(args)
    for k,v in kwards.items():
        # st.write({f'{k[:-4]}': f'{v}'})
        ref.push({f'{k[:-4]}':f'{v}'})


def load(what,f,year,semester,lab,group):
    ds=storage.bucket()
    bob=ds.blob(f.name)
    bob.upload_from_file(f)
    ds.rename_blob(bob,'{}/{}/{}/{}/{}_{}'.format(what,year,semester,lab,group,f.name))
@st.cache_data()
def displayPDF(lab):
    base_path = os.path.abspath(os.curdir)
    # Opening file from file path
    base_path = base_path + f'/{lab}'
    # st.write(os.path.dirname(base_path))
    for f in (os.listdir(os.path.dirname(base_path + '/%s' % lab))):
        # st.write(f)
        if f.endswith('pdf'):
            # st.write(f)
            # st.write(base_path+f'/{f}')
            with open(base_path+f'/{f}', "rb") as file:
                base64_pdf = base64.b64encode(file.read()).decode('utf-8')
            # base64_pdf = base64.b64encode(file).decode('utf-8')
            # Embedding PDF in HTML
            pdf = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
            return pdf

    # Displaying File
def base():
    st.header("Verifier")
    st.subheader('Assist you with your submissions')
    year = st.sidebar.selectbox('Please choose year', ['Tashpad', 'Tashpah', 'Tashpav'])
    labs = ('Choose', 'Robotica', 'Vision', 'Robolego', 'Yetsur', 'Android', 'IOT', 'Auto car 1', 'Auto car 2')
    semester = st.sidebar.selectbox("Please choose semester", ('A', 'B'))
    lab = st.sidebar.selectbox('Please select maabada', labs)
    options = range(1, 21)
    group = st.sidebar.select_slider('Please choose group number', options)
    location = st.sidebar.radio('Please choose location', ['None', 'Home', 'Lab'],key='location')
    return year,semester,lab,group,location

def display_form(members,df_group,i,end,ref):
    year, semester, lab, group, location=ref
    with st.sidebar.form(f'Location{i}'):
        if end==1:
            member = st.radio('Who R U?', members)
        else:
            member=members[i]
            st.markdown(f'###{member}')
        reciver = df_group[df_group['Group members'].str.strip() == member]['Email address'].values
        submitted = st.form_submit_button("Send password")
        if submitted:
            st_pass = send_pass(reciver[0].strip())
            if st_pass not in st.session_state:
                st.session_state['st_pass'] = st_pass
            st.write('Password was sent to your email')
            st.text_input('Write password', max_chars=8, type="password", key="user_pass")
        verify_btn = st.form_submit_button("Verify password")
        if verify_btn:
            if st.session_state.user_pass == st.session_state.st_pass:
                st.session_state.counter += 1
                if end == 1:
                    param = 'start read'
                else:
                    param = 'start lab'
                fbwrite(year, semester, lab, group, member[:-1], **{param: datetime.now()})
                st.write('Your password verified please press start session')
            else:
                st.error('Wrong password', icon="🚨")
        if location == 'Lab':
            missing = st.form_submit_button('Missing')
            if missing:
                st.write(member[:-1])
                fbwrite(year, semester, lab, group, member[:-1], missing=datetime.now().strftime("%d/%m/%y"))
                if 'missing' not in st.session_state:
                    st.session_state['missing'] = member
                st.session_state.counter += 1
        else:
            if 'member' not in st.session_state:
                st.session_state['member']=member
            else:
                st.session_state['member'] = member


def end_session(ref,members):
    year, semester, lab, group, location = ref
    if location == 'Home':
        param = 'end read'
        fbwrite(year, semester, lab, group, st.session_state.member, **{param: datetime.now()})
    else:
        param = 'finish lab'
        for m in members:
            if m not in st.session_state.missing:
                fbwrite(year, semester, lab, group, m[:-1], **{param: datetime.now()})

def upload(kind,obj,ref):
    if kind=='movie':
        siomet=('mp4',)
        err_code='Must be mp4'
    elif kind=='code':
        siomet=('txt','.py','.kv','txt','logo','csv')
        err_code='Must be one of py,kv,txt,nlogo or csv files'
    for c in obj:
        if c.name.lower()[-3:] in siomet:
            load(kind, c, *ref[:-1])
            new_ref = ref[:-1] + (kind,)
            fbwrite(*new_ref, **{c.name: datetime.now()})
        else:
            st.error(f'{err_code}', icon="🚨")

def main():
    if 'state' not in st.session_state:
        st.session_state.state='init'
    if st.session_state.state=='init':
        init()
        st.session_state.state='autho'
    elif st.session_state.state=='autho':
        year,semester,lab,group,location=base()
        ref=year,semester,lab,group,location
        if 'counter' not in st.session_state:
            st.session_state['counter']=0
        if location !='None':
            df_group=find_members(f'{group:02}')
            members=df_group['Group members']
            if location=='Home':
                end=1
                display_form(members,df_group,0,1,ref)
            else:
                end=len(members)
                for i in range(end):
                    display_form(members,df_group,i,end,ref)
            session_start=st.button("Start session")
            if session_start:
                if st.session_state.counter>=end and lab!='Choose':
                    pdf=displayPDF(lab)
                    st.markdown(pdf, unsafe_allow_html=True)
        if location=='Home':
            session_end=st.button('End session')
            if session_end:
                end_session(ref,members)
        elif location=='Lab':
            # st.write(st.session_state.counter)
            if st.session_state.counter>=len(members):
                movie=st.file_uploader("Please select your movie",accept_multiple_files=True,key='movie')
                if movie:
                    upload('movie',movie,ref)
                code=st.file_uploader("Please select your code submission files",accept_multiple_files=True,key='code')
                if code:
                    upload('code',code,ref)

main()