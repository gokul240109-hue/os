from mlxtend.frequent_patterns import apriori
from mlxtend.preprocessing import TransactionEncoder
import pandas as pd

def mine_patterns(messages):
    transactions = [msg.split() for msg in messages]

    te = TransactionEncoder()
    te_array = te.fit(transactions).transform(transactions)
    df = pd.DataFrame(te_array, columns=te.columns_)

    frequent_patterns = apriori(df, min_support=0.3, use_colnames=True)
    return frequent_patterns.sort_values(by="support", ascending=False)
