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
    cred = credentials.Certificate('apikey.json')
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://Lab9-c9743.firebaseio.com/',
                                         'storageBucket' :'lab9-c9743.appspot.com'})
@st.cache(allow_output_mutation=True)
def make_student_list(path):
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
    return groups

# @st.cache(allow_output_mutation=True)
def from_db(year,semester,maabada):
    init()
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
    return df

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
    destination_file_name=os.path.join(year,semester,maabada)    
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
        if f.lower().endswith('mp4'):
            video_file = open(os.path.join(path,f), 'rb')
            video_bytes = video_file.read()
            yield video_bytes

def main():
    st.header("Verifier decoder")
    st.subheader('Tries to find incorrect submissions')
    path = st.sidebar.file_uploader("Find the Overview.csv file of students groups")
    if path:
        groups = make_student_list(path)
        if st.sidebar.checkbox("Show students groups"):
            st.write('Students groups')
            st.dataframe(groups.dropna())
    year=st.sidebar.selectbox('Please choose year',['תשפג','תשפד','תשפה','תשפו','תשפז','תשפח','Tashpag'])
    labs=('Choose', 'Robotica', 'Vision', 'Robolego', 'Android', 'Yetsur', 'IOT','Auto car 1','Auto car 2')
    semester=st.sidebar.selectbox("Please choose semester",('A','B'))
    maabada = st.sidebar.selectbox('Please select maabada',labs)
    if maabada != 'Choose':
        df = from_db(year,semester,maabada)
        if st.sidebar.checkbox('Show data from FireBase?'):
            st.write('Data from Firebase')
            st.dataframe(df)
    if st.sidebar.checkbox('Download movies from Firebase?'):
        for i,r in df.iterrows():
            group=r['group']
            file=r['file']
            dir=download_blob(year, semester, maabada, group, file)
#             st.write(dir)
    if st.sidebar.checkbox('Analyze?'):
        set_fb_groups=set(df['group'])
        st.write(set_fb_groups)
        set_groups=set(strip(s) for s in groups[num])
        st.write(set_groups)
        dif=set_groups-set_fb_groups
        st.write(dif)
        txt='### Groups {} did not make maabada {} yet'.format(' '.join(dif),maabada)
        st.markdown(txt)
        numEx=[2,2,3,0,0,0,0,0,0]
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
            txt='### Groups {} used movies that were created before signed kartis avoda!!'.format(','.join(tmp))
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
#                             st.write(f)
                            if f[:-3]+'jpg' in caption:
                                mismatch.append(f)
                if len(mismatch)>0:
                    for video in make_movie(movies_dir,mismatch):
                        st.video(video)
        if st.sidebar.checkbox('Show all movies?'):
            for video in make_movie(movies_dir):
                st.video(video)
        options=st.sidebar.multiselect('Select movies to show',os.listdir(movies_dir))
        if len(options)>0:
            for video in make_movie(movies_dir,options):
                st.video(video)
        if maabada in ('Robotica','Vision'):
            tmp = df[['station', 'group']]
            tmp['station'] = tmp.station.astype('int')
            tmp=set(tmp['group'][tmp['station'] > 10].to_numpy())
            if len(tmp)>0:
                st.write('Groups {} submitted from wrong station in {}.'
                         .format(','.join(tmp),maabada))
        elif maabada in ('IOT','Auto car 1','Auto car 2'):
            tmp = df[['group', 'os']]
            tmp_set = set(tmp['group'][tmp.os=='Windows'])
            if len(tmp_set) > 0:
                st.write('groups {} submitted files on wrong OS in {}.'.format(','.join(tmp_set),maabada))

main()
