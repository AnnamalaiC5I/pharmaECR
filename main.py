import streamlit as st
import pandas as pd
import requests
import io
import json
import psycopg2
import psycopg2.extras

DATABRICKS_TOKEN='dapidd1838269e2c98dd0f74e764d71002ce'

input_fields = ['HCP_ID','NPI_ID','Number_of_Rx','Rx_last_1_Month','Rx_last_3_Month','Rx_last_6_Month','Rx_last_12_Month','Claims_last_1_Month','Procedures_radio_last_1_month','Procedures_Immuno_last_6_month','Procedures_Biopsy_last_3_month','Procedures_Biopsy_last_6_month']    

# def create_tf_serving_json(data):
#     return {'inputs': {name: data[name].tolist() for name in data.keys()} if isinstance(data, dict) else data.tolist()}

def create_tf_serving_json(data):
    if isinstance(data, dict):
        return {'inputs': {name: [value] if not isinstance(value, list) else value for name, value in data.items()}}
    else:
        return {'inputs': data.tolist()}

def score_model(dataset):
    url = 'https://dbc-480c2cb6-5325.cloud.databricks.com/serving-endpoints/phy_cov_endpoint/invocations'
    headers = {'Authorization': f'Bearer {DATABRICKS_TOKEN}', 
    'Content-Type': 'application/json'}
    ds_dict = {'dataframe_split': dataset.to_dict(orient='split')} if isinstance(dataset, pd.DataFrame) else create_tf_serving_json(dataset)
    data_json = json.dumps(ds_dict, allow_nan=False)
    
    # data_json={"dataframe_split": {"index": [0], "columns": ["NPI_ID", "HCP_ID", "Age", "Year_of_Experience", "Number_of_Rx", "Rx_last_1_Month", "Rx_last_3_Month", "Rx_last_6_Month", "Rx_last_12_Month", "Number_of_Px", "Px_last_1_Month", "Px_last_3_Month", "Px_last_6_Month", "Px_last_12_Month", "Claims_last_1_Month", "Claims_last_3_Month", "Claims_last_6_Month", "Claims_last_12_Month", "Procedures_chemo_last_1_month", "Procedures_chemo_last_3_month", "Procedures_chemo_last_6_month", "Procedures_chemo_last_12_month", "Procedures_radio_last_1_month", "Procedures_radio_last_3_month", "Procedures_radio_last_6_month", "Procedures_radio_last_12_month", "Procedures_Immuno_last_1_month", "Procedures_Immuno_last_3_month", "Procedures_Immuno_last_6_month", "Procedures_Immuno_last_12_month", "Procedures_Biopsy_last_1_month", "Procedures_Biopsy_last_3_month", "Procedures_Biopsy_last_6_month", "Procedures_Biopsy_last_12_month", "Promotional_doximity", "Promotional_doximity_last_1_month", "Promotional_doximity_last_3_month", "Promotional_doximity_last_6_month", "Promotional_doximity_last_12_month", "Promotional_medscape", "Promotional_medscape_last_1_month", "Promotional_medscape_last_3_month", "Promotional_medscape_last_6_month", "Promotional_medscape_last_12_month", "F2F_visit", "F2F_visit_last_1_month", "F2F_visit_last_3_month", "F2F_visit_last_6_month", "F2F_visit_last_12_month", "VRC_visit", "VRC_visit_last_1_month", "VRC_visit_last_3_month", "VRC_visit_last_6_month", "VRC_visit_last_12_month", "Sex_M", "Specialty_Immunology", "Specialty_Neuro-oncology", "Specialty_Oncology", "Specialty_Pediatric", "Specialty_Uro-oncology", "HCO_Affiliation_Type_Contract", "HCO_Affiliation_Type_Employment", "HCO_Affiliation_Type_Referral"], "data": [[9846255, "HCP_1", 64, 10, 290, 400, 492, 770, 1373, 234, 464, 738, 1060, 1949, 241, 395, 699, 1047, 48, 82, 112, 154, 43, 57, 79, 110, 41, 77, 80, 114, 49, 97, 182, 209, 8, 11, 15, 26, 47, 8, 12, 18, 30, 55, 1, 2, 3, 5, 9, 2, 3, 5, 9, 16, 1, 0, 0, 1, 0, 0, 0, 0, 1]]}}
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

        # Make batch predictions (replace with your prediction logic)
        # Batch predictions are often done asynchronously, and the results can be saved to a new CSV file.
        # For demonstration, we'll simply return the same data with a "Prediction" column.
        df['Predictions'] = 1  # Replace with your model's predictions
        # try:
        #     batch_prediction = score_model(df)
        #     # df['Prediction'] = batch_predictions
        # except Exception as e:
        #     st.error(f'Error making batch prediction: {str(e)}')
        # else:
        #     st.write('Batch Prediction Results:')
        #     st.write(df)
        #     st.download_button("Download Prediction Results", df.to_csv(index=False), key='batch_prediction')
        # Allow the user to download the results as a new CSV
        batch_predictions = score_model(df)
        st.write('Batch Prediction Results:')
        df['Predictions']=batch_predictions['predictions']
        # status=insertIntoTable(df,'pharma')
        if len(df) > 0:
            df_columns = list(df)
            # create (col1,col2,...)
            columns = ",".join(df_columns)

            # create VALUES('%s', '%s",...) one '%s' per column
            values = "VALUES({})".format(",".join(["%s" for _ in df_columns])) 

            #create INSERT INTO table (columns) VALUES('%s',...)
            insert_stmt = "INSERT INTO {} ({}) {}".format('pharma',columns,values)

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
    
    # Define input fields based on the specified columns
    # ['NPI_ID', 'HCP_ID', 'Age', 'Year_of_Experience', 'Number_of_Rx',
    #    'Rx_last_1_Month', 'Rx_last_3_Month', 'Rx_last_6_Month',
    #    'Rx_last_12_Month', 'Number_of_Px', 'Px_last_1_Month',
    #    'Px_last_3_Month', 'Px_last_6_Month', 'Px_last_12_Month',
    #    'Claims_last_1_Month', 'Claims_last_3_Month', 'Claims_last_6_Month',
    #    'Claims_last_12_Month', 'Procedures_chemo_last_1_month',
    #    'Procedures_chemo_last_3_month', 'Procedures_chemo_last_6_month',
    #    'Procedures_chemo_last_12_month', 'Procedures_radio_last_1_month',
    #    'Procedures_radio_last_3_month', 'Procedures_radio_last_6_month',
    #    'Procedures_radio_last_12_month', 'Procedures_Immuno_last_1_month',
    #    'Procedures_Immuno_last_3_month', 'Procedures_Immuno_last_6_month',
    #    'Procedures_Immuno_last_12_month', 'Procedures_Biopsy_last_1_month',
    #    'Procedures_Biopsy_last_3_month', 'Procedures_Biopsy_last_6_month',
    #    'Procedures_Biopsy_last_12_month', 'Promotional_doximity',
    #    'Promotional_doximity_last_1_month',
    #    'Promotional_doximity_last_3_month',
    #    'Promotional_doximity_last_6_month',
    #    'Promotional_doximity_last_12_month', 'Promotional_medscape',
    #    'Promotional_medscape_last_1_month',
    #    'Promotional_medscape_last_3_month',
    #    'Promotional_medscape_last_6_month',
    #    'Promotional_medscape_last_12_month', 'F2F_visit',
    #    'F2F_visit_last_1_month', 'F2F_visit_last_3_month',
    #    'F2F_visit_last_6_month', 'F2F_visit_last_12_month', 'VRC_visit',
    #    'VRC_visit_last_1_month', 'VRC_visit_last_3_month',
    #    'VRC_visit_last_6_month', 'VRC_visit_last_12_month', 'Sex_M',
    #    'Specialty_Immunology', 'Specialty_Neuro-oncology',
    #    'Specialty_Oncology', 'Specialty_Pediatric', 'Specialty_Uro-oncology',
    #    'HCO_Affiliation_Type_Contract', 'HCO_Affiliation_Type_Employment',
    #    'HCO_Affiliation_Type_Referral']

    # Create input fields for the user
    user_input = {}
    for field in input_fields:
        if field=='HCP_ID':
         user_input[field] = st.text_input(f'Enter {field}', value='HCP_1')
        else:
         user_input[field] = st.number_input(f'Enter {field}', value=0)
    st.write(user_input)
    user_input_dict = {field: str(value) if isinstance(value, str) else float(value) for field, value in user_input.items()}
    df = pd.DataFrame([user_input_dict],index=[0])
    # postgres_insert_query = """ INSERT INTO pharma (Number_of_Rx,Rx_last_1_Month,Rx_last_3_Month,Rx_last_6_Month,Rx_last_12_Month,Claims_last_1_Month,Procedures_radio_last_1_month,Procedures_Immuno_last_6_month,Procedures_Biopsy_last_3_month,Procedures_Biopsy_last_6_month,HCP_ID,NPI_ID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    # record_to_insert = tuple([np.float64(i) for i in query])
    # print(record_to_insert)
    # cursor.execute(postgres_insert_query, record_to_insert)  

    # conn.commit()
    # count = cursor.rowcount
    # print(count, "Record inserted successfully into mobile table") 


    if st.button('Predict'):

    # if st.button('Predict'):
    # Prepare the user's input data in the desired format
        try:
            # online_input = create_tf_serving_json(user_input)

            # Make an online prediction request
            online_predictions = score_model(df)
            df['Predictions']=online_predictions['predictions']
            if len(df) > 0:
                df_columns = list(df)
                # create (col1,col2,...)
                columns = ",".join(df_columns)

                # create VALUES('%s', '%s",...) one '%s' per column
                values = "VALUES({})".format(",".join(["%s" for _ in df_columns])) 

                #create INSERT INTO table (columns) VALUES('%s',...)
                insert_stmt = "INSERT INTO {} ({}) {}".format('pharma',columns,values)

                # cursor = conn.cursor()
                psycopg2.extras.execute_batch(cursor, insert_stmt, df.values)
                conn.commit()
                cursor.close()

        except Exception as e:
            st.error(f'Error making online prediction: {str(e)}')
        else:
            st.success(f'Predicted Output: {online_predictions}')

    
            # Define the API endpoint URL for online inference (replace with your actual endpoint)
        # endpoint_url = 'https://your-model-endpoint-url'

        # Prepare input data (use the user_input dictionary)
        # input_data = {
        #     'data': [list(user_input.values())],
        # }

        # # Make a POST request to the prediction endpoint
        # response = requests.post(endpoint_url, json=input_data)

        # if response.status_code == 200:
        #     prediction = response.json()  # Assuming the endpoint returns JSON
        #     st.success(f'Predicted Output: {prediction}')
        # else:
        #     st.error('Error making the prediction. Check the endpoint or input data.')


