import cv2
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
import pickle, time, os, sys, platform , datetime
from kivy.clock import Clock
from moviepy.editor import *


class AntyCopy(BoxLayout):
    group = ObjectProperty()
    station = ObjectProperty()
    error = ObjectProperty()

    def __init__(self, **kwargs):
        super(AntyCopy, self).__init__(**kwargs)
        try:
            self.dic = pickle.load(open("save.p", "rb"))
        except FileNotFoundError:
            input("Don't copy! make this lab by yourself!")
        Clock.schedule_once(self.start, 0.1)

    def start(self, dt):
        self.station.text = self.dic['station']
        self.group.text=self.dic['group']

    def load(self, path, selection):
        if self.group.text:
            pathWrite = os.path.join(os.curdir, 'Res')
            try:
                os.mkdir(pathWrite)
            except FileExistsError:
                pass
            processed=datetime.datetime.now().strftime("%d/%m %H:%M")
            station = self.station.text
            group = self.group.text
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

                    self.shmor_img( f, pathRead,pathWrite,created,processed,station,group)
                elif (f.lower().endswith('avi')) or (f.lower().endswith('mp4')):
                    self.save_movie(f, pathRead,pathWrite,created,processed,station,group)
                else:
                    self.error.text = 'Please choose images or movies!'
            # if len(movies)>0:
            #     self.save_movies(movies,path,nativ)

        else:
            self.open_pop('Before you proceed', 'Please write your group number')

    def save_movie(self,movie, pathRead,pathWrite,created,processed,station,group):
        clip1 = ImageSequenceClip(['logo.png'],durations=10,fps=30)
        clip1=clip1.set_duration(10)
        clip2 = VideoFileClip(pathRead)
        resized = clip1.resize(clip2.size)
        duration=min(clip2.duration,10)
        txt_clip = TextClip("{} {} {} {}".format(created,processed,station,group), fontsize=50, color='black',bg_color='white')
        txt_clip = txt_clip.set_pos('bottom').set_duration(duration)
        clip3 = CompositeVideoClip([clip2, txt_clip])
        video=concatenate_videoclips([resized,clip3])
        # video = CompositeVideoClip([clip2, txt_clip], size=clip2.size)
        video.write_videofile(os.path.join(pathWrite,movie),fps=30,codec='mpeg4')
        # resized.write_videofile("{}".format(nativ),fps=24,codec='mpeg4')

    def open_pop(self, title, content):
        print(title, content)
        self.popup = Popup(title=title, size=(100, 100), content=Label(text=content, font_size='25dp'))
        self.popup.open()
        Clock.schedule_once(self.close_pop, 5)

    def close_pop(self, dt):
        self.popup.dismiss()

    def shmor_img(self, fileName, pathRead,pathWrite,created,processed,station,group):
        print(pathRead)
        img = cv2.imread(pathRead)
        img = cv2.resize(img, (800, 600))
        self.error.text = ''
        logo = cv2.imread('logo.png')
        logo = cv2.resize(logo, (800, 600))
        img[75:105,100:800]=[255,]*3
        forth=cv2.putText(img,'{} {} {} {}'.format(
            created,processed,station,group),(100,100),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
        # first = cv2.putText(img, 'Date:{} Time:{}'.format(
        #     date, zman, self.group.text, self.station.text), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
        # second = cv2.putText(first, 'Group:{} Station:{}'.format(
        #     self.group.text, self.station.text), (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
        # third = cv2.putText(second, 'Date:{} Time:{}'.format(
        #     date, zman, self.group.text, self.station.text), (100, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255),4)
        # forth = cv2.putText(third, 'Group:{} Station:{}'.format(
        #     self.group.text, self.station.text), (100, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 4)
        fifth = cv2.addWeighted(forth, 0.85, logo, 0.15, 0.0)
        # print(os.path.join(nativ, filename))
        cv2.imwrite(os.path.join(pathWrite,fileName), fifth)

    def exit(self):
        pickle.dump(self.dic, open("save.p", "wb"))
        sys.exit()

class AntyApp(App):
    pass


if __name__ == '__main__':
    AntyApp().run()
