#Trevor Moss
#For Weng Lab, Summer 2024
#Created: 20240725
#Last updated: 20240729

import pandas as pd


####### USER INPUT #######
rawBatchOutput = 'featurelist_mzmine_v2.csv'  # Filename here
exportLocation = 'cleanedTest.csv'  # Output location here

# Group mz columns
groupMz = True  # The mz_range:min/max columns are 

# Replicate consistency based filtering
replicateMasking = True  # Removing rows without detected peaks in all replicates of at least one strain/infiltration

# Range Filtering - INCLUSIVE
mzRange =  [400, 500]  # False or [lowlimit, highlimit]
rtRange = False  # False or [lowlimit, highlimit]
heightRange = False  # False or [lowlimit, highlimit]

rangeVars = ['mzRange','rtRange','heightRange']  # If you add additional filters, add them as here {output_column_name}Range and they should work automatically



####### FILE IMPORT #######
df = pd.read_csv(rawBatchOutput)
columns = df.columns.to_list()
rowCountStart = df.shape[0]



####### REMOVING COLUMNS #######
colToDrop = []  # Will be filled with column indexes to drop
colRename = []  # Will be filled with cleaned column names

for column_name in columns:
    colType = column_name.split(':')[0].split('_')[0]  # Extracts the lowest level column type
    if colType not in ['id', 'mz', 'charge', 'height', 'rt', 'datafile']:  # Add columns we don't want to the drop list, keep only listed files
        colToDrop.append(column_name)
    elif colType == 'datafile':
        if column_name.split(':')[2] != 'area':  # Remove all datafile rows that are not areas
            colToDrop.append(column_name)
        else:
            colRename.append(column_name.split(':')[1].split('.')[0])  # Extracts the sample name from the datafile name
    else:
        colRename.append(column_name)  # Adds all other column names that we want

df.drop(colToDrop, axis=1, inplace = True)  # Drops all columns in the colToDrop list
columns = df.columns.to_list()  # Takes down new columns

renameDict = dict(zip(columns, colRename))  # Creates a dictionary with remaining columns and their renamed values
df.rename(columns=renameDict, inplace=True)  # Renames all remaining columns
columns = df.columns.to_list()



####### REORGANIZING COLUMNS #######
keys=[]  # Will be filled with a sortable strain/infiltration.replicate float
vals=[]  # Will be filled with current column position

for ind, column_name in enumerate(columns):  # Fills the lists
    if column_name[0].isnumeric():
        column_name = column_name.split('-')
        vals.append(ind)
        keys.append(float(column_name[0]+'.'+column_name[1][0]))

sortedCols = dict(sorted(dict(zip(keys, vals)).items()))  # Converts the lists to dictionary, sorts based on the strain.replicate float (0.1 min, n.9 max)
colOrder = list(sortedCols.values())  # Extracts the column order
colOrder = list(range(min(colOrder)))+colOrder  # Adds non-datafile column positions that will not be reordered
df=df[df.columns[colOrder]]  # Rearranges columns of the dataframe
columns = df.columns.to_list()



####### REMOVING ROWS BY REPLICATE MASKING #######
# This removes rows where a peak is not observed in all replicates of at least one strain/infiltration.
# It is toggelable with the  replicateMasking  boolean at the top of the script.

def cleanByReplicateMask(dfRows, dfl):
    replicateBreaks = {}  # Records the columns where a new strain/infiltration begins 
    firstDatafile=[]
    for ind, column_name in enumerate(columns):
        if column_name[0].isnumeric():
            replicateBreaks[int(column_name.split('-')[0])] = ind+1
            if not firstDatafile:
                firstDatafile = ind
    replicateBreaks = [firstDatafile] + list(replicateBreaks.values())
    strains = len(replicateBreaks)-1

    replMask = pd.Series(0, index=range(0,dfRows))
    tempMask = pd.Series()
    for step in range(strains):
        tempMask = dfl.iloc[:, replicateBreaks[step]:replicateBreaks[step+1]].isna().sum(axis=1)
        tempMask.mask(tempMask>0,1,inplace=True)
        replMask = replMask + tempMask

    replMask = replMask.mask(replMask<strains,0).astype(bool)
    dfl = dfl.loc[replMask == False]
    
    return dfl

if replicateMasking == True:
    df = cleanByReplicateMask(df.shape[0], df)



####### RANGE-BASED FILTERS #######
rangeDict = {v.replace('Range','') : eval(v) for v in rangeVars}
for key in rangeDict:
    if rangeDict.get(key):
        df = df.loc[(df[key] >= rangeDict.get(key)[0]) & (df[key] <= rangeDict.get(key)[1])]



####### ADD USER-FILLABLE COMPOUND ID COLUMN #######
df.insert(0, 'compound', '')



####### FILE EXPORT #######
rowCountEnd = df.shape[0]
df.to_csv(exportLocation, index=False)

print('')  # Output whitespace

print(f'File cleaned and exported to {exportLocation}', end =' ')  # Export report
if replicateMasking == True:
    print('with replicate-based filtering')
else:
    print('')

if rowCountEnd != rowCountStart:  # Filtering report
    print(f'{rowCountStart} identified peaks filtered down to {rowCountEnd}')
else:
    print(f'{rowCountStart} identified peaks')

print('')  # Output whitespace