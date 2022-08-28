import cv2, time , os
# import pytesseract as ocr
import  numpy as np
import pandas as pd
from io import StringIO
# from moviepy.editor import *
from zipfile import ZipFile
# importing required modules
# from zipfile import ZipFile
# from zipfile38 import ZipFile
import datetime, pickle,json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import shutil
import pytesseract as ocr
from moviepy.editor import *

class Decoder():
    def __init__(self):
        cred = credentials.Certificate("mykey.json")
        firebase_admin.initialize_app(cred, {'databaseURL': 'https://Lab9-c9743.firebaseio.com/'})
        # path=input('Enter path of CimLab groups csv file\n')
        # if not path:
        #     path = '/home/cimlab/Downloads/Overview.csv'
        path='Overview.csv'
        df = pd.read_csv(path, header=0)
        skiprows=df.index[df['Groups']==u'שלישיות מעבדה - 01'].values[0]
        tmp=df.index[df['Grouping name']=='Not in a grouping'].values[0]
        nrows=tmp-skiprows
        df = pd.read_csv(path, header=0, skiprows=lambda x: x in range(1, skiprows+1), nrows=nrows)
        df = df[[df.columns[1], df.columns[2]]]
        df['Groups'] = df['Groups'].str.split('-')
        tmp = pd.DataFrame(df['Groups'].tolist(), columns=['Group', 'num'])
        final = pd.concat([df, tmp], axis=1)
        self.groups = final[['Group members', 'num']]
        self.xconfig = '--psm 6 --oem 3 -c tessedit_char_whitelist= G0123456789'
        ocr.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
        print(self.groups.to_string())

    def from_fb(self):
        maabada=input('Please choose maabada\n')
        ref=db.reference(maabada)
        self.df=pd.json_normalize(ref.get())
        print(self.df.to_string())
        group=[col[0] for col in self.df.columns.str.split('.')][::6]
        pics=[col[2] for col in self.df.columns.str.split('.')][::6]
        cols=[col[3] for col in self.df.columns.str.split('.')][:6]
        print(group,pics,cols)
        tmp=self.df.to_numpy()
        tmp=tmp.reshape(-1,6)
        self.df=pd.DataFrame(tmp)
        self.df.columns=cols
        self.df['targil']=pics
        self.df['group']=group
        self.df=self.df.astype('string')
        print(self.df.to_string())

    def from_zip(self):
        # Need to map name to group
        # with ZipFile('C:/Users/cimlab/Downloads/cim.zip', 'r') as zip:
        group = []
        modified = []
        system = []
        with ZipFile('cim.zip', 'r') as zip:
            for info in zip.infolist():
                # print(*info.extra)
                name=info.filename
                print(name)
                shem=name[:name.index('_')]
                group_num=self.groups['num'][self.groups['Group members']==shem].values[0]
                group.append(group_num)
                modified.append(str(datetime.datetime(*info.date_time)))
                if info.create_system==0:
                    res='Windows'
                elif info.create_system==3:
                    res='Linux'
                system.append(res)
        # print(len(group),group,len(modified),modified,len(system),system,sep='\n')
        d={'zip_group': group ,'zip_modified': modified ,'zip_os': system }
        self.zipdf=pd.DataFrame(data=d)
        # print(zipdf.to_string())

    def from_movie(self,path):
        # path='/home/cimlab/Downloads/'
        # xconfig='--psm 6 --oem 3 -c tessedit_char_whitelist= G0123456789'
        # ocr.pytesseract.tesseract_cmd=r'/usr/bin/tesseract'
        clip=VideoFileClip(path)
        img=clip.get_frame(1)
        bw=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        ret,thresh1 = cv2.threshold(bw,127,255,cv2.THRESH_BINARY)
        # th3 = cv2.adaptiveThreshold(bw, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 11, 2)
        return ocr.image_to_string(thresh1, config=self.xconfig).strip()

    def from_extracted(self):
        group = []
        modified = []
        tar = []
        pic_group=[]
        for f in os.listdir('extracted')[:3]:
            # print(*info.extra)
            # print(f)
            shem = f[:f.index('_')]
            group_num = self.groups['num'][self.groups['Group members'] == shem].values[0].strip()
            group.append(group_num)
            pathRead = os.path.join('extracted', f)
            mtime=os.path.getmtime(pathRead)
            mtime = datetime.datetime.fromtimestamp(mtime).__format__("%d/%m/%y %H:%M")
            modified.append(mtime)
            indx=f.index('.')
            tar.append(f[indx-2:indx])
            pic_group.append(self.from_movie(pathRead))
        d = {'zip_modified': modified, 'zip_targil': tar,'zip_group': group ,'pic_group': pic_group}
        zipdf = pd.DataFrame(data=d,dtype='string')
        # zipdf=zipdf.iloc[:3]
        print(zipdf.to_string())
        res=pd.merge(self.df,zipdf,how='inner',left_on=['group','targil'],right_on=['zip_group','zip_targil'])
        # print(self.df.dtypes)
        # print(zipdf.dtypes)
        print(res.to_string())

    def syntetic_data(self):
        for i,f in enumerate (os.listdir('inflated/moodle')):
            if not f.endswith('mp4'):
                indx=f.index('.')
                dest=shutil.copyfile('H:/Gibui260318/pythonStuff/verifier/test/g{}.mp4'.format((i%18)+1)
                                ,'inflated/moodle/{}.mp4'.format(f[:indx]))
                print(dest)
        for f in os.listdir('inflated/moodle'):
            if not f.endswith('mp4'):
                os.remove(os.path.join('inflated/moodle',f))



        # groups=[]
        # modified=[]
        # sys=[]
        # for root, dirs, files in os.walk("cim_in"):
        #     path = root.split(os.sep)
        #
        #     print((len(path) - 1) * '\t', os.path.basename(root))
        #
        #     name = os.path.basename(root)
        #     # print(name)
        #     shem = name[:name.index('_')]
        #     group_num = self.groups['num'][self.groups['Group members'] == shem].values[0]
        #     groups.append(group_num)
        #     modified.append(str(datetime.datetime(*info.date_time)))
        #     if info.create_system == 0:
        #         res = 'Windows'
        #     elif info.create_system == 3:
        #         res = 'Linux'
        #     system.append(res)
        #
        #     for file in files:
        #         print(len(path) * '\t', file)



# syntetic_data()
# dec = Decoder()
# dec.from_fb()
# dec.from_zip()
# dec.syntetic_data()
# dec.from_movie()
# dec.from_extracted()
# dec.syntetic_data()


for i,f in enumerate(os.listdir('test')):
    path=os.path.join('test',f)
    clip = VideoFileClip(path)
    img=clip.get_frame(1)
    # img=cv2.imread('./tmp/img{}.tiff'.format(i))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # kernel = np.ones((1, 1), np.uint8)
    # img = cv2.dilate(img, kernel, iterations=1)
    # img = cv2.erode(img, kernel, iterations=1)
    # # Apply blur to smooth out the edges
    # img = cv2.GaussianBlur(img, (5, 5), 0)
    ret, thresh1 = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY)
    # cv2.imshow('pic',thresh1[300:,:450])
    # cv2.waitKey(0)
    # th3 = cv2.adaptiveThreshold(bw, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 11, 2)
    xconfig = '--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'
    # ocr.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
    ocr.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
    print(f,ocr.image_to_string(thresh1, config=xconfig).strip())

    # print(name[:name.index('_')] + name[name.find('.'):])
                # print('\tModified:\t' + str(datetime.datetime(*info.date_time)))
                # print('\tSystem:\t\t' + str(info.create_system) + '(0 = Windows, 3 =Linux)')
                # print('\tZIP version:\t' + str(info.create_version))
                # print('\tCompressed:\t' + str(info.compress_size) + ' bytes')
                # print('\tUncompressed:\t' + str(info.file_size) + ' bytes')






# print(pics,cols)
# # cols=[col[-1] for col in df.columns.str.split('.')]
# # print(cols)
# cols=['_'.join(col[2:]) for col in df.columns.str.split('.')]
# df.columns=cols
# pics=set([pic[0] for pic in df.columns.str.split('_')])
# df.columns=[pic[1] for pic in df.columns.str.split('_')]
# # df['pic']=pics
# # df['group']=group

# print(tmp)
# # print(pics)
#
# print(df.to_string())
# specifying the zip file name
# file_name = "test.zip"
#

# # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# xconfig='--psm 6 --oem 3 -c tessedit_char_whitelist= G0123456789'
# ocr.pytesseract.tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# ocr.pytesseract.tesseract_cmd=r'/usr/bin/tesseract'
# img=cv2.imread('test/g17.jpg')
# img=img[470:534,516:617]
# cv2.imshow('pic',img)
# cv2.waitKey(0)
# path='/media/cimlab/Transcend/Gibui260318/pythonStuff/verifier/test'
# for i in range(20):
#     img = np.zeros((480, 640, 3), np.uint8)
#     img[::] = 255
#     pic=cv2.putText(img,'G{}'.format(i),(0,470),0,3,(0,0,0),3)
#     cv2.imwrite('test/g{}.jpg'.format(i),pic)
#
# for i,f in enumerate(os.listdir('test')):
#     if f.endswith('jpg'):
#         img=cv2.imread(os.path.join(path,f))
#         cv2.imshow('p',img)
#         cv2.waitKey(0)
        # print(f,ocr.image_to_string(img))
# plist = [x for x in os.listdir() if x.endswith(".png")]
# for pt in plist:
#     img = cv2.imread(pt)
# #     ocr.image_to_string(img,config=xconfig)
# # name = f[:f.index('_')] + f[f.find('.'):]
# kovets=StringIO()
# kovets="StartWork DateCreated TimeCreated DateProcessed TimeProcessed Station Group\n"
# for f in os.listdir('Res'):
#     if f.endswith('jpg') or f.endswith('png'):
#         img = cv2.imread('Res/%s' %f)
#         img=img[75:105,0:800]
#     elif f.endswith('mp4') or f.endswith('avi'):
#         img=VideoFileClip('Res/%s' %f).get_frame(t=10)
#         img=cv2.resize(img,(800,600))
#         cv2.imshow('pic',img)
#         img=img[574:600,120:685]
#         cv2.imshow('p',img)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()
#     kovets += ocr.image_to_string(img, config=xconfig)
#
#
#
#
#
#
# print(kovets)
# df=pd.read_csv(StringIO(kovets),sep=' ')
# print(df)
#
# # cv2.imshow('pic',img)
# # cv2.waitKey(0)
# # cv2.destroyAllWindows()
#
# # Adding custom options
# # custom_config = r'--oem 3 --psm 6'
# # img=cv2.cvtColor(img[75:105,100:450],cv2.COLOR_BGR2GRAY)
# # img=cv2.threshold(img, 127, 255, cv2.THRESH_BINARY )[1]
# # img=cv2.resize(img,(800,600))
# # img=cv2.medianBlur(img,3)
# # cv2.imshow('pic',img)
# # cv2.waitKey(0)
# # print(ocr.image_to_string(img, config=custom_config))
# # print(ocr.image_to_string(img,  config=xconfig))
