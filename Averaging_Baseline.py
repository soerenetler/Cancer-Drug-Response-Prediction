
#%%
import ImportData
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression


#%%
df = ImportData.importDataAsTable(False, False)


#%%
df.head()


#%%
train_df, test_df = train_test_split(df, test_size=0.2)
y_test = test_df["IC50"]

#%% [markdown]
# # Based on the cell_line average

#%%
train_cell_line_mean = train_df.groupby(['cell_line'])['IC50'].mean()


#%%
y_pred_cell_line = [train_cell_line_mean[cell_line] for cell_line in test_df["cell_line"]]


#%%
mean_squared_error(y_test, y_pred_cell_line)

#%% [markdown]
# # Based on the drug_id average

#%%
train_drug_id_mean = train_df.groupby(['drug_id'])['IC50'].mean()


#%%
y_pred_drug_id = [train_drug_id_mean[drug_id] for drug_id in test_df["drug_id"]]


#%%
mean_squared_error(y_test, y_pred_drug_id)

#%% [markdown]
# # Based on the drug_id average and cell_line average

#%%
train_df.loc[:,"drug_id_average"] = [train_drug_id_mean[drug_id] for drug_id in train_df["drug_id"]]
train_df.loc[:,"cell_line_average"] = [train_cell_line_mean[cell_line] for cell_line in train_df["cell_line"]]

test_df.loc[:,"drug_id_average"] = [train_drug_id_mean[drug_id] for drug_id in test_df["drug_id"]]
test_df.loc[:,"cell_line_average"] = [train_cell_line_mean[cell_line] for cell_line in test_df["cell_line"]]


#%%
X_train = train_df[['drug_id_average', 'cell_line_average']]
y_train = train_df['IC50']


#%%
reg = LinearRegression().fit(X_train, y_train)


#%%
y_pred = reg.predict(test_df[['drug_id_average', 'cell_line_average']])


#%%
mean_squared_error(y_test, y_pred)