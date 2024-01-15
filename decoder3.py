import os
import firebase_admin
import streamlit as st
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import pytesseract as ocrstreamlit
import pandas as pd
import platform
from uuid import uuid4
from moviepy.editor import *

def init():
    try:
        firebase_admin.delete_app(firebase_admin.get_app())
    except ValueError:
        pass
    tmp = platform.platform()
    # print(tmp)
    if 'Windows' in tmp:
        cred = credentials.Certificate("H:/Gibui260318/pythonStuff/verifier/fb_key.json")
        # ocr.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    else:
        cred = credentials.Certificate(dict(st.secrets['fb']))
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://Lab9-c9743.firebaseio.com/',
                                             'storageBucket' :'lab9-c9743.appspot.com'})
def make_student_list(path,labs):
    df = pd.read_csv(path, header=0)
    skiprows = df.index[df['Groups'] == u'רישום לשלשות מעבדה - 01'].values[0]
    tmp = df.index[df['Grouping name'] == 'Not in a grouping'].values[0]
    df = df.iloc[skiprows:tmp]
    df = df[[df.columns[1], df.columns[2]]]
    df['Groups'] = df['Groups'].str.split('-')
    stam = pd.DataFrame(df['Groups'].tolist(), columns=['Group', 'num'])
    df = df.reset_index()
    final = df.join(stam)
    groups = final[['Group members', 'num']]
    num=len(groups)
    remarks = [l + '_rem' for l in labs[1:]]
    rem_data = {r: ['Lo nivdak'] * num for r in remarks}
    data={l:[100]*num for l in labs[1:]}
    data.update(rem_data)
    temp=list(zip(labs[1:],remarks))
    new_cols=[item for sublist in temp for item in sublist]
    grades=pd.DataFrame(columns=new_cols,data=data)
    concated=pd.concat([groups,grades],axis=1)
    concated.to_csv('grades.csv')
    st.write('grades.csv was created')
    return groups,grades

def from_db(year,semester,maabada):
    init()
    year=str(year)
    ref=db.reference('{}/{}/{}'.format(year,semester,maabada))
    df=pd.json_normalize(ref.get())
    # print(df.to_string())
    group=[col[0] for col in df.columns.str.split('.')][::7]
    pics=[col[2] for col in df.columns.str.split('.')][::7]
    cols=[col[3] for col in df.columns.str.split('.')][:7]
    tmp=df.to_numpy()
    tmp=tmp.reshape(-1,7)
    df=pd.DataFrame(tmp)
    df.columns=cols
    df['targil']=pics
    df['group']=group
    df=df.astype('string')
    return df

def download_blob(sug,year,semester,maabada,file):
    """Downloads a blob from the bucket."""
    source_blob_name=f'{sug}/{year}/{semester}/{maabada}/{file}'
    # destination_file_name=os.path.join(year,semester,maabada)
    destination_file_name =f'{sug}/{maabada}'
    bucket = firebase_admin.storage.bucket('lab9-c9743.appspot.com')
    blob = bucket.blob(source_blob_name)
    new_token = uuid4()
    metadata = {"firebaseStorageDownloadTokens": new_token}
    blob.metadata = metadata
    blob.download_to_filename(destination_file_name+f'/{file}')
    return destination_file_name+f'/{file}'

def make_movie(path):
    movie=os.listdir(path)[st.session_state['counter']]
    if movie=='0_0':
        st.session_state['counter']+=1
        movie=os.listdir(path)[st.session_state['counter']]
        # st.write(st.session_state['counter'],st.session_state['grades'])
    if movie.lower().endswith('mp4') or movie.lower().endswith('mov') or movie.lower().endswith('avi'):
        video_file = open(os.path.join(path,movie), 'rb')
        video_bytes = video_file.read()
        return video_bytes,movie

def comp_grades(lab):
    avg = sum(st.session_state['grades']) / len(st.session_state['grades'])
    groups = pd.read_csv('grades.csv')
    # st.dataframe(groups)
    groups = groups.astype({'num': 'int8'})
    # groups.loc[(groups.num == 1), 'IOT'] = 31
    groups.loc[(groups.num == int(st.session_state['team'])), lab] = avg
    groups.loc[(groups.num == int(st.session_state['team'])), lab + '_rem'] = ' '.join(st.session_state.remarks)
    # st.dataframe(groups)
    groups.to_csv('grades.csv', index=False)
    return groups

def grade_movie(team,lab):
    global Path
    # st.write(team,int(team))
    if 'team' not in st.session_state:
        st.session_state['team']=team
    # st.write('check=',int(st.session_state.counter),len(os.listdir(Path))-1)
    if team!=st.session_state['team']:
        comp_grades(lab)
        st.session_state.team=team
        st.session_state.grades=[]
        st.session_state.remarks=[]
    st.session_state.grades.append(int(st.session_state.mark))
    st.session_state.remarks.append(st.session_state.heara)
    st.session_state.counter += 1
    # st.write(st.session_state.mark,st.session_state.heara)

def not_make_maabada(df,maabada):
    txt='### All groups make this {}'.format(maabada)
    groups = pd.read_csv('grades.csv')
    set_fb_groups = set(df['group'].astype('int8'))
    set_groups = set(s for s in groups['num'])
    dif = set_groups - set_fb_groups
    if len(dif) > 0:
        txt = '### Groups {} did not make maabada {} yet'.format(' '.join(str(dif)), maabada)
    return txt

def not_completed_lab(numEx,labs,maabada,df):
    txt='### All groups completed all missions in {}'.format(maabada)
    tarMaabada = numEx[labs.index(maabada) - 1]
    tmp = df['group'].value_counts()
    tmp = tmp[tmp < tarMaabada]
    lst = [str(i) for i in tmp.index]
    if len(lst) > 0:
        txt = '### Groups {} did not complete all missions'.format(' '.join(lst))
    return txt

def get_download_lst(year,semester,maabada):
    tmp = pd.read_csv('grades.csv')
    groups = set(tmp['num'])
    m_lst = [];
    f_lst = []
    lst = m_lst
    data = 'movie'
    for _ in range(2):
        for g in groups:
            ref = db.reference(f'{year}/{semester}/{maabada}/{g}/{data}')
            tmp = ref.get()
            if tmp is not None:
                if data=='movie':
                    siomet='mp4'
                for k in tmp.keys():
                    lst.append(f'{g}_{k}')
        lst = f_lst
        data = 'code'
    return m_lst,f_lst

def main():
    '''
    session_state:counter,grades,mark,heara,team,remarks
    :return:
    '''
    global Path
    st.header("Verifier decoder")
    st.subheader('Tries to find incorrect submissions')
    year = st.sidebar.selectbox('Please choose year', ['Tashpag', 'Tashpad', 'Tashpah','Demo'])
    labs = ('Choose', 'Robotica', 'PreVision','Vision', 'Robolego', 'Yetsur','HMI', 'Android', 'IOT', 'Auto car 1', 'Auto car 2')
    semester = st.sidebar.selectbox("Please choose semester", ('A', 'B'))
    maabada = st.sidebar.selectbox('Please select maabada', labs)
    init()
    if not os.path.isfile('grades.csv'):
        make_student_list('Overview.csv',labs)
    else:
        st.write(os.path.abspath('grades.csv'))
        movies,codes=get_download_lst(year,semester,maabada)
        movies

    # ToDo config page make student list
    if maabada != 'Choose':
        if st.sidebar.button('Download codes from Firebase?'):
            for c in codes:
                f=c.replace('-','.')
                dir=download_blob('code',year, semester, maabada,f)
        if st.sidebar.button('Download movies from Firebase?'):
            for m in movies:
                f = m.replace('-', '.')
                dir=download_blob('movie',year, semester, maabada,f)
        if 'grades' not in st.session_state:
            st.session_state['grades']=[]
        if 'remarks' not in st.session_state:
            st.session_state['remarks']=[]
        if 'counter' not in st.session_state:
            st.session_state['counter']=0
        Path=f'movie/{maabada}/'
        if st.sidebar.checkbox('Grade Movies?'):
            os.listdir(Path)
            if st.session_state.counter < len(os.listdir(Path)) - 1:
                holder = st.empty()
                video,v_name=make_movie(Path)
                col1,col2=st.columns([8,2])
                with col1:
                    st.video(video)
                with col2:
                    with st.form("Grade this movie", clear_on_submit=True):
                        st.text_input('Movie grade',key='mark')
                        kvutsa,seret=v_name.split('_')
                        # st.write(kvutsa,int(kvutsa))
                        st.text_area('Remark','Checked',key='heara')
                        st.form_submit_button("Submit",on_click=grade_movie,args=(kvutsa,maabada))
                holder.text_input('Remarks', 'movie {} of group {} is being checked'.format(seret, kvutsa))
            elif st.session_state.counter == (len(os.listdir(Path))-1) :
                comp_grades(maabada)
            else:
                st.warning('No more movies ❗ 🛑')
        if st.sidebar.button('Show grades?'):
            groups=pd.read_csv('grades.csv',index_col=False)
            st.dataframe(groups)
        # if st.sidebar.button('Summarize Lab?'):
        #     txt=not_make_maabada(df,maabada)
        #     st.markdown(txt)
        #     numEx = [2, 2, 3, 3, 2, 3, 1, 0, 0]
        #     txt=not_completed_lab(numEx,labs,maabada,df)
        #     st.markdown(txt)
        if st.sidebar.button('Download grades.csv?'):
            df = pd.read_csv('grades.csv',index_col=False)
            downloaded=df.to_csv('grades.csv',encoding='utf-8',sep=',')
            st.sidebar.download_button(label='Download Grades',data='grades.csv', file_name='grades.csv', mime='csv')
main()
