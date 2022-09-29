import firebase_admin
import streamlit as st
from firebase_admin import credentials
from firebase_admin import db
import pytesseract as ocr
import pandas as pd
import platform
import os,numpy as np
import datetime
from moviepy.editor import *
import cv2
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
        cred = credentials.Certificate("H:/Gibui260318/pythonStuff/verifier/mykey.json")
        ocr.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    elif 'Linux' in tmp:
        cred = credentials.Certificate("/media/cimlab/Transcend/Gibui260318/pythonStuff/verifier/mykey.json")
        ocr.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://Lab9-c9743.firebaseio.com/'})
@st.cache(allow_output_mutation=True)
def make_student_list(path):
    df = pd.read_csv(path, header=0)
    skiprows = df.index[df['Groups'] == u'שלישיות מעבדה - 01'].values[0]
    tmp = df.index[df['Grouping name'] == 'Not in a grouping'].values[0]
    df = df.iloc[skiprows:tmp]
    df = df[[df.columns[1], df.columns[2]]]
    df['Groups'] = df['Groups'].str.split('-')
    stam = pd.DataFrame(df['Groups'].tolist(), columns=['Group', 'num'])
    df = df.reset_index()
    final = df.join(stam)
    groups = final[['Group members', 'num']]
    return groups

@st.cache(allow_output_mutation=True)
def from_db(maabada):
    init()
    # cred = credentials.Certificate("H:/Gibui260318/pythonStuff/verifier/mykey.json")
    ref=db.reference(maabada)
    df=pd.json_normalize(ref.get())
    print(df.to_string())
    group=[col[0] for col in df.columns.str.split('.')][::6]
    pics=[col[2] for col in df.columns.str.split('.')][::6]
    cols=[col[3] for col in df.columns.str.split('.')][:6]
    print(group,pics,cols)
    tmp=df.to_numpy()
    tmp=tmp.reshape(-1,6)
    df=pd.DataFrame(tmp)
    df.columns=cols
    df['targil']=pics
    df['group']=group
    df=df.astype('string')
    return df
@st.cache(allow_output_mutation=True)
def make_pic(path):
    clip = VideoFileClip(path)
    img = clip.get_frame(1)
    return img


@st.cache(allow_output_mutation=True)
def from_movie(path):
    # path='/home/cimlab/Downloads/'
    # xconfig='--psm 6 --oem 3 -c tessedit_char_whitelist= G0123456789'
    # ocr.pytesseract.tesseract_cmd=r'/usr/bin/tesseract'
    img=make_pic(path)
    bw=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret,thresh1 = cv2.threshold(bw,0,255,cv2.THRESH_BINARY)
    # th3 = cv2.adaptiveThreshold(bw, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 11, 2)
    # xconfig = '--psm 6 --oem 3 -c tessedit_char_whitelist= 0123456789'
    # ocr.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
    # ocr.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    xconfig = '--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'
    return ocr.image_to_string(thresh1, config=xconfig).strip() , img

@st.cache(allow_output_mutation=True)
def from_extracted(path,groups,df):
    group = []
    modified = []
    tar = []
    pic_group=[]
    errors=[]
    imgs=[]
    for ff in os.listdir(path):
        for f in os.listdir(ff):
            shem = f[:f.index('_')]
            group_num = groups['num'][groups['Group members'] == shem].values[0].strip()
            group.append(group_num)
            indx = f.index('.')
            targil=f[indx - 2:indx]
            tar.append(targil)
            pathRead = os.path.join(path,ff, f)
            siomet=f.lower()[-3:]
            if (siomet=='avi') or (siomet=='mp4') or (siomet=='mov'):
                mtime=os.path.getmtime(pathRead)
                mtime = datetime.datetime.fromtimestamp(mtime).__format__("%d/%m/%y %H:%M")
                modified.append(mtime)
                str_pic,img=from_movie(pathRead)
                pic_group.append(str_pic)
                imgs.append(img)
            else:
                modified.append(None)
                pic_group.append(None)
                errors.append('Group {} submitted to moodle targil {} with {} wrong format'.format(group_num,targil,siomet))

    d = {'zip_modified': modified, 'zip_targil': tar,'zip_group': group ,'pic_group': pic_group}
    zipdf = pd.DataFrame(data=d,dtype='string')
    # zipdf=zipdf.iloc[:3]
    # print(len(zipdf))
    res=pd.merge(df,zipdf,how='right',left_on=['group','targil'],right_on=['zip_group','zip_targil'])
    return res,errors,imgs

def main():
    st.header("Verifier decoder")
    st.subheader('Tries to find incorrect submissions')
    path=st.sidebar.file_uploader("Find the Overview.csv file of students groups")
    if path:
        groups=make_student_list(path)
        if st.sidebar.checkbox("Show students groups"):
            st.write('Students groups')
            st.dataframe(groups)
        maabada=st.sidebar.selectbox('Please select maabada',
                                     ('Choose','Robotica','Vision','Robolego','Android','Yetsur','IOT','Auto car 1'))
        if maabada!='Choose':
            df=from_db(maabada)
            if st.sidebar.checkbox('Show data from FireBase'):
                st.write('Data from Firebase')
                st.dataframe(df)
            if st.sidebar.checkbox('Show data from extracted movies'):
                extracted_path = st.sidebar.file_uploader("Upload zip movies from Moodle",type="zip")
                if extracted_path:
                    with ZipFile(extracted_path, 'r') as zipObj:
                        zipObj.extractall(maabada)
                    res,errors,imgs=from_extracted(maabada,groups,df)
                    if len(errors)>0:
                        st.write(errors)
                    st.write('Data from Moodle')
                    st.dataframe(res)
                    tmp=set(res['zip_group'][res['group'].isna()])
                    st.write('{} Groups not used verifier: {}'.format(len(tmp),','.join(tmp)))
                    if maabada in ('Robotica','Vision'):
                        tmp = res[['station', 'group']]
                        tmp['station']=tmp.station.astype('int')
                        st.write('Groups {} submitted from wrong station.'
                                 .format(','.join(set(tmp['group'][tmp['station'] > 10].to_numpy()))))
                    tmp=res[['group','zip_group']]
                    tmp=set(tmp['group'][tmp['group'] != tmp['zip_group']].to_numpy())
                    if len(tmp) > 0:
                        st.write('groups {} don"t match'.format(','.join(tmp)))
                    tmp = res[['zip_group','pic_group']].dropna()
                    tmp_set = set(tmp['zip_group'][tmp['zip_group'] != tmp['pic_group']].to_numpy())
                    if len(tmp_set) > 0:
                        st.write('groups {} don"t match with picture'.format(','.join(tmp_set)))
                        tmp.zip_group='group='+tmp.zip_group
                        st.write('Pic group number \u21d3')
                        st.image(imgs,caption=tmp.zip_group.tolist(),width=60)
                    tmp = res[['group','start','created']]
                    tmp_set=set(tmp['group'][tmp.start>=tmp.created])
                    if len(tmp_set) > 0:
                        st.write('groups {} movie was created b4 signing kartis avoda.'.format(','.join(tmp_set)))
                    if maabada in ('IOT','Auto car 1'):
                        tmp = res[['group', 'os']]
                        tmp_set = set(tmp['group'][tmp.os=='Windows'])
                        if len(tmp_set) > 0:
                            st.write('groups {} submitted files on wrong OS.'.format(','.join(tmp_set)))






main()

