import streamlit as st
import pandas as pd
import requests
import io
import os
import json
import psycopg2
import psycopg2.extras

DATABRICKS_TOKEN= 'dapi1a547e827c34e82fbdec9b461528013a'

input_fields = ['General_Health', 'Checkup', 'Age_Category', 'Height', 'Weight', 'BMI',
       'Alcohol_Consumption', 'Fruit_Consumption',
       'Green_Vegetables_Consumption', 'FriedPotato_Consumption',
       'Exercise_Yes', 'Skin_Cancer_Yes', 'Other_Cancer_Yes', 'Depression_Yes',
       'Diabetes_No_pre-diabetes_or_borderline_diabetes', 'Diabetes_Yes',
       'Diabetes_Yes_but_female_told_only_during_pregnancy', 'Arthritis_Yes',
       'Sex_Male', 'Smoking_History_Yes', 'PATIENT_ID']


def create_tf_serving_json(data):
    if isinstance(data, dict):
        return {'inputs': {name: [value] if not isinstance(value, list) else value for name, value in data.items()}}
    else:
        return {'inputs': data.tolist()}

def score_model(dataset):
    url = 'https://dbc-bfddaf47-d915.cloud.databricks.com/serving-endpoints/my-model/invocations'
    headers = {'Authorization': f'Bearer {DATABRICKS_TOKEN}', 
    'Content-Type': 'application/json'}
    ds_dict = {'dataframe_split': dataset.to_dict(orient='split')} if isinstance(dataset, pd.DataFrame) else create_tf_serving_json(dataset)
    data_json = json.dumps(ds_dict, allow_nan=False)
    
    
    response = requests.request(method='POST', headers=headers, url=url, data=data_json)
    if response.status_code != 200:
        raise Exception(f'Request failed with status {response.status_code}, {response.text}')
    
    return response.json()

conn = psycopg2.connect(host='mydb.czj96lm1eush.us-west-2.rds.amazonaws.com', dbname='postgres',
                        user='postgres', password='Admin123*')
cursor = conn.cursor()

def insertIntoTable(df, table):
        """
        Using cursor.executemany() to insert the dataframe
        """
        # Create a list of tupples from the dataframe values
        tuples = list(set([tuple(x) for x in df.to_numpy()]))
    
        # Comma-separated dataframe columns
        cols = ','.join(list(df.columns))
        # SQL query to execute
        query = "INSERT INTO %s(%s) VALUES(%%s,%%s,%%s,%%s)" % (
            table, cols)
        
    
        try:
            cursor.executemany(query, tuples)
            conn.commit() 
            return 'Data has been added'

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            conn.rollback()
            return 1



# Streamlit app title
st.title('Machine Learning Prediction App')

# Sidebar for user selection (batch or online)
inference_type = st.sidebar.radio("Inference Type", ('Batch Inference', 'Online Inference'))

if inference_type == 'Batch Inference':
    st.sidebar.write('Upload a CSV file for batch inference.')
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        # Read the uploaded CSV
        df = pd.read_csv(uploaded_file)
        df=df[input_fields].head(5)
        
        # Display the data
        st.write('Uploaded Data:')
        st.write(df.head(5))

        df['Predictions'] = 1  
      
        batch_predictions = score_model(df)
        st.write('Batch Prediction Results:')
        df['Predictions']=batch_predictions['predictions']
        st.dataframe(df.head(5))
        
        if len(df) > 0:
            
            df = df.rename(columns={"Diabetes_No_pre-diabetes_or_borderline_diabetes": "Diabetes_No_pre_diabetes_or_borderline_diabetes"}, errors="raise")
            df_columns = list(df)
            st.write(df_columns)
            # create (col1,col2,...)
            columns = ",".join(df_columns)

            # create VALUES('%s', '%s",...) one '%s' per column
            values = "VALUES({})".format(",".join(["%s" for _ in df_columns])) 

            #create INSERT INTO table (columns) VALUES('%s',...)
            insert_stmt = "INSERT INTO {} ({}) {}".format('cvd',columns,values)

            # cursor = conn.cursor()
            psycopg2.extras.execute_batch(cursor, insert_stmt, df.values)
            conn.commit()
            cursor.close()
        # st.write(status)
        st.write(batch_predictions)
        st.write(df)
        st.download_button(label="Download Prediction Results", data=df.to_csv().encode('utf-8'), key='batch_prediction',file_name='Predictions.csv')
        

elif inference_type == 'Online Inference':
    st.sidebar.write('Enter data for online inference.')
 
    user_input = {}
    for field in input_fields:
        if field=='HCP_ID':
         user_input[field] = st.text_input(f'Enter {field}', value='HCP_1')
        else:
         user_input[field] = st.number_input(f'Enter {field}', value=0)
    st.write(user_input)
    user_input_dict = {field: str(value) if isinstance(value, str) else float(value) for field, value in user_input.items()}
    df = pd.DataFrame([user_input_dict],index=[0])
   


    if st.button('Predict'):

    # if st.button('Predict'):
    # Prepare the user's input data in the desired format
        try:
            # online_input = create_tf_serving_json(user_input)

            # Make an online prediction request
            online_predictions = score_model(df)
            df['Predictions']=online_predictions['predictions']
            if len(df) > 0:
                df = df.rename(columns={"Diabetes_No_pre-diabetes_or_borderline_diabetes": "Diabetes_No_pre_diabetes_or_borderline_diabetes"}, errors="raise")
                df_columns = list(df)
                # create (col1,col2,...)
                columns = ",".join(df_columns)

                # create VALUES('%s', '%s",...) one '%s' per column
                values = "VALUES({})".format(",".join(["%s" for _ in df_columns])) 

                #create INSERT INTO table (columns) VALUES('%s',...)
                insert_stmt = "INSERT INTO {} ({}) {}".format('cvd',columns,values)

                # cursor = conn.cursor()
                psycopg2.extras.execute_batch(cursor, insert_stmt, df.values)
                conn.commit()
                cursor.close()

        except Exception as e:
            st.error(f'Error making online prediction: {str(e)}')
        else:
            if online_predictions['predictions'][0]==0:
                    st.success('you are less likely to have heart disease')
            else:
                   #st.success(f'Predicted Output: {online_predictions}')
                   st.success('you are more likely to have heart disease')

    
       
