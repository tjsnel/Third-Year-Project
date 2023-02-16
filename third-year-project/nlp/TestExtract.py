import pandas as pd
from POSExtract import POSExtract

pos_extract = POSExtract(path="C:\\Users\\tommy\\OneDrive\\University\\Year 3\\"
         "Third Year Project\\Platform Album Data\\new_unigram_data.h5", ids=pd.Series([1]))

pos_extract.get_candidates()