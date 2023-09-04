import pandas as pd
from datetime import datetime

def importCSV(csv, separator):
    return pd.read_csv(csv, sep=separator)

def exportJSON(df, json):
    df.to_json(json, orient='records', lines=True)

def exportCSV(df, csv, separator):
    df.to_csv(csv, sep=separator)

def getDataTypes(data):
    return data.dtypes

def checkMissingValues(data):
    return data.isna().sum()

def checkColumnValues(data):
    return data.value_counts()

def findDuplicateIds(df, columnId):
    return df[df[columnId].duplicated()]

def replaceDuplicateIds(df, columnId):
    duplicated_ids = findDuplicateIds(df, columnId)
    new_val = df[columnId].iloc[-1] + 1
    for i in duplicated_ids.index:
        df.loc[i, [columnId]] = new_val
        new_val=new_val+1

def dropEmptyColumn(df, columnId):
    if(len(df[columnId]) == checkMissingValues(df[columnId])):
        data_act_01.drop(columnId, axis=1, inplace=True)

def fillNaWithValue(df, columnId, value):
    df[columnId] = df[columnId].fillna(value)

def fillNaWithMode(df, columnId):
    moda = df[columnId].mode()[0]
    df[columnId] = df[columnId].fillna(moda)

def changeValue(df, columnId, oldValue, newValue):
    mask = (df[columnId] == oldValue)
    df.loc[mask, columnId] = newValue

def convertToDateTime(df, columnId):
    df[columnId] = pd.to_datetime(df[columnId])

def setMaxDateNow(df, columnId):
    if(columnId == 'OffenseDate'):
        now = datetime.today().strftime("%d-%m-%Y 00:00:00")
    else:     
        now = datetime.today().strftime("%d-%m-%Y %H:%M:%S")
    wrong_date = df.loc[(df[columnId] > now)]
    df.loc[wrong_date.index, columnId] = now

def cleanStrangeCharacters(df, columnId):
    df[columnId] = df[columnId].str.replace('[!,",#,$,%,&,*,+,.,;,\,^,_,`,|,~]','', regex=True)

def cleanWhiteSpaces(df, columnId):
    df[columnId] = df[columnId].str.strip()

def setFirstMayus(df, columnId):
    df[columnId] = df[columnId].str.title()

def setAllMayus(df, columnId):
    df[columnId] = df[columnId].str.upper()

def convertToType(df, columnId, newType):
    df[columnId] = df[columnId].astype(newType)

str_columns = ['OriginalCrimeTypeName', 'Disposition', 'Address', 'City', 'State', 'AddressType']
date_time_columns = ['OffenseDate', 'CallDateTime']
all_mayus_columns = ['OriginalCrimeTypeName', 'Disposition','AddressType']
first_mayus_columns = ['Address', 'City']

#-------------------------------------------------------------------------------------------------------

#IMPORT DATA
data_act_01 = importCSV('data_act_01.csv', ';')

#DELETE COLUMNS
dropEmptyColumn(data_act_01, 'Range')
data_act_01 = data_act_01.drop('CallTime', axis=1)

#DATA TREATMENT
for str_column in str_columns:
    cleanStrangeCharacters(data_act_01, str_column)
    cleanWhiteSpaces(data_act_01, str_column)

for all_mayus_column in all_mayus_columns:
    setAllMayus(data_act_01, all_mayus_column)

for first_mayus_column in first_mayus_columns:
    setFirstMayus(data_act_01, first_mayus_column)

#CRIME ID
replaceDuplicateIds(data_act_01, 'CrimeId')

#DATES AND TIMES
for date_time_column in date_time_columns:
    convertToDateTime(data_act_01, date_time_column)
    setMaxDateNow(data_act_01, date_time_column)
    convertToType(data_act_01, date_time_column, str)

#CITY
fillNaWithValue(data_act_01, 'City', 'Not Recorded')
changeValue(data_act_01, 'City', 'S', 'San Francisco')

#STATE
fillNaWithMode(data_act_01, 'State')

#AGENCY ID
moda = data_act_01['AgencyId'].mode()[0]
changeValue(data_act_01, 'AgencyId', 'CA', moda)
convertToType(data_act_01, 'AgencyId', int)

#ADDRESS TYPE
convertToType(data_act_01, 'AddressType', str)
changeValue(data_act_01, 'AddressType', 'INTERSECTIOON', 'INTERSECTION')
changeValue(data_act_01, 'AddressType', str(1), 'INTERSECTION')

#EXPORT DATA
exportJSON(data_act_01, 'data_act_01_clean.json')
exportCSV(data_act_01, 'data_act_01_clean.csv', ';')