import numpy as np
import pandas as pd
import scipy.stats
import re
import scipy
import limix
from sklearn.preprocessing import Imputer

def generate_kinship(bed,fam,snp_idxs,iid_idxs,chunk_size=100000):
    assert(all([x in fam.index for x in iid_idxs]))

    fill_NaN = Imputer(missing_values=np.nan, strategy='mean', axis=0)

    nI = len(iid_idxs)
    K = np.zeros((nI,nI))
    
    nChunks = nI/chunk_size + 1
    snp_count = 0
    for idx in range(nChunks):
        start = idx*chunk_size
        stop = (idx+1)*chunk_size
        snp_idxs_subset = snp_idxs[start:stop]

        #limit snp_df to snp subset, and individual subset
        snp_df = pd.DataFrame(data=bed[snp_idxs_subset,:].compute().transpose(),index=fam.index,columns=snp_idxs_subset)
        snp_df = snp_df.loc[iid_idxs,:]

        #drop snps that are all na
        snp_df = snp_df.dropna(how='all',axis=0)
        #impute missing snps
        snp_df = pd.DataFrame(data=fill_NaN.fit_transform(snp_df),columns=snp_df.columns,index=snp_df.index)
        #remove snps that don't vary 
        std = snp_df.apply(np.std,axis=0)
        snp_df = snp_df.loc[:,std>0]
        #number of snps we're using after dropping some (should be close to chunk_size)
        snp_count += len(snp_df.columns)

        X = snp_df.values
        X -= X.mean(0)
        X /= X.std(0)
        Ktemp = X.dot(X.T)
        K += Ktemp

    K /= snp_count
    kinship_df = pd.DataFrame(data=K,index=iid_idxs,columns=iid_idxs)
    return kinship_df

