'''
Same as veriffy5 but with kartis avoda
'''
import cv2
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
import pickle, time, os, sys, platform , datetime
from kivy.clock import Clock
from moviepy.editor import *
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

class AntyCopy(BoxLayout):
    group = ObjectProperty()
    targil = ObjectProperty()
    lab = ObjectProperty()

    def __init__(self, **kwargs):
        super(AntyCopy, self).__init__(**kwargs)
        try:
            self.dic = pickle.load(open("save.p", "rb"))
        except FileNotFoundError:
            input("Don't copy! Please fill Kartis Avoda")
        cred = credentials.Certificate("mykey.json")
        firebase_admin.initialize_app(cred,{
    'databaseURL': 'https://Lab9.firebaseio.com/'})
        Clock.schedule_once(self.start, 0.1)

    def start(self, dt):
        # self.station.text = self.dic['station']
        if self.dic.get('group') != None:
            self.group.text='Your group number is: '+self.dic['group']
            self.lab.text='Working now on '+ self.dic['lab']+' lab'
        else:
            self.open_pop("Attension!","You have to fill Kartis Avoda first")

    def load(self, path, selection):
        targil = self.targil.text.strip()
        if not targil.isdigit():
            self.open_pop('Dont proceed!', 'Please fill the targil number\n and press process button again')
        else:
            pathWrite = os.path.join(os.curdir, 'Res')
            try:
                os.mkdir(pathWrite)
            except FileExistsError:
                pass
            processed=datetime.datetime.now().strftime("%d/%m %H:%M")
            station = self.dic['station']
            group = self.dic['group']
            start=self.dic['start']
            lab=self.dic['lab']
            for f in os.listdir(path):
                pathRead=os.path.join(path, f)
                tmp = platform.platform()
                if 'Windows' in tmp:
                    created = os.path.getctime(pathRead)
                elif 'Linux' in tmp:
                    created = os.path.getatime(pathRead)
                created=datetime.datetime.fromtimestamp(created).__format__("%d/%m/%y %H:%M")
                if (f.lower().endswith('jpg')) or (f.lower().endswith('png')) \
                        or (f.lower().endswith('jpeg')) or  (f.lower().endswith('gif')):

                    self.shmor_img( f, pathRead,pathWrite,start,created,processed,station,group,lab,targil)
                elif (f.lower().endswith('avi')) or (f.lower().endswith('mp4')):
                    self.save_movie(f, pathRead,pathWrite,start,created,processed,station,group,lab,targil)
                else:
                    self.open_pop('Before you proceed', 'Please choose images or movies!')
                Clock.schedule_once(self.fbwrite, 0.1)
                # if len(movies)>0:
                #     self.save_movies(movies,path,nativ)

    def fbwrite(self,pathRead,pathWrite,start,created,processed,station,group,lab,targil):
        ref = db.reference('/{}/'.format(lab))
        ref.set({
            '{}'.format(group):{
                'targil': '{}'.format(targil),
                'start': '{}'.format(start),
                'created':'{}'.format(created),
                'processed':'{}'.format(processed),
                'station':'{}'.format(station)
            }
        })


    def save_movie(self,movie, pathRead,pathWrite,start,created,processed,station,group,lab,targil):
        clip1 = ImageSequenceClip(['logo.png'],durations=10,fps=30)
        clip1=clip1.set_duration(10)
        clip2 = VideoFileClip(pathRead)
        resized = clip1.resize(clip2.size)
        duration=min(clip2.duration,10)
        txt_clip = TextClip("{} {} {} {} {}".format(start,created,processed,station,group), fontsize=50, color='black',bg_color='white')
        txt_clip = txt_clip.set_pos('bottom').set_duration(duration)
        clip3 = CompositeVideoClip([clip2, txt_clip])
        video=concatenate_videoclips([resized,clip3])
        # video = CompositeVideoClip([clip2, txt_clip], size=clip2.size)
        video.write_videofile(os.path.join(pathWrite,movie),fps=30,codec='mpeg4')
        # resized.write_videofile("{}".format(nativ),fps=24,codec='mpeg4')

    def open_pop(self, title, content):
        self.popup = Popup(title=title, size=(100, 100), content=Label(text=content, font_size='25dp'),
                           size_hint=(0.5,0.5))
        self.popup.open()
        Clock.schedule_once(self.close_pop, 5)

    def close_pop(self, dt):
        self.popup.dismiss()

    def shmor_img(self, fileName, pathRead,pathWrite,start,created,processed,station,group,lab,targil):
        img = cv2.imread(pathRead)
        img = cv2.resize(img, (800, 600))
        logo = cv2.imread('logo.png')
        logo = cv2.resize(logo, (800, 600))
        img[75:105,0:800]=[255,]*3
        forth=cv2.putText(img,'{} {} {} {} {}'.format(
            start,created,processed,station,group),(0,100),cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 0), 4)
        fifth = cv2.addWeighted(forth, 0.85, logo, 0.15, 0.0)
        cv2.imwrite(os.path.join(pathWrite,fileName), fifth)

    def exit(self):
        dic={}
        dic['station']=self.dic['station']
        pickle.dump(dic, open("save.p", "wb"))
        sys.exit()

class AntyApp(App):
    pass


if __name__ == '__main__':
    AntyApp().run()
