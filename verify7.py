'''
Same as veriffy5 but with kartis avoda
'''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
import pickle, platform , datetime,os,sys
from kivy.clock import Clock
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

class  Welcome (BoxLayout):
    txt=ObjectProperty()
    hashoov=ObjectProperty()
    def __init__(self, **kwargs):
        super(Welcome, self).__init__(**kwargs)
        Clock.schedule_once(self.start,0.1)

    def start(self,dt):
        self.hashoov.text='\u2022[b][u][color=ff0000] In movie first you should film your group number on portrait orientation. [/color][/u][/b]'
        self.txt.text='\u2022 Start your application in windows in directory d:\documents\student. \
        \n\u2022 Start your application in Linux in directory Home/cimlab/PycharmProjects. \
        \n\u2022 Insert only movies in mp4 or avi or mov format. \
        \n\u2022 Each time you use Verifier you need to create new Kartis Avoda. \
        \n\u2022 Each time you use Verifier keep your movies under new directory. \
        \n\u2022 Keep the order of the movies as the order of the missions. \
        \n\u2022 [b][u][color=ff0000]Name your submissions 01 02 Etc, same as exercise numbers.[/color][/u][/b] \
        \n\u2022 After using Verifier upload your movies to moodle. \
        \n\u2022 We recomend to delete your movies after uploading to Moodle. '

    def new_screen(self):
        self.clear_widgets()
        self.add_widget(AntyCopy())


class AntyCopy(BoxLayout):
    group = ObjectProperty()
    lab = ObjectProperty()
    started = ObjectProperty()

    def __init__(self, **kwargs):
        super(AntyCopy, self).__init__(**kwargs)
        try:
            self.dic = pickle.load(open("save.p", "rb"))
            # print(self.dic)
        except FileNotFoundError:
            input("Don't copy! Please fill Kartis Avoda")
        cred = credentials.Certificate("mykey.json")
        firebase_admin.initialize_app(cred,{
    'databaseURL': 'https://Lab9-c9743.firebaseio.com/'})
        Clock.schedule_once(self.start, 0.1)

    def start(self, dt):
        # self.station.text = self.dic['station']
        if self.dic.get('group') != None:
            self.group.text='Your group number is: '+self.dic['group']
            self.lab.text='Working now on '+ self.dic['lab']+' lab'
            self.started.text='Started: '+self.dic['start']
        else:
            self.open_pop("Attension!","You have to fill Kartis Avoda first")
            Clock.schedule_once(self.exit,5)

    def load(self, path, selection):
        processed=datetime.datetime.now().strftime("%d/%m %H:%M")
        station = self.dic['station']
        group = self.dic['group']
        group = f"{group:0>2}"
        start=self.dic['start']
        lab=self.dic['lab']
        for f in os.listdir(path):
            if f[2]!='.' or f[0]!='0' or not f[1].isdigit():
                self.open_pop('Importent!!!','Name your movies 01 02 ETC')
                Clock.schedule_once(self.wrong_submissions, 5)

            pathRead=os.path.join(path, f)
            tmp = platform.platform()
            if 'Windows' in tmp:
                created_os = 'Windows'
                created = os.path.getctime(pathRead)
            elif 'Linux' in tmp:
                created_os = 'Linux'
                created = os.path.getmtime(pathRead)
            created=datetime.datetime.fromtimestamp(created).__format__("%d/%m/%y %H:%M")
            # if (f.lower().endswith('jpg')) or (f.lower().endswith('png')) \
            #         or (f.lower().endswith('jpeg')) or (f.lower().endswith('gif')) \
            if (f.lower().endswith('avi')) or (f.lower().endswith('mp4')) or \
                (f.lower().endswith('mov')):
                self.fbwrite(f,created_os,start,created,processed,station,group,lab)
                # Clock.schedule_once(partial(self.fbwrite,f,start,created,processed,station,group,lab),0.1)
            else:
                self.open_pop('Before you proceed', 'Please choose mp4, avi or mov movies !')
                Clock.schedule_once(self.wrong_submissions, 5)

    def fbwrite(self,f,created_os,start,created,processed,station,group,lab):
        # print(f,created_os,start,created,processed,station,group,lab)
        ref = db.reference('/{}/{}/'.format(lab,group))
        ref.push({
            '{}'.format(f[:f.index('.')]):{
                'file':f,
                'siomet':'{}'.format(f[f.index('.')+1:]),
                'os':'{}'.format(created_os),
                'start': '{}'.format(start),
                'created':'{}'.format(created),
                'processed':'{}'.format(processed),
                'station':'{}'.format(station)
            }
        })

    def open_pop(self, title, content):
        self.popup = Popup(title=title, size=(100, 100), content=Label(text=content, font_size='25dp'),
                           size_hint=(0.5,0.5))
        self.popup.open()
        Clock.schedule_once(self.close_pop, 5)

    def close_pop(self, dt):
        self.popup.dismiss()

    def wrong_submissions(self,dt):
        sys.exit()

    def exit(self,dt):
        dic={}
        dic['station']=self.dic['station']
        pickle.dump(dic, open("save.p", "wb"))
        sys.exit()

class AntyApp(App):
    pass


if __name__ == '__main__':
    AntyApp().run()
