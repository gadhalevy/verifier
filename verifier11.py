from datetime import datetime
import pytz
import streamlit as st,string,secrets
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import base64
import smtplib, ssl,os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
from uuid import uuid4
from streamlit_TTS import auto_play, text_to_speech, text_to_audio
import decoder3


def send_email(subject, body, receiver,files=None):
    '''
    Send email via khanuka1912 password or help files,
    :param subject:
    :param body:
    :param receiver:
    :param files:
    :return:
    '''
    with open('passtxt') as f:
        password = f.read()
    # password=st.secrets.sisma
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
    '''
    Make password for user.
    :return: Password.
    '''
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
    '''
    Send password for user via email.
    :param receiver:
    :return:
    '''
    subject='Password for ITL'
    pswrd=make_pass()
    body=f'Please enter this password: {pswrd}'
    # Unmark line below in production
    send_email(subject,body,receiver)
    return pswrd


@st.cache_resource()
def init():
    '''
    Init firebase through cloud.
    Using secrets.
    :return:
    '''
    try:
        firebase_admin.delete_app(firebase_admin.get_app())
    except ValueError:
        pass
    cred = credentials.Certificate(dict(st.secrets['fb']))
    # cred = credentials.Certificate('fb_key.json')
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://Lab9-c9743.firebaseio.com/',
                                             'storageBucket' :'lab9-c9743.appspot.com'})

@st.cache_data()
def make_student_list(path):
    '''
    Make df of students.
    :param path:
    :return: Df student_names, group_num, email.
    '''
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
    stam = pd.DataFrame(df['Groups'].tolist(), columns=['Group', 'group'])
    # return  stam['num']
    df = df.reset_index()
    final = df.join(stam)
    groups = final[['Group members', 'group','Email address']]
    st.dataframe(groups)
    return groups

def find_members(group):
    '''
    Find members of group.
    :param group:
    :return: Records of selected group.
    '''
    # groups=make_student_list('Overview.csv')
    groups=pd.read_csv('groups.csv',index_col=False)
    return groups[groups['group']==group]

def fbwrite(*args,**kwargs):
    '''
    Write logs to firebase realtime db.
    :param args:
    :param kwargs:
    :return:
    '''
    # print(f,created_os,start,created,processed,station,group,lab)
    todo=args[0]
    mystr=''
    for r in (args[1:]):
        mystr+=str(r)+'/'
    ref=db.reference(mystr[:-1])
    attr=getattr(ref,todo)
    for k,v in kwargs.items():
        # st.write({f'{k[:-4]}': f'{v}'})
        attr({f'{k}':f'{v}'})

def load(what,f,year,semester,lab,group):
    '''
    Loads files to firebase storage.
    :param what: Code or movie string.
    :param f: File.
    :param year:
    :param semester:
    :param lab:
    :param group:
    :return:
    '''
    ds=storage.bucket()
    bob=ds.blob(f.name)
    bob.upload_from_file(f)
    ds.rename_blob(bob,'{}/{}/{}/{}/{}_{}'.format(what,year,semester,lab,group,f.name))
@st.cache_data()
def displayPDF(lab):
    '''
    Display tadrich as HTML.
    :param lab:
    :return:
    '''
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
    '''
    Display entry sidebar screen.
    :return: Year,semester,lab,group,location,dic_4_help
    '''
    if 'edflg' not in st.session_state:
        st.session_state.edflg=False
    st.header("Verifier")
    st.subheader('Assist you with your submissions')
    year = st.sidebar.selectbox('Please choose year', ['Tashpad', 'Tashpah', 'Tashpav','Demo'],index=0,disabled=st.session_state.edflg)
    labs = ('Robotica', 'PreVision','Vision', 'Robolego', 'Yetsur', 'Android','HMI', 'IOT', 'Auto car','Social networks')
    help_4_lab=(2,7,2,1,1,1,2,5,2,2)
    dic_4_help={labs[i]:help_4_lab[i] for i in range(len(labs))}
    semester = st.sidebar.selectbox("Please choose semester", ('A', 'B'),index=1,disabled=st.session_state.edflg)
    lab = st.sidebar.selectbox('Please select maabada', labs,disabled=st.session_state.edflg)
    options = range(0, 24)
    group = st.sidebar.select_slider('Please choose group number', options,disabled=st.session_state.edflg)
    location = st.sidebar.radio('Please choose location', ['None', 'Home', 'Lab'],key='location',disabled=st.session_state.edflg)
    return year,semester,lab,group,location,dic_4_help

def form_home(members,df_group,ref):
    '''
    Display form home, todo unite 2 forms.
    :param members:
    :param df_group:
    :param ref:
    :return:
    '''
    year, semester, lab, group, location = ref
    with st.sidebar.form('Location'):
        member = st.radio('Who R U?', members)
        param = 'start_read'
        reciver = df_group[df_group['full_name'].str.strip() == member]['Email address'].values
        submitted = st.form_submit_button("Send password")
        pratiut=st.checkbox(':red[הנני מאשר את הצהרת הפרטיות וזכויות היוצרים  שעליהן חתמתי במודל]:rotating_light:')
        if submitted and pratiut:
            st_pass = send_pass(reciver[0].strip())
            if st_pass not in st.session_state:
                st.session_state['st_pass'] = st_pass
            st.write('Password was sent to your email')
            st.text_input('Write password', max_chars=8, type="password", key="user_pass")
        verify_btn = st.form_submit_button("Verify password")
        if verify_btn:
            if st.session_state.user_pass == st.session_state.st_pass:
                fbwrite('push',year, semester, lab, group, member, **{param: datetime.now(pytz.timezone('Asia/Jerusalem')).strftime('%d-%m-%y %H:%M')})
                st.write('Your password verified please press start session')
                st.session_state.state='verified'
            else:
                st.error('Wrong password', icon="🚨")
            if 'member' not in st.session_state:
                st.session_state['member'] = member
            else:
                st.session_state['member'] = member
def display_form(members,df_group,ref):
    '''
    Display form lab.
    :param members:
    :param df_group:
    :param ref:
    :return:
    '''
    year, semester, lab, group, location=ref
    with st.sidebar.form('Location'):
        member=members.iloc[st.session_state.counter]
        st.markdown("**:red[%s]**" %member)
        param='start_lab'
        reciver = df_group[df_group['full_name'].str.strip() == member]['Email address'].values
        submitted = st.form_submit_button("Send password")
        pratiut = st.checkbox(
            ':red[הנני מאשר את הצהרת הפרטיות וזכויות היוצרים  שעליהן חתמתי במודל]:rotating_light:')
        if submitted and pratiut:
            st_pass = send_pass(reciver[0].strip())
            if st_pass not in st.session_state:
                st.session_state['st_pass'] = st_pass
            st.write('Password was sent to your email')
            st.text_input('Write password', max_chars=8, type="password", key="user_pass")
        verify_btn = st.form_submit_button("Verify password")
        if verify_btn:
            if st.session_state.user_pass == st.session_state.st_pass:
                st.session_state.counter += 1
                fbwrite('push',year, semester, lab, group, member, **{param: datetime.now(pytz.timezone('Asia/Jerusalem')).strftime('%d-%m-%y %H:%M')})
                st.write('Your password verified please press start session')
                st.form_submit_button('Submit')
            else:
                st.error('Wrong password', icon="🚨")
        missing = st.form_submit_button('Missing')
        if missing:
            # st.write(member[:-1])
            fbwrite('set',year, semester, lab, group, member, missing=datetime.now().strftime("%d/%m/%y"))
            if 'missing' not in st.session_state:
                st.session_state['missing'] = [member]
            else:
                st.session_state['missing'].append(member)
            st.session_state.counter += 1
            st.form_submit_button('Continue')
        if st.session_state.counter>=len(members):
            st.session_state.state='verified'


def start_session(members,location):
    '''
    Change state and display tadrich on screen.
    :param members:
    :param lab:
    :param location:
    :return:
    '''
    if (location=='Lab' and st.session_state.counter >= len(members) ) or (location=='Home' and st.session_state.state=='verified'):
        session_start = st.button("Start session")
        if session_start:
            st.session_state.state = 'pdf'
def end_session(ref,members):
    '''
    Write logs of end_session to fb_realtime db.
    :param ref:
    :param members:
    :return:
    '''
    year, semester, lab, group, location = ref
    if location == 'Home':
        param = 'end read'
        fbwrite('push',year, semester, lab, group, st.session_state.member, **{param: datetime.now(pytz.timezone('Asia/Jerusalem')).strftime('%d-%m-%y %H:%M')})
    else:
        param = 'finish lab'
        for m in members:
            try:
                if m not in st.session_state.missing:
                    fbwrite('push',year, semester, lab, group, m, **{param: datetime.now(pytz.timezone('Asia/Jerusalem')).strftime('%d-%m-%y %H:%M')})
            except AttributeError:
                pass

def upload(kind,obj,ref):
    '''
    Upload movies or files to fb storage, use voice and st.error.
    :param kind:
    :param obj:
    :param ref:
    :return:
    '''
    if kind=='movie':
        siomet=('mp4','mpeg4')
        err_code='Must be mp4'
    elif kind=='code':
        siomet=('txt','.py','.kv','txt','logo','csv')
        err_code='Must be one of py,kv,txt,nlogo or csv files and file name should be exercise number'
    # st.write(obj)
    for c in obj:
        pre,post=c.name.split('.')
        if c.name.lower()[-3:] in siomet and pre.isdigit():
            load(kind, c, *ref[:-1])
            fname=c.name.replace('.','-')
            new_ref = ('set',)+ref[:-1] + (kind,fname)
            fbwrite(*new_ref, **{pre: datetime.now(pytz.timezone('Asia/Jerusalem')).strftime('%d-%m-%y %H:%M')})
        else:
            audio=text_to_audio("Remove the uploaded file, rename your files as a plain number eg 01.mp4 or 01.py, and load them again",language='en')
            auto_play(audio)
            st.error(f'{err_code}', icon="🚨")
def download_blob(what,maabada,counter):
    '''
    Download from fb storage assuming file name groupNum_exNum eg. 11_2.mp4
    :param what:
    :param maabada:
    :param counter:
    :return:
    '''
    counter+=1
    source_blob_name=f'{what}/{maabada}/{maabada}{counter}'
    # destination_file_name=os.path.join(year,semester,maabada)
    destination_file_name =f'tmp/{maabada}{counter}'
    bucket = firebase_admin.storage.bucket('lab9-c9743.appspot.com')
    blob = bucket.blob(source_blob_name)
    new_token = uuid4()
    metadata = {"firebaseStorageDownloadTokens": new_token}
    blob.metadata = metadata
    blob.download_to_filename(destination_file_name)
    return destination_file_name

def download_fb_files(year,semester,maabada,file):
    '''
    Download blob from fb bucket.
    :param year:
    :param semester:
    :param maabada:
    :param file:
    :return:
    '''
    source_blob_name=f'code/{year}/{semester}/{maabada}/{file}'
    # destination_file_name=os.path.join(year,semester,maabada)
    destination_file_name =f'tmp/{file}'
    bucket = firebase_admin.storage.bucket('lab9-c9743.appspot.com')
    blob = bucket.blob(source_blob_name)
    new_token = uuid4()
    metadata = {"firebaseStorageDownloadTokens": new_token}
    blob.metadata = metadata
    blob.download_to_filename(destination_file_name)
    return destination_file_name

def send_help(members,emails,ref,dic):
    '''
    Send help files to users.
    :param members:
    :param emails:
    :param ref:
    :param dic:
    :return:
    '''
    year,semester,lab,group,location=ref
    files=[]
    for i in range (dic[lab]):
        dir=download_blob('Help',lab,i)
        files.append(dir)
    for f in files:
        subject = f'Help file {f} for {lab}'
        body = f'Attached your file {f}'
        if st.button(f):
            for m,e in zip(members,emails):
                file=f[4:]
                param=f'help file {file} was sent'
                send_email(subject, body, e, [f])
                fbwrite('set',year,semester,lab,group,m,file,**{param: datetime.now(pytz.timezone('Asia/Jerusalem')).strftime('%d-%m-%y %H:%M')})

def download_files(year,semester,maabada,group):
    '''
    Allow users to download their submissions from firebase to their PC.
    :param year:
    :param semester:
    :param maabada:
    :param group:
    :return:
    '''
    _,files=decoder3.get_download_lst(year,semester,maabada)
    kvatsim=[]
    kvutsa='25'
    for f in files:
        try:
            kvutsa,_=f.split('_')
        except ValueError:
            pass
        if str(kvutsa)==str(group):
            kovets=f.replace('-','.')
            dir=download_fb_files(year,semester,maabada,kovets)
            st.write(dir)
            kvatsim.append(dir)
    st.write(kvatsim)
    for k in kvatsim:
        with open(k) as data:
            txt = data.read()
        st.download_button(label=f'Download {k}?', data=txt, file_name=k, mime='text/py')



def main():
    # st.session_state.update(st.session_state)
    # st.write(st.session_state.keys())
    if 'state' not in st.session_state:
        st.session_state['state']='begin'
    year, semester, lab, group, location, dic4Help= base()
    ref = year, semester, lab, group, location
    df_group = find_members(group)
    members = df_group['full_name']
    if st.session_state.state=='begin':
        init()
        auth=st.sidebar.button('Authenticate')
        if auth:
            st.session_state.edflg=True
            st.session_state.state='auth'
    # st.write(st.session_state.state)
    if st.session_state.state=='auth':
        if 'counter' not in st.session_state:
            st.session_state['counter']=0
        if location=='Home':
            form_home(members,df_group,ref)
        elif location=='Lab':
            display_form(members,df_group,ref)
    if st.session_state.state=='verified':
        pdf=st.button('Start session')
        if pdf:
            st.session_state.state='pdf'
        if st.sidebar.checkbox('Download your codes?'):
            download_files(year,semester,lab,group)
    if st.session_state.state=='pdf':
        pdf=displayPDF(lab)
        st.markdown(pdf, unsafe_allow_html=True)
        ezra=st.checkbox('Do you need help coding?')
        if ezra:
            emails=df_group['Email address'].values
            send_help(members,emails,ref,dic4Help)
        if location=='Lab':
            # st.write(st.session_state.counter)
            # if st.session_state.counter>=len(members):
            movie=st.file_uploader("Please select your movie",accept_multiple_files=True,key='movie')
            if movie:
                upload('movie',movie,ref)
            code=st.file_uploader("Please select your code submission files",accept_multiple_files=True,key='code')
            if code:
                upload('code',code,ref)
        st.markdown("## :red[When you done please press End session otherwise your session won't be registered in our system]:rotating_light:")
        session_end = st.button('End session')
        if session_end:
            end_session(ref, members)
    #         st.session_state='end'
    # if st.session_state=='end':
            st.success("We hope you liked the lab, if you haven't finish please continue some other time.",icon="✅")
    #     st.session_state.state='begin'


if __name__=='__main__':
    main()
