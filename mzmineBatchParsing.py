#Trevor Moss
#For Weng Lab, Summer 2024
#Created: 20240725
#Last updated: 20240725

import pandas as pd
import os
import re

rawBatchOutput = 'featurelist_mzmine_v2.csv' #Filename here

df = pd.read_csv(rawBatchOutput)
columns = df.columns.to_list()

colToDrop = [] #Will be filled with column indexes to drop
colRename = [] #Will be filled with cleaned column names
for column_name in columns:
    colType = column_name.split(':')[0].split('_')[0] #Extracts the lowest level column type
    if colType not in ['id', 'mz', 'charge', 'height', 'rt', 'datafile']: #Add columns we don't want to the drop list
        colToDrop.append(column_name)
    elif colType == 'datafile':
        if column_name.split(':')[2] != 'area': #Remove all datafile rows that are not areas
            colToDrop.append(column_name)
        else:
            colRename.append(column_name.split(':')[1].split('.')[0]) #Extracts the sample name from the datafile name
    else:
        colRename.append(column_name) #Adds all other column names that we want

df.drop(colToDrop, axis=1, inplace = True) #Drops all columns in the colToDrop list
columns = df.columns.to_list() #Takes down new columns

renameDict = dict(zip(columns, colRename)) #Creates a dictionary with remaining columns and their renamed values
df.rename(columns=renameDict, inplace=True) #Renames all remaining columns

print(df) #Temp