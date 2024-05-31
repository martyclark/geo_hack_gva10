import streamlit as st
import numpy as np
import pandas as pd

from pandas import DataFrame
import json
import mysql.connector


def cnvrtCoord(val) -> float:
    return float(val)

def generate_1d_dataframe(dataframe ):# stmt
    #result = stmt.fetchall()
    column_names = list(dataframe.columns)
    column1 = column_names[0]
    column2 = column_names[1]
    labels_dim1 = []
    for row_idx, row in dataframe.iterrows():
        label1 = dataframe.iloc[row_idx][column1]
        if not label1 in labels_dim1:
            labels_dim1.append(label1)

    result2 = np.zeros(len(labels_dim1))
    for row_idx, row in dataframe.iterrows():
        #labal1 = row[0]
        label1 = dataframe.iloc[row_idx][column1]
        idx1 = labels_dim1.index(label1)
        value = dataframe.iloc[row_idx][column2]
        result2[idx1] = value
    print(labels_dim1)
    print(result2)
    test = []
    test.append("count")
    
    df = DataFrame(result2, labels_dim1, ["Team ID"])
    return df

def generate_2d_dataframe(dataframe):  # stmt
    column_names = list(dataframe.columns)
    col_label1, col_label2, col_value = column_names[0], column_names[1], column_names[2]
    labels_dim1, labels_dim2  = [], []
    # retrieve all dimention1 and dimension 2 labels
    for row_idx, row in dataframe.iterrows():
        label1, label2 = dataframe.iloc[row_idx][col_label1], dataframe.iloc[row_idx][col_label2]
        if not label2 in labels_dim2:
            labels_dim2.append(label2)
        if not label1 in labels_dim1:
            labels_dim1.append(label1)

    array_2d = np.zeros((len(labels_dim1), len(labels_dim2)))
    for row_idx, row in dataframe.iterrows():
        label1, label2 = dataframe.iloc[row_idx][col_label1], dataframe.iloc[row_idx][col_label2]
        value = dataframe.iloc[row_idx][col_value]
        idx1 = labels_dim1.index(label1)
        idx2 = labels_dim2.index(label2)
        array_2d[idx1][idx2] = row[2]
    print(labels_dim1, labels_dim2)
    print(array_2d)
    df = DataFrame(array_2d, labels_dim1, labels_dim2)
    return df


# Function to generate a pivot table from the dataframe
def generate_pivot_table(dataframe):
    # Convert year to string without comma
    dataframe['year'] = dataframe['year'].astype(str)
    pivot_df = dataframe.pivot_table(
        index=['collection_name', 'year'],
        columns='type',
        values='card_count',
        aggfunc='sum',
        fill_value=0
    )
    # Reorder columns to have 'player' first, then 'team', then 'other'
    pivot_df = pivot_df[['player', 'team', 'other']]
    return pivot_df



def connect_to_db():
    return connect_to_db2(None)
def connect_to_db2(dbname):
    dbname2 = dbconfig["database"]
    if dbname is not None:
        dbname2 = dbname
    print("dbname2", dbname2)
    return mysql.connector.connect(
        host=dbconfig["host"],  # e.g., 'localhost' ou adresse IP
        database=dbname2,
        user=dbconfig["user"],
        password=dbconfig["password"],
        port=dbconfig["port"]  #  MySQL port par défaut est 3306
    )


config_file = open('config.json')
dbconfig = json.load(config_file)
print(dbconfig)
test = dbconfig["host"]
#connection_string = "mysql+mysqldb://" + dbconfig["user"] + ":" + dbconfig["password"] + "@" \
#                    + dbconfig["host"]+ ":" + str(dbconfig["port"]) + "/" + dbconfig["database"]

#engine = create_engine(connection_string, echo=False)
