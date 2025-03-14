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

# + [markdown] id="OD2g9xsgxSYy"
# # Withings Body+ Scale: Guide to Extracting and Analyzing Data 
#
# <img src="https://helios-i.mashable.com/imagery/reviews/004D6FxeJ3thoEUqJ7bum9h/hero-image.fill.size_1248x702.v1648656157.png" width="500"/>
#
# Are smart TVs, smartphones, or smart watches not enough? Introducing the [Withings Body+ Scale](https://www.withings.com/us/en/body-plus), a smart scale that can not only weigh you, but also leverage its Wi-Fi capabilities to enable you to store your historical weight data for your viewing pleasure. While this notebook is meant for the Body+ Scale, it can be easily adapted to any other Withings scale with minor modifications.
#
# Also note that you need to set up your Withings Body+ Scale prior to running this notebook. To do this, simply follow the instructions on the app to (1) pair your phone to your scale and (2) connect your scale to your home internet.
#
# If you want to know more about Withings Body+ Scale, visit this [link](http://wearipedia.com/wearables/withings-body-plus) for a detailed analysis of performances, sensors, data privacy, and extraction pipelines.
#
# The API makes the following parameters available:
#
# Parameter Name  | Sampling Frequency 
# -------------------|------------------
# Weight (kg)      |  Per weighing
# Fat Free Mass (kg) | Per weighing
# Fat Ratio (%) | Per weighing
# Fat Mass Weight (kg) | Per weighing
# Muscle Mass (kg) | Per weighing
# Hydration (kg) | Per weighing
# Bone Mass (kg) | Per weighing
#
#
# <br><br>
# In this guide, we sequentially cover the following **nine** topics to extract from the Withings API:
# 1. **Setup** 
# 2. **Authentication and Authorization** 
#     - This requires a couple extra steps on your part using OAuth and a 2-step verification process through `wearipedia`.
# 3. **Data extraction**
#     - We can get data via our `wearipedia` package
#     - Due to our own limited sample size, which precludes long time horizon data analysis, we include a data extraction step that loads an artificial dataset we randomly generate.
#     
# 4. **Data Exporting** 
#     - We export the data via Pandas DataFrame into file formats compatible by R, Excel, and Matlab.
# 6. **Adherence** 
#     - We simulate non-adherence by dynamically removing datapoints from our simulated data.
# 6. **Visualization** 
#     - We look at trends in both weight and fat (%) over time (months).
# 7. **Advanced Visualization** 
#     - We plot a calendar heatmap of weight measurements every day, revealing which days the user has used the scale.
#     - We also look at how weight varies over the time of day and downsample weight to a single measurement per day.
# 8. **Outlier Detection and Data Cleaning** 
#     - We perform data cleaning for multiple measurements taken within short time frames.
#     - We detect outliers in our data and filter them out.
# 9. **Statistical Data analysis** 
#     - We aggregate body weight by time of day, then conduct a brief statistical analysis to check whether body weight indeed increases after a meal.
#     - We analyze whether weight values and fat ratios are correlated.
#
#
# Disclaimer: this notebook is purely for educational purposes. All of the data currently stored in this notebook is purely *synthetic*, meaning randomly generated according to rules we created. Despite this, the end-to-end data extraction pipeline has been tested on our own data, meaning that if you enter your own credentials on your own Colab instance, you can visualize your own *real* data. That being said, we were unable to thoroughly test the timezone functionality, though, since we only have one account, so beware.

# + [markdown] id="EGZZcSOH3PT1"
# # 1. Setup
#
# ## 1.1 Study participant setup and usage
# Dear Participant,
#
# Thank you for using this notebook! To set up the scale itself so that you can run this notebook, download the Withings app and follow the instructions on the app. The app will pair via bluetooth to the scale, creating an interface to connect the scale to Wi-Fi. In our experience, this process was frought with difficulties.
#
# Note that the Wi-Fi network must have no captive portal, only simple username / password authentication. This means that connecting the scale to Wi-Fi may be challenging on a university campus setting, where Wi-Fi is hidden behind layers of authentication. One potential workaround is to view the serial number (which is the same as the MAC address) and register the MAC address through the IT department, which should allow a connection to university campus Wi-Fi.
#
# Best,
#
# Wearipedia
# ## 1.2 Wearipedia Library Install
# Relevant libraries are imported below. Just run the code to import all the libraries.

# + colab={"base_uri": "https://localhost:8080/"} id="C2Xoi3ci9bVF" outputId="8c0cb8ae-6397-45ac-a241-0c0decf86a8d"
#@title Library import + setup

# sneak in the library imports etc. here :)

# upgrade scipy, since we need "intercept_stderr"
# from https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html
# !pip install --upgrade scipy -q

import requests
import urllib
import json
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.ndimage import gaussian_filter
from scipy import stats

# suppresses unnecessary warning
pd.options.mode.chained_assignment = None

# + colab={"base_uri": "https://localhost:8080/"} id="w0nDiO2ZiQmx" outputId="6cded7a5-9280-4d7f-8b15-7f332de86c99"
# !pip install wearipedia
# !pip install july -q # for calendar plotting

# + id="5olKMW2LnqBb"
import wearipedia
device = wearipedia.get_device('withings/bodyplus')

# + [markdown] id="d2Kbo6d4waj9"
# # 2. Authentication and Authorization
#
# To be able to make requests to the API, the easiest way is to use the public developer API. This section roughly follows the steps outlined [here](https://developer.dexcom.com/authentication) on their website.
#
# First, follow the non-colab steps listed below:
#
# 1. Visit the [developer portal](https://developer.withings.com/) and click "Open Developer Dashboard" on the top right.
# 2. Once logged in, click "Add an app".
# 3. For now, you can just click "I don't know" under "Services", accept terms of use, and click "Next".
# 4. Put whatever you want under "Application Name" (we used `withings-test`), anything under "Application Description", and "https://wbsapi.withings.net/v2/oauth2" under Registered URLs, then click "Done".
#     - NOTE: "registered URLs" is intended to be a URL to a webserver you control and can receive requests from. However, in this notebook we are simply using it as a placeholder, as this functionality is not strictly necessary for obtaining your data.
#
# In the end, you should see something like the below.
#
# <img src="https://i.imgur.com/ttWojjU.png"></img>
#
# Now we can proceed with the rest of the notebook.
#
# To be able to make requests to the API and extract the data we need, we need to first issue an access token. This (ephemeral) access token will serve as our key to the data. While, you don't necessarily need to be familiar with how the issuing of the authtoken occurs, you can learn more about it by visiting [the official Withings tutorial](https://developer.withings.com/developer-guide/v3/integration-guide/public-health-data-api/get-access/oauth-web-flow/).

# + id="T_wCSag3u9yU"
#@title 5. Enter your credentials below (from the application you just created) or click synthetic if you do not want real data
CLIENT_ID = "" #@param {type:"string"}
CUSTOMER_SECRET = "" #@param {type:"string"}
use_synthetic = True #@param {type:"boolean"}
credentials = {"client_id": CLIENT_ID, "client_secret": CUSTOMER_SECRET}
if not use_synthetic:
  device.authenticate(credentials)


# + [markdown] id="kpLZcG86vSuL"
# 6. Now visit the above URL and click "Allow this app", and copy the **entire** URL you were redirected to into the input text field above that says "redirect url below: ." Note that if you mess up once, you have to go through the above URL again (including clicking "Allow this app"). Also, the URL is only valid for 30 seconds, so be quick in pasting!

# + [markdown] id="JObtRZuFvuJl"
# Now that we have our access token, we can begin making requests to the API! This access token will last only three hours, though, so you would need to re-do step 6 if three hours pass.

# + [markdown] id="GUtc7x14ebLe"
# # 3. Data Extraction
#
# Here, data extraction is pretty simple! 
#
# Data can be extracted via wearipedia, our open-source Python package that unifies dozens of complex wearable device APIs into one simple, common interface.
#
# First, we'll set a date range and then extract all of the data within that date range. You can select whether you would like synthetic data or not with the checkbox.
#
# Please go back to step 5 of Authentication/Authorization where you can uncheck the "use_synthetic" box to instead use your own *real* data via Withings API calls!

# + colab={"base_uri": "https://localhost:8080/", "height": 424} id="DnMDh0td1R7a" outputId="e79dfec6-7282-4744-80df-52d4b90ebb41"
#@title Extract data via the API!
#set start and end dates - this will give you all the data from 2000-01-01 (January 1st, 2000) to 2100-02-03 (February 3rd, 2100), for example
start_date='2020-01-01' #@param {type:"date"}
end_date='2022-12-01' #@param {type:"date"}
params = {"start": start_date, "end": end_date}

df = device.get_data("measurements", params=params)
df

# + [markdown] id="eag-47xkhUhP"
# # 4. Data Exporting
#
# In this section, we export all of this data to formats compatible with popular scientific computing software (R, Excel, Google Sheets, Matlab). Specifically, we will first export to JSON, which can be read by R and Matlab. Then, we will export to CSV, which can be consumed by Excel, Google Sheets, and every other popular programming language.
#
# ## Exporting to JSON (R, Matlab, etc.), CSV, and XLSX (Excel, Google Sheets, R, Matlab, etc.)
#
# Exporting to all these formats is fairly simple since we return a Pandas DataFrame. We export each datatype separately (JSON only) and also export a complete version that includes all simultaneously.

# + id="cH7DnZZC-rAY"
# set which format you prefer to export
use_JSON = True #@param {type:"boolean"}
use_CSV = True #@param {type:"boolean"}
use_Excel = True #@param {type:"boolean"}

if use_JSON:
  for column in df.columns:
    column_list = df[column].tolist()

    # If the first column contains Timestamp objects, convert to strings
    if isinstance(column_list[0], pd.Timestamp):
        column_list = [x.strftime("%Y-%m-%d %H:%M:%S") for x in column_list]

    # Write the list to a JSON file with its corresponding type as the title
    filename = column + ".json"
    with open(filename, 'w') as f:
        json.dump(column_list, f)

  # Convert the df to dictionary and make sure TimeStamps are strings
  df_JSON = df
  df_JSON['date'] = df_JSON['date'].apply(lambda x: str(x))
  df_JSON = df_JSON.to_dict(orient='records')

  # Write the dictionary to a JSON file
  with open('data.json', 'w') as outfile:
      json.dump(df_JSON, outfile)

if use_CSV:
  # Write the dataframe to a CSV file
  df.to_csv("data.csv", index=False)

if use_Excel:
  # Write the dataframe to an Excel file
  df.to_excel("data.xlsx", index=False)


# + [markdown] id="RNjuB-ssiSlI"
# Feel free to open the file viewer (see left pane) to look at the outputs!
#

# + [markdown] id="YCEqx0XYDt0J"
# # 5. Adherence
#
# The device simulator already automatically randomly deletes small chunks of the day. In this section, we will simulate non-adherence over longer periods of time from the participant (day-level and week-level).
#
# Then, we will detect this non-adherence and give a Pandas DataFrame that concisely describes when the participant had used the scale on and off throughout the entirety of the time period, allowing you to calculate measurement consistency etc.
#
# We will first delete a certain % of blocks either at the day level or week level, with user input. However, you can also select whether you want to only detect adherence by selecting the detect adherence only option for real data.

# + id="RrtvU6Ry4Gz2"
#@title Non-adherence simulation and detection
block_level = "day" #@param ["day", "week"]
nonadherence_percent = 0.2 #@param {type:"slider", min:0, max:1, step:0.01}
detect_adherence_only = True #@param {type:"boolean"}

# + id="gxA71QkT4p-x"
df_adherence = df
if not detect_adherence_only:
  if block_level == "day":
      block_length = 1
  elif block_level == "week":
      block_length = 7

  num_blocks = len(df['date'].tolist()) # length of entries in DF using the 1st column
  num_blocks_to_keep = int(nonadherence_percent * num_blocks)


  df_adherence = df_adherence.reset_index(drop=True) # reset the index
  idxes = np.random.choice(np.arange(num_blocks), replace=False, size=num_blocks_to_keep)
  df_adherence = df_adherence.drop(idxes.tolist())


# + [markdown] id="_d36DygdQvtE"
# And now we simulated having significantly fewer datapoints! This will give us a more realistic situation, where participants may take off their device for days or weeks at a time. 
#
# Now let's detect non-adherence. We will return a Pandas DataFrame sampled at everyday.

# + id="HuPOiU9W1w9A"
start_date = df.iloc[0]['date']
end_date = df.iloc[-1]['date']
weight_concat = []
for weight in df_adherence['Weight (kg)'].tolist():
    weight_concat += [weight]

ts_col = pd.date_range(start_date, end_date, freq="D", normalize=True)
using_arr = np.zeros(len(ts_col))
for i, dt in enumerate(df_adherence['date']):
    ts = pd.Timestamp(pd.to_datetime(dt).date())
    idxes = np.where(ts_col == ts)[0]
    if len(idxes) >= 1:
      using_arr[idxes[0]] = 1

df_adherence_detect = pd.DataFrame()
df_adherence_detect['timestamp'] = ts_col
df_adherence_detect['is_using'] = using_arr.astype('bool')

# + [markdown] id="ZAJbUcQGcdE-"
# We can plot this out, and we get adherence at a daily frequency throughout the entirety of the data collection period.

# + colab={"base_uri": "https://localhost:8080/", "height": 391} id="EexsEfo9c4r7" outputId="675ac3d1-1972-4886-db32-0e93c7db2fba"
plt.figure(figsize=(12, 6))
plt.plot(df_adherence_detect.timestamp, df_adherence_detect.is_using)

# + [markdown] id="4KbBMUmkde5l"
# We can also turn this into a list of start and stop points.

# + colab={"base_uri": "https://localhost:8080/"} id="MC6mikoAdf1p" outputId="105a4063-df18-464d-9b17-b35014b4e4f6"
from itertools import groupby

def contiguous_regions(a):
    i = 0
    res = []

    for k, g in groupby(a):
        l = len(list(g))
        if k:
            res.append((i,i+l))
        i += l

    return res

start_stops = []
for x in contiguous_regions(df_adherence_detect.is_using):
    if x[0] >= 0 and x[0] < len(df_adherence_detect) and x[1] >= 0 and x[1] < len(df_adherence_detect):
        start_stops.append((df_adherence_detect.timestamp[x[0]], df_adherence_detect.timestamp[x[1]]))
start_stops

# + [markdown] id="C8C0XU-npjwf"
# # 6. Visualization
#
# We've extracted lots of data, but what does it look like?
#
# In this section, we will be visualizing our two measurements in a simple, customizable plot! This plot is intended to provide a starter example for plotting, whereas later examples emphasize deep control and aesthetics. We've also added a feature to choose parameters for when a specific intervention started and which measurement you desire to plot. Specifically, you can select the index in which a treatment has been applied to a user, or enter '0' if no treatment was ever applied. You can also enter the date a treatment has started which will override the start index. Please note that if there is not a measurement for a specified date, we will plot out the next possible measurement past the treatment date (unless there is no measurement past it).

# + cellView="form" colab={"base_uri": "https://localhost:8080/", "height": 585} id="t2cUjldWl4ku" outputId="b9178881-2c90-4da0-cb69-f64574b39a65"
#@title Plot all of the data

from scipy.ndimage import gaussian_filter

# convert date column to datetime object
df['date'] = pd.to_datetime(df['date'])
x_timestamp = np.array(df.date.apply(lambda x: x.timestamp()))

# set treatment start date
specify_start_date="2022-01-01" #@param {type:"date"}
start_date = pd.to_datetime(specify_start_date)

# set treatment start index at a specific entry number
TREATMENT_START_IDX=200#@param {type:"number"}
if start_date:
  temp_index = None
  while not temp_index or start_date == df['date'].iloc[-1]:
    temp_index = (df['date'] - start_date).loc[lambda x: x >= pd.Timedelta(0)].idxmin()
    start_date = pd.Timedelta(days=1)
  if temp_index:
    TREATMENT_START_IDX = temp_index
# set measurement to plot
MEASUREMENT_TYPE='Weight (kg)'#@param['Weight (kg)', 'Fat Ratio (%)']

# 2 days
MIN_NEEDED_FOR_BREAK = 5 * 24 * 3600

# get the gaps. we include [6] as well because when you do np.diff,
# it actually leaves out exactly one element
differences = np.concatenate((np.diff(x_timestamp), [6]))

# interpret a gap (i.e. when a user takes off the device for some prolonged
# period of time) as any two measurements that are taken more than
# MIN_NEEDED_FOR_BREAK seconds apart
gap_idxes = np.where(differences > MIN_NEEDED_FOR_BREAK)[0]

with plt.style.context('seaborn'):
    plt.figure(figsize=(14,8))

    # filter the weight so that it looks smoother
    filtered = gaussian_filter(df[MEASUREMENT_TYPE], 100)

    # plot the weight curve and its filtered counterpart
    plt.plot(df.date, df[MEASUREMENT_TYPE], linewidth=.5, color='#d1d1d1')
    plt.plot(df.date, filtered, linewidth=2, color='black', label='Pre-Treatment')

    # plot the fill from x-axis up to weight curve
    plt.fill_between(df.date, df[MEASUREMENT_TYPE], color='#e3e3e3', alpha=0.3)

    # overlay treatment color
    plt.plot(df.date.iloc[TREATMENT_START_IDX:],
             df[MEASUREMENT_TYPE].iloc[TREATMENT_START_IDX:],
             linewidth=0.5, color='#3f8fc5')
    plt.plot(df.date.iloc[TREATMENT_START_IDX:],
             filtered[TREATMENT_START_IDX:],
             linewidth=2, color='#0f5f94', label='Treatment')
    plt.fill_between(df.date.iloc[TREATMENT_START_IDX:],
                     df[MEASUREMENT_TYPE].iloc[TREATMENT_START_IDX:],
                     color='#eaf1f6', alpha=0.3)

    # overlay gaps
    for gap_idx in gap_idxes:
        plt.plot(df.date.iloc[gap_idx-3:gap_idx+3], df[MEASUREMENT_TYPE].iloc[gap_idx-3:gap_idx+3], linewidth=2, color='white')
        plt.plot(df.date.iloc[gap_idx-3:gap_idx+3], filtered[gap_idx-3:gap_idx+3], linewidth=3, color='white')
        plt.fill_between(df.date.iloc[gap_idx-3:gap_idx+3], df[MEASUREMENT_TYPE].iloc[max(gap_idx-100,0):gap_idx+100].max(), color='white')


    plt.title(MEASUREMENT_TYPE + ' over time', fontsize=20)
    plt.ylabel(MEASUREMENT_TYPE)
    plt.xlabel('Time')

    # set background color *inside the figure*
    plt.gca().set_facecolor(color='white')

    # add horizontal grid
    plt.gca().grid(axis='x', color='#e5e5e5')
    plt.gca().grid(axis='y', color='#e5e5e5', which='major')

    # ensure the bottom axis is slightly darker and extends all the way
    # to the left
    plt.gca().spines['bottom'].set_edgecolor('grey')
    plt.gca().spines['bottom'].set_linewidth(1)
    plt.gca().spines['bottom'].set_visible(True)

    if MEASUREMENT_TYPE == 'Weight (kg)':
      plt.ylim(df['Weight (kg)'].min(), df['Weight (kg)'].max())
    else:
      plt.ylim(10, 40)
    plt.legend(prop={'size': 15})

    plt.tight_layout()

# + [markdown] id="V-9IFYQAk9JZ"
# # 7. Advanced Visualization
#
# Now we'll do some more advanced plotting that at times features hardcore matplotlib hacking with the benefit of aesthetic quality.
#
# Note that the timestamps that were extracted above correspond to days demarcated by midnight *not necessarily in UTC*, but rather where the user lives. To be precise, the timestamps themselves are in UTC, but the day element they belong to is determined by their location of residence.
#
# ## 7.1: Calendar Plot of Usage 
#
# First, it's important to know when the user has been using the scale as well as having a day-to-day plot of the user's weight and fat ratio trends. That way, we know the high-level time frame for the measurements, and can know where to focus analysis on.
#
# To figure this out, we'll make a calendar plot. Fortunately, this idea is easy to execute with the use of july, a custom library that allows us to create beautiful calendar plots. We'll interpret weight measurements as a proxy for usage and plot colors accordingly.

# + cellView="form" colab={"base_uri": "https://localhost:8080/", "height": 1000} id="yRR6HaQqwSez" outputId="ee1944a5-7902-4600-c5ea-0a1ff93f3f11"
# sum across hour axis
import july
# set measurement to plot
FEATURE_TYPE='Weight (kg)'#@param['Weight (kg)', 'Fat Ratio (%)']


# # copy so we can restore the rcParams later on; july changes it
IPython_default = plt.rcParams.copy()

july.calendar_plot(df.date, df[FEATURE_TYPE], value_label=True, weeknum_label=False, title=False)
plt.suptitle(FEATURE_TYPE + ' Over A Calendar Period', fontsize="x-large", y=1.03)
plt.show()  # suppress output from above line

# + [markdown] id="syGjL1bJyAoa"
# Now we can see the periods of inactivity with the scale! This helps to visualize the extent of non-adherence which lends us insight into unexplained changes in data.
#
# ---
#
#

# + [markdown] id="JvSoAF9JntAl"
# ## 7.2: Time of day
#
# It might also be interesting to look at how these quantities vary over the time of day. We'll aggregate all measurements by the hour of the day they were taken, then do a violin plot.

# + colab={"base_uri": "https://localhost:8080/", "height": 761} id="O8mDUsLw7cRD" outputId="1c5ee7f5-255c-4549-97d5-0a7503fb6b30"
#@title Plot weight by time of day
df['Hour of the day'] = df.date.apply(lambda x: x.hour)

plt.figure(figsize=(14,8))
sns.boxplot(x='Hour of the day', y='Weight (kg)', data=df)
plt.title('Weight by time of day')

# + [markdown] id="IP9zqyBECVcl"
# Looks like things vary quite a bit by time of day, and the user also seems to have taken more than one measurement per day on average (given that we have ~1400 measurements over the course of just two years). What if we want to just get a single weight value for each day the user has weighed themselves? We will do this data cleaning in the next section!
#
#

# + [markdown] id="9d3KbewTtkbi"
# # 8. Outlier Detection and Data Cleaning
#
# In this section, we will perform some data cleaning and detect outliers in our extracted data in order to impute them.
#
# Let's solve the previous problem by doing the following. Choose a time to be the canonical weighing time, say 5pm (technically speaking, 5pm-6pm). If a user has weighed themselves during that time interval, do nothing. If a user weighed themselves at some other time, say 3pm, then just add an offset corresponding to the average offset between weighings at 3pm and 5pm.
#
# If a user has weighed themselves at multiple points other than 5pm, just average their corrected weight values.
#
# To deduce the average offsets in the first place, just go through and find each instance where the user weighed themselves at 5pm, look in the neighborhood of 5 days within that day, and compute the offsets for the hours captured by those measurements.
#
#

# + id="P285tNJPEMhS"
#@title Get the offsets
days = df.date.apply(lambda x: x.timestamp()) / (24 * 3600)
days = days.reset_index(drop=True)

#need to reset index for when there is start/end truncation
df_temp = df
df_temp = df_temp.reset_index(drop=True)

# note that index 17 should be garbage, we don't care about it
offsets = [[] for i in range(24)]

for idx in np.where(df['Hour of the day'] == 17)[0]:
    to_offset = df_temp['Hour of the day'].iloc[np.where(np.abs(days[idx] - days) < 5)[0]]

    for i, val in zip(to_offset.index, to_offset):
        offsets[val].append(df_temp['Weight (kg)'].iloc[idx] - df_temp['Weight (kg)'].iloc[i])


def compute_mean(x):
    if len(x) > 0:
        return np.mean(x)
    else:
        return 0

offsets = [compute_mean(offset) for offset in offsets]

# + [markdown] id="7lOfIf7eIOUK"
# Now that we have our offsets we can create a new dataframe that is just the downsampled version of what we already had, but now just one value per day!

# + colab={"base_uri": "https://localhost:8080/", "height": 424} id="NroUECn2H4y3" outputId="cda434e1-d9bd-4f94-903b-780bf1982aa0"
#@title Get downsampled dataframe
downsampled_dict = []

for day in range(int(days.iloc[0]), int(days.iloc[-1])):
    # check if there are any measurements here
    day_idxes = np.where(days.apply(lambda x: int(x)) == day)[0]

    # if there are, do offset
    corrected_weights = []
    for day_idx in day_idxes:
        corrected_weight = df_temp['Weight (kg)'].iloc[day_idx] + offsets[df_temp['Hour of the day'].iloc[day_idx]]
        corrected_weights.append(corrected_weight)

    # save
    if len(corrected_weights) > 0:
        row = {
            'date': datetime.fromtimestamp(day * 24 * 3600),
            'Weight (kg)': np.mean(corrected_weights)
        }

        downsampled_dict.append(row)

downsampled_df = pd.DataFrame.from_dict(downsampled_dict)
downsampled_df

# + [markdown] id="EjPjbklWKQjt"
# As you can see, we've now got a dataframe without any repeating days!

# + [markdown] id="Ne-ykehnU-dh"
# Now lets do some outliers! Since there are currently no outliers (by construction, since it is simulated to have none), we will manually inject a couple.

# + colab={"base_uri": "https://localhost:8080/", "height": 424} id="vE5mtbF2zM2T" outputId="1f39110a-85d8-4514-c1b6-40cca500a5d4"
df_outlier = df.copy()  # Create a copy of the original DataFrame

new_data1 = {'date': pd.Timestamp('2022-06-16 23:04:39.745184'), 'Weight (kg)': 155.56, 'Fat Ratio (%)': 27.5}
new_data2 = {'date': pd.Timestamp('2022-06-17 22:04:39.9'), 'Weight (kg)': 68.78, 'Fat Ratio (%)': 10.5}

# Create DataFrames from new_data1 and new_data2
new_data1_df = pd.DataFrame([new_data1])
new_data2_df = pd.DataFrame([new_data2])

# Concatenate the new data DataFrames with the original DataFrame
df_outlier = pd.concat([df_outlier, new_data1_df, new_data2_df], ignore_index=True)

# Convert the 'date' column to Timestamp data type
df_outlier['date'] = pd.to_datetime(df_outlier['date'])

df_outlier = df_outlier.sort_values(by='date')
df_outlier = df_outlier.reset_index(drop=True)  # Necessary for future index searching
df_outlier

# + [markdown] id="krthBdM1zeXQ"
# Now that we've manually injected them, let's demonstrate that we can detect these.
#
# We will use a simple statistical method for detecting outliers. Specifically, we will rely on the assumption that weight and fat ratio percentages roughly do not change very much from one timestep to the next, and that if there is one measurement that very clearly sticks up much higher than the rest surrounding it, then it is likely an outlier.
#
# We will capture this notion by assuming the slope of datapoints fit a normal distribution and calculate Z-scores for every entry. 

# + colab={"base_uri": "https://localhost:8080/"} id="rhEWiGr6p1QI" outputId="d3588910-6a53-4b96-f1e4-24945e28669c"
from scipy.stats import norm # necessary for normal distribution

wt_list = [x for x in df_outlier['Weight (kg)'].tolist()]
fr_list = [x for x in df_outlier['Fat Ratio (%)'].tolist()]

wt_slopes = [(wt_list[i+1] - wt_list[i]) for i in range(len(wt_list)-1)]
fr_slopes = [(fr_list[i+1] - fr_list[i]) for i in range(len(fr_list)-1)]

# Calculate mean and standard deviation of the weights and fat ratio columns
wt_mu, wt_sigma = norm.fit(wt_slopes)
fr_mu, fr_sigma = norm.fit(fr_slopes)

# Calculate the z-score for each data point
wt_z_scores = [(x - wt_mu) / wt_sigma for x in wt_slopes]
fr_z_scores = [(x - fr_mu) / fr_sigma for x in fr_slopes]
print(wt_list[-1])

# + [markdown] id="vez22yq1-UO6"
# We will find any elements that deviate by more than $6\sigma$ from the mean, consider these outliers, and impute their value in the original data. We will average around these outliers if possible by a singular entry before and after. In the case of the first and last entries, we will average around 2 consecutive measurements after and before (respectively). 

# + colab={"base_uri": "https://localhost:8080/"} id="aqxH6UhAGVMr" outputId="f3243b2d-3e1c-40e5-d46b-419fca686948"
wt_outlier_indices = [i for i, z in enumerate(wt_z_scores) if z >= 6 or z <= -6]
fr_outlier_indices = [i for i, z in enumerate(fr_z_scores) if z >= 6 or z <= -6]

skip_to_outlier = False
# change this to iterate through ratios and if you find a common i and i+1, i is the index except for the last val where we check if the 2nd to last one was an outlier
for outlier in wt_outlier_indices:
  orig_val = wt_list[outlier]
  new_mean = orig_val
  if outlier == 0:
    new_mean += wt_list[outlier+1] + wt_list[outlier+2]
  elif outlier == len(df_outlier) - 1:
    new_mean += wt_list[outlier-1] + wt_list[outlier-2]
  else:
    if not skip_to_outlier:
      skip_to_outlier = True
      continue
    skip_to_outlier = False
    new_mean += wt_list[outlier-1] + wt_list[outlier-2]
  df_outlier.iloc[outlier, df_outlier.columns.get_loc('Weight (kg)')] = new_mean / 3
  print(f'Replacing {orig_val} with ', df_outlier.iloc[outlier, df_outlier.columns.get_loc('Weight (kg)')], ' obtained by averaging around it.')
  print(f'Index in Weight (kg) array is {outlier} and the z-score of this entry was {wt_z_scores[outlier]}')

skip_to_outlier = False
for outlier in fr_outlier_indices:
  orig_val = fr_list[outlier]
  new_mean = orig_val
  if outlier == 0:
    new_mean += fr_list[outlier+1] + fr_list[outlier+2]
  elif outlier == len(df_outlier) - 1:
    new_mean += fr_list[outlier-1] + fr_list[outlier-2]
  else:
    if not skip_to_outlier:
      skip_to_outlier = True
      continue
    skip_to_outlier = False
    new_mean += fr_list[outlier-1] + fr_list[outlier-2]
  df_outlier.iloc[outlier, df_outlier.columns.get_loc('Fat Ratio (%)')] = new_mean / 3
  print(f'Replacing {orig_val} with ', df_outlier.iloc[outlier, df_outlier.columns.get_loc('Fat Ratio (%)')], ' obtained by averaging around it.')
  print(f'Index in Fat Ratio (%) array is {outlier} and the z-score of this entry was {fr_z_scores[outlier]}')


# + [markdown] id="5z3sNYnUF006"
# Nice! We found our outliers, imputed them, and smoothed the entries around them as well.

# + [markdown] id="UF7cO1mVqM4X"
# # 9. Statistical Data Analysis
#
# First let's try to look for some trends.
#
# ## 9.1: Before and after meal
#
# First, let's confirm that the weights after meals are greater than the weights before meals.
#
# Note that this is slightly trickier than simply aggregating all of the weighings that occurred before a meal together and aggregating all of the weighings that occurred after a meal together, then comparing, since the user lost weight. This is because these local fluctuations are much smaller than the change due to the treatment over the course of two years, so they will be washed out.
#
# So instead we'll compare weighings to the weighings immediately surrounding them, and see if weighings that occurred after a meal tend to be higher. First, we'll compute a new column that represents whether the weighing was before a meal, after a meal, or neither.

# + id="v-bxVrVPYB_W"
def apply_func(x):
    hour = int(x.strftime('%H'))

    if hour in [12+4,12+5]:
        return 'before'
    elif hour in [12+7,12+8,12+9]:
        return 'after'
    else:
        return 'N/A'

df['meal_relative'] = df.date.apply(apply_func)

# + [markdown] id="8Iq5nI6csXX4"
# Now that we have this column, let's compute the deviation of each weighing to their neighboring weighings using a Gaussian filter.

# + id="Ag1no11FfvA6"
df['weight_deviations'] = df['Weight (kg)'] - gaussian_filter(df['Weight (kg)'], sigma=100)

# + [markdown] id="UT_EZZ5hsiZ7"
# Now we can finally check this hypothesis!

# + colab={"base_uri": "https://localhost:8080/", "height": 381} id="JVpQQZuzsk7U" outputId="2923be1a-674b-401a-d171-3e018e3abbef"
with plt.style.context('ggplot'):
    sns.stripplot(x='meal_relative', y='weight_deviations', data=df)

# + [markdown] id="NPuE0Ya7s8o7"
# It looks like whether the user just ate a meal or not has an impact on the weight. In fact, we can check the difference in the mean of both groups below.

# + colab={"base_uri": "https://localhost:8080/"} id="EmaUUMpbtkW6" outputId="dd5347a4-5c90-45d0-b4bc-590fe333ac0a"
print(f'Mean of weight deviation for weighings before a meal: {df.weight_deviations[df.meal_relative == "before"].mean():.3g}')
print(f'Mean of weight deviation for weighings after a meal: {df.weight_deviations[df.meal_relative == "after"].mean():.3g}')

# + [markdown] id="QrV7MSP1tjum"
# Let's check that this is significant with a two-tailed T-test.

# + colab={"base_uri": "https://localhost:8080/"} id="5BnOw0drtG4j" outputId="37e65734-d2cb-438c-9dfb-532f460d1d80"
result = stats.ttest_ind(df.weight_deviations[df.meal_relative == 'before'],
                         df.weight_deviations[df.meal_relative == 'after'])

print(f'P-value is {result.pvalue:.3g}')

# + [markdown] id="22vMcQtMtyf5"
# It's significant!
#
# ## 9.2: Treatment effectiveness
#
# While with only one person's data it is impossible to conclusively state that the treatment has or has not been effective (there is no control group), we can perform a linear regression, which provides a quantitative basis for the promising trend in weight we've seen in the plots in section 6.
#
# Specifically, we will perform a linear regression on the datapoints $(x,y)$, where $x$ is the timestamp and $y$ is the weight, strictly after the treatment start (index 200) and check its p-value. First, we'll just plot this out to remind ourselves what the data looks like.

# + colab={"base_uri": "https://localhost:8080/", "height": 749} id="Z1R0MAYc3yqj" outputId="d7eaf458-6f6d-42b0-c4b6-62ee913cb47f"
df['Timestamp'] = df.date.apply(lambda x: x.timestamp())
with plt.style.context('ggplot'):
    plt.figure(figsize=(15,8))
    plt.plot(df.iloc[200:, df.columns.get_loc('date')], df.iloc[200:, df.columns.get_loc('Weight (kg)')])
    plt.xlabel('Time')
    plt.ylabel('Weight (kg)')
    plt.title('Weight (kg) over time during period of treatment with Arilitaxel')

# + [markdown] id="cfT_fJvF4LV2"
# The treatment seems to have an effect! Let's do the statistical test now to confirm this quantitatively. In order to strongly support our findings, we will attempt to reject our null hypothesis: that there is no significant difference in weight loss between individuals who receive the treatment and individuals who do not receive the treatment. Specifically, we will conduct the Wald Test and further cement our findings.

# + colab={"base_uri": "https://localhost:8080/"} id="Na4mHq10M92O" outputId="f64bedfa-743c-4648-e811-c0870314e03d"
from scipy import stats
from scipy.stats import t

res = stats.linregress(df['Timestamp'].iloc[200:],
                       df['Weight (kg)'].iloc[200:])

tinv = lambda p, df: abs(t.ppf(p/2, df))
ts = tinv(0.05, len(df.date)-2)

print(f'Slope (95% confidence): {res.slope:.3g} +/- {ts*res.stderr:.3g}')
#print(f'Intercept (95% confidence): {res.intercept:.6f}'
      #f' +/- {ts*res.intercept_stderr:.6f}')
print(f'Coefficient of determination: {res.rvalue**2:.3g}')
print(f'p-value: {res.pvalue:.3g}')

# + [markdown] id="imy2dZAmNsL1"
# From these values, we see that our p-value which indicates the probability of us obtaining a slope of 0 or something similar in magnitude is < 5%. We can reject our null hypothesis that our treatment does not affect weight loss. Therefore, our findings look significant, and the confidence intervals for the slope and y-intercept are pretty tight! Below we plot what these confidence intervals entail, visually. 

# + colab={"base_uri": "https://localhost:8080/", "height": 745} id="cy2o--ziNAII" outputId="2e8a182f-d573-420c-c791-cebb8b2301fe"
sns.set(rc = {'figure.figsize':(15,8)})

# Note 1: c=95 to ensure that CI is 95%
# Note 2: plotting timestamp but then replacing tick labels, since
# dates don't work with sns.regplot
df_slice = df.iloc[200:]
sns.regplot(x='Timestamp', y='Weight (kg)', data=df_slice, scatter_kws={'s':1}, ci=95)

ax = plt.gca()
xticks = ax.get_xticks()
ax.set_xticks(xticks)
xticks_dates = [datetime.fromtimestamp(x).strftime('%Y-%m') for x in xticks]
ax.set_xticklabels(xticks_dates)

plt.xlabel('Date')

plt.title('Weight (kg) over time during period of treatment with Arilitaxel', fontsize=20, pad=10)

# + [markdown] id="wo6hT7T34mCb"
#
# ## 9.3. Weight vs. Fat Ratio
#
# Let's continue analyzing our synthetic data by investigating the relationship between weight and fat ratio percent. Although, we can already understand the gist between these two values, lets conduct a statistical analysis to ensure our intuition is correct. 
#
# First we will extract our weight and fat ratio columns from our original dataframe to remove the time dimension. 

# + [markdown] id="vqEEDO4LQti0"
# We can barely see the confidence interval, and that's because the data is so structured that we are very confident about where the line lies!

# + colab={"base_uri": "https://localhost:8080/", "height": 424} id="tYDtiKHr7VBT" outputId="0f816b3d-654f-42ae-fb9d-48484cf7c423"
new_df = df.loc[:, ["Weight (kg)", "Fat Ratio (%)"]]
new_df

# + [markdown] id="JV40MsUp8hxr"
# First we can visualize how concentrated our data is for a particular person using a density plot from Seaborn. Currently, we are utilizing a single person's data for this analysis, so this won't tell us much. However, if we aggregate data from many people, this density plot will show us the range in where our analysis should focus on. 

# + colab={"base_uri": "https://localhost:8080/", "height": 736} id="1FGjAQrt9wou" outputId="54a57509-61f4-45cc-844e-af629647501f"
# Density Plot
sns.kdeplot(x='Weight (kg)', y='Fat Ratio (%)', data=new_df, color = 'red')

# get the current Axes object
ax = plt.gca()

# set the title of the plot and format it
ax.set_title("Weight (kg) vs. Fat Ratio Density Distribution", fontsize=16, fontweight="bold", color="blue", pad=20)

# display the plot
plt.show()


# + [markdown] id="3PUAsEgp_eKD"
# Already, we can spot the intuitive positive trend between weight and fat ratio. Again, the more data aggregated, the more the density curve will stretch to accomodate variations in people's body composition. 
#
# Lets dive deeper; now we will plot a scatter plot of all the data points with a line of best fit to solidify our hypothesis. 

# + colab={"base_uri": "https://localhost:8080/", "height": 736} id="-ew3-d43AxrA" outputId="f6f2f8ce-878d-493d-dc0d-7003e9d0b5d5"
sns.regplot(x='Weight (kg)', y='Fat Ratio (%)', data=new_df, color = 'green')

# get the current Axes object
ax = plt.gca()

# set the title of the plot and format it
ax.set_title("Weight (kg) vs. Fat Ratio Scatter Plot", fontsize=16, fontweight="bold", color="red", pad=20)

# display the plot
plt.show()

# + [markdown] id="nuBH9X4qB1pM"
# From our synthetic person's data, we can spot a strong positive correlation between weight and fat ratio values, despite all the noise. However, this still isn't enough; we need to completely reject our null hypothesis that fat ratio does not increase with weight in order to eliminate coincidence. We will conduct the Wald test and verify it is so.

# + colab={"base_uri": "https://localhost:8080/"} id="hntjhdyvCnjj" outputId="142b5c97-879a-4d49-ff94-5566d3c1fcfe"
res = stats.linregress(new_df['Weight (kg)'],
                       new_df['Fat Ratio (%)'])

tinv = lambda p, df: abs(t.ppf(p/2, df))
ts = tinv(0.05, len(df.date)-2)

print(f'Slope (95% confidence): {res.slope:.3g} +/- {ts*res.stderr:.3g}')
#print(f'Intercept (95% confidence): {res.intercept:.6f}'
      #f' +/- {ts*res.intercept_stderr:.6f}')
print(f'Coefficient of determination: {res.rvalue**2:.3g}')
print(f'p-value: {res.pvalue:.3g}')

# + [markdown] id="s-9VwLV4DGre"
# From the Wald test, we can confirm our intuition; the p-value is <.05, which means we can reject our initial null hypothesis and further support that weight and fat ratios are positively correlated.
