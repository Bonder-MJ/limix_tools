import limix
import numpy as np
import pandas as pd
import re
from limix.varDecomp import VarianceDecomposition

def variance_decomposition(quant_df,metadata_df):

    #Drop rows with any NA values in the metadata_df
    metadata_df.dropna(inplace=True)
    
    selected_columns = list(metadata_df.columns)
    
    random_effect_dict = dict()
    for column_name in selected_columns:
        random_effect_mat = []
        for categorical_value in metadata_df[column_name]:
            random_effect_mat.append(metadata_df[column_name].map(lambda x : int(x==categorical_value)).values)
        random_effect_mat = np.array(random_effect_mat)
        random_effect_dict[column_name] = pd.DataFrame(data=random_effect_mat,index=metadata_df.index,columns=metadata_df.index)

    var_df = pd.DataFrame(index = quant_df.index,columns=selected_columns+['residual'])

    rel_var_columns = selected_columns+['residual']

    for idx,feature_id in enumerate(quant_df.index[:50]):
        if (idx%50==0):
            print idx
        phenotypes = quant_df.loc[feature_id,:].dropna()
        samples = list(set(phenotypes.index)&set(metadata_df.index))
        print rel_var_columns
        print phenotypes
        # variance component model
        vc = VarianceDecomposition(phenotypes.values)
        vc.addFixedEffect()
        for key in selected_columns:
            random_effect_matrix = random_effect_dict[key].loc[samples,samples].as_matrix()
            vc.addRandomEffect(K=random_effect_matrix)
        vc.addRandomEffect(is_noise=True)
        vc.optimize()
        var_data = vc.getVarianceComps()[0]
        print var_data
        var_dataseries = pd.Series(data=var_data,index=rel_var_columns)
        var_dataseries = var_dataseries/var_dataseries.sum()

        var_df.loc[feature_id,rel_var_columns] = var_dataseries
        
    return var_df
