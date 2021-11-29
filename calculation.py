import numpy as np
import pandas as pd
from mypulp import *
import streamlit as st
from importlib.resources import *
import random

st.set_page_config(
    page_title="SaizeApp ",
    #page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title('SaizeriyaOptimization')

option = st.selectbox(
    '使いたい機能を選んでください',
     ('1000円ガチャ', 'カロリー最適化',))
st.write('You selected:', option)
df= pd.read_csv("saize_menu.csv", index_col=0)
    #df.head()
N = len(df)+1
menu_index = [i for i in range(1,N)]
#print(menu_index)
menu, P, C, S= {},{},{},{}
for i in menu_index:
    menu[i] = df["name"][i]
    P[i] = df["price"][i]
    C[i] = df["calorie"][i]
    S[i] = df["salt"][i]

if option == "カロリー最適化":

    money = st.sidebar.slider("予算", 300, 5000, 1000, 100)
    calorie_limit = st.sidebar.slider("摂取カロリー上限", 300, 3000, 1000, 100)

    model = Model() # モデルの定義

    x = {}
    for i in menu_index:
        #x[i] = model.addVar(vtype='B', name=f'x({i})')
        x[i] = model.addVar(vtype='B', name=str(i))
    model.update()

    for i in menu_index:
        model.addConstr(quicksum(P[i]*x[i] for i in menu_index) <= money)
        model.addConstr(quicksum(C[i]*x[i] for i in menu_index) <= calorie_limit)
    s = 0
    if st.sidebar.checkbox("塩分制約を追加する"):
        s = 1
        salt_limit = st.sidebar.slider("単位g", 0.5, 10.0, 1.0, 0.5)
        model.addConstr(quicksum(S[i]*x[i] for i in menu_index) <= salt_limit)

    model.setObjective(quicksum(C[i]*x[i] for i in menu_index), GRB.MAXIMIZE)

    if st.checkbox("計算"):

        model.optimize()
        print('Optimal solution:', model.ObjVal)
        st.write("======================================")
        sum_calorie,sum_price,sum_salt=0,0,0
        for v in model.getVars():
            if v.X> 0:
                st.write(menu[int(v.VarName)],P[int(v.VarName)],"円")
                sum_calorie+=int(C[int(v.VarName)])
                sum_price+=int(P[int(v.VarName)])
                sum_salt+=int(S[int(v.VarName)])
        st.write("=======================================")
        st.write("計",sum_calorie,"キロカロリー")
        st.write("合計金額",sum_price, "円")
        if s == 1:
            st.write(sum_salt, "g")

elif option == "1000円ガチャ":
    budget = st.sidebar.slider("予算を設定", 300, 5000, 1000, 100)
    L = [i for i in P if P[i] <= budget]
    s = 0
    if st.button("ガチャる"):
        st.write("======================================")
        while len(L) > 0:
            meal_number = L[random.randint(1,len(L)-1)]
            #print(L,len(L))
            st.write(menu[meal_number],P[meal_number],"円")
            s += P[meal_number]
            budget -= P[meal_number]
            L = [i for i in P if P[i] <= budget] 
        st.write("======================================")
        st.write("合計金額",s,"円")