import pandas as pd
import numpy as np
from tqdm import tqdm

def importDataAsMatrix(filename_labels = 'Data/Labels.txt',
    file_cell_line_name = "Data/Cell_line_IDs.txt",
    file_drug_name = "Data/Drug_PubChem_IDs.txt",
    file_drug_information = 'Data/drug_features_pubchem_id.csv',
    file_cell_line_information = 'Data/cell_line_features_cell_line_ids.csv'):
    
    # Read Cell Line Names into list
    with open(file_cell_line_name) as f:
        cell_line_names = [line.strip() for line in f]

    # Read Drug Names into list
    with open(file_drug_name) as f:
        drug_names = [line.strip() for line in f]

    # Create a matrix (cell line x drug)
    data = pd.read_csv(filename_labels, sep = "\t", header=None, names=cell_line_names)
    data["drug_id"] = drug_names
    data.set_index("drug_id", inplace=True)
    
    return data

def importDataAsTable(includeDrugFeatures, includeCellFeatures,
    filename_labels = 'Data/Labels.txt',
    file_cell_line_name = "Data/Cell_line_IDs.txt",
    file_drug_name = "Data/Drug_PubChem_IDs.txt",
    file_drug_information = 'Data/drug_features_pubchem_id.csv',
    file_cell_line_information = 'Data/cell_line_features_cell_line_ids.csv'):

    data = importDataAsMatrix(filename_labels = filename_labels,
                                file_cell_line_name = file_cell_line_name,
                                file_drug_name = file_drug_name,
                                file_drug_information = file_drug_information,
                                file_cell_line_information = file_cell_line_information)

    # 
    cell_lines = []
    drug_ids = []
    ic50s = []

    data.index
    data.columns

    for row in data.index: # iterate over rows
        for column in data.columns:
            cell_lines.append(column)
            drug_ids.append(row)
            ic50s.append(data[column][row])


    d = {"cell_line": cell_lines, "drug_id": drug_ids, "IC50": ic50s}
    df = pd.DataFrame(data=d)
    df["drug_id"] = df["drug_id"].astype(np.int64)

    if includeDrugFeatures:
        # Read Drug Information
        drug_df = pd.read_csv(file_drug_information)
        drug_df.drop(['Unnamed: 0', 'Unnamed: 0.1'], axis=1,inplace=True)
        drug_df.set_index("pubchem_id", inplace=True)
        # Reduce Memory Size by changing dtype of the columns
        for column in tqdm(drug_df.columns, ascii="Transform Drug Information"):
            if set(drug_df[column]).issubset({0, 1}):
                drug_df[column] = drug_df[column].astype(np.bool)
        drug_df = drug_df.to_sparse(fill_value=False)

    if includeCellFeatures:
        # Read Cell Line Information
        cell_df = pd.read_csv(file_cell_line_information)
        cell_df.drop(['Unnamed: 0'], axis=1,inplace=True)
        cell_df.set_index("cell_line_id", inplace=True)
        # Reduce Memory Size by changing dtype of the columns
        for column in tqdm(cell_df.columns, ascii="Transform Cell Line Information"):
            if set(cell_df[column]).issubset({0, 1}):
                cell_df[column] = cell_df[column].astype(np.bool)
            elif [x % 1 == 0 for x in set(cell_df[column])]:
                cell_df[column] = cell_df[column].astype(np.int8)
            else:
                print(column, set(cell_df[column]))
        cell_df = cell_df.to_sparse(fill_value=False)


    if includeCellFeatures and includeDrugFeatures:
        return pd.merge(df, drug_df, left_on="drug_id", right_index=True, validate="many_to_one", sort=False).merge(cell_df, left_on="cell_line", right_index=True, validate="many_to_one", sort=False).to_sparse(fill_value=False)
    elif includeCellFeatures:
        return pd.merge(df, cell_df, left_on="drug_id", right_index=True, validate="many_to_one", sort=False).to_sparse(fill_value=False)
    elif includeCellFeatures:
        return pd.merge(df, drug_df, left_on="drug_id", right_index=True, validate="many_to_one", sort=False).to_sparse(fill_value=False)
    else:
        return df