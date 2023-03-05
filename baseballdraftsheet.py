import pandas as pd
from scipy import stats
import numpy as np

df = pd.read_csv("pitcher.csv", index_col=["playerid"]) #Preseason Pitchers

expr1= (df['GS']/(df['ER']*(df['GS']/df['G']))).fillna(0).replace([np.inf, -np.inf], 0)
expr2= (df['IP']*(df['GS']/df['G'])).fillna(0)
expr3= (((df['GS']+df['G'])/(2*df['G']))**2).fillna(0)
expr4= (expr1*expr2*expr3)
#df['EstimatedQS']=(expr1*expr2*expr3)
#df['Estimated QS']= (expr1*expr2*expr3).fillna(0).astype(float)
df['ER']=(df['ER']*-1)
df['EstimatedQS']= expr4
df=df.drop(['ER','GS', 'G'],axis=1)

df['F-Strike%'] = df['F-Strike%'].str.rstrip('%').astype('float')
df['Barrel%'] = df['Barrel%'].str.rstrip('%').astype('float')
df['CSW%'] = df['CSW%'].str.rstrip('%').astype('float')
df['SwStr%'] = df['SwStr%'].str.rstrip('%').astype('float')
df['HardHit%'] = df['HardHit%'].str.rstrip('%').astype('float')
df['Barrel%']= df['Barrel%']*-1

numbers = df.select_dtypes(include='number').columns
df[numbers] = df[numbers].apply(stats.zscore)
df['SV']=df['SV']*1.5
df['Barrel%']= df['Barrel%']*1.5
df['xFIP-']= df['xFIP-']*1.5
df['SwStr%']= df['SwStr%']*1.5
df['F-Strike%']= df['F-Strike%']*1.5
df['CSW%']= df['CSW%']*1.5
df['K%+']= df['K%+']*5
df['BB%+']= df['BB%+']*5
df['EstimatedQS']= df['EstimatedQS']*5
# numbers2 = df[['SV', 'xFIP-', 'SV', 'SwStr%', 'F-Strike%', 'Barrel%','CSW%','K%+', 'BB%+', 'EstimatedQS']]
#df[numbers2]= (float(df[numbers2]))*2

df['Total Z-Score']= df.sum(axis = 1)
#df['Total Z-Score']= df['Total Z-Score']

rounded_df = df.round(decimals=2).sort_values(by='Total Z-Score', ascending=False)
#print(rounded_df)
#rounded_df.to_excel("Pitchers.xlsx", sheet_name='Pitchers')
rounded_df.to_csv("ZPitchers.csv")

df = pd.read_csv("hitter.csv", index_col=["playerid"]) #Preseason Hitters

df['Barrel%'] = df['Barrel%'] = df['Barrel%'].str.rstrip('%').astype('float')

filter= df[(df['PA'] > 250) & (df['HR'] > 5)]

numbers = df.select_dtypes(include='number').columns
df[numbers] = df[numbers].apply(stats.zscore)

df['Total Z-Score']= df.sum(axis = 1)

rounded_df = df.round(decimals=2).sort_values(by='Total Z-Score', ascending=False)

#rounded_df.to_excel("Hitters.xlsx", sheet_name='Hitters')
rounded_df.to_csv("ZHitters.csv")

dffgpit = pd.read_csv("fg2.csv")
dfstuff = pd.read_csv("stuffplus.csv")
dfadp = pd.read_csv("adp.csv")
dfzpit = pd.read_csv("ZPitchers.csv")
dfzhit = pd.read_csv("ZHitters.csv")
dffghit = pd.read_csv("fg.csv")

dflist = [dffgpit, dfzpit, dfzhit, dfadp, dfstuff, dffghit]

dffgpit = dffgpit.replace(r'[^\w\s]|_\*', '', regex=True).replace(r'\bJr$', '', regex=True).replace(r'II$', '', regex=True)
dfstuff = dfstuff.replace(r'[^\w\s]|_\*', '', regex=True).replace(r'\bJr$', '', regex=True).replace(r'II$', '', regex=True)
dfadp= dfadp.replace(r'[^\w\s]|_\*', '', regex=True).replace(r'\bJr$', '', regex=True).replace(r'II$', '',regex=True)
dfzpit= dfzpit.replace(r'[^\w\s]|_\*', '', regex=True).replace(r'\bJr$', '', regex=True).replace(r'II$', '',regex=True)
dffghit= dffghit.replace(r'[^\w\s]|_\*', '', regex=True).replace(r'\bJr$', '', regex=True).replace(r'II$', '',regex=True)
dfzhit= dfzhit.replace(r'[^\w\s]|_\*', '', regex=True).replace(r'\bJr$', '', regex=True).replace(r'II$', '',regex=True)

#for index in range(len(dflist)):
#    dflist[index] = dflist[index].replace(r'[^\w\s]|_\*', '', regex=True).replace(r'\bJr$', '', regex=True).replace(r'II$', '',regex=True)

dfadp = dfadp.astype(str)

func = lambda x: ''.join([i[:3] for i in x.strip().split(' ')])
dffgpit['Key'] = dffgpit.Name.apply(func)
dfstuff['Key'] = dfstuff.player_name.apply(func)
dfadp['Key'] = dfadp.Player.apply(func)
dfzpit['Key'] = dfzpit.Name.apply(func)
dfzhit['Key'] = dfzhit.Name.apply(func)
dffghit['Key'] = dffghit.Name.apply(func)

dffgpit.columns = dffgpit.columns.str.strip()
dffghit.columns = dffghit.columns.str.strip()
dfstuff.columns = dfstuff.columns.str.strip()
dfadp.columns = dfadp.columns.str.strip()

dfadp = dfadp.drop(['ESPN','CBS','RTS','NFBC','FT'], axis=1)

df1 = dfadp.merge(dffgpit, on=["Key"], how="left").merge(dfstuff[['Key', 'STUFFplus', 'LOCATIONplus', 'PITCHINGplus']], on=["Key"], how="left").merge(dfzpit[['Key', 'Total Z-Score']], on=["Key"], how="left").merge(dfzhit[['Key', 'Total Z-Score']], on=["Key"], how="left").merge(dffghit, on=["Key"], how="left")
df1 = df1.drop(['Team_y', 'playerid_y','Name_y', 'Team'], axis=1)
df1['Rank'] = df1['Rank'].astype(float)
df1 = df1.fillna('')
#df2 = df1.sort_values(by=['Rank'])

df1.to_csv('draftsheet.csv')