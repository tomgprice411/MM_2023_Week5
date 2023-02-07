import pandas as pd


df = pd.read_csv("nyc_slice_rawdata.csv", encoding='cp1252')

df.head()
df.info()

#insert a '-' between the month and day of the date column and convert to a datetime
df["Date"] = df["Date"].apply(lambda x: x[:7]+ "-"+x[7:])
df["Date"] = pd.to_datetime(df["Date"])


#get the price on the most recent date for each pizzeria

#first only select plain pizza's, and only take the columsn we will need
df_plain = df.loc[df["Style"] == "Plain", ["Link to IG Post", "Name", "location_lat", "location_lng", "Date", "Year", "Price as number", "Style"]].copy()

#rank each pizzeria so that the most recent date has a rank of 1
df_plain["Date Rank"] = df_plain.sort_values(by = "Date", ascending = False).groupby(["Name"])["Date"].transform("rank")

#now filter only where the rank equals 1
df_plain_2 = df_plain.loc[df_plain["Date Rank"] == 1].copy()

