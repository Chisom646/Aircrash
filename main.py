import pandas as pd
import altair as alt
import streamlit as st
import numpy as np
# import needed libaries

def load_data():
    #import data
    df = pd.read_csv("aircrahesFullDataUpdated_2024.csv")
    #remove null values
    df = df.dropna()
    #to remove rows with "'-" and "10" as the Country/Region
    df = df[~df.isin(["'-"]).any(axis=1)]
    df = df[~df.isin(["10"]).any(axis=1)]
    return df

df = load_data()

## App title 
st.title("AirCraft Crashes")

#Calculations 
fatalities = df["Fatalities (air)"].sum()
Years = df["Year"].nunique()
Aboard = df["Aboard"].sum()
aircrafts = df["Aircraft"].nunique()
aircraft_manufacturer = df["Aircraft Manufacturer"].nunique()
operators = df["Operator"].nunique()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("No_of_Years", Years)
with col2:
    st.metric("No_of_People_Aboard", Aboard)
with col3:
    st.metric("No_of_Fatalities", fatalities)

col4, col5, col6 = st.columns(3)
with col4:
    st.metric("No_of_Aircraft_Manufacturers", aircraft_manufacturer)
with col5:
    st.metric("No_of_aircrafts_involved", aircrafts)
with col6:
    st.metric("No_of_operators", operators)


#create filters
filters = {
    "Year" : df['Year'].unique(),
    "Country/Region" : df["Country/Region"].unique(),
    "Aircraft Manufacturer" : df["Aircraft Manufacturer"].unique(),
    "Aircraft" : df["Aircraft"].unique(),
    "Location" : df["Location"].unique(),
    "Operator" : df["Operator"].unique()
}

#create selected filters
selected_filters = {}

#create a multi selcet widget
for key, option in filters.items():
    selected_filters[key] = st.sidebar.multiselect(key,option)

#copy the full data 
filtered_df = df.copy()

#apply filters on the data
for key, selected_values in selected_filters.items():
    if selected_values:
        filtered_df = filtered_df[filtered_df[key].isin(selected_values)]

#display the data
st.dataframe(filtered_df.head())


st.subheader("Years vs Number of Aircrashes for each Year_Group")

#group the years 
bins = [1908,1919,1930,1941,1952,1963,1974,1985,1996,2007,2018,2024]
labels = ["1908-1919","1920-1930","1931-1941","1942-1952","1953-1963","1964-1974","1975-1985","1986-1996","1997-2007","2008-2018","2019-2024"]
df["Group_Year"] = pd.cut(df["Year"],bins = bins,labels = labels)
data = df["Group_Year"].value_counts().sort_index()
data = data.reset_index()  
data.columns = ["Group_Year", "Count"]
#print the head of the data
st.write(data.head())
chart1 = alt.Chart(data).mark_bar(color = 'pink').encode(
    x = alt.X("Group_Year:O", title= "Group of  the years"),
    y = alt.Y("Count:Q", title = "Number of crashes for the years")
)
st.altair_chart(chart1 , use_container_width = True)

#the grouped years versus the number of deaths on air 
st.subheader("Years Vs Number of fatalites On Air")
data2 = df.groupby("Group_Year")["Fatalities (air)"].sum().reset_index()
data2.columns = ["Group_Year", "Counts"]

chart2 = alt.Chart(data2).mark_line(color = "brown").encode(
    x = alt.X("Group_Year" , title = "Group of Years"),
    y = alt.Y("Counts" , title = "Number of Fatalities")
)
st.altair_chart(chart2, use_container_width=  True)

#the grouped years versus the number of deaths on ground
st.subheader("Years Vs Number of fatalites On Ground")
data9 = df.groupby("Group_Year")["Ground"].sum().reset_index()
data9.columns = ["Group_Year", "Counts"]

chart9 = alt.Chart(data9).mark_line(color = "Pink").encode(
    x = alt.X("Group_Year" , title = "Group of Years"),
    y = alt.Y("Counts" , title = "Number of Fatalities")
)
st.altair_chart(chart9, use_container_width=  True)

# groupby quater 
st.subheader("amount of aircrashes in each quarter of the year ")
data3 = df["Quarter"].value_counts().reset_index()
data3.columns = ["Quarter","No_of_aircrash"]

chart3 = alt.Chart(data3).mark_bar(color = "brown").encode(
    x = alt.X("Quarter:O", title = "Quarters"),
    y = alt.Y("No_of_aircrash:Q", title = "Amount of aircrash")
)

st.altair_chart(chart3,use_container_width = True)

st.subheader("Quaters Vs Number of Aboard and Number of Fatalities")

#
d1 = df.groupby("Quarter")["Aboard"].sum().reset_index()
d2 = df.groupby("Quarter")["Fatalities (air)"].sum().reset_index()
merged_data = pd.merge(d1,d2,on = "Quarter")


# Reshape the merged data into long format
data4 = merged_data.melt(
    id_vars='Quarter',
    value_vars=['Aboard', 'Fatalities (air)'],
    var_name='Metric',
    value_name='Value'
)


# Grouped bar chart
chart4 = alt.Chart(data4).mark_bar(size=30).encode(
    x=alt.X('Quarter:N', title='Quarter'),
    y=alt.Y('Value:Q', title='Count'),
    color=alt.Color('Metric:N', title='Metric',scale=alt.Scale(domain=['Aboard', 'Fatalities (air)'],
                        range=['pink', 'brown'])),
    xOffset='Metric:N',  # This makes the bars appear side-by-side within each Quarter
    tooltip=['Quarter', 'Metric', 'Value']
).properties(
    width=400,
    height=300
)

st.altair_chart(chart4, use_container_width=True)

#
st.subheader("Months versus number of aircrashes")
data5 = df["Month"].value_counts().reset_index()
# Define proper month order
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

# Convert 'Month' column to categorical with correct order
data5['Month'] = pd.Categorical(data5['Month'], categories=month_order, ordered=True)

# Sort the DataFrame just to make sure it's in order
data5 = data5.sort_values('Month')

data5.columns = ["Month","Counts"]

chart5 = alt.Chart(data5).mark_line( color="pink").encode(
    x = alt.X("Month", title = "Months of the year", sort = month_order),
    y = alt.Y("Counts", title = "No of Aircrashes")
)
st.altair_chart(chart5,use_container_width = True)


#scatter plot
st.subheader("People Aboard Vs. No of Fatalities.")
data6 = df[["Aboard", "Fatalities (air)"]]
chart6 = alt.Chart(data6).mark_point(color = "brown").encode(
    x = alt.X("Aboard" , title = "Number of people aboard"),
    y = alt.Y("Fatalities (air)", title = "number of fatalities")
)
st.altair_chart(chart6,use_container_width= True)

# 

st.subheader("10 largest death in aircrafts with the number of people aboard and number of people who died on ground")
data7 = df["Aircraft"].value_counts().nlargest(10)
data7 = data7.to_frame(name="Count")

fatalities_sum = df.groupby("Aircraft")["Fatalities (air)"].sum()
ground_sum = df.groupby("Aircraft")["Ground"].sum()
people_aboard = df.groupby("Aircraft")["Aboard"].sum()
data7["fatalities(air)"] = fatalities_sum
data7["Ground"] = ground_sum
data7["Aboard"] = people_aboard

data7 = data7.reset_index().rename(columns={"index": "Aircraft"})

st.dataframe(data7)

data1 = data7.melt(
    id_vars = "Aircraft",
    value_vars= ["fatalities(air)","Ground","Aboard"],
    var_name = "Metric",
    value_name = "Value"
)

chart7 = alt.Chart(data1).mark_line().encode(
    x = alt.X('Aircraft', title='Aircrafts'),
    y=alt.Y('Value:Q', title='Count'),
    color=alt.Color('Metric:N', title='Metric',scale=alt.Scale(domain=['fatalities(air)',"Ground","Aboard"],
                        range=['pink', 'brown',"red"])),
    xOffset='Metric:N',  # This makes the bars appear side-by-side within each Quarter
    tooltip=['Aircraft', 'Metric', 'Value']
).properties(
    width=400,
    height=300
)

st.altair_chart(chart7, use_container_width=True)

st.subheader("The percentage of aircrash in each season.")
conditions = [
    df['Month'].isin(['March', 'April', 'May']),
    df['Month'].isin(['June', 'July', 'August']),
    df['Month'].isin(['September', 'October', 'November'])
]

# Define corresponding choices
choices = ['Spring', 'Summer', 'Autumn']

# Apply logic
df['Season'] = np.select(conditions, choices, default='Winter')

data8 = df["Season"].value_counts().reset_index()
data8 = data8.rename(columns={"index": "Season", "Season": "Counts"})


data8.columns = ['Season', 'Counts']

data8['Percentage'] = ((data8['Counts'] / data8['Counts'].sum()) * 100).round(2)

st.write(data8.head())

color_p =[ "#42A5F5","Orange" ,"#FFEB3B","#A8E6A1"]  
chart8 = alt.Chart(data8).mark_arc().encode(
    theta=alt.Theta(field="Counts", type="quantitative",stack="normalize"),
    color=alt.Color(field="Season", type="nominal",scale=alt.Scale(domain=data8['Season'].tolist(), range = color_p)),
    tooltip=["Season", "Counts","Percentage"]
)

st.altair_chart(chart8, use_container_width=True)

