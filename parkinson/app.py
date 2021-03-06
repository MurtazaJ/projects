import streamlit as st
st.set_page_config(
     page_title="Parkinson App",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "# This is a header. This is an *extremely* cool app!"
     }
 )
from models import best_model, get_score, grid_cv
import seaborn as sns
import altair as alt
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler


st.title('Predict if a person has Parkinson')


def create_df():   
    df= pd.read_csv("parkinson/parkinson_disease.csv")
    # print(df.head())
    # print(df.name.nunique() / df.shape[0])
    # print(df.name.nunique())
    # print(df.shape[0])
    # print(df.shape)
    # print(df.isnull().values.sum())    
    # df.nunique()
    return df


def train_and_test(df):
    x = df.drop(['status','name' ], axis=1)
    y = df.status
    X_train, X_test, y_train, y_test = train_test_split(x,y, test_size=0.3)
    print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)
    return X_train, X_test, y_train, y_test


df = create_df()
X_train, X_test, y_train, y_test = train_and_test(df)




#Download the file
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="Parkinson_disease.csv">Download CSV File</a>'
    return href
st.sidebar.subheader('Press download to download the CSV file')
# st.markdown(filedownload(df), unsafe_allow_html=True)
st.sidebar.download_button('Download csv file', filedownload(df), key='downloadfile')
st.sidebar.subheader('')


#displaying the dataframe
selected_columns = df.drop('name', axis = 1).columns.tolist()
st.subheader('Select the features to view the dataframe')
selected_columns_st = st.multiselect('', selected_columns,selected_columns)
df_altered = df[(selected_columns_st)]
st.dataframe(df_altered.head())
st.header('')


# Heatmap
col1 , col2, col3 = st.columns(3)
button1 = col1.button('Intercorrelation Heatmap', key='heatmap')
button2 = col2.button('close', key='close0')
col3.header('')
# col4.header('')


#%%
def corelation(df):
    corrs = {}
    cols = []
    for col in df.drop(['name'], axis = 1).columns:
        c = pd.DataFrame(df.corrwith(df[col]), columns = ['corrs'])
        values = c[c.corrs > 0.6].index.values.tolist()[1:]
        if len(values) > 0:
            corrs[col] = values
    for cols1 in corrs:
        cols.append(cols1) 
    return cols
df3 = df[corelation(df)]



if button1:  
    # col10, col11 = st.columns([1,0.5])
    st.code('''
    corrs = {}
    for col in df.drop(['name'], axis = 1).columns:
        c = pd.DataFrame(df.corrwith(df[col]), columns = ['corrs'])
        values = c[c.corrs > 0.6].index.values.tolist()[1:]
            if len(values) > 0:
                corrs[col] = values''', language= 'python')
    st.subheader('Intercorrelation Matrix Heatmap')
    corr = df3.corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True    
    fig, ax = plt.subplots(figsize= (6, 6))
    ax = sns.heatmap(corr, square=True, fmt='0.1f' , annot=True)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    st.image(buf)
else:
    if button2:
        print(button1)  
        
# Sidebar for defining the height and width of the graphs
st.sidebar.subheader('Please select a size of the plots with this slidebar')
width = st.sidebar.slider("Plot width", 4., 9., 6., key='width_slider' )
height = st.sidebar.slider("Plot height", 4., 9., 6., key='height_slider')  



#Plotting the scatter plots
st.title('Select your features from sidebar')
x_axis = st.sidebar.selectbox('Choose X-axis to plot from the features' ,(X_train.columns))
y_axis = st.sidebar.selectbox('Choose y-axis to plot from the features' ,(X_train.columns))
x_axis_df = df[(x_axis)]
y_axis_df = df[(y_axis)]
fig, ax = plt.subplots(figsize=(width, height))
scatter = ax.scatter(x_axis_df, y_axis_df, c = df['status'] )
plt.xlabel(x_axis_df.name)
plt.ylabel(y_axis_df.name)
plt.legend(*scatter.legend_elements())
plt.title('0 = no & 1 = yes')
buf = BytesIO()
fig.savefig(buf, format="png")
st.image(buf)

st.title('Best models')
col10, col11, col12, col13, col14 =st.columns(5) 
button3 = col10.button('Best models', key='best_model')
button4 = col11.button('close', key='close2')
col12.header('')
col13.header('')
col14.header('')
if button3:
    st.table(pd.read_csv('parkinson/best_models.csv'))
else:
    if button4:
        print(button3)

st.title('Grid Search for Random forest Classifier')
col15, col16, col17, col18, col19 =st.columns(5) 
button5 = col15.button('Best parameters', key='bestpara')
button6 = col16.button('close', key='close')
col17.header('')
col18.header('')
col19.header('')
if button5:
    st.code('''
    params = {
    'max_depth' : [8, 12, 15, 18, 20, 25, 30],
    'n_estimators' : [100,200,300],
    'class_weight' : [None, 'balanced'],
    'criterion' : ['gini', 'entropy'],
    'bootstrap' : [True, False],
    'max_features' : ["auto", "sqrt", "log2"]
            }
    ''')
    st.table(pd.read_csv('parkinson/best_params.csv'))
else:
    if button6:
        print(button5)

parameters = {  'bootstrap': True,
                'criterion': 'entropy',
                'max_depth':18,
                'max_features':'sqrt',
                'n_estimators':300
                }
results, ytest, pred = get_score(X_train, y_train, X_test, y_test, model = RandomForestClassifier(**parameters), scaler = StandardScaler())

st.title('Training the model')
col20, col21, col22, col23, col24 =st.columns(5) 
button7 = col20.button('Train', key='train')
button8 = col21.button('close', key='close3')
col22.header('')
col23.header('')
col24.header('')
if button7:
    st.code('''  
                  precision  recall    f1-score   support

           0       0.91      0.71      0.80        14
           1       0.92      0.98      0.95        45

    accuracy                           0.92        59
   macro avg       0.91      0.85      0.87        59
weighted avg       0.91      0.92      0.91        59''')

    fig, ax = plt.subplots(figsize= (4, 4))
    ax = sns.heatmap(confusion_matrix(ytest, pred), fmt = '.1f', annot = True)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    st.image(buf)
else:
    if button8:
        print(button7)


if __name__ =='__main__':
    create_df()