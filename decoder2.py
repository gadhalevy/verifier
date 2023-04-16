import firebase_admin
import streamlit as st
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import pytesseract as ocr
import pandas as pd
import platform
from google.oauth2 import service_account
from uuid import uuid4
from google.cloud import storage
import os,numpy as np
import datetime
import moviepy
from moviepy.editor import *
import cv2
import tempfile
from zipfile import ZipFile
@st.cache(allow_output_mutation=True)
def init():
    try:
        firebase_admin.delete_app(firebase_admin.get_app())
    except ValueError:
        pass
    tmp = platform.platform()
    # print(tmp)
    if 'Windows' in tmp:
        cred = credentials.Certificate("H:/Gibui260318/pythonStuff/verifier/apikey.json")
        ocr.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    else:
        cred = credentials.Certificate('apikey.json')
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://Lab9-c9743.firebaseio.com/',
                                             'storageBucket' :'lab9-c9743.appspot.com'})
    seen_lst=[]
    # st.session_state['counter']=0
    return seen_lst

@st.cache(allow_output_mutation=True)
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

# @st.cache(allow_output_mutation=True)
def from_db(year,semester,maabada):
    seen_lst=init()
    year=str(year)
    ref=db.reference('{}/{}/{}'.format(year,semester,maabada))
    df=pd.json_normalize(ref.get())
    # print(df.to_string())
    group=[col[0] for col in df.columns.str.split('.')][::7]
    pics=[col[2] for col in df.columns.str.split('.')][::7]
    cols=[col[3] for col in df.columns.str.split('.')][:7]
    # print(group,pics,cols)
    tmp=df.to_numpy()
#     print(tmp)
    tmp=tmp.reshape(-1,7)
    df=pd.DataFrame(tmp)
    df.columns=cols
    df['targil']=pics
    df['group']=group
    df=df.astype('string')
    return df,seen_lst

@st.cache(allow_output_mutation=True)
def make_pic(year,semester,maabada,f):
    if (f.lower().endswith('avi')) or (f.lower().endswith('mp4')) or (f.lower().endswith('mov')):
        path='{}/{}/{}'.format(year,semester,maabada)
        pathRead=os.path.join(path,f)
        clip = VideoFileClip(pathRead)
        pathWrite=pathRead[:-3]+'jpg'
        img = clip.save_frame(pathWrite,t=1)
        return img


@st.cache(allow_output_mutation=True)
def from_movie(img):
    img=cv2.imread(img)
    bw=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret,thresh1 = cv2.threshold(bw,0,255,cv2.THRESH_BINARY)
    xconfig = '--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'
    return ocr.image_to_string(thresh1, config=xconfig).strip()

def download_blob(year,semester,maabada,group,file):
    """Downloads a blob from the bucket."""
    source_blob_name='Movies/{}/{}/{}/{}_{}'.format(year, semester, maabada, group, file)
    # destination_file_name=os.path.join(year,semester,maabada)
    destination_file_name ='/{}/{}/{}'.format(year,semester,maabada)
    bucket = firebase_admin.storage.bucket('lab9-c9743.appspot.com')
    blob = bucket.blob(source_blob_name)
    new_token = uuid4()
    metadata = {"firebaseStorageDownloadTokens": new_token}
    blob.metadata = metadata
    blob.download_to_filename(destination_file_name+'/{}_{}'.format(group,file))
    return destination_file_name+'/{}_{}'.format(group,file)

# @st.cache(allow_output_mutation=True)
def make_movie(path,mismatch=[]):
    if len(mismatch)==0:
        mismatch=os.listdir(path)
    for f in mismatch:
        if f.lower().endswith('mp4') or f.lower().endswith('mov') or f.lower().endswith('avi'):
            video_file = open(os.path.join(path,f), 'rb')
            video_bytes = video_file.read()
            yield video_bytes

# @st.cache(allow_output_mutation=True)
def show_movies(rem,groups,group,maabada):
    groups = groups.astype({'num': 'int8'})
    groups.loc[(groups.num == group), maabada] = st.session_state['grade']
    groups.loc[(groups.num == group), maabada + '_rem'] = rem
    groups.to_csv('H:/Gibui260318/pythonStuff/verifier/grades.csv',index=False)
    st.session_state['counter']+=1

def main():
    st.header("Verifier decoder")
    st.subheader('Tries to find incorrect submissions')
    if not 'counter' in st.session_state:
        st.session_state['counter']=0
    year=st.sidebar.selectbox('Please choose year',['Tashpag','Tashpad','Tashpah'])
    labs=('Choose', 'Robotica', 'Vision', 'Robolego', 'Yetsur', 'Android', 'IOT','Auto car 1','Auto car 2')
    semester=st.sidebar.selectbox("Please choose semester",('A','B'))
    maabada = st.sidebar.selectbox('Please select maabada',labs)
    path = 'Overview.csv'
    if path:
        st.sidebar.warning('This button press is done once a year only!', icon="👇")
        if st.sidebar.button("Press to make new student list  ❗"):
            make_student_list(path,labs)
            st.write('New students list was created')
    if maabada != 'Choose':
        df,seen_lst = from_db(year,semester,maabada)
        if st.sidebar.checkbox('Show data from FireBase?'):
            st.write('Data from Firebase')
            st.dataframe(df)
    if st.sidebar.checkbox('Download movies from Firebase?'):
        for i,r in df.iterrows():
            group=r['group']
            file=r['file']
            dir=download_blob(year, semester, maabada, group, file)
    if st.sidebar.checkbox('Analyze?'):
        if path:
            groups=pd.read_csv('grades.csv')
            set_fb_groups=set(df['group'].astype('int8'))
            set_groups=set(s for s in groups['num'])
            dif=set_groups-set_fb_groups
            txt='### Groups {} did not make maabada {} yet'.format(' '.join(str(dif)),maabada)
            if len(dif)>0:
                st.markdown(txt)
        numEx=[2,2,3,3,2,3,1,0,0]
        tarMaabada=numEx[labs.index(maabada)-1]
        tmp=df['group'].value_counts()
        tmp=tmp[tmp<tarMaabada]
        lst=[str(i) for i in tmp.index]
        if len(lst)>0:import firebase_admin
import streamlit as st
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import pytesseract as ocr
import pandas as pd
import platform
from google.oauth2 import service_account
from uuid import uuid4
from google.cloud import storage
import os,numpy as np
import datetime
import moviepy
from moviepy.editor import *
import cv2
import tempfile
from zipfile import ZipFile
@st.cache(allow_output_mutation=True)
def init():
    try:
        firebase_admin.delete_app(firebase_admin.get_app())
    except ValueError:
        pass
    tmp = platform.platform()
    # print(tmp)
    if 'Windows' in tmp:
        cred = credentials.Certificate("H:/Gibui260318/pythonStuff/verifier/apikey.json")
        ocr.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    else:
        cred = credentials.Certificate('apikey.json')
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://Lab9-c9743.firebaseio.com/',
                                             'storageBucket' :'lab9-c9743.appspot.com'})
    seen_lst=[]
    # st.session_state['counter']=0
    return seen_lst

@st.cache(allow_output_mutation=True)
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

# @st.cache(allow_output_mutation=True)
def from_db(year,semester,maabada):
    seen_lst=init()
    year=str(year)
    ref=db.reference('{}/{}/{}'.format(year,semester,maabada))
    df=pd.json_normalize(ref.get())
    # print(df.to_string())
    group=[col[0] for col in df.columns.str.split('.')][::7]
    pics=[col[2] for col in df.columns.str.split('.')][::7]
    cols=[col[3] for col in df.columns.str.split('.')][:7]
    # print(group,pics,cols)
    tmp=df.to_numpy()
#     print(tmp)
    tmp=tmp.reshape(-1,7)
    df=pd.DataFrame(tmp)
    df.columns=cols
    df['targil']=pics
    df['group']=group
    df=df.astype('string')
    return df,seen_lst

@st.cache(allow_output_mutation=True)
def make_pic(year,semester,maabada,f):
    if (f.lower().endswith('avi')) or (f.lower().endswith('mp4')) or (f.lower().endswith('mov')):
        path='{}/{}/{}'.format(year,semester,maabada)
        pathRead=os.path.join(path,f)
        clip = VideoFileClip(pathRead)
        pathWrite=pathRead[:-3]+'jpg'
        img = clip.save_frame(pathWrite,t=1)
        return img


@st.cache(allow_output_mutation=True)
def from_movie(img):
    img=cv2.imread(img)
    bw=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret,thresh1 = cv2.threshold(bw,0,255,cv2.THRESH_BINARY)
    xconfig = '--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'
    return ocr.image_to_string(thresh1, config=xconfig).strip()

def download_blob(year,semester,maabada,group,file):
    """Downloads a blob from the bucket."""
    source_blob_name='Movies/{}/{}/{}/{}_{}'.format(year, semester, maabada, group, file)
    # destination_file_name=os.path.join(year,semester,maabada)
    destination_file_name ='/{}/{}/{}'.format(year,semester,maabada)
    bucket = firebase_admin.storage.bucket('lab9-c9743.appspot.com')
    blob = bucket.blob(source_blob_name)
    new_token = uuid4()
    metadata = {"firebaseStorageDownloadTokens": new_token}
    blob.metadata = metadata
    blob.download_to_filename(destination_file_name+'/{}_{}'.format(group,file))
    return destination_file_name+'/{}_{}'.format(group,file)

# @st.cache(allow_output_mutation=True)
def make_movie(path,mismatch=[]):
    if len(mismatch)==0:
        mismatch=os.listdir(path)
    for f in mismatch:
        if f.lower().endswith('mp4') or f.lower().endswith('mov') or f.lower().endswith('avi'):
            video_file = open(os.path.join(path,f), 'rb')
            video_bytes = video_file.read()
            yield video_bytes

# @st.cache(allow_output_mutation=True)
def show_movies(rem,groups,group,maabada):
    groups = groups.astype({'num': 'int8'})
    groups.loc[(groups.num == group), maabada] = st.session_state['grade']
    groups.loc[(groups.num == group), maabada + '_rem'] = rem
    groups.to_csv('H:/Gibui260318/pythonStuff/verifier/grades.csv',index=False)
    st.session_state['counter']+=1

def main():
    st.header("Verifier decoder")
    st.subheader('Tries to find incorrect submissions')
    if not 'counter' in st.session_state:
        st.session_state['counter']=0
    year=st.sidebar.selectbox('Please choose year',['Tashpag','Tashpad','Tashpah'])
    labs=('Choose', 'Robotica', 'Vision', 'Robolego', 'Yetsur', 'Android', 'IOT','Auto car 1','Auto car 2')
    semester=st.sidebar.selectbox("Please choose semester",('A','B'))
    maabada = st.sidebar.selectbox('Please select maabada',labs)
    path = 'Overview.csv'
    if path:
        st.sidebar.warning('This button press is done once a year only!', icon="👇")
        if st.sidebar.button("Press to make new student list  ❗"):
            make_student_list(path,labs)
            st.write('New students list was created')
    if maabada != 'Choose':
        df,seen_lst = from_db(year,semester,maabada)
        if st.sidebar.checkbox('Show data from FireBase?'):
            st.write('Data from Firebase')
            st.dataframe(df)
    if st.sidebar.checkbox('Download movies from Firebase?'):
        for i,r in df.iterrows():
            group=r['group']
            file=r['file']
            dir=download_blob(year, semester, maabada, group, file)
    if st.sidebar.checkbox('Analyze?'):
        if path:
            groups=pd.read_csv('grades.csv')
            set_fb_groups=set(df['group'].astype('int8'))
            set_groups=set(s for s in groups['num'])
            dif=set_groups-set_fb_groups
            txt='### Groups {} did not make maabada {} yet'.format(' '.join(str(dif)),maabada)
            if len(dif)>0:
                st.markdown(txt)
        numEx=[2,2,3,3,2,3,1,0,0]
        tarMaabada=numEx[labs.index(maabada)-1]
        tmp=df['group'].value_counts()
        tmp=tmp[tmp<tarMaabada]
        lst=[str(i) for i in tmp.index]
        if len(lst)>0:
            txt='### Groups {} did not complete all missions'.format(' '.join(lst))
            st.markdown(txt)
        tmp=df[['group','start','created']]
        tmp=set(tmp['group'][tmp['start']>tmp['created']].to_numpy())
        if len(tmp)>0:
            txt='#### Groups {} used movies that were created before signed kartis avoda!!'.format(','.join(tmp))
            st.markdown(txt)
        movies_dir='{}/{}/{}'.format(year,semester,maabada)
        for f in os.listdir(movies_dir):
            make_pic(year,semester,maabada,f)
        imgs = []
        caption = []
        for f in os.listdir(movies_dir):
            if f.endswith('jpg'):
                kvutsa=from_movie(os.path.join(movies_dir,f))
                # st.write('k=',kvutsa,'name=',f[:2])
                if kvutsa!=f[:2]:
                    st.write('group {} differ from picture analyse {}'.format(f[:2],kvutsa))
                    img=cv2.imread(os.path.join(movies_dir,f))
                    imgs.append(img)
                    caption.append(f)
        if len(imgs)>0:
            txt=f'### Mismatch pictures and groups'
            st.markdown(txt)
            st.image(imgs,caption=caption,width=60)
            if st.sidebar.checkbox('Show mismach movies?'):
                mismatch=[]
                for f in os.listdir(movies_dir):
                  if (f.lower().endswith('avi')) or (f.lower().endswith('mp4')) or (f.lower().endswith('mov')):
                    st.write(f)
                    if f[:-3]+'jpg' in caption:
                        mismatch.append(f)
                if len(mismatch)>0:
                    video=make_movie(movies_dir,mismatch).__next__()
                    counter=st.session_state['counter']
                    st.write('check',mismatch[counter],seen_lst)
                    if mismatch[counter] not in seen_lst:
                        if st.sidebar.button('Show group {} movie {}?'.format(mismatch[counter].split('_')[0],mismatch[counter].split('_')[1])):
                            col1,col2=st.columns([8,2])
                            seen_lst.append(mismatch[counter])
                            with col1:
                                st.video(video)
                            with col2:
                                rem=st.text_input(":red[Please add remark] 👇 ",value="nivdak")
                                st.text_input('Movie grade',on_change=show_movies,args=(rem,groups,group,maabada),key='grade')
        if st.sidebar.button('Show DF'):
            grades=pd.read_csv('grades.csv')
            st.dataframe(grades)

        if st.sidebar.checkbox('Show all movies?'):
            yielded,video_name=make_movie(movies_dir)
            for video in yielded:
                if st.button('Show this movie?',key=2):
                    st.video(video)
        options=st.sidebar.multiselect('Select movies to show',os.listdir(movies_dir))
        if len(options)>0:
            for video in make_movie(movies_dir,options):
                if st.button('Show movie?',key=3):
                    st.video(video)
        if maabada in ('Robotica','Vision'):
            tmp = df[['station', 'group']]
            tmp['station'] = tmp.station.astype('int')
            tmp=set(tmp['group'][tmp['station'] > 10].to_numpy())
            if len(tmp)>0:
                st.markdown('#### Groups {} submitted from wrong station in {}.'
                         .format(','.join(tmp),maabada))
        elif maabada in ('IOT','Auto car 1','Auto car 2'):
            tmp = df[['group', 'os']]
            tmp_set = set(tmp['group'][tmp.os=='Windows'])
            if len(tmp_set) > 0:
                st.write('groups {} submitted files on wrong OS in {}.'.format(','.join(tmp_set),maabada))

main()

            txt='### Groups {} did not complete all missions'.format(' '.join(lst))
            st.markdown(txt)
        tmp=df[['group','start','created']]
        tmp=set(tmp['group'][tmp['start']>tmp['created']].to_numpy())
        if len(tmp)>0:
            txt='#### Groups {} used movies that were created before signed kartis avoda!!'.format(','.join(tmp))
            st.markdown(txt)
        movies_dir='{}/{}/{}'.format(year,semester,maabada)
        for f in os.listdir(movies_dir):
            make_pic(year,semester,maabada,f)
        imgs = []
        caption = []
        for f in os.listdir(movies_dir):
            if f.endswith('jpg'):
                kvutsa=from_movie(os.path.join(movies_dir,f))
                # st.write('k=',kvutsa,'name=',f[:2])
                if kvutsa!=f[:2]:
                    st.write('group {} differ from picture analyse {}'.format(f[:2],kvutsa))
                    img=cv2.imread(os.path.join(movies_dir,f))
                    imgs.append(img)
                    caption.append(f)
        if len(imgs)>0:
            txt=f'### Mismatch pictures and groups'
            st.markdown(txt)
            st.image(imgs,caption=caption,width=60)
            if st.sidebar.checkbox('Show mismach movies?'):
                mismatch=[]
                for f in os.listdir(movies_dir):
                  if (f.lower().endswith('avi')) or (f.lower().endswith('mp4')) or (f.lower().endswith('mov')):
                    st.write(f)
                    if f[:-3]+'jpg' in caption:
                        mismatch.append(f)
                if len(mismatch)>0:
                    video=make_movie(movies_dir,mismatch).__next__()
                    counter=st.session_state['counter']
                    st.write('check',mismatch[counter],seen_lst)
                    if mismatch[counter] not in seen_lst:
                        if st.sidebar.button('Show group {} movie {}?'.format(mismatch[counter].split('_')[0],mismatch[counter].split('_')[1])):
                            col1,col2=st.columns([8,2])
                            seen_lst.append(mismatch[counter])
                            with col1:
                                st.video(video)
                            with col2:
                                rem=st.text_input(":red[Please add remark] 👇 ",value="nivdak")
                                st.text_input('Movie grade',on_change=show_movies,args=(rem,groups,group,maabada),key='grade')
        if st.sidebar.button('Show DF'):
            grades=pd.read_csv('grades.csv')
            st.dataframe(grades)

        if st.sidebar.checkbox('Show all movies?'):
            yielded,video_name=make_movie(movies_dir)
            for video in yielded:
                if st.button('Show this movie?',key=2):
                    st.video(video)
        options=st.sidebar.multiselect('Select movies to show',os.listdir(movies_dir))
        if len(options)>0:
            for video in make_movie(movies_dir,options):
                if st.button('Show movie?',key=3):
                    st.video(video)
        if maabada in ('Robotica','Vision'):
            tmp = df[['station', 'group']]
            tmp['station'] = tmp.station.astype('int')
            tmp=set(tmp['group'][tmp['station'] > 10].to_numpy())
            if len(tmp)>0:
                st.markdown('#### Groups {} submitted from wrong station in {}.'
                         .format(','.join(tmp),maabada))
        elif maabada in ('IOT','Auto car 1','Auto car 2'):
            tmp = df[['group', 'os']]
            tmp_set = set(tmp['group'][tmp.os=='Windows'])
            if len(tmp_set) > 0:
                st.write('groups {} submitted files on wrong OS in {}.'.format(','.join(tmp_set),maabada))

main()
