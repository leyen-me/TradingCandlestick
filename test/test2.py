import pandas as pd

df = pd.read_csv('kline_data.csv')

def is_uptrend(df, idx, n=3):
    if idx < n:
        return False
    for i in range(idx-n, idx):
        if df.iloc[i]['close'] <= df.iloc[i]['open']:
            return False
    return True

def is_downtrend(df, idx, n=3):
    if idx < n:
        return False
    for i in range(idx-n, idx):
        if df.iloc[i]['close'] >= df.iloc[i]['open']:
            return False
    return True

def is_hammer_with_trend(row, idx, df):
    body = abs(row['close'] - row['open'])
    lower_shadow = min(row['open'], row['close']) - row['low']
    upper_shadow = row['high'] - max(row['open'], row['close'])
    is_hammer = (
        body < (row['high'] - row['low']) * 0.3 and
        lower_shadow > body * 2 and
        upper_shadow < body
    )
    return is_hammer and is_downtrend(df, idx)

def is_inverted_hammer_with_trend(row, idx, df):
    body = abs(row['close'] - row['open'])
    lower_shadow = min(row['open'], row['close']) - row['low']
    upper_shadow = row['high'] - max(row['open'], row['close'])
    is_inverted_hammer = (
        body < (row['high'] - row['low']) * 0.3 and
        upper_shadow > body * 2 and
        lower_shadow < body
    )
    return is_inverted_hammer and is_uptrend(df, idx)

df['is_hammer_with_trend'] = [
    is_hammer_with_trend(row, idx, df) for idx, row in df.iterrows()
]
df['is_inverted_hammer_with_trend'] = [
    is_inverted_hammer_with_trend(row, idx, df) for idx, row in df.iterrows()
]
print("锤子线:")
print(df[df['is_hammer_with_trend']])
print("倒锤线:")
print(df[df['is_inverted_hammer_with_trend']])