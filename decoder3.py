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
from collections import  Counter
from difflib import *
import re
import math

@st.cache_resource()
def init():
    try:
        firebase_admin.delete_app(firebase_admin.get_app())
    except ValueError:
        pass
    cred = credentials.Certificate(dict(st.secrets['fb']))
    # cred = credentials.Certificate('fb_key.json')
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
    groups = pd.read_csv('grades.csv')
    # st.dataframe(groups)
    groups = groups.astype({'num': 'int8'})
    # groups.loc[(groups.num == 1), 'IOT'] = 31
    avg = sum(st.session_state['grades']) / len(st.session_state['grades'])
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

def not_make_maabada(movies,maabada):
    nobody=False
    txt=f'### :green[All groups make this {maabada}]'
    groups = pd.read_csv('grades.csv',index_col=False)
    fb_groups=(m.split('_')[0] for m in movies)
    set_fb_groups=set(map(int,fb_groups))
    set_groups = set(s for s in groups['num'])
    dif = set_groups - set_fb_groups
    if len(dif) > 0:
        txt = f'### :red[Groups {" ".join(str(dif))} did not make maabada {maabada} yet]'
    if len(dif)==len(set_groups):
        txt= f'### :red[Nobody make maabada {maabada} yet]'
        nobody=True
    return txt,nobody

def not_completed_lab(numEx,labs,maabada,movies,flag):
    txt=f'### :green[All groups completed all missions in {maabada}]'
    tarMaabada = numEx[labs.index(maabada) - 1]
    fb_groups = (m.split('_')[0] for m in movies)
    fb_groups = set(map(int, fb_groups))
    tmp=Counter(fb_groups)
    mystr=''
    for k,v in tmp.items():
        if v<tarMaabada:
            mystr+=str(k)+' '
    if len(mystr)>0 and not flag:
        txt = f'### :red[Groups {mystr} did not complete all missions]'
    if flag:
        txt= f'### :red[Nobody make maabada {maabada} yet]'
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

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def check_siomet(f):
    siomet = ('txt', 'py', 'kv', 'txt', 'logo', 'csv', 'mp4','mpeg4')
    try:
        pre,post=f.split('.')
        if post.lower() in siomet:
            return True
    except:
        return False

def compare_code(maabada):
    dic = {}
    for f in os.listdir(f'code/{maabada}'):
        if f.endswith('py'):
            with open(f'code/{maabada}/{f}') as data:
                dic[f] = data.read()
    ratios = {};
    suspects = {}
    for k in list(dic.keys())[1:]:
        s = SequenceMatcher(None, dic[list(dic.keys())[0]], dic[k])
        ratios[k] = round(s.ratio(), 2)
    lst = [k for k, v in ratios.items() if v == 1]
    if len(lst) > 0:
        lst.append(list(dic.keys())[0])
    suspects[1] = lst
    counts = Counter(ratios.values())
    # Create a new dictionary with only the keys whose value has a count greater than 1
    result = {k: v for k, v in ratios.items() if counts[v] > 1}
    set_ratios = set(list(result.values()))
    for i, s in enumerate(set_ratios, 2):
        lst = [k for k, v in result.items() if v == s]
        suspects[i] = lst
    for k, v in suspects.items():
        st.write(f'**:red[Suspected files {" ".join(v)}]**')
        for f in v:
            st.download_button(label=f'Download {f}?', data=dic[f], file_name=f, mime='text/py')
    return suspects

def show_suspects(suspects):
    for v in suspects.values():
        str = f'### :red[Groups '
        for f in v:
            group, tmp = f.split('_')
            ex, _ = tmp.split('.')
            str += f'{group} '
        str += f'Suspected of coping exercise {ex}]'
        st.markdown(str)

def build_json_df(what,year,semester,maabada):
    ref=db.reference(f'{year}/{semester}/{maabada}')
    tmp=pd.json_normalize(ref.get())
    cols=[c for c in tmp.columns if what in c]
    df=tmp[cols]
    return df

def show_missings(what,year,semester,maabada):
    df=build_json_df()
    st.write(df)
    dic={}
    for k,v in df.items():
        w=v.dropna()
        dic[k]=w
    st.markdown(f'## :red[{what}]:')
    my_str=''
    for k,v in dic.items():
        match=re.search(r'\d+/\d+/\d+',str(v))
        pre,post=str(k).split('.')
        my_str+=f' {pre} {match.group()},'
    st.markdown(f'### :red[{my_str}]')


def main():
    '''
    session_state:counter,grades,mark,heara,team,remarks
    :return:
    '''
    global Path
    st.header("Verifier decoder")
    st.subheader('Tries to find incorrect submissions')
    year = st.sidebar.selectbox('Please choose year', ['Tashpag', 'Tashpad', 'Tashpah','Demo'])
    labs = ('Choose', 'Robotica', 'PreVision','Vision', 'Robolego', 'Yetsur','HMI', 'Android', 'IOT', 'Auto car 1', 'Auto car 2','Social networks')
    semester = st.sidebar.selectbox("Please choose semester", ('A', 'B'))
    maabada = st.sidebar.selectbox('Please select maabada', labs)
    init()
    if not os.path.isfile('grades.csv'):
        make_student_list('Overview.csv',labs)
    else:
        movies,codes=get_download_lst(year,semester,maabada)

    # ToDo config page make student list
    if maabada != 'Choose':
        if st.sidebar.button('Download codes from Firebase?'):
            for c in codes:
                f=c.replace('-','.')
                if check_siomet(f):
                    download_blob('code',year, semester, maabada,f)
        if st.sidebar.button('Download movies from Firebase?'):
            for m in movies:
                f = m.replace('-', '.')
                if check_siomet(f):
                    download_blob('movie',year, semester, maabada,f)
        if 'grades' not in st.session_state:
            st.session_state['grades']=[]
        if 'remarks' not in st.session_state:
            st.session_state['remarks']=[]
        if 'counter' not in st.session_state:
            st.session_state['counter']=0
        Path=f'movie/{maabada}/'
        if st.sidebar.checkbox('Grade Movies?'):
            if st.session_state.counter < len(os.listdir(Path)) -1:
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
            elif st.session_state.counter == (len(os.listdir(Path))-1) and len(os.listdir(Path))>1:
                comp_grades(maabada)
            else:
                st.warning('No more movies ❗ 🛑')
        if st.sidebar.button('Show grades?'):
            groups=pd.read_csv('grades.csv',index_col=False)
            st.dataframe(groups)
        if st.sidebar.checkbox('Compare codes?'):
            suspects=compare_code(maabada)
        if st.sidebar.button('Summarize Lab?'):
            try:
                if len(suspects)>0:
                    show_suspects(suspects)
            except:
                pass
            show_missings('missing',year,semester,maabada)
            # from_fb('help file',year,semester,maabada)
            txt,flag=not_make_maabada(movies,maabada)
            st.markdown(txt)
            numEx = [2, 7,  3, 3, 3, 2, 3, 1, 0, 0]
            txt=not_completed_lab(numEx,labs,maabada,movies,flag)
            st.markdown(txt)
        if st.sidebar.button('Download grades.csv?'):
            df = pd.read_csv('grades.csv',index_col=False)
            csv = convert_df(df)
            st.sidebar.download_button(label="Download data as CSV",data=csv, file_name='grades.csv',mime='text/csv')
main()
