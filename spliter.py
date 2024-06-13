# #This will not run on online IDE
# from selenium import webdriver
# from selenium.webdriver.common.action_chains import ActionChains
# import requests
# from bs4 import BeautifulSoup
# import time,streamlit as st
# class Cross:
#     def set_places(self):
#         # if url is None:
#         #     # url = "https://geek.co.il/~mooffie/crossword/temporary/40017/print"
#         #     url="https://geek.co.il/~mooffie/crossword/"
#         # URL=self.url
#         # print(self.url)
#         URL=self.url
#         r = requests.get(URL)
#         soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib
#         # with open('html.txt','w') as f:
#         #     f.write(soup.prettify())
#         table=soup.find('table',attrs={'class':'crossword non-preview'})
#         row_count=0
#         dic={}
#         for row in table.find_all('tr'):
#             col_count=0
#             for col in row.findAllNext('td'):
#                 if col.text.isdigit():
#                     dic[col.text]=row_count,col_count
#                 col_count+=1
#             row_count+=1
#         return dic

#     def make_cross(self,txt=None):
#         driver = webdriver.Firefox()
#         driver.get("https://geek.co.il/~mooffie/crossword/")
#         area=driver.find_element('id',"raw-words")
#         area.clear()
#         with open(txt,'r') as f:
#             text=f.read()
#         area.send_keys(text)
#         time.sleep(5)
#         last_height = driver.execute_script("return document.body.scrollHeight")
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         btn=driver.find_element('name',"action_same")
#         action = ActionChains(driver)
#         action.click(on_element=btn)
#         action.perform()
#         time.sleep(5)
#         save_btm = driver.find_element('id', 'save-create-temp-btn')
#         action = ActionChains(driver)
#         action.click(on_element=save_btm)
#         action.perform()
#         time.sleep(5)
#         # print(driver.current_url)
#         self.url=driver.current_url+'/print'
#         driver.close()
#     def main(self):
#         empty=st.empty()
#         chk=empty.checkbox('רוצה לכתוב תשבץ!')
#         if chk:
#             txt=st.text_area('כתוב את הגדרות התשבץ בבקשה!',key='_text')
#             st.session_state['text']=txt
#             # if st.button('המשך?',on_click=self.save_val):
#             st.write(st.session_state.text)
#             with open('words.txt','w') as f:
#                 f.writelines(st.session_state['text'])
#                 empty.empty()
#         btn1=st.button('רוצה להשתמש בקובץ קיים?')
#         if btn1:
#             self.make_cross('words.txt')
#             st.write(self.set_places())
# if __name__=='__main__':
#     cross=Cross()
#     cross.main()
#     # cross.make_cross()
#     # print(cross.set_places())
#     # set_places()
#     # make_cross()
# import streamlit as st,os
# from pypdf import PdfReader,PdfWriter
# import base64,os
# def split_pdfs(input_file_path,lab):
#     inputpdf = PdfReader(open(input_file_path, "rb"))
#
#     out_paths = []
#     if not os.path.exists("splitted"):
#         os.makedirs("splitted")
#
#     for i, page in enumerate(inputpdf.pages):
#         output = PdfWriter()
#         output.add_page(page)
#
#         out_file_path = f"splitted/{lab}/{lab}_{i}.pdf"
#         with open(out_file_path, "wb") as output_stream:
#             output.write(output_stream)
#
#         out_paths.append(out_file_path)
#     return out_paths
# # split_pdfs('PreVision/preVision.pdf')
# def main():
#     labs = ('Robotica', 'PreVision', 'Vision', 'Robolego', 'Yetsur', 'HMI', 'Android', 'IOT', 'Auto car 1','Social networks')
#     for lab in labs:
#         for l in os.listdir(lab):
#             if l.endswith('pdf'):
#                 split_pdfs(f'{lab}/l',lab)
#
# main()
import streamlit as st
import pandas as pd
st.header("Verifier decoder")
st.subheader('Tries to find incorrect submissions')
year = st.sidebar.selectbox('Please choose year', ['Tashpag', 'Tashpad', 'Tashpah','Demo'],1)
labs = ('Choose', 'Robotica', 'PreVision','Vision', 'Robolego', 'Yetsur','HMI', 'Android', 'IOT', 'Auto car 1', 'Auto car 2','Social networks')
semester = st.sidebar.selectbox("Please choose semester", ('A', 'B'),1)
maabada = st.sidebar.selectbox('Please select maabada', labs)
kvutsot = pd.read_csv('groups.csv', header=0)
st.write(kvutsot)
num=len(kvutsot)
remarks = [l + '_rem' for l in labs[1:]]
rem_data = {r: ['Lo nivdak'] * num for r in remarks}
data={l:[100]*num for l in labs[1:]}
data.update(rem_data)
temp=list(zip(labs[1:],remarks))
new_cols=[item for sublist in temp for item in sublist]
grades=pd.DataFrame(columns=new_cols,data=data)
concated=pd.concat([kvutsot,grades],axis=1)
st.write(concated)
# concated.to_csv('grades.csv')


