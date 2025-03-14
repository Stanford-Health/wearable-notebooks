# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# + [markdown] id="JqgX4MYtGuDF"
# # Fitbit Charge 6: Guide to data extraction and analysis

# + [markdown] id="HOCO7bMFIgrP"
# <img src="https://imgur.com/nR08yax.png" width="300">
#
# _A picture of the Fitbit Charge 6 that was used for this notebook_

# + [markdown] id="ofW3O4rMJKvI"
# The Fitbit Charge 6 is a new version of the Fitbit Charge series. We have covered the data extraction and analysis for the Fitbit Charge 4 in [this notebook](https://github.com/Stanford-Health/wearable-notebooks/blob/main/notebooks/fitbit_charge_4.ipynb), and you can extract any data that you can extract from the Fitbit Charge 4, also from the Fitbit Charge 6!
#
# What we will be covering in this notebook will be **intraday** data specifically. Here is a list of high frequency data that can be extracted from any Fitbit watch.
#
# Data | Frequency of Sampling
# :-------------------:|:----------------------:
# intraday_breath_rate | per sleep
# intraday_active_zone_minute | per minute
# intraday_activity | per minute
# heart_rate | per second
# intraday_hrv | per 5 minutes during sleep
# intraday_spo2 | per minute during sleep
#
# In this guide, we sequentially cover the following **nine** topics to extract data from the Fitbit API:
#
#
# 1. **Setup**
#     - 1.1: Data receiver setup
#     - 1.2: Study participant setup
#     - 1.3: Library imports
# 2. **Authentication and Authorization**
# 3. **Data Extraction**
#     - Select the dates to extract data
# 4. **Data Exporting**
#     - We export all of this data to CSV, Excel and JSON
# 5. **Adherence**
#     - We detect when the user isn't using the device by plotting a block plot
# 6. **Visualization**
#     - We create a simple plot to visualize our data.
# 7. **Advanced Visualization**
#     - 7.1: Replicating a graph of heart rate over time in the app
# 8. **Outlier Detection and Data Cleaning**
#     - We detect outliers in our data and filter them out.
# 9. **Statistical Data Analysis**
#     - 9.1: Sleep apnea detection from SPO2 and breathing rate during sleep
#     - 9.2: Distribution of breathing rates during different stage of sleep
#
#
# *Note: Full documentation of APIs by Fitbit can be found [here](https://dev.fitbit.com/build/reference).

# + [markdown] id="wjmrdIMbMyIb"
# # 1. Setup
# ## 1.1 Data Receiver Setup
#
# Please follow the below steps:
#
# 1. Create an email address for the participant, for example `foo@email.com`.
# 2. Create a Fitbit account with the email `foo@email.com` and some random password.
# 3. Keep `foo@email.com` and password stored somewhere safe.
# 4. Distribute the device to the participant and instruct them to follow the participant setup letter in section 1.2.
#
# To extract data from the Fitbit, you will first need to log in to the fitbit account at [https://dev.fitbit.com/login](https://dev.fitbit.com/login) by using the email and password that you registered. Click "REGISTER AN APP" on the menu bar, which should lead you to the application form.
#
# For redirect url where you will receive the access token, you can fill in the local host https://127.0.0.1/8080, but any redirect url should work fine. **To access intraday data without additional request forms, select OAuth 2.0 Application Type to be "Personal".** Other entries can be filled in without particular specifications. An example is shown below.
#
# <img src="https://imgur.com/ATwWvA8.png" width="600">
#
# After you have agreed to the terms of service and clicked register, you should be able to see your client id and client secrete in "Applications I registered":
#
# <img src="https://imgur.com/qnSnvud.png" width="600">
#
# Your client id and client secret will be needed to obtain the access token as described in section 2.
#
# ## 1.2 Study Participant setup
# Dear participant,
#
# Please start by charging the watch and connecting it to your account. Your login credentials should be provided by the research coordinator. Please download the Fitbit app from the appstore/playstore and start using your Fitbit. Remember to sync the device every few days. Otherwise, the collected high frequency data will be converted to low frequency summary for certain data types.
#
# Best,
#
# Wearipedia
#
# ## 1.3 Library imports
#
# Now that we have the Fitbit and application setup, we can start using wearipedia to extract and simulate data. We will start by importing `wearipedia` itself.

# + colab={"base_uri": "https://localhost:8080/"} id="KmeBDcKDDW_f" outputId="67753c51-a4f4-451d-bbcb-dc344cd52860"
# # !pip3.11 install git+https://github.com/stefren/wearipedia@fitbit-updates
import wearipedia

# + [markdown] id="fExIpAE3OjbV"
# Next, we will import all other necessary libraries. These include `matplotlib` for graph plotting, `pandas`, `numpy`, `scipy` for data processing and statistical analysis.

# + id="3Xon7tWfG0Jc"
import base64
import hashlib
import html
import json
import os
import re
import urllib.parse
import requests
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.covariance import EllipticEnvelope
import seaborn as sns
from scipy import stats
from scipy.ndimage import gaussian_filter
import numpy as np

# + [markdown] id="iew5gUfjSHHc"
# # 2. Authentication and Authorization
#
# In this section, we will cover user authentication with `wearipedia`. First you will need your client id and client secret from section 1.1.

# + id="QIuaj_F_SaSW"
#@title Insert client_id and client_secret

CLIENT_ID = "23Q3WK" #@param {type:"string"}
CLIENT_SECRET = "4ed2de2da7157c5fbaeadff8e785285d" #@param {type:"string"}
auth_creds = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}

# + [markdown] id="VBKfg77USmmx"
# Next, you can specify the start date and end date of the data that you would like to extract (or simulate).

# + id="2eNx1aBOTDFJ"
#@title Enter start date and end data for data extraction/simulation

START_DATE = "2024-11-01" #@param {type:"string"}
END_DATE = "2024-11-30" #@param {type:"string"}
params = {"seed": 100, "start_date": START_DATE, "end_date": END_DATE, "single_date": "2024-11-10"}

# + [markdown] id="g9aT8ziSTLEA"
# Now, we will initialize the device object for the Fitbit Charge 6. We will also specify if we will use real data. Check the box if you would like to use synthetic data instead of real data.
#
# *If you choose to use real data*, running the cell below should prompt you to click on an url. This will redirect you to your redirect url that you have chosen when you registered for an app. Please check all boxes to access all available data. Afterwards, copy the url in the address bar and paste in the box below.
#
# <img src="https://imgur.com/Hh8Jbaz.png" width="400">
#
#
#

# + id="JY3xEIOsF3MS"
device = wearipedia.get_device("fitbit/fitbit_charge_6")

synthetic = False #@param {type:"boolean"}
if not synthetic:
  # If the data is not synthetic, authenticate using the access token
  device.authenticate(auth_creds)

# + [markdown] id="wRQ1S6WWUzK_"
# # 3. Data Extraction
#
# Now we are ready to extract data from the Fitbit device. To extract data, simply call the `get_data` function with the data type you would like to extract. The types of intraday data available are `"intraday_breath_rate"`, `"intraday_active_zone_minute"`, `"intraday_activity"`, `"heart_rate"`, `"intraday_hrv"` and `"intraday_spo2"`.
#
# Since intraday data is high frequency data, there is a lot of data to be extracted/generated. It should take a while for the data to be retreived.

# + id="YDkjW7BJGLyQ"
br = device.get_data("intraday_breath_rate", params)
azm = device.get_data("intraday_active_zone_minute", params)
# activity = device.get_data("intraday_activity", params)
hr = device.get_data("intraday_heart_rate", params)
hrv = device.get_data("intraday_hrv", params)
spo2 = device.get_data("intraday_spo2", params)

# + [markdown] id="O2Q47VdvXDIA"
# Let's take a look at the data that is extracted! As an example, the active zone minute (azm) has the following format. Other data types also follow a similar dictionary format.

# + colab={"base_uri": "https://localhost:8080/"} id="PC_DBqw8GOgA" outputId="fbbb51a2-70fc-4530-83ff-3ae300110932"
azm

# + [markdown] id="_Z5B8M5w50Aw"
# At first glance, we can see that this dictionary contains some information about cardio active zone minutes, active zone minutes, and their corresponding recorded time during the day. Each minute, the fitbit determines if the user is in fat burn, cardio, or peak heart rate zone, and convert it into "active zone minutes". activeZoneMinutes is simply a total count of active zone minutes earned. For more information, you can refer to the fitbit web API [active zone minute endpoint description](https://dev.fitbit.com/build/reference/web-api/intraday/get-azm-intraday-by-date/).
#
# Although the data looks a bit messy, it is important to understand the structure of the extracted data so that we can reorganize it into a format we want (we will demonstrate organizing the data into dataframes in upcoming sections).

# + colab={"base_uri": "https://localhost:8080/"} id="Cl63vZV352bm" outputId="df2d7cfa-e5e7-4585-b0ba-6045fc91b021"
print(f"Number of days with azm recorded: {len(azm)}")

# + colab={"base_uri": "https://localhost:8080/"} id="ts4iCSAN8Imi" outputId="38f74a49-0d68-47ef-d6c8-ae37c8d31b87"
# For the i-th day, the dictionary containing the AZM data can be access via azm[i]['activities-active-zone-minutes-intraday'][0]
# Let's look at the data for the first day!

azm[0]['activities-active-zone-minutes-intraday'][0]

# + [markdown] id="fB__dYEp_48E"
# The above dictionary has two keys -- `'dateTime'` and `'minutes'`. `'dateTime'` contains the date of the AZM data, and `'minutes'` is a list of dictionaries, each containing the AZM information and the minute during the daya at which it was recorded.

# + [markdown] id="OcClr8tMXHz4"
# # 4. Data Exporting
#
# In this section, we export all of this data to JSON, which with popular scientific computing software (R, Matlab). We export each datatype separately and also export a complete version that includes all simultaneously.

# + cellView="form" id="_8EsdRzSXCvg"
import json

#@title Select which format to export data

# set which format you prefer to export
use_JSON = True #@param {type:"boolean"}
use_CSV = True #@param {type:"boolean"}
use_Excel = True #@param {type:"boolean"}

if use_JSON:

  json.dump(br, open("br.json", "w"))
  json.dump(azm, open("azm.json", "w"))
  json.dump(activity, open("activity.json", "w"))
  json.dump(hr, open("hr.json", "w"))
  json.dump(hrv, open("hrv.json", "w"))
  json.dump(spo2, open("spo2.json", "w"))

  complete = {
      "br": br,
      "azm": azm,
      "activity": activity,
      "hr": hr,
      "hrv": hrv,
      "spo2": spo2,

  }

  json.dump(complete, open("complete.json", "w"))

if use_CSV:
  pd.DataFrame(br).to_csv("br.csv", index=False)
  pd.DataFrame(azm).to_csv("azm.csv", index=False)
  pd.DataFrame(activity).to_csv("activity.csv", index=False)
  pd.DataFrame(hr).to_csv("hr.csv", index=False)
  pd.DataFrame(hrv).to_csv("hrv.csv", index=False)
  pd.DataFrame(spo2).to_csv("spo2.csv", index=False)


if use_Excel:
  pd.DataFrame(br).to_excel("br.xlsx", index=False)
  pd.DataFrame(azm).to_excel("azm.xlsx", index=False)
  pd.DataFrame(activity).to_excel("activity.xlsx", index=False)
  pd.DataFrame(hr).to_excel("hr.xlsx", index=False)
  pd.DataFrame(hrv).to_excel("hrv.xlsx", index=False)
  pd.DataFrame(spo2).to_excel("spo2.xlsx", index=False)


# + [markdown] id="0JtuU63rxRZX"
# # 5. Data Adherence
#
# In this section, we will simulate non-adherence over long periods of time. We will demonstrate this with the heart rate data. First, we will have to extract the time and corresponding heart rate value from our raw json format.

# + id="WvzvbEn0yLjF"
from datetime import datetime

results = []

for record in hr:
    date_str = record["heart_rate_day"][0]["activities-heart"][0]["dateTime"]
    dataset = record["heart_rate_day"][0]["activities-heart-intraday"]["dataset"]

    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

    for entry in dataset:
        time_str = entry["time"]
        heart_rate_value = entry["value"]

        time_obj = datetime.strptime(time_str, "%H:%M:%S").time()

        date_time = datetime.combine(date_obj, time_obj)

        results.append([date_time, heart_rate_value])

df = pd.DataFrame(results, columns=["datetime", "heart_rate"])
df['datetime'] = pd.to_datetime(df['datetime'])

# + colab={"base_uri": "https://localhost:8080/", "height": 424} id="hWUHqR0b2GyV" outputId="d3f4ace3-c4f6-4b7c-fb0b-0c149b28e2de"
df

# + [markdown] id="c0FgPHlH_2wJ"
# Since our simulated data has data entries for all timesteps, in order to simulate non-adherence, we will randomly select a portion of data to be None. We will first select 30% of the dates among all dates in the dataframe on which non-adherence occurs.

# + id="qx7VGb112sZ9"
seed_value = 42
np.random.seed(seed_value)

unique_dates = df['datetime'].dt.date.unique()
selected_dates = np.random.choice(unique_dates, size=int(len(unique_dates) * 0.3), replace=False)

# + [markdown] id="c1sK0Vjx6s1_"
# In order for the nonadherence to be realistic, we will select random intervals that are hours long where there is no data recorded -- instead of random entries -- to be `None` (after all, the user won't take of the watch for one second and put on the watch another second!).

# + id="KFeosZau7ueu"
import random

random.seed(seed_value)

def create_random_intervals(date):
    intervals = []
    num_intervals = random.choice([1, 2])
    for _ in range(num_intervals):
        start_hour = random.randint(0, 23)
        start_minute = random.randint(0, 59)
        start_second = random.randint(0, 59)
        start_time = pd.Timestamp(date) + pd.Timedelta(hours=start_hour, minutes=start_minute, seconds=start_second)

        duration_hours = random.randint(0, 5)
        duration_minutes = random.randint(0, 59)
        duration_seconds = random.randint(0, 59)
        end_time = start_time + pd.Timedelta(hours=duration_hours, minutes=duration_minutes, seconds=duration_seconds)

        intervals.append((start_time, end_time))
    return intervals


# + id="6T5P1NsL70Nu"
intervals_to_nullify = []
for date in selected_dates:
    intervals_to_nullify.extend(create_random_intervals(date))

intervals_to_nullify = [(pd.Timestamp(start), pd.Timestamp(end)) for start, end in intervals_to_nullify]

# + [markdown] id="qJsBPaPv76RO"
# Since in the real data, the fitbit doesn't record when the user is not using the watch, in our synthetic we will delete those rows which have value `None`.

# + id="cijbizZaHwgu"
non_adherence_df = df.copy()
for start_time, end_time in intervals_to_nullify:
    non_adherence_df = non_adherence_df[(non_adherence_df['datetime'] < start_time) | (non_adherence_df['datetime'] > end_time)]

# + id="v6IQSUuVt7x1"
date_range = pd.date_range(start=START_DATE, end=END_DATE + " 23:59:59", freq='S')

# Reindex non_adherence_df using the complete date range
non_adherence_df = non_adherence_df.set_index('datetime').reindex(date_range).reset_index()

# Replace NaN values in heart_rate with None
non_adherence_df['heart_rate'] = non_adherence_df['heart_rate'].apply(lambda x: None if pd.isna(x) else x)

# Reset column names if needed
non_adherence_df.columns = ['datetime', 'heart_rate']

# + [markdown] id="W1vS6lKmGtMT"
# Next, we can specify the start date and end date to visualize. We will also plot a block plot to visualize the dates and times of when the user had used the watch.
#
# To plot the block plot, we plot a value of 1 if a valid heart rate value is recorded. Otherwise, we plot a value of 0.

# + colab={"base_uri": "https://localhost:8080/", "height": 573} id="-Wu7ou6NHKmK" outputId="96d7c008-d518-4c4b-d4fe-429a09297aca"
VISUAL_START_DATE = "2024-01-17" #@param {type:"string"}
VISUAL_END_DATE = "2024-01-19" #@param {type:"string"}

visual_start_date = pd.to_datetime(VISUAL_START_DATE)
visual_end_date = pd.to_datetime(VISUAL_END_DATE)

selected_rows = non_adherence_df[(non_adherence_df['datetime'] >= visual_start_date) &
                                 (non_adherence_df['datetime'] < visual_end_date)]

# Replace heart rate: 1 if not NaN, otherwise 0 using .loc and .copy()
selected_rows_copy = selected_rows.copy()
selected_rows_copy['heart_rate'] = selected_rows_copy['heart_rate'].apply(lambda x: 1 if pd.notna(x) else 0)

# Plot a block plot
plt.figure(figsize=(12, 6))
plt.plot(selected_rows_copy['datetime'], selected_rows_copy['heart_rate'], drawstyle='steps-post', color='blue')
plt.title('Heart Rate Non-Adherence Block Plot')
plt.xlabel('Datetime')
plt.ylabel('Heart Rate (1: Present, 0: NaN)')
plt.grid(True)
plt.show()

# + [markdown] id="jpkiE-K2_Zih"
# # 6. Visualization
#
# In this section, we will be visualizing our three kinds of data in a simple, customizable plot! This plot is intended to provide a starter example for plotting, whereas later examples emphasize deep control and aesthetics.
#
# Similar to the previous section, we would first have to reorganize our raw JSON format data.

# + id="t4ZMA92v99UN"
# Reorganize heart rate data
hr_df = df.copy()

# Reorganize breath rate data
extracted_data = []
for entry in br:
    for br_entry in entry['br']:
        row = {
            'datetime': br_entry['dateTime'],
            'deepSleepSummary': br_entry['value']['deepSleepSummary']['breathingRate'],
            'remSleepSummary': br_entry['value']['remSleepSummary']['breathingRate'],
            'fullSleepSummary': br_entry['value']['fullSleepSummary']['breathingRate'],
            'lightSleepSummary': br_entry['value']['lightSleepSummary']['breathingRate']
        }
        extracted_data.append(row)

br_df = pd.DataFrame(extracted_data)
br_df['datetime'] = pd.to_datetime(br_df['datetime'])

# Reorganize hrv data
rmssd_data = []
for entry in hrv:
    for hrv_entry in entry['hrv']:
        for minute_entry in hrv_entry['minutes']:
            rmssd_data.append({'minute': minute_entry['minute'], 'rmssd': minute_entry['value']['rmssd']})

rmssd_df = pd.DataFrame(rmssd_data)
rmssd_df['minute'] = pd.to_datetime(rmssd_df['minute'])

lf_hf_data = []
for entry in hrv:
    for hrv_entry in entry['hrv']:
        for minute_entry in hrv_entry['minutes']:
            lf_hf_data.append({'minute': minute_entry['minute'], 'lf': minute_entry['value']['lf'], 'hf': minute_entry['value']['hf']})

lf_hf_df = pd.DataFrame(lf_hf_data)
lf_hf_df['minute'] = pd.to_datetime(lf_hf_df['minute'])

# Reorganize spo2 data
minute_value_data = []
for entry in spo2:
    for minute_entry in entry['minutes']:
        minute_value_data.append({'minute': minute_entry['minute'], 'value': minute_entry['value']})

spo2_df = pd.DataFrame(minute_value_data)
spo2_df['minute'] = pd.to_datetime(spo2_df['minute'])

# + [markdown] id="CfnB5qggJXy7"
# We will plot graphs to visualize the following data:
# - Heart rate (per second)
# - Heart rate variability (hrv) in terms of Root Mean Square of Successive Differences (RMSSD)
# - Heart rate variability (hrv) in terms of the power in interbeat interval fluctuations within the low frequency band and high frequency band ([see description from Fitbit web api](https://dev.fitbit.com/build/reference/web-api/intraday/get-hrv-intraday-by-date/))
# - SPO2 (per minute during sleep)
# - Average breathing rate during each sleep stage (per sleep).
#
# Here, you can specify the visualization start date and end date.

# + id="l3OMe3_8AU9Q" jupyter={"outputs_hidden": true}
VISUALIZATION_START_DATE = "2024-01-10" #@param {type:"string"}
VISUALIZATION_END_DATE = "2024-01-17" #@param {type:"string"}

visualization_start_date = pd.to_datetime(VISUALIZATION_START_DATE)
visualization_end_date = pd.to_datetime(VISUALIZATION_END_DATE)

# + id="6QclYBE4AVk7"
selected_hr_df = hr_df[(hr_df['datetime'] >= visualization_start_date) & (hr_df['datetime'] < visualization_end_date)]
selected_br_df = br_df[(br_df['datetime'] >= visualization_start_date) & (br_df['datetime'] < visualization_end_date)]
selected_rmssd_df = rmssd_df[(rmssd_df['minute'] >= visualization_start_date) & (rmssd_df['minute'] < visualization_end_date)]
selected_lf_hf_df = lf_hf_df[(lf_hf_df['minute'] >= visualization_start_date) & (lf_hf_df['minute'] < visualization_end_date)]
selected_spo2_df = spo2_df[(spo2_df['minute'] >= visualization_start_date) & (spo2_df['minute'] < visualization_end_date)]

# + cellView="form" colab={"base_uri": "https://localhost:8080/", "height": 573} id="yPPBIC8HKpwo" outputId="19db5f64-e718-42a0-afd6-9a33cb2ac912"
#@title Select the data to plot

feature = "hrv (lf and hf)" #@param ["heart rate", "breathing rate", "hrv (rmssd)", "hrv (lf and hf)", "spo2"]

if feature == "heart rate":
  plt.figure(figsize=(15, 6))
  plt.grid(True)
  plt.scatter(selected_hr_df['datetime'], selected_hr_df['heart_rate'], color='red', s=0.1, alpha=0.7)
  plt.title('Heart Rate Over Time')
  plt.xlabel('Datetime')
  plt.ylabel('Heart Rate')
  plt.ylim(0, 225)

  plt.show()
elif feature == "breathing rate":
  plt.figure(figsize=(15, 6))

  for column in selected_br_df.columns[1:]:
      plt.plot(selected_br_df['datetime'], selected_br_df[column], label=column)

  plt.title('Breath rate on selected dates')
  plt.xlabel('Date')
  plt.ylabel('Breathing rate')
  plt.xticks(rotation=45)
  plt.ylim(0, 25)
  plt.legend()
  plt.grid(True)
  plt.tight_layout()
  plt.show()
elif feature == "hrv (rmssd)":
  plt.figure(figsize=(15, 6))
  plt.scatter(selected_rmssd_df['minute'], selected_rmssd_df['rmssd'], color='red', s=0.5)
  plt.title('HRV (RMSSD) Over Time')
  plt.xlabel('Datetime')
  plt.ylabel('RMSSD')
  plt.ylim(0, 100)
  plt.grid(True)
  plt.show()
elif feature == "hrv (lf and hf)":
  plt.figure(figsize=(15, 6))
  for band in ["lf", "hf"]:
    if band == "hf":
      color = "red"
    else:
      color = "green"
    plt.scatter(selected_lf_hf_df['minute'], selected_lf_hf_df[band], color=color, s=0.5, label=band)

  plt.legend()
  plt.title('HRV (lf and hf) Over Time')
  plt.xlabel('Datetime')
  plt.ylabel('Power (ms^2)')
  plt.ylim(0, 1200)
  plt.grid(True)
  plt.show()
else:
  plt.figure(figsize=(15, 6))
  plt.scatter(selected_spo2_df['minute'], selected_spo2_df['value'], color='blue', s=0.1)
  plt.title('SPO2 Over Time')
  plt.xlabel('Datetime')
  plt.ylabel('SPO2 (%)')
  plt.ylim(90, 100)
  plt.grid(True)
  plt.show()



# + [markdown] id="QXGeE9HDSW38"
# # 7. Advanced Visualization
#
# In this section, we will try more advanced data visualization, by replicating some plots from the fitbit. This will more manual adjustments for positioning texts, customizing colors, etc.
#
# ## 7.1 Heart rate in a day
#
# Here we are going to try replicating this plot of heart rate versus time in the day from the fitbit app. The main feature is that the plot indicates the heart rate zone the time intervals during the day corresponds to. It provides a visual representation of how heart rate varies throughout the day. This can reveal patterns such as spikes during exercise, dips during sleep, or variations in response to stress or activity.
#
# <img src="https://imgur.com/Goz1UD2.png" width="300">

# + id="7_tumXHMKXND"
from datetime import timedelta

DAY = "2024-01-20"
vis_day = pd.to_datetime(DAY)
vis_end_day = vis_day + timedelta(days = 1)
DAY_hr_df = hr_df[(hr_df['datetime'] >= vis_day) & (hr_df['datetime'] < vis_end_day)]
DAY_hr_df = DAY_hr_df.reset_index(drop=True)

DAY_hr_df['datetime'] = pd.to_datetime(DAY_hr_df['datetime'])

specific_times = ['00:00:00', '06:00:00', '12:00:00', '18:00:00', '23:59:00']

time_stamps = [pd.to_datetime(f"{DAY} {time}") for time in specific_times]

# + colab={"base_uri": "https://localhost:8080/", "height": 564} id="T5SH5nYZLWAg" outputId="d0b00839-16c8-44d6-a124-f1c00d3d0be3"
with plt.style.context('dark_background'):
    # Creating the plot
    fig, ax = plt.subplots()
    fig.set_size_inches(3, 5.5)
    plt.plot(DAY_hr_df['datetime'], DAY_hr_df['heart_rate'], color='#4DC3C3', lw=0.5)

    fig.patch.set_facecolor('#097194')
    plt.gca().set_facecolor('#097194')

    # Adjusting the labels
    plt.xticks(ticks=time_stamps, labels=['12', '6', '12PM', '6', '12'])
    plt.ylim(top=200, bottom=40)

    # Removing the borders from four sides
    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)

    # Adjust tick sizes
    plt.tick_params(axis='x', labelsize=8)
    plt.tick_params(axis='y', labelsize=8)

    # Adding labels
    plt.figtext(0.5, 1.0, "Jan 20, 2024", fontsize=14, ha='center', color='w')
    plt.figtext(0.5, 0.96, 'Beats Per Minute', fontsize=14, ha='center', color='w', fontweight='bold')

    for i in range(len(DAY_hr_df) - 1):
        hr = DAY_hr_df.iloc[i]['heart_rate']
        hr_next = DAY_hr_df.iloc[i + 1]['heart_rate']
        time = DAY_hr_df.iloc[i]['datetime']
        time_next = DAY_hr_df.iloc[i + 1]['datetime']

        if 110 <= hr <= 136:
            color = 'yellow'
        elif 136 < hr <= 169:
            color = 'orange'
        elif hr > 169:
            color = 'red'
        else:
            color = '#4DC3C3'

        plt.plot([time, time_next], [hr, hr_next], color=color, lw=0.5)

    # Adding the legend with colored squares
    legend_labels = ['Fat Burn', 'Cardio', 'Peak']
    legend_colors = ['yellow', 'orange', 'red']
    y_position = 0.92
    x_positions = [0.20, 0.45, 0.65]
    square_size = 9

    for i, (label, color) in enumerate(zip(legend_labels, legend_colors)):
        plt.figtext(x_positions[i], y_position + 0.01, '■', fontsize=square_size, color=color, va='center')
        plt.figtext(x_positions[i] + 0.05, y_position, label, fontsize=9, ha='left', color='w', fontweight='light')

    plt.show()

# + [markdown] id="28lf9pkpT1Av"
# # 8. Outlier Detection and Data Cleaning
#
# In data analysis, outliers are data points that significantly differ from the rest. They might indicate measurement variability or errors. For BPM data, outliers could signal physiological anomalies, errors, or artifacts.
# Unconditional Outlier Detection, $P(\text{BPM})$
#
# This approach examines each BPM measurement independently. It aims to identify data points that deviate substantially from the overall BPM distribution, without considering time sequence.
# ### Unconditional Outlier Detection:
#
# #### Standard Deviation Method:
#
# - Assumes BPM values follow a normal distribution.
# - Identifies values beyond a certain number of standard deviations from the mean as outliers.
# - Typically uses a cutoff between 1 and 4 standard deviations.
#
# #### Interquartile Range (IQR) Method:
# - Doesn't assume normal data distribution.
# - Computes IQR between the 25th and 75th percentiles.
# - Considers data points below $\text{Q1} - 1.5\times\text{IQR}$ or above $\text{Q3} + 1.5\times\text{IQR}$ as outliers.
#
# ### Conditional Outlier Detection, $P(\text{BPM}_{t}\mid\text{BPM}_{t-1})$
#
# This method evaluates each BPM reading considering its preceding value. This is important because BPM values are correlated over time, especially in short intervals like 10 seconds.
# Methods for Conditional Outlier Detection:
#
# #### Change Detection:
# - Calculates the difference between consecutive BPM readings.
# - Identifies significant deviations from the expected fluctuation range as outliers.
#
# #### Time Series Analysis:
# - Advanced methods like ARIMA model BPM time series to predict future values.
# - Identifies outliers as readings significantly different from the model's predictions.
#
# ### Assumptions and Calculations
#
# The choice of outlier detection method depends on certain assumptions. For example, the standard deviation method assumes a normal distribution of BPM values. Whether to use a conditional or unconditional method depends on the influence of preceding data on the current value.
#
# For BPM data, considering its sequential nature, conditional methods may be more insightful. They can reveal sudden physiological changes or errors manifested as abrupt BPM spikes.
#
# The mathematics behind conditional outlier detection may involve calculating BPM changes between successive readings:
#
# $\Delta \text{BPM}_t = \text{BPM}_t - \text{BPM}_{t-1}$
#
# Then, a threshold is established based on the standard deviation of these changes:
#
# $Threshold = Mean(\Delta \text{BPM}) \pm k \times StdDev(\Delta \text{BPM})$,
#
# where $k$ represents the number of standard deviations to consider.
#
# The idea is that while BPM can naturally vary from one reading to the next, extreme changes within a brief interval are unexpected unless due to an unusual event or error.
#
#
# Since we have high frequency heart rate data, we will use conditional outlier detection.
#
# #### Step 1: Inject some anomalies
#
# Since our synthetic data resembles a health adult, we would have to inject some anomalies to the data.

# + id="IGMU7rZcss7e"
from datetime import timedelta

VIS_START_DATE = "2024-01-18" #@param {type:"string"}
vis_start_date = pd.to_datetime(VIS_START_DATE)
vis_end_date = vis_start_date + timedelta(days = 1)
day_hr_df = hr_df[(hr_df['datetime'] >= vis_start_date) & (hr_df['datetime'] < vis_end_date)]

# Randomly select 1% of rows in day_hr_df
sample_size = int(len(day_hr_df) * 0.00005)
sampled_rows = day_hr_df.sample(n=sample_size)

# Define the list of possible heart rate values
heart_rate_values = [80, 82]

# Assign random heart rate values to the selected rows
sampled_rows['heart_rate'] = np.random.choice(heart_rate_values, size=sample_size)

# Update the original DataFrame with the modified rows
day_hr_df.loc[sampled_rows.index, 'heart_rate'] = sampled_rows['heart_rate']


# + [markdown] id="edMRD548sZup"
# #### Step 2: Calculate the Differences Between Consecutive Measurements
#
# Second, we will calculate the differences between consecutive measurements. Since we have quite a lot of data, we will demonstrate this outlier detection with just one day of data.

# + id="J6mK1EBDOijS"
# Create a copy of the DataFrame
day_hr_df_copy = day_hr_df.copy()

# Add the 'hr_diff' column to the copy
day_hr_df_copy['hr_diff'] = day_hr_df['heart_rate'].diff()

# Update the original DataFrame with the modified copy
day_hr_df = day_hr_df_copy


# + colab={"base_uri": "https://localhost:8080/", "height": 424} id="IWvO-RZlqOPw" jupyter={"outputs_hidden": true} outputId="06b16029-1445-468b-a279-31b59c684fd3"
day_hr_df

# + [markdown] id="aA_ZA_0OoTN9"
# #### Step 2: Establish a Statistical Threshold
#
# The threshold is calculated by multiplying the standard deviation of the BPM differences by a factor. This factor is chosen to capture the most extreme variations, which are less probable to occur naturally.

# + colab={"base_uri": "https://localhost:8080/"} id="4NjC3jwKnr6s" outputId="c7c0c6b1-d653-4c0a-8ad0-041737452bb4"
# Calculate the standard deviation and mean of the differences
mean_diff = day_hr_df["hr_diff"].mean()
std_diff = day_hr_df["hr_diff"].std()

# Set a threshold for detecting outliers, typically between 1 and 4 standard deviations
threshold = 4 * std_diff
threshold

# + [markdown] id="tqp4pQZnoeQn"
# #### Step 3: Identify Conditional Outliers
#
# This step filters the data to find instances where the absolute value of the HRV difference exceeds our threshold, suggesting an unusual and abrupt change in BPM.

# + id="Tb6IEcbXojJg"
# Identify where the difference exceeds the threshold
conditional_outliers = day_hr_df[abs(day_hr_df['hr_diff']) > threshold]

# + [markdown] id="4G1X5gxvorK1"
# #### Step 4: Visualize Outliers
#
# Visualization is crucial as it provides an immediate sense of where outliers occur in the dataset, offering insights into their potential causes and implications.

# + colab={"base_uri": "https://localhost:8080/", "height": 573} id="igmiiB0Zoqvy" outputId="5c05c970-46f4-4b39-86c5-810cb43a1a47"
# Plot HRV data with conditional outliers highlighted
plt.figure(figsize=(10, 6))
plt.plot(day_hr_df['heart_rate'], label='heart rate data', alpha=0.7)
plt.scatter(conditional_outliers.index, conditional_outliers['heart_rate'], color='r', label='Conditional Outliers')
plt.legend()
plt.title('Heart Rate Data with Conditional Outliers Highlighted')
plt.xlabel('Time Index')
plt.ylabel('Heart Rate')
plt.show()

# + [markdown] id="p1rLIIeTvi6J"
# # 9. Statistical Data Analysis
#
# Data isn't much without some analysis, so we're going to do some in this section. Please do not use the analyses below as evidence supporting any scientific claims. These analyses are purely intended for educational purposes.
#
# ## 9.1 Breathing rate and SPO2 during sleep
# Suppose we have a mini research question:
#
# **Mini Research Question**: Can sleep apnea be identified by the joint distribution of blood oxygen saturation and breathing rate?
#
# **Significance**: Sleep apnea is characterized as periods of low blood oxygen saturation accompanied by fluctuations in breathing rate. Therefore, analyzing the relationship between these two variables during sleep can provide valuable insights into the presence and severity of sleep apnea episodes.
#
#
# #### Step 1: Data Loading and Preparation
# Our first step would be extract the average SPO2 values that corresponding to the breathing rate during sleep. We will also merge the two dataframes.

# + id="le_DDRbp5Ce4"
spo2_df['date'] = spo2_df['minute'].dt.date


day_spo2_df = spo2_df.groupby('date')['value'].mean().reset_index()

day_spo2_df.columns = ['date', 'mean_spo2']

# + id="eF2AAJgd5kSJ"
day_br_df = br_df[['datetime', 'fullSleepSummary']].copy()

day_br_df.columns = ['date', 'mean_breath_rate']

# + id="m5LW6Gf354Ew"
day_spo2_df['date'] = pd.to_datetime(day_spo2_df['date'])
day_br_df['date'] = pd.to_datetime(day_br_df['date'])

# Merge the two DataFrames on the 'date' column
merged_df = pd.merge(day_spo2_df, day_br_df, on='date')

# + [markdown] id="EikZYjtJWbyp"
# #### Step 2: Inject sleep apnea data
#
# Since our data simulates a healthy person, let us modify a proportion of data and reflect the data of a patient with sleep apnea.

# + id="08TvgF5uWn74"
# Simulate sleep apnea by modifying certain rows
num_apnea_days = int(0.15 * len(merged_df))  # Simulate apnea on 15% of the days
apnea_indices = np.random.choice(merged_df.index, num_apnea_days, replace=False)

for i in apnea_indices:
    merged_df.at[i, 'mean_spo2'] = random.uniform(91, 95)  # Lower SpO2 to simulate apnea
    merged_df.at[i, 'mean_breath_rate'] = random.uniform(12, 14)  # Lower breath rate to simulate apnea

# + [markdown] id="oAABcyicWyNn"
# #### Step 3: Visualize the data
#

# + colab={"base_uri": "https://localhost:8080/", "height": 704} id="2CG8WIPEUG4k" outputId="e8699d1b-48a9-4f1d-d009-99114618bb53"
import seaborn as sns
sns.set(style="whitegrid")

fig, ax1 = plt.subplots(figsize=(14, 7))

# Add a y-axis for the average SpO2 data
color = 'tab:red'
ax1.set_xlabel('Date')
ax1.set_ylabel('Average SpO2 (%)', color=color)
ax1.plot(merged_df['date'], merged_df['mean_spo2'], color=color, marker='o', label='Average SpO2')
ax1.tick_params(axis='y', labelcolor=color)
ax1.axhline(y=95, color=color, linestyle='-', linewidth=0.8, label='SpO2 Threshold (95%)')

# Add a y-axis for the breathing rate data
ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('Average Breathing Rate (bpm)', color=color)
ax2.plot(merged_df['date'], merged_df['mean_breath_rate'], color=color, marker='o', label='Average Breathing Rate')
ax2.tick_params(axis='y', labelcolor=color)
ax2.axhline(y=14, color=color, linestyle='-', linewidth=0.8, label='Breathing Rate Threshold (14 bpm)')


fig.tight_layout()
fig.suptitle('Average SpO2 and Breathing Rate Over Time', y=1.02, fontsize=16)
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

plt.show()

# + [markdown] id="2rRJJ5h1wtUO"
# ### Using `jointplot` instead of line plots
#
# When examining the line plot above, it's evident that the patient experiences nights with both low average SpO2 levels and irregular breathing. However, if we were to investigate the correlation between SpO2 and breathing rate, it still remains ambiguous just by looking at the line plot.
#
# A nice and convenient alternative to view this correlation is to use `jointplot` from `seaborn`, which allows us to visualize the distribution of data points on both axes and assess their correlation.
#
# Furthermore, applying KMeans clustering to these data points can uncover distinct clusters, potentially revealing patterns or groups of nights with similar characteristics.

# + colab={"base_uri": "https://localhost:8080/", "height": 631} id="gU_tn-tSx0Bi" outputId="659ffff7-d56d-4e98-e1c1-1e4843a3bcc9"
from sklearn.cluster import KMeans

# Prepare the data for clustering
X = merged_df[['mean_spo2', 'mean_breath_rate']]

# Apply KMeans clustering
kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
merged_df['cluster'] = kmeans.fit_predict(X)

# Create the joint plot with marginal histograms
g = sns.JointGrid(data=merged_df, x='mean_spo2', y='mean_breath_rate', hue='cluster', palette=['red', 'blue'])

# Scatter plot with clusters
g = g.plot(sns.scatterplot, sns.histplot)


g.ax_joint.axvline(x=95, color='red', linestyle='--', linewidth=0.8, label='SpO2 Threshold (95%)')
g.ax_joint.axhline(y=14, color='blue', linestyle='--', linewidth=0.8, label='Breathing Rate Threshold (14 bpm)')

plt.suptitle('Jointplot of Average SpO2 and Breathing Rate During Sleep', y=1.02, fontsize=16)
plt.xlabel('Mean SPO2')
plt.ylabel('Mean breathing rate')
g.ax_joint.legend_.remove()

plt.show()

# + [markdown] id="Wma596mzzZz5"
# ## 9.2 Breathing rates at different sleep stages
#
# We might also be interested if breathing rate changes in each stage. We can also use `seaborn` to plot histograms to visualize the distribution of breathing rates.
#
#

# + colab={"base_uri": "https://localhost:8080/", "height": 727} id="z9JztSsY0wR9" outputId="fd20a8a7-5eae-46d5-c21c-f5749cd04718"
# Plotting normalized histograms
plt.figure(figsize=(12, 8))

sns.histplot(br_df['deepSleepSummary'], bins=20, kde=True, label='Deep Sleep', color='blue', stat='density')
sns.histplot(br_df['remSleepSummary'], bins=20, kde=True, label='REM Sleep', color='green', stat='density')
sns.histplot(br_df['lightSleepSummary'], bins=20, kde=True, label='Light Sleep', color='orange', stat='density')

plt.title('Normalized Histograms of Breathing Rates for Different Sleep Stages')
plt.xlabel('Breathing Rate')
plt.ylabel('Density')
plt.legend()
plt.show()

# + [markdown] id="3s0H99UM1FOv"
# Let us also look into the mean and standard deviation of breathing rates for each of the sleep stages.

# + colab={"base_uri": "https://localhost:8080/"} id="YJTQGWgq1ETp" outputId="3071b987-2f18-454b-ac7a-54164b7eb6a4"
deep_sleep_mean = br_df['deepSleepSummary'].mean()
deep_sleep_std = br_df['deepSleepSummary'].std()

rem_sleep_mean = br_df['remSleepSummary'].mean()
rem_sleep_std = br_df['remSleepSummary'].std()

light_sleep_mean = br_df['lightSleepSummary'].mean()
light_sleep_std = br_df['lightSleepSummary'].std()

print(f"Deep Sleep - Mean: {deep_sleep_mean:.2f}, Std Dev: {deep_sleep_std:.2f}")
print(f"REM Sleep - Mean: {rem_sleep_mean:.2f}, Std Dev: {rem_sleep_std:.2f}")
print(f"Light Sleep - Mean: {light_sleep_mean:.2f}, Std Dev: {light_sleep_std:.2f}")

# + [markdown] id="ysQhCLAr3b82"
# For distributions like this one, we can use Analysis of Variance (ANOVA) to determine if the distributions are significantly distinct.
#
# ### Analysis of Variance (ANOVA)
#
# Analysis of Variance (ANOVA) is a statistical method used to compare means between two or more groups. It assesses whether there are significant differences in the means of groups based on the variance observed in their measurements.
#
# ANOVA assesses the null hypothesis that all groups have the same mean. It calculates an F-statistic by dividing the variance between the groups (explained variance) by the variance within the groups (unexplained variance). If the F-statistic is large enough to reject the null hypothesis, it indicates that at least one group mean is significantly different from the others.
#
# $$F = \frac{\text{Between-group variability}}{\text{Within-group variability}} $$
#
# Here, we can simly input our three distributions into the `f_oneway` function from `scipy.stats` and inspect the resulting p-value. If the p-value is less than 0.05, it indicates that there is a significant difference between sleep stages.

# + colab={"base_uri": "https://localhost:8080/", "height": 800} id="9RwdtAeC2A4z" outputId="3a17a7c3-0cff-4e78-8951-f7fcb41aab03"
from scipy.stats import f_oneway

# Perform ANOVA
anova_result = f_oneway(br_df['deepSleepSummary'], br_df['remSleepSummary'], br_df['lightSleepSummary'])

print(f"One-way ANOVA Results:")
print(f"F-value: {anova_result.statistic}")
print(f"P-value: {anova_result.pvalue}")

if anova_result.pvalue < 0.05:
    print("Reject null hypothesis: There is a significant difference between sleep stages.")
else:
    print("Fail to reject null hypothesis: There is no significant difference between sleep stages.")

# Plotting updated histograms with mean values
plt.figure(figsize=(12, 8))

sns.histplot(br_df['deepSleepSummary'], bins=20, kde=True, label='Deep Sleep', color='blue', stat='density')
sns.histplot(br_df['remSleepSummary'], bins=20, kde=True, label='REM Sleep', color='green', stat='density')
sns.histplot(br_df['lightSleepSummary'], bins=20, kde=True, label='Light Sleep', color='orange', stat='density')

plt.title('Normalized Histograms of Breathing Rates for Different Sleep Stages')
plt.xlabel('Breathing Rate')
plt.ylabel('Density')

# Adding vertical lines for mean values
plt.axvline(x=deep_sleep_mean, color='blue', linestyle='--', linewidth=0.8, label=f'Deep Sleep Mean ({deep_sleep_mean:.2f})')
plt.axvline(x=rem_sleep_mean, color='green', linestyle='--', linewidth=0.8, label=f'REM Sleep Mean ({rem_sleep_mean:.2f})')
plt.axvline(x=light_sleep_mean, color='orange', linestyle='--', linewidth=0.8, label=f'Light Sleep Mean ({light_sleep_mean:.2f})')

plt.legend()
plt.show()

# + [markdown] id="HZbM2Pbz1OS7"
# The p-value is far less than 0.05, indicating that the null hypothesis that all groups have the same mean is rejected. This suggests that there is a correlation between breathing rate and sleep stage.
#
# This does make sense, since the deep sleep stage typically involves slower and more regular breathing patterns, resulting in a lower mean breathing rate with relatively low variability. Conversely, the REM sleep stage involves rapid eye movements and vivid dreaming, exhibits a higher mean breathing rate along with a slightly higher standard deviation, reflecting the intermittent nature of breathing during this stage. Lastly, light sleep, which acts as a transition between deep sleep and wakefulness, displays an intermediate mean breathing rate and standard deviation.

# + [markdown] id="sYF1PxNmFkLk"
# Lastly, please be reminded that the data presented and any subsequent results are purely synthetic and intended only for demonstrative purposes. They do not reflect actual biological data or clinical findings. This synthetic approach is only used to illustrate data processing, visualization, and analytical techniques.
