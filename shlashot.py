import streamlit as st
import pandas as pd
import os,sys,numpy as np
def main():
    st.header('List of students and groups')
    st.write(np.__version__)
    st.sidebar.subheader('Choose group members up to 3 students.')
    if not os.path.isfile('groups.csv'):
        groups=pd.read_csv('students.csv')
        groups['full_name']=groups['First name']+' '+groups['Last name']
        groups['group']=-1
        groups=groups[['full_name','group','Email address']]
        groups.loc[len(groups.index)]=["Yoav Ziv",0,'yoavziv1@mail.tau.ac.il']
        groups.loc[len(groups.index)]=["Gad Halevy",0,'gad3dh@gmail.com']
        groups.to_csv('groups.csv', index=False)
    else:
        groups=pd.read_csv('groups.csv')
    st.dataframe(groups,height=38*(len(groups)-2))
    options=groups.loc[groups['group']==-1]
    members=st.sidebar.multiselect('Please select your group',options['full_name'],max_selections=3)
    if st.sidebar.button('Update'):
        if len(members)>1:
            max_num=groups['group'].max()+1
            my_str=''
            for m in members:
                groups.loc[groups['full_name']==m,'group']=max_num
                my_str+=m+' '
            groups.to_csv('groups.csv',index=False)
            my_str+=f'belong to group {max_num} all your submissions should start with this group number.'
            st.sidebar.markdown(f'### :red[{my_str}]')
        else:
            st.sidebar.markdown('## :red[Should be 2 or 3 students in group.]')

if __name__=='__main__':
    main()





