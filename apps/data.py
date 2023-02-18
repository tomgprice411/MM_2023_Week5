import pandas as pd


df = pd.read_csv("nyc_slice_rawdata.csv", encoding='cp1252')
df_images = pd.read_csv("instagram-data.csv", encoding='cp1252')

#insert a '-' between the month and day of the date column and convert to a datetime
df["Date"] = df["Date"].apply(lambda x: x[:7]+ "-"+x[7:])
df["Date"] = pd.to_datetime(df["Date"])

#attach the name of the jpg in the assets folder onto df_3
df = df.merge(df_images[["Url", "Image Name"]], left_on = "Link to IG Post", right_on = "Url", how = "left")

#first only select plain pizza's, and only take the columsn we will need
df_2 = df[["Link to IG Post", "Name", "location_lat", "location_lng", "Date", "Year", "Price as number", "Style", "Image Name"]].copy()

#rank each pizzeria so that the most recent date has a rank of 1
df_2["Date Rank"] = df_2.sort_values(by = "Date", ascending = False).groupby(["Name", "Style"])["Date"].transform("rank")

#now filter only where the rank equals 1
df_3 = df_2.loc[df_2["Date Rank"] == 1].copy()

#re categorise the style
df_3["Style_Renamed"] = df_3["Style"]
df_3.loc[df_3["Style"] != 'Plain', "Style_Renamed"] = 'Other'


#add colours for each style (plain or other)
df_3["Colour"] = "#BA4A00"
df_3.loc[df_3["Style"] == "Plain", "Colour"] = "#D4AC0D"

#add in the size of the markers depending upon the price
df_3["Price size"] = 25
df_3.loc[(df_3["Price as number"] < 3) & (df_3["Price as number"] >= 2), "Price size"] = 15
df_3.loc[(df_3["Price as number"] < 4) & (df_3["Price as number"] >= 3), "Price size"] = 10
df_3.loc[(df_3["Price as number"] >= 4), "Price size"] = 5

#add in the label for the price range
df_3["Price range"] = "Under $2"
df_3.loc[(df_3["Price as number"] < 3) & (df_3["Price as number"] >= 2), "Price range"] = "$2-3"
df_3.loc[(df_3["Price as number"] < 4) & (df_3["Price as number"] >= 3), "Price range"] = "$3-4"
df_3.loc[(df_3["Price as number"] >= 4), "Price range"] = "$4 and over"


