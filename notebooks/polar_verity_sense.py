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

# + [markdown] id="LgdgFSzo9SYs"
# # Polar Verity Sense: Guide to data extraction and analysis

# + [markdown] id="H7zTf9DPDIXS"
# <img src='https://i.imgur.com/LbNai7M.jpg' height="500">
# <img src='https://i.imgur.com/JiO4aLG.jpg' height="500">
#
#

# + [markdown] id="naL5gEN2DaZ4"
# *^ (Left): A picture of the polar verity sense heart rate monitor (Right): Worn on arm^*

# + [markdown] id="XI6MGYdH9-pH"
# The [Polar Verity Sense](https://www.polar.com/en/products/accessories/polar-verity-sense) is a $89 armband heart rate sensor that has often been reviewed as a viable alternative to ECG chest-strap style monitors. Portable and comfortable, it can be worn on the arm (as pictured above) or near the temple (when attached to goggles) while performing exercises indoors, outdoors, and even in the pool.
#
# Beyond its accuracy as a heart rate monitor, the Verity Sense's utility lies in its interface with Polar's official app, which helps keep track of data collected from the sensor as well as providing plenty of useful visualizations and analytics. 
#
# In the following sections, we will present what we have learned from using the Verity Sense and how to extract its data for visualizations and statistical analyses. With the [wearipedia library](http://wearipedia.com/wearables/polar-verity-sense), this process will only require your username and password!

# + [markdown] id="qfKAFMwf-cm2"
# We will be able to extract the following parameters (in bold are parameters we will be using in this notebook). Per Activity means one measurement through a single session of exercise. Per second means one measurement every second throughout an exercise.
#
# Parameter Name  | Sampling Frequency 
# -------------------|-----------------
# Calories |  Per Activity
# Duration | Per Activity
# Sessions | Per day
# Continuous Heart Rate |  Per second 
#

# + [markdown] id="I_NoC7rF_G64"
# In this guide, we sequentially cover the following **nine** topics:
#
# 1. **Setup**<br>
# 2. **Authentication and Authorization**<br>
#    - Requires only username and password, no OAuth.
# 3. **Data Extraction**<br>
#   - We get data via `wearipedia` in a couple lines of code.
# 4. **Data Exporting**
#   - We export all of this data to file formats compatible by R, Excel, and MatLab.
# 5. **Adherence**
#     - We simulate non-adherence by dynamically removing datapoints from our simulated data.
# 6. **Visualization**
#     - We create a simple plot to visualize our data.
# 7. **Advanced Visualization** <br>
#   - 7.1 Heart Rate Zones during an Exercise Session <br>
#   - 7.2 Visualizing Heart Rate Averages and Sessions over a Month <br>
#   - 7.3 Visualizing Continuous Heart Rate data <br>
# 8. **Outlier Detection and Data Cleaning**
#     - We detect outliers in our data and filter them out.
# 9. **Statistical Data Analysis** <br>
#   - 9.1 Analyzing correlation between Average Heart Rate and Calories Burned per Minute <br>
#   - 9.2 Analyzing correlation between Duration of Workouts and Calories Burned
#   - 9.3 Analyzing how activity intensity compares in first half and second half of a session
#
# **Note that we are not making any scientific claims here as our sample size is small and the data collection process was not rigorously vetted (it is our own data), only demonstrating that this code could potentially be used to perform rigorous analyses in the future.**
#
# Disclaimer: this notebook is purely for educational purposes. All of the data currently stored in this notebook is purely *synthetic*, meaning randomly generated according to rules we created. Despite this, the end-to-end data extraction pipeline has been tested on our own data, meaning that if you enter your own email and password on your own Colab instance, you can visualize your own *real* data. That being said, we were unable to thoroughly test the timezone functionality, though, since we only have one account, so beware.

# + [markdown] id="xKwooMsw90yZ"
#
#
# # 1. Setup

# + [markdown] id="QbaGwQiCcOHz"
# ## Participant Setup

# + [markdown] id="Hj6CmfBJcTHY"
# Dear Participant,
#
# Once you unbox your Polar Verity Sense, please set up the device by following the video:
#
#
# *   Video Guide: https://www.youtube.com/watch?v=wiA_ucJJV7Y&t
#
#
# Make sure that your phone is paired to it using the Polar Flow login credentials (email and password) given to you by the study coordinator.
#
# Best,
#
# Wearipedia

# + [markdown] id="yNaCJSmVcRM5"
# ## Data Receiver Setup

# + [markdown] id="E1DMSOoddDFK"
# Please follow the below steps:
#
# 1. Create an email address for the participant, for example `foo@email.com`
# 2. Create a Polar Flow account with the email `foo@email.com` and some random password.
# 3. Keep `foo@email.com` and password stored somewhere safe.
# 4. Distribute the device to the participant and instruct them to follow the participant setup letter above.
# 5. Install the `wearipedia` Python package to easily extract data from this device.

# + colab={"base_uri": "https://localhost:8080/"} id="-MYY4ukfbH-K" outputId="15732c15-21d2-499f-90c9-3dea7bf247cb"
# !pip install git+https://github.com/Stanford-Health/wearipedia

# + [markdown] id="xVLQb6ux-hDj"
# # 2. Authentication and Authorization
# To obtain access to data, authorization is required. All you'll need to do here is just put in your email and password for your Polar Verity Sense device. We'll use this username and password to extract the data in the sections below.

# + id="_45KxrBEGbfX"
#@title Enter Polar login credentials

email_address = '' #@param {type:"string"}
password = ''#@param {type:"string"}

# + [markdown] id="q116WA9g-x1J"
# # 3. Data Extraction

# + [markdown] id="H4uekNkDKQGo"
# Data can be extracted via [wearipedia](https://github.com/Stanford-Health/wearipedia/), our open-source Python package that unifies dozens of complex wearable device APIs into one simple, common interface.
#
# First, we'll set a date range and then extract all of the data within that date range. You can select whether you would like synthetic data or not with the checkbox.

# + id="I_v0JMCAenpX"
#@title Enter start and end dates (in the format yyyy-mm-dd)

#set start and end dates - this will give you all the data from 2000-01-01 (January 1st, 2000) to 2100-02-03 (February 3rd, 2100), for example
start_date='2022-03-01' #@param {type:"string"}
end_date='2022-06-11' #@param {type:"string"}
synthetic = True #@param {type:"boolean"}

# + id="haj-SgI9fEJY" colab={"base_uri": "https://localhost:8080/"} outputId="ea50a88a-9bbc-4559-9efd-ea2df9e97041"
import wearipedia

device = wearipedia.get_device("polar/verity_sense")

if not synthetic:
  device.authenticate({"email": email_address, "password": password})
  params = {"start_date": start_date, "end_date": end_date}
  data = device.get_data("sessions", params = params)
else:
  params = {"start_date": start_date, "end_date": end_date}
  data = device.get_data("sessions", params = params)

# + [markdown] id="HwWvlNBLEhyE"
# To get a list of the days that actually have data, we can list out the keys for the returned data. Note it might not be feasible to actually print out the entire set of returned data, as it can be quite large.

# + colab={"base_uri": "https://localhost:8080/"} id="D5G_5jR6_BAp" outputId="41c0b2d8-d021-4edd-9eae-a79ce73d6869"
print(data.keys())

# + [markdown] id="cfUa31-NJLH6"
# # 4. Data Exporting

# + [markdown] id="FY0XyxmxdowU"
# In this section, we export all of this data to formats compatible with popular scientific computing software (R, Excel, Google Sheets, Matlab). Specifically, we will first export to JSON, which can be read by R and Matlab. Then, we will export to CSV, which can be consumed by Excel, Google Sheets, and every other popular programming language.
#
# ## Exporting to JSON (R, Matlab, etc.)
#
# Exporting to JSON is fairly simple. We export each datatype separately and also export a complete version that includes all simultaneously.

# + id="MUP8QbnmtdF6"
import json

hrs = [data[k]['heart_rates'] for k in data.keys()]
calories = [data[k]['calories'] for k in data.keys()]
hr_avgs = [sum(data[k]['heart_rates']) / (data[k]['minutes'] * 60) for k in data.keys()]
durations = [data[k]['minutes'] for k in data.keys()]

json.dump(list(data.keys()), open("dates.json", "w"))
json.dump(calories, open("calories.json", "w"))
json.dump(hrs, open("hrs.json", "w"))
json.dump(hr_avgs, open("hr_avgs.json", "w"))
json.dump(durations, open("durations.json", "w"))

complete = {
    "dates": list(data.keys()),
    "calories": calories,
    "hrs": hrs,
    "hr_avgs": hr_avgs,
    "durations": durations,
}


json.dump(complete, open("complete.json", "w"))

# + [markdown] id="lywBjc_DBDTw"
# ## Exporting to CSV and XLSX (Excel, Google Sheets, R, Matlab, etc.)

# + [markdown] id="Z6wODk-cBIW_"
# Exporting to CSV/XLSX will require us to first process the data into a pandas dataframe format, which can then be converted into our desired file type.
#
# Here we will export three separate files: the first will contain heart rate data (labeled by date and time), and the second will contain daily summary data such as calories, average heart rate, and minutes (labeled by date). Additionally, we will make a third dataframe containing only heart rate data for one session (of your choice) to help us with further visualizations and analysis in the following sections of this notebook.

# + id="ZwrOmk0GFVGK"
day = "2022-03-01" #@param {type: "string"}

# set the day of interest automatically if not specified
if day == "":
  day = list(data.keys())[0]

# + id="S2T9oM7Vdz1w" colab={"base_uri": "https://localhost:8080/", "height": 1000} outputId="df798f96-e663-46fe-a86f-7040d45d9479"
import pandas as pd
from datetime import timedelta
from datetime import datetime
import numpy as np
import copy

# Third dataframe and list of dataframes:
hr_df = None
hr_dfs = []

# 1. First dataframe
# we initialize a variable all_df that will hold all the session data for this dataframe
all_df = None
for key in data.keys():
  # determine duration of a workout
  duration = data[key]['minutes']*60
  
  # set the start time of every session to 0s
  start_time = timedelta(hours=0, minutes=0, seconds=0)

  # create times columns which is the series of seconds in the duration
  times = [str(start_time + timedelta(seconds=i)).zfill(8) for i in range(int(duration))]
  tdf = pd.DataFrame(zip(times,data[key]['heart_rates']),columns=['time','bpm'])

  # mapping is a function that will format the time to include the date of exercise
  mapping = lambda x: np.datetime64(key+ " " + x)
  tdf["time"] = tdf["time"].apply(mapping)

  # append the new dataframe for the session to the main dataframe
  # save the dataframe as hr_df which is our "third" dataframe
  if key == day:
    hr_df = tdf
  if type(all_df) == type(None):
    all_df = tdf
  else:
    all_df = all_df.append(tdf)
  hr_dfs.append(copy.deepcopy(tdf))
#print("DataFrame 1: All heart rates")
#display(df1)

# 2. Second dataframe
df2 = None
for key in data.keys():
  # calculate the average heart rate for this session
  avg_rate = sum(data[key]['heart_rates']) / (data[key]['minutes'] * 60)

  # if the dataframe is null, create. Otherwise, append the new session summary to it
  if type(df2) == type(None):
    df2 = pd.DataFrame([[key,data[key]['minutes'],data[key]['calories'], avg_rate]],columns=['day','minutes','calories', 'avg_rate'])
  else:
    tdf = pd.DataFrame([[key,data[key]['minutes'],data[key]['calories'], avg_rate]],columns=['day','minutes','calories', 'avg_rate'])
    df2 = df2.append(tdf)
#print("DataFrame 2: Summary Data")
#display(df2)

# 3. Third dataframe
print("DataFrame 3: Single session heart rate")
display(hr_df)

# + [markdown] id="lX5c4u2F-Kze"
# With this, we have retrieved all the data we need! Now we can start visualizing our data.

# + [markdown] id="00EXnoNha36z"
# # 5. Adherence

# + [markdown] id="UYv17T2osq2N"
# The device simulator already automatically randomly deletes exercise session data. In this section, we will simulate non-adherence over longer periods of time from the participant (day-level and week-level). Additionally, while unlikely, there is a potential for the heart rate monitor to fall off mid session and for the participant to not realize. We will simulate this as well.
#
# Then, we will detect these instances of non-adherence and give a Pandas DataFrame that concisely describes when the participant has had their device on and off throughout the entirety of the time period, allowing you to calculate how long they've had it on/off etc.
#
# We will simulate non-adherence by deleting or inserting 0s (indicating sensor removal) from a certain % of blocks either at the day level or week level, with user input.

# + id="xfyU84Fos63M"
#@title Non-adherence simulation
block_level = "day" #@param ["day","week"]
adherence_percent = 0.65 #@param {type:"slider", min:0, max:1, step:0.01}

# + id="7cK3DZV9tINS"
import numpy as np
import pandas as pd
from datetime import datetime
import copy
import random

if block_level == "day":
  block_length = 1
elif block_level == "week":
    block_length = 7

dates = np.array(list(data.keys()))

num_blocks = len(dates) // block_length

num_blocks_to_remove = int((1-adherence_percent) * num_blocks)

remove = np.random.choice(dates, replace=False, size=num_blocks_to_remove)

adhered_data = copy.deepcopy(data)
adhered_dates = copy.deepcopy(list(data.keys()))

for key in remove:
  # some non-adherence will be completely removed data sessions
  if np.random.rand() < 0.8:
    adhered_data.pop(key)
    adhered_dates.remove(key)
  # other non-adherence may be because the device stopped recording data part way through the session
  else:
    adhered_data[key]['heart_rates'] += (list(np.zeros(100)))

# + [markdown] id="fk-Kpjrr3FIQ"
# And now we have significantly fewer datapoints! This will give us a more realistic situation, where participants may not use their device for days or weeks at a time.
#
# Now let's detect non-adherence. We will plot the days when the participant uses the watch and when they do not, as well as the days where they record complete sessions (i.e. they do not remove the sensor partway through their session).

# + colab={"base_uri": "https://localhost:8080/", "height": 409} id="M5qPB71U4gLv" outputId="46aa38a7-a31d-4ac5-a34c-4e46a7f4ff60"
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd

datelist = pd.date_range(start_date, end_date)
is_wearing = []
print(adhered_dates)
for date in datelist:
  day = datetime.strftime(date, "%Y-%m-%d")
  if day in adhered_dates:
    if 0.0 in adhered_data[day]['heart_rates']:
      is_wearing.append(0)
    else:
      is_wearing.append(1)
  else:
    is_wearing.append(0)

plt.figure(figsize=(12, 6))
plt.plot(datelist,is_wearing,drawstyle="steps-mid")

# + [markdown] id="BbYnd1Lza5us"
# # 6. Visualization

# + [markdown] id="_Z9FANojswgS"
# We've extracted lots of data, but what does it look like?
#
# In this section, we will be visualizing our three kinds of data in a simple, customizable plot! This plot is intended to provide a starter example for plotting, whereas later examples emphasize deep control and aesthetics.

# + colab={"base_uri": "https://localhost:8080/", "height": 679} cellView="form" id="j6BMkOXgfGCH" outputId="48fbcc74-70f1-4ce6-c281-9f5412205337"
#@title Basic Plot
feature = "heart rate" #@param ["heart rate", "average heart rate", "calories"]
start_date = "2022-04-06" #@param {type:"date"}
time_interval = "one day" #@param ["one day", "one week", "full time"]
smoothness = 0.05 #@param {type:"slider", min:0, max:1, step:0.01}
smooth_plot = True #@param {type:"boolean"}

from scipy.special import y0
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
from scipy.ndimage.filters import gaussian_filter1d

if time_interval == "one day":
  datelist = pd.date_range(start_date, periods=2)
elif time_interval == "one week":
  datelist = pd.date_range(start_date, periods=8)
elif time_interval == "full time":
  datelist = pd.date_range(start_date, end_date)

plt.figure(figsize=(16,10))

for d in datelist:
  end = d + timedelta(days=1)
  start = d

  if feature == "heart rate":
    tempdf = all_df[all_df["time"].map(lambda x: datetime.strptime(datetime.strftime(x,"%Y-%m-%d"),"%Y-%m-%d") >= start and datetime.strptime(datetime.strftime(x,"%Y-%m-%d"),"%Y-%m-%d") <= end)]
    y = tempdf["bpm"]
    x = list(range(len(y)))#tempdf["time"]
    sigma = 200*smoothness
  elif feature == "average heart rate":
    tempdf = df2[df2["day"].map(lambda x: datetime.strptime(x,"%Y-%m-%d") <= end and datetime.strptime(x,"%Y-%m-%d") >= start)]
    y = tempdf["avg_rate"]
    x = tempdf["day"]
    sigma = 5*smoothness
  elif feature == "calories":
    tempdf = df2[df2["day"].map(lambda x: datetime.strptime(x,"%Y-%m-%d") <= end and datetime.strptime(x,"%Y-%m-%d") >= start)]
    y = tempdf["calories"]
    x = tempdf["day"]
    sigma = 5*smoothness

  if smooth_plot:
    y = list(gaussian_filter1d(y, sigma=sigma))
  
  if feature == "heart rate":
    plt.plot(x, y)
  else:
    plt.bar(x,y)

title_fillin = feature
if time_interval == "one day":
  plt.title(f"{title_fillin} on {start_date}",fontsize=20)
else:
  plt.title(f"{title_fillin} from {start_date} to {datetime.strftime(end,'%Y-%m-%d')}",fontsize=20)
plt.xlabel("Time")
plt.ylabel(title_fillin[:-1])

# + [markdown] id="RwmVAxHm_cC_"
# This plot allows you to quickly scan various sessions of your data and for different kinds of measurements (heart rate, average heart rate, and calories), which enables easy and fast data exploration.

# + [markdown] id="xCiqKLIq-0_i"
# # 7. Advanced Visualization

# + [markdown] id="OHjeuQmiKFrZ"
# ## 7.1 Visualizing Participants Heart Rate Zones during Exercise

# + [markdown] id="vJxOApUv3ak5"
# One of the graphs the you see when you open an exercise session on polar is a bar chart of heart rate zone durations, or how long your heart rate zone stayed in some range throughout your exercise. It looks something like this:

# + [markdown] id="dN9IAHg5YeMB"
#
# <img src='https://i.imgur.com/RBqN6pZ.png' width='750px'>

# + [markdown] id="zLaER1dCQO23"
# At the bottom (gray) zone is the amount of time spent with heart rate between 100-120 bpm, the next being 120-140 bpm, then 140-160 bpm, 160-180 bpm, and finally 180-200 bpm.
#
# We will want the following data:
#
# *   The zones we want to plot
# *   Time in each heart rate zone
#
# Polar uses the following zones: 100-120 bpm, 120-140 bpm, 140-160 bpm, 160-180 bpm, 180-200 bpm, which is what we will be using as well. 
#
# To get the time spent in each heart rate zone, we can use the pandas groupby function to aggregate the heart rates by zones, and then count the number of entries in each group. Since the continuous heart rate data has an entry for every second, this directly gives us the time spent in each heart rate zone.

# + colab={"base_uri": "https://localhost:8080/", "height": 121} id="dhTTlNxHnJTI" outputId="bc71adbe-8e16-4375-ee3c-c0ad913d8f4a"
import pandas as pd

ranges = [100,120,140,160,180,200]
z1 = hr_df.groupby(pd.cut(hr_df.bpm, ranges), as_index=False).count()
z2 = pd.to_datetime(z1['bpm'], unit='s')
z2 = pd.DataFrame(z2.dt.strftime('%H:%M:%S'))
display(z2['bpm'])

# + [markdown] id="J3yqY-_zbHNE"
# z2 is exactly the heart rate zone data, as we wanted. Now we want to set up two more python arrays that we will use as the y-axis labels, shown here. This data is already available in our z2 series, so we can extract them as necessary.

# + id="FDnEkmZmNTuX"
zones = ['1','2','3','4','5']
times = [e for e in z1['bpm']][::-1]
time_labels = [e for e in z2['bpm']]

# + [markdown] id="oy4glSixQzZo"
# The zones array will be the left side y-axis label, and the times will be the actual data. We can place these in a pandas dataframe so it will be easier to plot using the python matplotlib library.

# + id="RSzx9FzvQ5Xa"
import pandas as pd

d = {"zones":zones, "times": times}
df1 = pd.DataFrame(data=d)
df1.set_index('zones', inplace=True)

# + [markdown] id="fMODQ5pbRejn"
# And now we can finally plot the data. We will be using the [horizontal bar plot](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.barh.html) from matplotlib, barh. Since we already have the data we need, we can use barh to directly plot the necessary bars, after which we can apply our desired styling to make the graph look like the one pictured.

# + colab={"base_uri": "https://localhost:8080/", "height": 315} id="ln4Hmt2eMaHH" outputId="bad029da-3015-48c0-f957-5158373ecb72"
from matplotlib import pyplot as plt, patches
import seaborn as sns

sns.set_theme(style="dark")
fig1, ax = plt.subplots(figsize=(16,6))
clrs = ["#c0c8c8", "#46c7ee", "#6acc2b", "#f9bf1c", "#de0f5b"][::-1] #colors array for the zones

#plot the base graph
plt. margins(y=0)
plt.xlim(0, sum(i for i in df1["times"])) #this sets the graph to have its width equal to the total session time
bar1 = ax.barh(df1.index[::-1], df1["times"][::-1], align="center", height=1., color = clrs[::-1]) #plot the bar graph
plt.xticks(color='w') #hide the x tick labels
plt.yticks(color='w')
ax.tick_params(axis='both', labelsize=25, pad=12.5)

# Adding the times for each zone
for i in range(len(time_labels)):
  plt.text(.97,0.15 + 0.15*i,time_labels[i],fontsize=18,transform=fig1.transFigure,
          horizontalalignment='center', weight=300)

#add colored backgrounds behind each zone
rect = patches.Rectangle((0, 0.805), 0.5, 0.194, color='#de0f5b')
rect2 = patches.Rectangle((0, 0.602), 0.5, 0.198, color='#f9bf1c')
rect3 = patches.Rectangle((0, 0.402), 0.5, 0.194, color='#6acc2b')
rect4 = patches.Rectangle((0, 0.202), 0.5, 0.194, color='#46c7ee')
rect5 = patches.Rectangle((0, 0.0), 0.5, 0.195, color='#c0c8c8')

lax = fig1.add_axes([0.08,0.126,1.,0.752], anchor='NE', zorder=-1)
lax.add_patch(rect)
lax.add_patch(rect2)
lax.add_patch(rect3)
lax.add_patch(rect4)
lax.add_patch(rect5)
lax.axis('off')

#add gray rectangles behind times 
b1 = patches.Rectangle((0, 0.805), 0.5, 0.194, color='#eaeaf2')
b2 = patches.Rectangle((0, 0.602), 0.5, 0.194, color='#eaeaf2')
b3 = patches.Rectangle((0, 0.402), 0.5, 0.194, color='#eaeaf2')
b4 = patches.Rectangle((0, 0.202), 0.5, 0.194, color='#eaeaf2')
b5 = patches.Rectangle((0, 0.0), 0.5, 0.194, color='#eaeaf2')
rax = fig1.add_axes([.8,0.126,.42,0.752], anchor='NE', zorder=-1)
rax.add_patch(b1)
rax.add_patch(b2)
rax.add_patch(b3)
rax.add_patch(b4)
rax.add_patch(b5)
rax.axis('off')

#set grid lines separating bars
ax.set_yticks([0.5,1.5,2.5,3.5,4.5], minor=True)
ax.yaxis.grid(True, which='minor')

# + [markdown] id="5W8UarpyyawJ"
# This plot is important because it gives us a quick way to understand the general distribution of activity levels throughout a participant's exercise session, and can display how vigorous the exercise session was.

# + [markdown] id="aMJC9uHCaINg"
# ## 7.2 Visualizing Heart Rate Averages per Session over a month

# + [markdown] id="JsZvdweM6qDS"
# Another graph that polar displays is a bar chart showing the duration of exercise sessions throughout the past thirty days along with a plot of the average heart rates per session.

# + [markdown] id="Lho0NmMPFfCN"
#
# <img src='https://i.imgur.com/AkrUlco.png' width='750px'>

# + [markdown] id="RBGD5tOUg7zt"
# To start we want to extract the necessary data. This will include: 
#
#
# *   Dates of exercises
# *   Durations of each exercise
# *   Average heart rates of each exercise
#
#

# + id="5FtAHv14hDyF"
import pandas as pd
import numpy as np
from datetime import datetime

durations = []
avg_rates = []
dates = []
day_array = list(df2['day'])
rate_array = list(df2['avg_rate'])
duration_array = list(df2['minutes'])
for i in range(len(df2['day'])):
  
  if datetime.strptime(day_array[i],'%Y-%M-%d') < (datetime.strptime(start_date,'%Y-%M-%d') + timedelta(days=30)) and datetime.strptime(day_array[i],'%Y-%M-%d') >= datetime.strptime(start_date,'%Y-%M-%d'):
    dates.append(np.datetime64(day_array[i]))
    durations.append(duration_array[i]*60000)
    avg_rates.append(rate_array[i])

c = sorted(dates, key=lambda x: x)
s = dates[0]
dates = []
for d in c:
  if d > (s+np.timedelta64(30,'D')):
    break
  else:
    dates.append(d)
dates = dates[:30] # we will only plot a month of data just like in the original

# + [markdown] id="1wXrNnH2hD52"
# Now that we have everything we need, we can move on to plotting the graph! 
#
# To do this we will start by plotting a [matplotlib bar graph](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html), which will represent the durations of each exercise. Then we will overlay this plot with a second graph, the [matplotlib line plot](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html). This is all we need for the base graph!
#
# All that remains after is to add the necessary styling to achieve the graph pictured above.

# + id="O8hVSOdCdnMn" colab={"base_uri": "https://localhost:8080/", "height": 504} outputId="db97f18e-4613-422b-f027-02137e797196"
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from matplotlib.ticker import AutoMinorLocator
import copy
import pandas as pd

#set the style of the plot, initialize it
sns.set_style("whitegrid")
fig, ax = plt.subplots(figsize=(24,8))
ax.set_facecolor('#f2f2f2')

#before we begin, we need to add in a buffer at either end of the data so we can extend the graph
rbound = np.datetime64((pd.Timestamp(dates[len(dates)-1])).strftime('%Y-%m-%d'))
lbound = np.datetime64((pd.Timestamp(dates[0]) - pd.DateOffset(days=1)).strftime('%Y-%m-%d'))
xdates = list(pd.date_range(start=lbound, end=rbound))
xdates.append(xdates[len(xdates)-1])

gridticks = copy.deepcopy(xdates)
xdates += list(np.array(xdates) - timedelta(hours=12))
xdates = sorted(xdates, key=lambda x: x) # check

#process and fill our data arrays so that they match dimensions of x axis
points = {np.datetime64(datetime.strftime(pd.to_datetime(date), '%Y-%m-%d')):(avg_rate,duration) for date, avg_rate, duration in zip(dates,avg_rates,durations)}
data1 = []
data2 = {}
for i in range(len(xdates)):
  cdate = np.datetime64(datetime.strftime(xdates[i],'%Y-%m-%d'))
  if i == 0:
    added = points[np.datetime64(datetime.strftime(xdates[3],'%Y-%m-%d'))][0]
  # if even (is artifical)
  if pd.Timestamp(xdates[i]).hour == 12:
    data1.append(added)
    continue
  if cdate in points:
    added = points[cdate][0]
    data1.append(added)
    data2[cdate] = points[cdate][1]/3600000
  else:
    data1.append(added)
    data2[cdate] = 0
plt.xticks(rotation=45)
ax2 = ax.twinx()

#plot the bar graph
ax.bar(data2.keys(),data2.values(), color ='#e71735', width=0.30)
ax.set_yticklabels(np.arange(0, 2., 0.5), weight='light')
ax.set_yticks(np.arange(0, 2., 0.5)) # 2nd param was: max(data2.values())+0.5 for adaptability

#plot the average heart rate
plt.plot(xdates, data1, color='#e71735', linestyle='dashed')
plt.xticks(gridticks)
ax.set_xticklabels(gridticks, weight='light')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

#clip the graph ends to get our desired look 
axis = plt.axis()
plt.xlim(xdates[0], xdates[len(xdates)-2])
ax2.yaxis.grid(False)
ax2.set_yticks(np.arange(50,200,25))
ax2.set_yticklabels(np.arange(50, 200, 25), weight='light')

# shift grid lines so they are in between dates
gridticks = np.array(gridticks) - timedelta(hours=12)
ax.set_xticks(gridticks, minor=True)
ax.xaxis.grid(False)
ax.grid(which='minor')
ax.tick_params(axis='x', length=10, which='minor')

#hide ticks
ax2.tick_params(axis='y', length=0) 
ax.tick_params(axis='y', length=0) 

# + [markdown] id="PDxTkANicRAB"
# This plot is important because it shows us whether the participant wore the monitor and how long they wore the monitor each day. Additionally, their average heart rate throughout the session can be a basic indicator of the intensity of their exercises.

# + [markdown] id="LoVTLHJyHPgx"
# ## 7.3 Continuous Heart Rate Graph

# + [markdown] id="GaosKE5p7Wjn"
# One final visualization that Polar offers is a graph of the continuous heart rate data per session of exercise, shown below.

# + [markdown] id="15aeF03j3N61"
#
# <img src='https://i.imgur.com/R9nfO0R.png' width='750px'>

# + [markdown] id="hNntOOC0gqq3"
# In this plot the line plot represents the heart rate (bpm) at every second of the exercise session, and the colored regions indicate the "zone" in which the heart rate (bpm) lies. We will need:
#
#
# *   Continuous heart rate data
#

# + id="zH1L-IvOHlZK"
import pandas as pd

heart_rts = list(hr_df["bpm"]) 
#we must add in '2000-01-10' as a dummy date to help with formatting concerns
times = list(hr_df["time"]) 

# + [markdown] id="zFHHY6vOIYBG"
# We will now graph this using the matplotlib [line plot](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html) function, which will give us the base graph, after which we can focus on aesthetics.

# + colab={"base_uri": "https://localhost:8080/", "height": 391} id="N2-eIqrsIXP2" outputId="bb98aa11-b062-40ca-f451-dea99c7d2eec"
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import matplotlib.dates as mdates

sns.set_style("whitegrid")
fig, ax = plt.subplots(figsize=(18,6))
ax.set_facecolor('#f2f2f2')

ax = plt.gca()
plt.plot(times, heart_rts, color='#e71735')

#set x axis values
xts = np.arange(min(times), max(times), timedelta(minutes=10))
ax.set_xticks(xts)
ax.set_xticklabels(xts, weight='bold')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

#set left y axis
yts = np.arange(100, 220, 20)
ax.set_yticks(yts)

#ax.set_yscale('function', functions=(forward,inverse))
ax.axhspan(100, 120, facecolor='#e3e5e5', alpha=0.5)
ax.axhspan(120, 140, facecolor='#bee5f1', alpha=0.5)
ax.axhspan(140, 160, facecolor='#c9e7b6', alpha=0.5)
ax.axhspan(160, 180, facecolor='#f4e3b1', alpha=0.5)
ax.axhspan(180, 200, facecolor='#ecaec4', alpha=0.5)

#right side y axis
f = lambda x: (x/200)*100
i = lambda x: (x/100)*200
ax2 = ax.secondary_yaxis("right", functions=(f,i))
yticks = ax2.yaxis.get_major_ticks()
yticks[1].set_visible(False)
ax.tick_params(axis='y', colors='red')  
ax2.tick_params(axis='y', colors='red') 
ax.set_yticklabels(ax.get_yticks(), weight='bold')

#cut off the edges
plt.xlim(times[0], times[len(times)-1])

# + [markdown] id="iEx6cSnVc6_b"
# This plot is important because it shows us the heart rate of the participant for each second, giving us a detailed look at a particular workout session. Also, the colored zones allow us to quickly identify the level of vigor at which the user exercised.

# + [markdown] id="1g-4Tru0-4ws"
# # 8. Outlier Detection and Data Cleaning

# + [markdown] id="9XU60Wu0aDMM"
# **NOTICE:** If you are using synthetically generated data, the analyses may yield unintuitive results due to the randomly generated nature of the data

# + [markdown] id="oa2BJu4KRzKt"
# In this section, we will detect outliers in our extracted data.
#
# Since there are currently no outliers (by construction, since it is simulated to have none), we will manually inject a couple into our general sessions dataframe (the method for finding outliers here will work for any heart rate dataframe).

# + id="GJyjKwufUPsF"
import pandas as pd

outliers = {'time': ['01:11:52', '01:11:53'], 'bpm': [240, 50]}
hr = hr_df.append(pd.DataFrame(outliers),ignore_index=True)

# + [markdown] id="BPyoSJbgWVIm"
# Now we need a method to find these outliers. While there are many known methods for finding outliers, one of the quickest ways is to use something known as a z-score.
#
# The formula for the z-score is 
#
#
# ```
# Z = (data point - mean of data set) / standard deviation
# ```
# We will compute this formula on every data point in our data set, giving us a massive list of z-score values. 
#
# What the z score tells us is how far, in terms of standard deviations, any one data point is from the mean. In statistics, data points at increasing standard deviations away from the mean are less likely to occur. This means that the greater our z-score, the more unlikely for the data point to be real. 
#
# We can decide what distance from the mean constitutes an outlier by setting the **threshold** value, so if a data point's z-score is above that threshold we might guess it to be an outlier.
#
# One intuitive idea is that the heart rate should not vary too much from one second to the next. To capitalize on this, we can improve our analysis by first calculating the distance each heart rate sample is away from neighboring heart rate samples. We can then use the z-scores to determine which heart rates differ from their neighbors by an unusually large margin. These will likely be our outliers.

# + id="BqGX6sqheP9c"
import math
import pandas as pd

nx = hr["bpm"]

distances = []

f = lambda x: x**2

#take the current count, subtract it by the points to its left and right some distance, then 
#square each of these differences, add, then sqrt
for l1, l2, m, r1, r2 in zip(nx[:-4],nx[1:-3],nx[2:-2],nx[3:-1],nx[4:]):
  difference = math.sqrt(f(m-l1)+f(m-l2)+f(m-r1)+f(m-r2))
  distances.append(difference)

# + [markdown] id="7TJ687gBhrHT"
# Now we can calculate our z-scores for the heart rate data in one training session, and identify those data points that seem like outliers. Luckily, we can save some time by using the [z-score function](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.zscore.html) from scipy's statistics library, which will give us a z-score calculation for all data points.

# + colab={"base_uri": "https://localhost:8080/"} id="VxV9PJfFSp2s" outputId="a3bbdf0b-7b23-4ef7-a853-efef477a77fd"
from scipy import stats
import pandas as pd
import numpy as np

threshold = 3 #@param{type: "integer"}
z_scores = np.abs(stats.zscore(nx))
hr['z'] = z_scores
print(hr.loc[hr['z'] > threshold])

cx = list(hr["bpm"].values)
for idx in hr.index[hr['z'] > threshold].tolist():
  vals = cx[idx-3:idx-2]+cx[idx-2:idx-1]+cx[idx+1:idx+2]+cx[idx+2:idx+3]
  mean_val = np.mean(vals)
  hr.loc[idx, 'bpm'] = mean_val

# + [markdown] id="_VOtYJMGYRD3"
# It looks like the code was able to successfully identify the two outliers!

# + [markdown] id="dbAciV8Zd0Tm"
# # 9. Statistical Data Analysis

# + [markdown] id="r_BHhJ3-IlFW"
# ## 9.1 Correlation between average heart rate and calories burned
#

# + [markdown] id="wZs38sFLDWus"
# We want to test the hypothesis that for a session, the average heart rate correlates with the number of calories burned.
#
# Let us begin by extracting the necessary data. This includes:
#
#
# *   the average heart rate for each exercise session
# *   the calories burned per minute for each exercise session
#
#
#
# To do this we will refer to the exercise_data list of exercises which we kept from section 3. In practice you can use the following code:

# + [markdown] id="liJzZsWazMTA"
#
#
# ```
# avg_rates = [s['heart_rate']['average'] for s in exercise_data]
# calories_per_minute = [s["calories"]/(float(pd.Timedelta(s["duration"]).total_seconds()/60)) for s in exercise_data]
# ```
#
#

# + id="wKgdTOBpzmZq"
import pandas as pd

avg_rates = [avg_rate for avg_rate in df2['avg_rate']]
calories_per_minute = [c/(m) for c, m in zip(df2['calories'],df2['minutes'])]

# + [markdown] id="XwCdE4Whzol6"
# And now we can actually graph the data to see the correlation. This is done by using a [seaborn linear regression plot](https://seaborn.pydata.org/generated/seaborn.lmplot.html) which we can use to visualize the correlation.

# + colab={"base_uri": "https://localhost:8080/", "height": 365} id="mjBZKvYADvq2" outputId="9762fbc4-8ffb-4962-edf5-dfcb620267cf"
import seaborn as sns
import matplotlib.pyplot as plt

# plot the data 
d = {'calories burned (kcal/minute)': calories_per_minute, 'average heart rate (bpm)': avg_rates}
df = pd.DataFrame(data=d)

graph = sns.lmplot(data=df, y='calories burned (kcal/minute)', x='average heart rate (bpm)')

graph.map(plt.scatter, 'average heart rate (bpm)','calories burned (kcal/minute)', edgecolor ="w").add_legend()
sns.set(context='notebook', style='whitegrid', font='sans-serif', font_scale=1, color_codes=True)

plt.show(block=True)

# + [markdown] id="kDC-YCxYPUpz"
# From the plot, we can see that the line of best fit actually fits all the data points rather tightly, and this is our first indicator that the correlation between the two factors exists. 
#
# But we can do more to confirm this correlation - we can calculate the p-value to determine statistical significance using scipy's stats library, as shown here:

# + colab={"base_uri": "https://localhost:8080/"} id="wdbkk52zPWpB" outputId="24b7d84e-4552-442f-9156-a1299ee34f0d"
from scipy import stats

p_value = stats.linregress(calories_per_minute,avg_rates)[3]
correlation_coefficient = stats.pearsonr(calories_per_minute, avg_rates)[0]
print("P value: " + str(p_value))
print("Correlation coefficient: " + str(correlation_coefficient))

# + [markdown] id="32-u3DYbO7kF"
# Based on the p-value 0.0023 < 0.05, we have statistical significance. This means that there is 0.2% probability that the datapoints of our dataset occurred by chance. 
# In addition, our correlation coefficient of 0.96 implies a very strong correlation. 
# This relationship is intuitive, because Polar uses an equation to calculate the calories burned. But looking at this data allows to see that polar's calorie counter makes sense!

# + [markdown] id="jpW1e0fSQv-s"
# ## 9.2 Correlation between duration of exercise and calories burned

# + [markdown] id="wg7xkzpEHatn"
# Now we can clearly see the that average heart rate and calories burned per minute are tightly correlated. But how about the correlation between the duration of an exercise and the amount calories burned? We will first extract the necessary data through the code segment shown below:

# + [markdown] id="0ZsYfurAfvcn"
#
#
# ```
# durations = [float(pd.Timedelta(s["duration"]).total_seconds()) for s in exercise_data]
# calories = [s["calories"] for s in exercise_data]
# ```
#
#

# + [markdown] id="ZTjmXySgr1Pn"
# As before, our example will use manually inputted data points (which come from real sessions), but feel free to replace the code with the above segment to test out your data!

# + id="tWxo-XxhdTDe"
import pandas as pd

durations = [m*60 for m in df2['minutes']]
calories = [c for c in df2['calories']]

# + [markdown] id="mtnNfzZLsHzk"
# Now we will recreate the graph plotted in 5.1 this time using our new durations and calories data.

# + colab={"base_uri": "https://localhost:8080/", "height": 365} id="P8N_iFCHdbzQ" outputId="41a5492b-5d2f-4f67-faec-1029e83d017e"
import pandas as pd
import seaborn as sns

# plot the data 
d = {'calories burned (kcal)': calories, 'duration (s)': durations}
df = pd.DataFrame(data=d)

graph = sns.lmplot(data=df, y='calories burned (kcal)', x='duration (s)')

graph.map(plt.scatter, 'duration (s)','calories burned (kcal)', edgecolor ="w").add_legend()
sns.set(context='notebook', style='whitegrid', font='sans-serif', font_scale=1, color_codes=True)

plt.show(block=True)

# + colab={"base_uri": "https://localhost:8080/"} id="dVQTMPDiqBkx" outputId="d5b1d883-5466-49c8-b413-50215d0e01ae"
p_value = stats.linregress(calories,durations)[3]
correlation_coefficient = stats.pearsonr(calories, durations)[0]
print("P value: " + str(p_value))
print("Correlation coefficient: " + str(correlation_coefficient))

# + [markdown] id="zG5mILo_xBdG"
# Since our P-value is 0.017 < 0.05, meaning the we have 1.7% probability that our data occurred by chance, we again have statistical significance. Interestingly enough, our correlation coefficient for duration to calories burned is less than our correlation coefficient for average heart rate to calories burned (0.889 < 0.96). Although we can't say from our simple analysis that average heart rate is more correlated to calories burned than duration is (further analysis has to be done to determine whether the difference in correlation coefficient values is significant, and we also should get more data before making a conclusion!), it definitely reveals a question for further investigation!

# + [markdown] id="F7W7D_Ba_RPb"
# ## 9.3. T test on activity intensity through workout
#
# We might also be interested in determining whether the participant exercises with different overall intensity at different halves of their sessions.
#
# The T-test is a statistical test used to determine comapre the mean of some value in two separate groups. Here our first group will be the first half of an exercise session, and the second group will be the second half of an exercise session. 
#
# Choosing on exercise session to focus on, we can use the T-test to see if the exercise intensity in the first half of the session is different from the intensity in the second half.

# + colab={"base_uri": "https://localhost:8080/"} id="p2GcB-Y6AzLo" outputId="0b30ba75-41f9-42ae-9fd5-f70746a54cfd"
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind

def differ(df):
  rows = len(df.index)
  f = df.iloc[range(rows//2)]["bpm"]
  s = df.iloc[range(rows//2,rows)]["bpm"]
  return ttest_ind(f,s)

print(differ(hr_df))

# + [markdown] id="4--zRqufTaKt"
# Since the t-test returned a negative value, the sample mean heart rate in the first half of the exercise session is less than the sample mean heart rate in the second half of the session. Further, since our pvalue is small (< 0.05), we can reject the null hypothesis and conclude that the the first half of the exercise tended to have lower heart rates than the second half.

# + [markdown] id="RkhVCf9-C23R"
# We can now repeat this process on multiple exercise sessions and visualize our findings in a plot, giving us a view of the participant's exercise habits (i.e. whether they tend to slow down throughout a session, or whether their intensity increases).

# + colab={"base_uri": "https://localhost:8080/", "height": 644} id="8UTXXe3BDb-s" outputId="addd17dd-9f32-456a-db97-611c2d2d4641"
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

y = []
x = df2["day"]

for df in hr_dfs:
  v,p = differ(df)
  if p < 0.05:
    y.append(v)
  else:
    # there is no difference
    y.append(0)

plt.figure(figsize=(16,10))
plt.bar(x, y)
end = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=30)
plt.title(f"T-test of exercise intensity between first half and second half of session from {start_date} to {datetime.strftime(end,'%Y-%m-%d')}",fontsize=20)
plt.xlabel("Time")
plt.ylabel("T-test of exercise intensity between first half and second half of session")
