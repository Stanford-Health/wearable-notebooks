# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python 3
#     name: python3
# ---

# + [markdown] id="DOJ7AvNr2hET"
# # Guide to Extracting Data w/ APIs from the Dexcom G6 PRO
#
# <img src="https://provider.dexcom.com/sites/default/files/2022-03/G6-Pro_3_0.png" width="500"/>
#
#
# Ever wanted to constantly monitor your blood glucose every 5 minutes, 24/7? With the [Dexcom G6 PRO CGM device](https://provider.dexcom.com/products/dexcom-g6-pro), you can track your glucose levels continuously over time and beam this data back so you can analyze it for yourself. In this notebook, we'll be showing you how to do just that, assuming you already have a Dexcom G6 PRO CGM device set up and tracking.
#
# If you want to know more about the Dexcom G6 PRO CGM device, see the [README](https://github.com/alrojo/wearipedia/tree/main/wearables/dexcom-g6-pro) for a detailed analysis of performances, sensors, data privacy, and extraction pipelines.
#
# We were able to extract glucose levels at a sampling rate of every 5 minutes from the API.
#
# <br><br>
# In this guide, we sequentially cover the following **five** topics to extract from the Dexcom API:
# 1. **Setup**
# 2. **Authentication and Authorization**
#     - This requires a couple extra steps on your part
# 3. **Data Extraction**
#     - You can get data from the API between any given date range in a couple lines of code.
# 4. **Data Exporting**
#     - The data can be exported to json format or excel.
# 5. **Adherence**
#     - We visualize when data was collected throughout the year.
#         - We achieve this by plotting a calendar heatmap depicting when the user has been wearing the device by coloring according to the number of hours in the day at least 3 glucose measurements were logged.
# 6. **Visualization**
#     - 6.1: We visualize the aggregated glucose levels over the course of a given day.
#     - 6.2: We reproduce the glucose level day profile from the Dexcom Clarity website that shows the variation of glucose level in each day.
# 7. **Advanced Visualization**
#     - 7.1: We reproduce the plot of glucose levels over a *particular day of interest*.
# 8. **Outlier Detection and Data Cleaning**
#     - We check for anomalies in the data and clean the data.
# 9. **Statistical Data Analysis**
#     - 9.1: We analyze whether glucose levels change significantly between nighttime and daytime.
#     - 9.2: We analyze whether glucose level *variability* changes significantly between nighttime and daytime.
#
# Disclaimer: this notebook is purely for educational purposes. All of the data currently stored in this notebook is purely *synthetic*, meaning randomly generated according to rules we created. Despite this, the end-to-end data extraction pipeline has been tested on our own data, meaning that if you enter your own credentials on your own Colab instance, you can visualize your own *real* data. That being said, we were unable to thoroughly test the timezone functionality, though, since we only have one account, so beware.

# + [markdown] id="X-MJnhzu4T_g"
# # 1. Setup
#
# ## 1.1 Data receiver setup
#
# First, set up your developer app:
#
# 1. Register for a new developer account at [this link](https://developer.dexcom.com/user/register). Note that you can use any email you like, and it *does not* need to match the email for the study participant.
# 2. Once logged in, click the green button titled "Add an app".
# 3. Give the app any name you want, any description, and for Redirect URI you can entire in `https://www.google.com` (can be any valid base URL, but this is probably simplest).
#
# In the end, you should see something like the below.
#
# <img src="https://i.imgur.com/j8WBnHH.png"></img>
#
#
#
#
# ## 1.1 Study participant setup and usage
#
# Dear Participant,
#
# Please follow the [video on the website](https://provider.dexcom.com/education-research/cgm-education-use/videos/getting-started-dexcom-g6-and-setting-g6-app) to set up your device. Specifically, you should have a dexcom account (email and password), please provide the research coordinator your email and password so they can access your data. Make sure to use the device for at least 24 hours for meaningful data collection to occur.
#
# Best,
#
# Wearipedia
#
#

# + [markdown] id="cab7P6_f4eHn"
# # 2. Authentication and Authorization
#
# On the left bottom corner of your app, you should be able to see your client id and client secret. Please enter the credentials in the cell below, and make sure that the redirect URI matches.

# + colab={"base_uri": "https://localhost:8080/"} id="RO3IljoG01Fd" outputId="984bf547-c7b3-453a-8a08-00744f8f1e62" cellView="form"
#@title Enter your credentials

# for calendar plot
# %pip install -q july
# %pip install --upgrade certifi

import requests
import urllib
import json
from datetime import datetime
import http.client

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import july
from july.utils import date_range


your_client_secret = "0AZzW4O8EVxHek3veOwelaq0LScLS2la" #@param {type:"string"}
your_client_id = "7OO7B5JBv7p0K1DV" #@param {type:"string"}
your_redirect_uri = "https://www.google.com" #@param {type:"string"}
your_state_value = '1234'

url = f'https://api.dexcom.com/v2/oauth2/login?client_id={your_client_id}&redirect_uri={your_redirect_uri}&response_type=code&scope=offline_access&state={your_state_value}'

print(url)

# + [markdown] id="6TtWtEhq78N9"
# Visit the above URL and you should see a page like this.
#
# <img src="https://imgur.com/9QyqTAd.png"></img>
#
# Here you will need to login with the study participant's email and password. After logging in, you will have to grant access to the data. You may have to go through a second page where the study participant has to type in his/her signature. Once you go through this portal, copy the URL you were redirected to below. You must do this quickly (there is a one minute expiration countdown).
#
# This will grant you an access token that lasts 10 minutes.

# + id="bl-_tkzG1bKr" cellView="form"
#@title Copy the URL into the text box below
redirect_url = "" #@param {type:"string"}

try:
    your_authorization_code = urllib.parse.parse_qs(urllib.parse.urlparse(redirect_url).query)['code'][0]
except Exception as e:
    print(f'Caught error:\n{e}\n')
    print("Please copy and paste the entire URL (including https)")


conn = http.client.HTTPSConnection("api.dexcom.com")

payload = f"client_secret={your_client_secret}&client_id={your_client_id}&code={your_authorization_code}&grant_type=authorization_code&redirect_uri={your_redirect_uri}"

headers = {
    'content-type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache"
    }

conn.request("POST", "/v2/oauth2/token", payload, headers)

res = conn.getresponse()
data = res.read()

json_response = json.loads(data.decode('utf-8'))

if 'error' in json_response.keys() and json_response['error'] == 'invalid_grant':
    print('The code you got has expired.')
    print('Authorize and enter the redirect URL again.')
else:
    access_token = json.loads(data.decode('utf-8'))['access_token']

    print(f'Entire response was {data.decode("utf-8")}')
    print(f'Our access token is {access_token}')

# + [markdown] id="M9UupU4kAFW8"
# # 3. Data Extraction
#
# Data extraction is fairly simple for this API. For documentation about what endpoints you can hit and what data you can get, see [this official link](https://developer.dexcom.com/endpoint-overview). Here, we'll just extract the time-varying CGM values.
# Note: the start and end dates must be within 90 days of each other.

# + colab={"base_uri": "https://localhost:8080/"} id="I93tIZpKCjQ7" outputId="fa44566f-df03-4046-fc5e-6bdc26c3da5d"
#@title Enter start and end dates

from datetime import timedelta
from tqdm import tqdm
from scipy.ndimage import gaussian_filter

start_day = datetime.strptime('2022-03-31', '%Y-%m-%d')

def lerp(x1, x2, t):
    return t * x2 + (1 - t) * x1

base_keypoints = [100] * 4 + [120] * 4 + [130] * 8 + [120] * 4 + [100] * 4

def create_synth_df():
    datetimes = []
    glucoses = []

    for day_offset in tqdm(range(12)):
        if day_offset != 0:
            overlap = keypoints[-1]
        keypoints = list(np.random.randn(24) * 10 + np.array(base_keypoints))
        if day_offset != 0:
            keypoints[0] = overlap

        keypoints = keypoints + [keypoints[0]]

        for minute_offset in range(0, 24 * 60, 5):
            minute = start_day + timedelta(days=day_offset) + timedelta(minutes=minute_offset)

            scaled_offset = minute_offset / 60

            k1 = keypoints[np.floor(scaled_offset).astype('int')]
            k2 = keypoints[np.ceil(scaled_offset).astype('int')]

            value = lerp(k1, k2, scaled_offset % 1)
            if value > 130:
                scaling = 30
            else:
                scaling = 15
            value += np.random.randn() * scaling

            datetimes.append(minute)
            glucoses.append(value)

    synth_df = pd.DataFrame()

    synth_df['datetime'] = datetimes
    synth_df['glucose_level'] = gaussian_filter(glucoses, 2, mode='constant')

    synth_df['Time of Day'] = ['Day' if dt.hour in range(8, 20) else 'Night' for dt in datetimes]
    synth_df['Rates of change'] = np.random.randn(synth_df.shape[0])
    synth_df.loc[synth_df['Time of Day'] == 'Day', 'Rates of change'] *= 3


    # take out some rows to create missing values

    missing_start = datetime.strptime('2022-04-06', '%Y-%m-%d') + timedelta(hours=14)
    missing_end = missing_start + timedelta(minutes=70)

    synth_df = synth_df.drop(np.where(np.logical_and(synth_df.datetime > missing_start, synth_df.datetime < missing_end))[0])

    return synth_df

start_date = "2022-02-16" #@param {type:"date"}
end_date = "2022-05-16" #@param {type:"date"}
synthetic = True #@param {type:"boolean"}

if synthetic:
    df = create_synth_df()
else:
    start_date = start_date + 'T15:30:00'
    end_date = end_date + 'T15:45:00'

    headers = {
        'authorization': f"Bearer {access_token}"
    }

    endpoint = f'https://api.dexcom.com/v2/users/self/egvs?startDate={start_date}&endDate={end_date}'

    out = json.loads(requests.get(endpoint, headers=headers).text)

    if 'errors' in out.keys():
        print(f'Got error(s) {out["errors"]}. Fix start and end dates and rerun.')
    elif 'fault' in out.keys():
        print(f'Got fault {out["fault"]}. You might need to request another access token.')
    else:
        def dt_string_to_obj(dt_str):
            # converts string like "2022-04-10T10:13:00" to a datetime object
            return datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S')


        data_dict = [{'datetime': dt_string_to_obj(x['displayTime']), 'glucose_level': x['realtimeValue']} for x in out['egvs'][::-1]]

        df = pd.DataFrame.from_dict(data_dict)

# + [markdown] id="rNVJFNSJLLR8"
# The code hidden above initialized `df`, a Pandas dataframe that represents the time series values for glucose. If we look at the `glucose_level` column without time information, we'll see the following...

# + colab={"base_uri": "https://localhost:8080/"} id="nYrn9JpDNWoF" outputId="1a828304-e0f8-4c54-ea03-e51da8fdc180"
df.glucose_level.describe()

# + [markdown] id="91Opux_fNbUS"
# As we can see, this user's glucose levels are around 100 mg/dL on average.
#
# And if we see how quickly the values were sampled at, we can see that they tend to be sampled in increments of 300 seconds, or 5 minutes.

# + colab={"base_uri": "https://localhost:8080/", "height": 300} id="Czf8IGuaPo6S" outputId="a0392bf6-1a4f-4c96-b58b-d51e1585693f"
diffs = np.diff(df.datetime.apply(lambda x: x.timestamp()))
pd.DataFrame(diffs).describe()

# + [markdown] id="VvbdpWl6qRxN"
# # 4. Data Exporting
#
# Here we can export all of this data to JSON, which  with popular scientific computing software (R, Matlab). We can also export the data to excel.

# + id="t2AP-XFNmIVq"
export_type = "excel" # @param ["json", "excel"]

if export_type == "json":
  df.to_json("data.json", orient="records", date_format="iso")
else:
  df.to_excel("data.xlsx", index=False)

# + [markdown] id="GgnYwxeh-dyY"
# Feel free to open the file viewer (see left pane) to look at the outputs! The file should contain the datetime information, glucose level, time of day (Night or Day), and rates of change.

# + [markdown] id="SavkeS3svdyR"
# # 5. Adherence
#
# Here, we are interested in knowing on which days our user used the device to track glucose level. As a reasonable proxy of glucose level coverage throughout a particular day, we count the number of hours in that day that the device has logged at least 3 glucose measurements for.
#
# The cell below will calculate `data`. `data` is a 2D numpy array with axes (day, hour), where the first axis refers to a particular day and the second axis refers to a particular hour of the day. The value for, say `data[130,8]`, is exactly one if the user wore his watch from 8am to 9am on day 130 (which is 130 days after start_date as specified above) and otherwise zero.

# + colab={"base_uri": "https://localhost:8080/"} id="Pz0f-xa5vrAw" outputId="7d20942f-eaec-4113-bfe3-d15dc73df7d6" cellView="form"
#@title Specify start and end dates and extract watch usage metrics
start_date = "2022-03-19" #@param {type:"date"}
end_date = "2022-05-21" #@param {type:"date"}

from tqdm import tqdm
import pytz

dates = date_range(start_date, end_date)
data = np.zeros((len(dates), 24))

# populate data array
for idx, date in tqdm(list(enumerate(dates))):
    local_tz = pytz.timezone('America/Los_Angeles')

    day_start = pd.Timestamp(date).replace(tzinfo=local_tz)

    for i in range(24):
        hour_start, hour_end = day_start + pd.Timedelta(hours=i), day_start + pd.Timedelta(hours=i+1)

        # check for number of measurements during this time
        bool_arr = np.logical_and(datetime.fromtimestamp(int(hour_start.timestamp())) < df.datetime,
               df.datetime < datetime.fromtimestamp(int(hour_end.timestamp())))

        num_measurements = len(np.where(bool_arr)[0])

        if num_measurements >= 3:
            data[idx, i] = 1

# + [markdown] id="E-49TGO2xtP4"
# Now we can make a calendar plot of device usage using the library `july`.

# + colab={"base_uri": "https://localhost:8080/", "height": 325} id="FrhAUdbVxjVm" outputId="dd3fe4ce-2326-4368-aa7c-de1fae26f9bb"
july.calendar_plot(dates, data.sum(axis=1), value_label=True, weeknum_label=False, title=False)
plt.suptitle('Watch usage', fontsize="x-large", y=1.03)
plt.show()

# + [markdown] id="qNPSNav2xsed"
# As we can see, our user was fairly consistent about wearing the device during that time period. She wore the device for every hour of the day for 9 consecutive days.

# + [markdown] id="lBkqdg8FK34F"
# # 6. Visualization
#
# Now, let us try to visualize some of the data. As a first attempt, let's see what they look like when we plot the levels over time (where time is the display time on the device).

# + cellView="form" colab={"base_uri": "https://localhost:8080/", "height": 593} id="7SlMIhyxLKvY" outputId="ac8411db-35ff-4d24-d17f-d6d65c93f3c9"
#@title 6.1. Plot levels over time for all of the data
# # copy so we can restore the rcParams later on
IPython_default = plt.rcParams.copy()

plt.figure(figsize=(16,8))

with plt.style.context('ggplot'):

    plt.plot(df.datetime, df.glucose_level, linewidth=.75)

    #gaussian_filter(glucoses, 10, mode='constant')

    plt.title('Glucose levels over time', fontsize=15)

    plt.xlabel('Time')
    plt.ylabel('Glucose (mg/dL)')
    plt.show()

# + [markdown] id="6gDMXZem_qdB"
# If we are also interested in looking if there are specific patterns in glucose level variation across each day, we can plot multiple plots like a calendar, just like this plot from the website:
#
# <img src="https://imgur.com/mNaWmLR.png" width="1000px"></img>

# + colab={"base_uri": "https://localhost:8080/", "height": 454} cellView="form" id="5y3w4nKFICFo" outputId="66731744-c318-415b-a32e-e7268862ff5f"
#@title 6.2. Plot day profiles
from matplotlib import gridspec

start_date = "2022-03-31" #@param {type:"date"}
end_date = "2022-05-01" #@param {type:"date"}

start_date = datetime.strptime(start_date, "%Y-%m-%d")
end_date = datetime.strptime(end_date, "%Y-%m-%d")

# Find the nearest Monday before start_date
start_date = start_date - timedelta(days=start_date.weekday())
# Find the nearest Sunday after end_date
end_date = end_date + timedelta(days=6 - end_date.weekday())

all_dates = []
current_date = start_date
while current_date <= end_date:
    all_dates.append(current_date)
    current_date += timedelta(days=1)


start_date = all_dates[0]
end_date = all_dates[-1]

num_days = len(all_dates)
rows = int(num_days / 7)

fig = plt.figure()
fig.set_figheight(10)
fig.set_figwidth(16)
spec = gridspec.GridSpec(ncols=7, nrows=rows,
                         width_ratios=np.ones(7), wspace=0.3,
                         hspace=0.3, height_ratios=np.ones(rows))
date_dict = {}
glucose_dict = {}
datetime_list = df['datetime'].tolist()
datetime_list = [timestamp.to_pydatetime() for timestamp in datetime_list]
glucose_list = df['glucose_level'].tolist()
for i, datetime_all in enumerate(all_dates):
    date_all = datetime_all.date()
    matching_datetimes = [datetime_df for datetime_df in datetime_list if datetime_df.date() == date_all]
    date_dict[i] = matching_datetimes if matching_datetimes else None


glucose_dict = {}
for i, matching_datetimes in date_dict.items():
    if matching_datetimes is not None:
        glucose_levels = [df.loc[df['datetime'] == datetime_df, 'glucose_level'].iloc[0] for datetime_df in matching_datetimes]
        glucose_dict[i] = glucose_levels
    else:
        glucose_dict[i] = None

fig.text(0.5, 0.95, 'Monday        Tuesday      Wednesday      Thursday      Friday       Saturday      Sunday', ha='center', fontsize=16)
fig.text(0.1, 0.6, 'Daily Glucose Profile', fontsize=12, rotation='vertical')
for i in range(0, num_days):
    if glucose_dict[i] is not None:
        ax = fig.add_subplot(spec[i])
        ax.plot(date_dict[i], glucose_dict[i], color='darkorange')
        ax.tick_params(axis='y', which='both', length=0, labelsize=7)
        ax.set_xticks([])
        ax.set_yticks([100, 150])

        # Add day number to the top left corner of the subplot
        day_number = all_dates[i].day
        ax.text(0.05, 0.8, str(day_number), transform=ax.transAxes, fontsize=12, fontweight='bold')

        # Draw horizontal lines at y = 75 and y = 175
        ax.axhline(y=75, color='gray', linestyle='--')
        ax.axhline(y=175, color='gray', linestyle='--')

        # Shade the region between the lines
        ax.fill_between(date_dict[i], 75, 175, color=(0.9, 0.9, 0.9), alpha=0.7)
        ax.patch.set_edgecolor('gray')  # Set frame color to gray
        ax.patch.set_linewidth(1)  # Set frame linewidth

plt.show()



# + [markdown] id="ZoVI0AkBNw9v"
# # 7. Advanced Visualization
#
# Now, we'll do some more advanced plotting.
#
# ## 7.1. Aggregated day-long glucose levels
#
# As a starting point, let's try to reproduce the below graph that you can export from the online Clarity webapp, which shows rough glucose levels over the course of an average day (aggregated over all days measured).
#
# <img src="https://imgur.com/qQwXJIv.png"></img>
#
# *This graph is taken directly from an exported PDF from the online webapp*
#
# First, we'll aggregate across all days and get aggregate glucose level statistics for every 15 minute interval. Then, we'll create a custom plot by leveraging lots of matplotlib functionality, including by poking deeper into the [Matplotlib architecture](https://www.aosabook.org/en/matplotlib.html) into the Artist layer and directly adding rounded rectangles to the plot (the error bars).
#
# Disclaimer: We aren't sure exactly how the error bars are derived, so the reproduced output is different.

# + cellView="form" colab={"base_uri": "https://localhost:8080/", "height": 319} id="DUSoIsoYIYFj" outputId="9557ed95-73d5-4342-aa64-30b2dd61c413"
#@title Aggregated day-long glucose level plot
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
import matplotlib.patches as patches

def dt_to_raw_min(dt_obj):
    return int(datetime.strftime(dt_obj, '%H')) * 60 + int(datetime.strftime(dt_obj, '%M'))

raw_mins = np.array([dt_to_raw_min(x) for x in df.datetime])

stats = []

for i in range(0, 24 * 60, 15):
    idxes_of_interest = np.where(np.logical_and(i < raw_mins, raw_mins < i + 15))[0]

    levels = np.array(df.glucose_level.iloc[idxes_of_interest])

    median_level = np.median(levels)

    mean_level = np.mean(levels)

    std_level = np.std(levels)
    stde_level = np.std(levels) / np.sqrt(levels.shape[0])

    stats.append([median_level, mean_level, std_level, stde_level])


# now let's actually plot

fig, ax = plt.subplots(figsize=(15, 4))

# background color in vertical-wise intervals accordingly
for i in range(0, 500, 100):
    plt.axhspan(i, i + 50, facecolor='whitesmoke')#, alpha=0.5)

for i in range(50, 550, 100):
    plt.axhspan(i, i + 50, facecolor='white')

# now do the actual data

# add 7 to make it all centered
plt.plot(range(7, 24 * 60 + 7, 15), [x[0] for x in stats], marker='o', markerfacecolor='black', markeredgecolor='white', color='black')

RECT_WIDTH = 5

for i, (median, mean, std, stde) in enumerate(stats):
    rect_center = 15 * i + 7
    rect_height = stde * 7
    rect = patches.FancyBboxPatch((rect_center - RECT_WIDTH / 2, mean - rect_height / 2),
                                  RECT_WIDTH, rect_height,
                                  boxstyle="round,pad=-0.0040,rounding_size=5.5",
                                  #boxstyle='round',
                                  linewidth=3, fc='silver', ec='silver')

    ax.add_patch(rect)

# now plot horizontal lines
plt.plot([0, 24 * 60], [180, 180], color='orange', linewidth=2)
plt.plot([0, 24 * 60], [70, 70], color='red', linewidth=2)


# now in the rest of the code we'll handle the ticks and borders etc.
plt.ylim(25, 425)

plt.xticks(ticks=np.linspace(0, 24 * 60, 9), labels=['12am', '3', '6', '9', '12pm', '3', '6', '9', '12am'])

# make sure both major and minor x ticks are visible
plt.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom=True,      # ticks along the bottom edge are off
    labelsize=16
)

# make major x ticks longer
plt.tick_params(
    axis='x',
    which='major',
    length=10
)

plt.yticks(np.linspace(100, 400, 4).astype(int))

plt.tick_params(
    axis='y',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    right=True,      # ticks along the bottom edge are off
    labelsize=12
)

# 2 and 1 minor ticks per major tick on x and y-axis, respectively (https://matplotlib.org/3.1.1/gallery/ticks_and_spines/major_minor_demo.html)
plt.gca().xaxis.set_minor_locator(AutoMinorLocator(3))
plt.gca().yaxis.set_minor_locator(AutoMinorLocator(2))

# disable vertical and horizontal grid lines
plt.gca().xaxis.grid(False, which='both')
plt.gca().yaxis.grid(False, which='both')

# get the y-axis ticks to appear on the right
plt.gca().yaxis.tick_right()

# show the borders of the box (https://stackoverflow.com/questions/9750699/how-to-display-only-a-left-and-bottom-box-border-in-matplotlib)
for side in ['left', 'right', 'top', 'bottom']:
    plt.gca().spines[side].set_visible(True)
    plt.gca().spines[side].set_color('black')

# https://stackoverflow.com/questions/42045767/how-can-i-change-the-x-axis-in-matplotlib-so-there-is-no-white-space
plt.margins(x=0)

plt.show()

# + [markdown] id="ky8uqx-L5iPu"
# *Above is a plot we created ourselves!*
#
# Looks like we can pretty faithfully recover the same data that's displayed online for us!

# + [markdown] id="quK9m2VKOAJ2"
# Now that we've seen high-level data, it's time to dig a bit deeper into day-level statistics.
#
# ## 7.2: Glucose levels throughout a particular day
#
# In this section, we reproduce the plot below that you can find when exporting data from the Dexcom Clarity website.
#
# <img src="https://i.imgur.com/w4x37Ua.png" width="1000"/>
#
# *Above is a plot taken directly from the Dexcom Clarity website!*
#
# Just enter any date you would like to plot, and the code below will plot its glucose levels, including missing values.

# + cellView="form" colab={"base_uri": "https://localhost:8080/", "height": 367} id="bNsSk5Pbp7ob" outputId="a95339c7-1ee4-4a08-a476-939058077b1a"
#@title Visualize single day glucose levels
date_to_visualize = "2022-04-06" #@param {type:"date"}

date_to_visualize_orig = date_to_visualize
date_to_visualize = '-'.join(date_to_visualize.split('-')[1:])

from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
import matplotlib.patches as patches

import warnings
warnings.filterwarnings("ignore")

# restore rcParams
# plt.rcParams.update(IPython_default)

def dt_to_raw_min(dt_obj):
    return int(datetime.strftime(dt_obj, '%H')) * 60 + int(datetime.strftime(dt_obj, '%M'))

raw_mins = np.array([dt_to_raw_min(x) for x in df.datetime])

idxes = np.where(df.datetime.apply(lambda x: datetime.strftime(x, '%m-%d')) == date_to_visualize)[0]
raw_mins = df.datetime.iloc[idxes].apply(lambda x: dt_to_raw_min(x))
glucose_levels = df.glucose_level.iloc[idxes]

# now let's actually plot

fig, ax = plt.subplots(figsize=(15, 4))

# background color in vertical-wise intervals accordingly
for i in range(0, 500, 100):
    plt.axhspan(i, i + 50, facecolor='whitesmoke')

for i in range(50, 550, 100):
    plt.axhspan(i, i + 50, facecolor='white')

# now do the actual data

gaps = list(np.where(np.diff(raw_mins) > 10)[0] + 1)
cur_start = 0
for gap in (gaps + [len(raw_mins)]):
    plt.plot(raw_mins.iloc[cur_start:gap],
             glucose_levels.iloc[cur_start:gap], color='black',
             linewidth=2)
    cur_start = gap

# now plot horizontal lines
plt.plot([0, 24 * 60], [180, 180], color='orange', linewidth=2)
plt.plot([0, 24 * 60], [70, 70], color='red', linewidth=2)


# now in the rest of the code we'll handle the ticks and borders etc.
plt.ylim(25, 425)

plt.xticks(ticks=np.linspace(0, 24 * 60, 9), labels=['12am', '3', '6', '9', '12pm', '3', '6', '9', '12am'])

# make sure both major and minor x ticks are visible
plt.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom=True,      # ticks along the bottom edge are off
    labelsize=16
)

# make major x ticks longer
plt.tick_params(
    axis='x',
    which='major',
    length=10
)

plt.yticks(np.linspace(100, 400, 4).astype(int))

plt.tick_params(
    axis='y',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    right=True,      # ticks along the bottom edge are off
    labelsize=12
)

# 2 and 1 minor ticks per major tick on x and y-axis, respectively (https://matplotlib.org/3.1.1/gallery/ticks_and_spines/major_minor_demo.html)
plt.gca().xaxis.set_minor_locator(AutoMinorLocator(3))
plt.gca().yaxis.set_minor_locator(AutoMinorLocator(2))

# disable vertical and horizontal grid lines
plt.gca().xaxis.grid(False, which='both')
plt.gca().yaxis.grid(False, which='both')

# get the y-axis ticks to appear on the right
plt.gca().yaxis.tick_left()

# show the borders of the box (https://stackoverflow.com/questions/9750699/how-to-display-only-a-left-and-bottom-box-border-in-matplotlib)
for side in ['left', 'right', 'top', 'bottom']:
    plt.gca().spines[side].set_visible(True)
    plt.gca().spines[side].set_color('black')

# https://stackoverflow.com/questions/42045767/how-can-i-change-the-x-axis-in-matplotlib-so-there-is-no-white-space
plt.margins(x=0)

date_to_visualize_fmted = datetime.strftime(datetime.strptime(date_to_visualize_orig, '%Y-%m-%d'), '%a, %b %-d, %Y')

plt.title(f'{date_to_visualize_fmted}', fontsize=15, fontweight='bold')

plt.show()

# + [markdown] id="gSVQJoZ4CTTF"
# *Above is a plot we created ourselves!*
#
# # 8. Outlier Detection and Data Cleaning
#
# Finally, we'll be checking for anomalies in the data. This is a crucial step in any sort of analysis, as we want to make sure that all of the data we are analyzing are legit.
#
# Outliers are data points that deviate significantly from the rest of the dataset. They may indicate anomalies or errors in the data collection process.
#
# Conditional Outlier Detection, $P(\text{BPM}_{t}\mid\text{BPM}_{t-1})$
#
# This method assesses each BPM reading in relation to its preceding value, leveraging the serial correlation inherent in BPM data.
# Methods for Conditional Outlier Detection:
#
# - Change Detection:
#   - Calculates the difference between consecutive BPM readings.
#   - Large deviations from the expected range of fluctuation may indicate outliers.
#
# - Time Series Analysis:
#   - Utilizes advanced techniques like ARIMA modeling to forecast BPM values.
#   - Identifies observations significantly deviating from the model's predictions as outliers.
#
# In the case of BPM data, conditional methods can be insightful due to the temporal relationship between successive readings.
#
# The conditional outlier detection process involves computing the difference between consecutive BPM readings:
#
# $$\Delta \text{glucose level}_t = \text{glucose level}_t - \text{glucose level}_{t-1}$$
#
# Subsequently, a threshold is determined based on the standard deviation of these differences:
#
# $$\text{Threshold} = Mean(\Delta \text{glucose level}) \pm k × StdDev(\Delta \text{glucose level})$$
#
# where $k$ represents the number of standard deviations to consider. The rationale behind this approach is that while glucose level naturally fluctuates from one reading to the next, extreme changes within a short interval are unexpected unless there's an unusual event or measurement error.
#
# **Step 1**: Let us start our conditional outlier detection by looking at the distribution of glucose level differences.

# + colab={"base_uri": "https://localhost:8080/", "height": 582} cellView="form" id="qdj8BFKC9PKU" outputId="9d51bf25-d524-4863-9ffb-0b314f5f8314"
#@title Visualize the distribution of glucose level differences

df['glucose_level_diff'] = df['glucose_level'].diff()

glucose_level_diff = df['glucose_level_diff'].dropna()  # Drop NA values resulting from diff()
plt.style.use('default')
plt.figure(figsize=(10, 6))
plt.hist(glucose_level_diff, bins=80, alpha=0.7)
plt.title('Distribution of glucose level Differences')
plt.xlabel('Glucose Level Difference')
plt.ylabel('Frequency')
plt.show()

mean_diff = glucose_level_diff.mean()
std_diff = glucose_level_diff.std()

threshold = 4 * std_diff
threshold

# + [markdown] id="edwCJNm_B3sk"
# In the cell above, we have defined the threshold to be 4 times the standard deviation of the distribution, which would be approximately 10.92.
#
# **Step 2**: Next, let's find which values are the conditional outliers and when they occured, this would be the values which are higher than our threshold

# + colab={"base_uri": "https://localhost:8080/", "height": 457} cellView="form" id="PuEM-zka-AaN" outputId="1a05378c-da17-44f1-fd5f-b708ad0e5fd4"
#@title Find out which values are the conditional outliers and when they occured

conditional_outliers = df[abs(df['glucose_level_diff']) > threshold]
conditional_outliers

# + [markdown] id="EcliD-VICix_"
# **Step 3**: Plot the anomaly data points.
#
# Here we will plot the anomalies that we identified above, and mark them in a different color to see where they occured.

# + colab={"base_uri": "https://localhost:8080/", "height": 567} cellView="form" id="2LAFVsdI-J0z" outputId="95e4ddf2-4d8d-4005-aadf-6200df8f69fa"
#@title Visualize the anomalies

plt.figure(figsize=(16,8))

with plt.style.context('ggplot'):

    plt.plot(df.datetime, df.glucose_level, linewidth=.75)
    plt.scatter(conditional_outliers.datetime, conditional_outliers.glucose_level, s=10, c='blue')
    plt.ylim(top=230)

    plt.title('Glucose levels over time', fontsize=15)

    plt.xlabel('Time')
    plt.ylabel('Glucose (mg/dL)')
    plt.show()

# + [markdown] id="0p4cvTwA_i2g"
# Understanding the context of outliers is crucial for interpreting their significance. Outliers could stem from various sources such as measurement errors, physiological events, or artifacts. Recognizing the source can guide appropriate handling in analysis and drive enhancements in data collection or processing methods.
#
# In our scenario, where the data was synthetically generated, the conditional outliers lack clinical significance. Therefore, while they may impact statistical analyses, they don't represent real-world physiological variations.
#
# **Step 4**: Lastly, we remove these outliers from our data. This will be important if we want to use the data for further investigation.

# + colab={"base_uri": "https://localhost:8080/", "height": 424} cellView="form" id="zhz7gdID_aF8" outputId="bde6d052-e584-4117-a16e-74ade7bc4a64"
#@title Clean the anomalies
outliers = np.array(conditional_outliers.index)
cleaned_df = df[~df.index.isin(outliers)]
cleaned_df.drop(columns=['glucose_level_diff'], inplace=True)
cleaned_df

# + [markdown] id="AdPn9COMAwz3"
# Here we have the cleaned glucose level data.

# + [markdown] id="Relv4GLFLATI"
# # 9. Statistical Data Analysis
#
# Data isn't much without some analysis, so we're going to do some in this section.
#
# DISCLAIMER: the analyses below may not be 100% biologically or scientifically grounded; the code is here to assist in your process, if you are interested in asking these kinds of questions.
#
# ## 9.1: Blood glucose level vs. time of day (day vs. night)
#
# Since people (generally) sleep at night and eat during the day, one hypothesis is that glucose values will be different during the day compared to the night. Let's see if this is true. First, we will get the glucose values for each day and separate them into day time and night time values. We define day time as 9AM to 12AM (midnight) and night time as 12AM (midnight) to 9 am here, although these values can be adjusted as dayStart and dayEnd in the code.

# + id="9w8V7ATnUazz"
from datetime import time
import scipy.stats as stats

dayStart = time(9, 00, 00)
dayEnd = time(0, 00, 00)

allTimes = pd.to_datetime(df.loc[:,'datetime']).dt.time

if dayStart < dayEnd:
    mask = (allTimes >= dayStart) & (allTimes <= dayEnd)
else:
    mask = (allTimes >= dayStart) | (allTimes <= dayEnd)

df["Time of Day"] = mask
df["Time of Day"] = df["Time of Day"].map({True: 'Day', False: 'Night'})

# + [markdown] id="lVPSd4-aGtC9"
# Let's use [seaborn](https://seaborn.pydata.org/) to generate a scatter plot to take an initial look.

# + colab={"base_uri": "https://localhost:8080/", "height": 524} id="7aEGSXQ5HCj4" outputId="5b085276-37a2-4dc6-df71-a17948d358a1"
sns.catplot(x="Time of Day", y="glucose_level", data=df)

# + [markdown] id="U3koCLm3HFcJ"
# Now, since we're compmaring two means, we could use a one-way ANOVA (analysis of variance). For this to be a valid analysis, we have to ensure the data is [independent, normally distributed, and homoscedastic](https://www.statisticssolutions.com/free-resources/directory-of-statistical-analyses/anova/).
#
# Let's check normality first.

# + colab={"base_uri": "https://localhost:8080/", "height": 887} id="a57xSQ4zMh0_" outputId="f7180244-2dba-464d-91a2-122d4f428f99"
plt.hist(df.loc[df["Time of Day"] == 'Day']['glucose_level'])
plt.title("Day Time")
plt.show()

plt.hist(df.loc[df["Time of Day"] == 'Night']['glucose_level'])
plt.title("Night Time")
plt.show()

# + [markdown] id="kLj4_lImNEWL"
# Since the data do not look normally distributed, we can use a [Kruskal-Wallis test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html#scipy.stats.kruskal) instead of an ANOVA.

# + colab={"base_uri": "https://localhost:8080/"} id="NQ8rMfK4HFyh" outputId="05688437-b24d-47da-81d0-1c362d199d85"
stats.kruskal(df.loc[df["Time of Day"] == 'Day']['glucose_level'],df.loc[df["Time of Day"] == 'Night']['glucose_level'])

# + [markdown] id="GGabjOuHNjxG"
# Thus we can reject the null hypothesis that the population medians do not significantly differ (p<\0.05), and that night time values are different from day time values.
#
# ## 9.2: Blood glucose variability vs. time of day (day vs. night)
#
# We also might have an intuition that during the night glucose levels are calmer and vary less in general. Let's see if this is true. We'll check the variability for whether they exhibit significant differences across both groups, as done analogously above. We represent the variability with the standard deviation in the rate of change in the blood glucose levels, as done in [[Clarke & Kovatchev, 2009]](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2903980/).

# + id="HARIE4Svacgo"
from datetime import time
import scipy.stats as stats

dayStart = time(9, 00, 00)
dayEnd = time(0, 00, 00)

allTimes = pd.to_datetime(df.loc[:,'datetime']).dt.time

if dayStart < dayEnd:
    mask = (allTimes >= dayStart) & (allTimes <= dayEnd)
else:
    mask = (allTimes >= dayStart) | (allTimes <= dayEnd)

df["Time of Day"] = mask
df["Time of Day"] = df["Time of Day"].map({True: 'Day', False: 'Night'})

rates_of_change = [(df.glucose_level.iloc[i+1] - df.glucose_level.iloc[i]) / ((df.datetime.iloc[i+1] - df.datetime.iloc[i]).seconds / 60) for i in range(df.glucose_level.shape[0] - 1)]
df['Rates of change'] = rates_of_change + [0]  # add extra element to make shapes match

# + colab={"base_uri": "https://localhost:8080/", "height": 525} id="xOZDb4WQawPQ" outputId="7486b650-74a7-4f13-93f8-aed1f10608be"
sns.catplot(x="Time of Day", y="Rates of change", data=df)

# + [markdown] id="N4rxqlKWd8wk"
# From the plot, it looks like the rate of change tends to vary much more during the day! Let's check if this is significant with the F-test, assuming both distributions are normal-distributed.
#
# Note for stats geeks: The F-test works out-of-the-box with variances of the two groups, but since variance is a monotonic + increasing function of standard deviation, it would work out equivalently if we (in theory) went through the trouble of re-deriving the F-distribution and its PDF for standard deviation instead of variance. Therefore, we're still making a statement about standard deviations!

# + colab={"base_uri": "https://localhost:8080/"} id="FjhydneWa2J-" outputId="e0951fd5-974b-45c6-8f78-ab579fdde6bd"
from scipy.stats import f_oneway
from scipy.stats import f

day_glucoses = np.array(
    df['Rates of change'].iloc[np.where(df['Time of Day'] == 'Day')[0]]
)
night_glucoses = np.array(
    df['Rates of change'].iloc[np.where(df['Time of Day'] == 'Night')[0]]
)

# here we assume that the day variance is greater than the night variance
# if this assumption is violated, the order has to switch

F = np.var(day_glucoses) / np.var(night_glucoses)

df1 = day_glucoses.shape[0] - 1
df2 = night_glucoses.shape[0] - 1

p_value = 1 - f.cdf(F, df1, df2)

print(f'F-value (ratio between variances): {F:.3g}')
print(f'p-value: {p_value:.3g}')

# + [markdown] id="aj4OofwJlhmp"
# Looks significant!
#
# Note: statistical test code was adapted from [this StackOverflow post](https://stackoverflow.com/questions/21494141/how-do-i-do-a-f-test-in-python), though the top answer is incorrect (so the version here is fixed).
