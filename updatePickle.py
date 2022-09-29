import pickle
with open('save.p','rb') as f:
    dic=pickle.load(f)
    print(dic)
# dic={}
# with open('save.p','wb') as w:
#     dic['station']=11
#     dic['year']='תשפג'
#     dic['semester']='A'
#     pickle.dump(dic,w)
