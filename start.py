from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.clock import Clock
import pickle,datetime
from kivy.uix.popup import Popup
from kivy.uix.label import Label

# Window.size = (320, 470)
Window.set_title('Kartis Avoda')
class Form(GridLayout):
    group = ObjectProperty()
    targil = ObjectProperty()
    out = ObjectProperty()
    maabada = ObjectProperty
    def __init__(self, **kwargs):
        super(Form, self).__init__(**kwargs)
        try:
            self.dic = pickle.load(open("save.p", "rb"))
            # print(self.dic)
            # print(self.dic)
        except:
            self.dic={}
            year=input('Please enter year of semester A\n')
            semester=input('Please enter semester A or B (capitals).\n')
            station=input('Please enter station number\n')
            self.dic['station']=station


    def shmor(self):
        dic={}
        print(self.maabada.text=='Vision' )
        group=self.group.text.strip()
        if not group.isdigit() or self.maabada.text not in \
            ('Robotica','Vision','Robolego','Android','Yetsur','IOT','Auto car 1','Auto car 2') :
            self.open_pop('Wrong data', 'Please fill your group number\n and choose lab name')
        else:
            self.out.disabled=False
            dic['start']=datetime.datetime.now().strftime("%d/%m/%y %H:%M")
            dic['group']=group
            dic['station']=self.dic['station']
            dic['lab']=self.maabada.text
            pickle.dump(dic, open("save.p", "wb"))


    def open_pop(self, title, content):
        self.popup = Popup(title=title, size=(100, 100), content=Label(text=content, font_size='20dp'))
        self.popup.open()
        Clock.schedule_once(self.close_pop, 5)

    def close_pop(self, dt):
        self.popup.dismiss()

    def exit(self):
        App.get_running_app().stop()
        # sys.exit(0)


class StartApp(App):
    pass

if __name__ == '__main__':
    StartApp().run()