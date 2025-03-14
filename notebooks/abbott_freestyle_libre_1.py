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

# + [markdown] id="e_dmeLdCgHlO"
# # Abbott Freestyle Libre CGM: Guide to data extraction and analysis

# + [markdown] id="DAn8JGTbFTD4"
# <img src="https://assets.nutrisense.io/62c477aa7b7db12cfffa5de3/633386632eabe28ff072973d_Activity.webp" width="200px" />
#
#

# + [markdown] id="ftAnpNNrgMZy"
# The [Abbott Freestyle Libre Version 1 Continuous Glucose Monitor](https://www.freestyle.abbott/us-en/products/freestyle-libre-3.html?utm_source=Google&utm_medium=SEM&utm_campaign=Brand&utm_content=General%20FSL3&gclid=EAIaIQobChMIyaaZs4Gv_gIVkSytBh11yQZOEAAYASAAEgIiY_D_BwE&gclsrc=aw.ds) is a sensor that tracks your blood glucose levels over a period of two weeks. A variety of vendors use the Freestyle Libre CGM; in this notebook, we use [Nutrisense](https://to.nutrisense.io/cgm-3?g_acctid=195-120-5766&g_adgroupid=145363696209&g_adid=588697352068&g_adtype=search&g_campaign=brand_exact_desktop_tcpa_conv_groups+_low_cpc&g_campaignid=18640003106&g_keyword=nutrisense%20cgm&g_keywordid=kwd-927595745176&g_network=g&utm_adgroup=conv&utm_adpos=&utm_campaign=brand_exact_desktop_tcpa_conv_groups__low_cpc&utm_keyword=nutrisense%20cgm&utm_medium=cpc&utm_source=google&gclid=EAIaIQobChMI_Ie08PTD_QIVsRR9Ch3A_wRrEAAYASAAEgJBPfD_BwE). In addition to logging continuous data, purchasing the Nutrisense CGM pairs you with a dietitian who helps you interpret, understand, and manage your glucose levels.
#
# Having used the Nutrisense CGM, we'll show you how to extract, visualize, and compute statistics for data collected by the monitor. All you will need for this notebook is your username and password!
#
# You can extract the parameters with known sampling frequencies as below:
#
# Parameter Name  | Sampling Frequency
# -------------------|------------------
# Glucose level      |  15 minutes
# Glucose Peak |  24 hours
# Glucose Average |  24 hours
# Glucose Adaptability | 24 hours
# Glucose Variability | 24 hours
#
# In this guide, we sequentially cover the following **nine** topics to extract from the Nutrisense CGM:
# 1. **Setup**
# 2. **Authentication and Authorization**
#     - Requires only username and password, no OAuth.
# 3. **Data extraction**
#     - We get data via `wearipedia` in a couple lines of code.
# 4. **Data Exporting**
#     - We export all of this data to file formats compatible by R, Excel, and MatLab.
# 5. **Adherence**
#     - We simulate non-adherence by dynamically removing datapoints from our simulated data.
# 6. **Visualization**
#     - We create a simple plot to visualize our data.
# 7. **Advanced visualization**
#     - 7.1: We plot the glucose levels over a day
#     - 7.2: We recreate the glucose scores plot displayed on the nutrisense cgm app.
#     - 7.3: We recreate the glucose summary statistics chart displayed on the nutrisense cgm app.
# 8. **Outlier Detection and Data Cleaning**
#     - We detect outliers in our data and filter them out.
# 9. **Statistical Data analysis**
#     - 9.1: We create a plot to visualize the difference between glucose levels at night and at day.
#     - 9.2: We plot the change in blood glucose level after changes of behavior.
#     - Note that we are not making any scientific claims here as our sample size is small and the data collection process was not rigorously vetted (it is our own data), only demonstrating that this code could potentially be used to perform rigorous analyses in the future.
#
# Disclaimer: this notebook is purely for educational purposes. All of the data currently stored in this notebook is purely *synthetic*, meaning randomly generated according to rules we created. Despite this, the end-to-end data extraction pipeline has been tested on our own data, meaning that if you enter your own email and password on your own Colab instance, you can visualize your own *real* data.
#
#

# + [markdown] id="Y2ZKhRCp94-0"
# # 1. Setup
#
# ## Participant Setup
#
# Dear Participant,
#
# Once you unbox your Nutrisense CGM, please set up the device by following the Official Guide: https://support.nutrisense.io/hc/en-us/articles/4402815217687-How-Do-I-Put-on-My-CGM-
#
# This guide is also available on the nutrisense app, which is where you will log and view your data.
#
# Make sure that your phone is paired to it using the Nutrisense login credentials (email and password) given to you by the data receiver.
#
# Best,
#
# Wearipedia
#
# ## Data Receiver Setup
#
# Please follow the below steps:
#
# 1. Create an email address for the participant, for example `foo@email.com`.
# 2. Create a Nutrisense account with the email `foo@email.com` and some random password.
# 3. Keep `foo@email.com` and password stored somewhere safe.
# 4. Distribute the device to the participant and instruct them to follow the participant setup letter above.
# 5. Install the `wearipedia` Python package to easily extract data from this device.

# + id="bup39dgzkHaJ" colab={"base_uri": "https://localhost:8080/"} outputId="1d5b6ae0-5aa6-4598-f9e4-03075402f65c"
# !pip install git+https://github.com/TrafficCop/wearipedia-1

# + [markdown] id="MYztPubjgX_f"
# # 2. Authentication and Authorization
#
# To obtain access to data, authorization is required. All you'll need to do here is just put in your email and password for your nutrisense account. We'll use this username and password to extract the data in the sections below.

# + id="hAbsFbuZhBiP"
#@title Enter Nutrisense login credentials
email_address = "" #@param {type:"string"}
password = "" #@param {type:"string"}

# + [markdown] id="6iHF2-kagcQc"
# # 3. Data Extraction
#
# Data can be extracted via [wearipedia](https://github.com/Stanford-Health/wearipedia/), our open-source Python package that unifies dozens of complex wearable device APIs into one simple, common interface.
#
# First, we'll set a date range and then extract all of the data within that date range. You can select whether you would like synthetic data or not with the checkbox.

# + id="puUo4f7bhYk8"
#@title Enter start and end dates (in the format yyyy-mm-dd)

#set start and end dates - this will give you all the data from 2000-01-01 (January 1st, 2000) to 2100-02-03 (February 3rd, 2100), for example
start_date='2022-03-01' #@param {type:"string"}
end_date='2023-03-12' #@param {type:"string"}
synthetic = True #@param {type:"boolean"}

# + id="-3yf-G4CPyZ6" colab={"base_uri": "https://localhost:8080/"} outputId="18215b67-632a-48bb-e03e-6c0eaedda7fc"
import wearipedia

device = wearipedia.get_device("nutrisense/cgm")

if not synthetic:
    device.authenticate({"email": email_address, "password": password})

params = {"start_date": start_date, "end_date": end_date}

continuous = device.get_data("continuous", params=params)
statistics = device.get_data("statistics", params=params)
scoremain = device.get_data("scores", params=params)
summary = device.get_data("summary", params=params)

# + [markdown] id="TyC9aya7gd2f"
# # 4. Data Exporting

# + [markdown] id="qOkOh_7y-4tk"
# In this section, we export all of this data to formats compatible with popular scientific computing software (R, Excel, Google Sheets, Matlab). Specifically, we will first export to JSON, which can be read by R and Matlab. Then, we will export to CSV, which can be consumed by Excel, Google Sheets, and every other popular programming language.
#
# ## Exporting to JSON (R, Matlab, etc.)
#
# Exporting to JSON is fairly simple. We export each datatype separately and also export a complete version that includes all simultaneously.

# + id="F-YvOQ9b_ASD"
import json

json.dump(continuous, open("continuous.json", "w"))
json.dump(statistics, open("statistics.json", "w"))
json.dump(scoremain, open("scores.json", "w"))
json.dump(summary, open("summary.json", "w"))

complete = {
    "continuous": continuous,
    "statistics": statistics,
    "scores": scoremain,
    "summary": summary
}

json.dump(complete, open("complete.json", "w"))

# + [markdown] id="PfJ-NuNl_Avl"
# Feel free to open the file viewer (see left pane) to look at the outputs!
#
# ## Exporting to CSV and XLSX (Excel, Google Sheets, R, Matlab, etc.)
#
# Exporting to CSV/XLSX requires a bit more processing, since they enforce a pretty restrictive schema.
#
# Here we will put the continuous glucose data into a dataframe.

# + id="nTHM-QzTAFRd" colab={"base_uri": "https://localhost:8080/", "height": 424} outputId="6fdd1252-e1f8-4a90-95b8-c0fa0d050186"
import pandas as pd
import copy

# glucose scores dataframe
data = []
datas = []
for elem in continuous:
  t = pd.DataFrame({'time': [elem['x']], 'level': [elem['y']], 'interpolated': [elem['interpolated']]})
  data.append(copy.deepcopy(t))

datas = copy.deepcopy(data)
data = pd.concat(data)

display(data)

# + [markdown] id="59pl2tLwgg8b"
# # 5. Adherence
#
# Since the Nutrisense CGM only holds around 8 hours of data at a time, if the user forgets to sync their data to their phone on time, there'll likely be a gap with missing data. Take it from us, it happens more than you might think!
#
# In this section, we will simulate this non-adherence over different periods of time from the participant.
#
# Then, we will detect this non-adherence and give a Pandas DataFrame that concisely describes when the participant has had their device on and off throughout the entirety of the time period, allowing you to calculate how long they've had it on/off etc.
#
# We will first delete a certain % of blocks, with user input.

# + id="dSWRLMQwG_BU" cellView="form"
#@title Non-adherence simulation
start_date='2022-03-01' #@param {type:"string"}
days=1 #@param {type:"number"}
adherence_percent = 0.94 #@param {type:"slider", min:0, max:1, step:0.01}

# + [markdown] id="0bOICDIfXSpm"
# Now let's detect non-adherence. We will plot the periods when the participant syncs their data.

# + id="S8CwR-4Hawlr" colab={"base_uri": "https://localhost:8080/", "height": 539} outputId="a4a6b34b-90b1-482b-f794-c739c55e4e7b"
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import copy

# convert string to date
def strToD(s):
  c = s[:19]
  return datetime.strptime(c, "%Y-%m-%dT%H:%M:%S")

start = datetime.strptime(start_date, "%Y-%m-%d")
end = start + timedelta(days=days)

dta = []
for elem in continuous:
  if strToD(elem["x"]) < start:
    continue
  elif strToD(elem["x"]) > end:
    break

  dta.append(copy.deepcopy(elem))
  if np.random.uniform(low=0, high=1, size=(1,))[0] > adherence_percent:
    dta[-1]["interpolated"] = True


datelist = pd.date_range(start_date,datetime.strftime(end,"%Y-%m-%d"), freq="15min")
valid = []
for point in dta:
  if point['interpolated'] == True:
    valid.append(0)
  else:
    valid.append(1)

plt.figure(figsize=(12, 6))
datelist = datelist[:len(valid)]
plt.plot(datelist,valid,drawstyle="steps-mid")

# + [markdown] id="rwxfl8stgkCP"
# # 6. Visualization

# + [markdown] id="USB3t03SP9c2"
# We've extracted lots of data, but what does it look like?
#
# In this section, we will be visualizing our three kinds of data in a simple, customizable plot! This plot is intended to provide a starter example for plotting, whereas later examples emphasize deep control and aesthetics.

# + id="C-tfx2OGavTy" colab={"base_uri": "https://localhost:8080/", "height": 880} outputId="2849762f-397b-4593-9ad0-d9bba43c8846"
#@title Basic Plot
feature = "continuous" #@param ["continuous"]
start_date = "2022-06-17" #@param {type:"date"}
smoothness = 0.1 #@param {type:"slider", min:0, max:1, step:0.01}
smooth_plot = True #@param {type:"boolean"}
periods = 96

from scipy.special import y0
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
from scipy.ndimage import gaussian_filter1d

datelist = pd.date_range(start_date,datetime.strftime(datetime.strptime(start_date,"%Y-%m-%d")+timedelta(minutes=15*periods),"%Y-%m-%d"), freq="15min")
start = datelist[0]
end = datelist[len(datelist)-1]
title_fillin = "Continuous Glucose Data"

# convert string to date
def strToD(s):
  c = s[:19]
  return datetime.strptime(c, "%Y-%m-%dT%H:%M:%S")

dta = copy.deepcopy(data)

# extract the necessary data. notice we must convert
# the dates in the dataframe from string to actual datetime object
dta['time'] = dta['time'].apply(strToD)
dta = dta[dta['time'] >= start]
dta = dta[dta['time'] < end]
x = dta['time']
y = dta["level"]

sigma = 5*smoothness

if smooth_plot:
  y = list(gaussian_filter1d(y, sigma=sigma))
plt.figure(figsize=(16,10))

plt.plot(x, y);
plt.ylim(40,200);

plt.title(f"{title_fillin} from {start_date} to {datetime.strftime(end,'%Y-%m-%d')}",fontsize=20);
plt.xlabel("Time");
plt.ylabel(title_fillin[:-1]);

# + [markdown] id="uiaccbddglyJ"
# # 7. Advanced Visualization

# + [markdown] id="DMGIGfYEiTkC"
# ## 7.1 Glucose levels over a day

# + [markdown] id="CUjo-lgytxoM"
# Here we will be graphing a more highly stylized plot, specifically the glucose levels chart displayed in the main screen of the official Nutrisense app. This graph shows the glucose levels (mg/dL) at each time of day.

# + [markdown] id="5d6sCznqtswr"
# <img src="https://i.imgur.com/I60vYHU.png" width='750px'>

# + [markdown] id="7zRZ_Bu_6PnQ"
# The darker green sections of the graph denote healthy levels of glucose, which is defined as being between 70 mg/dL and 140 mg/dL. Anything outside of this range is colored light green.
#
# To make this plot, we can extract the glucose levels data from our pandas dataframe and the associated time from the dataframe as well.

# + cellView="form" id="mx6rr_rrY0A7"
#@title Glucose Plot Date
start_date = "2022-06-17" #@param {type:"date"}

import pandas as pd

datelist = pd.date_range(start_date, periods=2)
start = datelist[0]
end = datelist[-1]

# + id="MsTn8tELPeij"
from datetime import datetime, timedelta
import copy

# convert string to date
def strToD(s):
  c = s[:19]
  return datetime.strptime(c, "%Y-%m-%dT%H:%M:%S")

dta = copy.deepcopy(data)

# extract the necessary data. notice we must convert
# the dates in the dataframe from string to actual datetime object
dta['time'] = dta['time'].apply(strToD)
dta = dta[dta['time'] >= start]
dta = dta[dta['time'] < end]
x = list(dta['time'])

cp = copy.deepcopy(dta)

# for datapoints that were "interpolated" (i.e. made up),
# set the value to a very large negative. This behavior
# matches how nutrisense deals with missing datapoints
cp.loc[cp["interpolated"] == True, "level"] = -float('inf')
y1 = list(cp['level'])
x = x[:len(y1)]

# + [markdown] id="f3crlPTs7B5J"
# Having extracted the necessary data, we can use a matplotlib plot to get the basic shape of the desired graph. The remaining work is in the styling!

# + id="B2J8dbk7iXgU" colab={"base_uri": "https://localhost:8080/", "height": 539} outputId="6d2b89f4-33e3-4410-cbd1-55a5919147ca"
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import numpy as np
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

healthy = 140

figsize = (10, 6)
fig = plt.figure(figsize=figsize, facecolor="#1d2525")

# set the grid style
ax = plt.axes()
# ax.yaxis.grid(linewidth='2', ls=":", dashes=(1,3,1,3), color="#7c7d7d")
ax.yaxis.grid(linewidth='1', ls=":", dashes=(0.5,5,0.5,5), color="#7c7d7d")

# remove frame
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# set colors
ax.set_facecolor("#1d2525")

# set the range and style of ticks
plt.yticks(np.arange(60.0, max(y1)+10, 10.0), color="#7c7d7d", fontsize=10)
plt.xticks(color="#7c7d7d")
plt.ylim(60, max(y1)+10)
plt.xlim(x[0], x[len(x)-1])

# set the xaxis labels to the time
xts = list(pd.date_range(start_date,datetime.strftime(datetime.strptime(end_date,"%Y-%m-%d")+timedelta(days=1),"%Y-%m-%d"), freq="3H"))
ax.xaxis.set_major_locator(mticker.FixedLocator(ax.xaxis.get_ticklocs()))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%l%p'))

# smooth the plot points
y = list(gaussian_filter1d(y1, sigma=0.01*5))
bottom = [min(e,70) for e in y]

# plot the graph and fill in the correct colors
plt.plot(x,y,color="#76885f", alpha=.0)
plt.plot(np.where(np.array(y)>= healthy, np.array(y), None), color="#c1c59a", label="1", alpha=.0)
plt.plot(np.where(np.array(y)<= healthy, np.array(y), None), color="#76885f", label="1", alpha=.0)

# lower bound:
plt.plot(x,bottom,color="#c1c59a", alpha=.0)

lower = np.array(y).clip(max=healthy)
upper = np.array(y)

ax.fill_between(x, lower, upper, color='#c1c59a', alpha=.8)
ax.fill_between(x, 0, lower, color='#76885f', alpha=.8)
ax.fill_between(x, 0, bottom, color="#c1c59a", alpha=.8)

# + [markdown] id="a0E_RboQ7vsl"
# This plot is important because it quickly helps us visualize all of the continuous data collected by the monitor, as well as identify healthy ranges of glucose levels, spikes, and times when the participant failed to log data.

# + [markdown] id="r8eKQTw2iZpb"
# ## 7.2 Glucose Scores

# + [markdown] id="gAZrEz_Nt3tY"
# For our second chart, we will be attempting to replicate the glucose scores summary, which displays various statistics about your daily glucose levels.

# + [markdown] id="1s7KzEpBZWCg"
# <img src="https://i.imgur.com/4k5hgln.png" width='750px'>

# + [markdown] id="_H7gRjlduFEM"
# The only data we will need here are the summary scores taken from the `scoremain` dictionary variable which we created during data extraction.
#
# Here will begin by setting up the colors and score arrays:

# + id="pJiz_TN4C2Kp"
import pandas as pd
import numpy as np

# colors dict: put a color for every index
# we will do: (0) peak, (1) average, (2) adaptability, (3) variability

scores = [scoremain["scorePeak"], scoremain["scoreMean"], scoremain["scoreTimeOutsideRange"], scoremain["scoreStdDev"]]
lpos = [-0.112,-0.06,0.0,-0.03]

# This will give us our desired 10-block bar chart
basescore = [0.1]*10
base2 = {'peak': basescore}
bg2 =pd.DataFrame(base2).transpose()

# the labels for the plots
lsb = ["Peak", "Average", "Adaptability", "Variability"]

# set an array of colors which will be used to determine partition coloring
colors = ['#343e33']
for score in scores:
  # divisions: 0-4, 5-7,
  if score <= 4:
    colors.append('#ff3e4d')
  elif score <= 7:
    colors.append('#ef893f')
  else:
    colors.append('#a9c180')
colors.append('#343e33')

# + [markdown] id="M5E0Qu1bu435"
# All that is left for us to do now is tons of plotting and styling!

# + id="ZDUH9oOvbrOJ" colab={"base_uri": "https://localhost:8080/", "height": 358} outputId="c514c64d-a57f-4e97-bef7-21da465b5b16"
# position will tell matplotlib where to place each plot, figsize is dynamic based off of our number of plots
from collections import defaultdict
from matplotlib.patches import FancyBboxPatch

# initialize the figure
Position = range(1,5)
figsize = (7, 4)
fig = plt.figure(figsize=figsize, facecolor="#1d2525")

for i in range(4):

  # color array that will be applied to the current plot
  cs = []
  for j in range(scores[i]):
    cs.append(colors[i+1])
  while len(cs) < 10:
    cs.append(colors[0])

  # add one bar chart for each statistic
  ax2 = fig.add_subplot(4, 1, Position[i], facecolor="#1d2525")
  ax = bg2.plot(kind='barh', stacked=True, legend=False, secondary_y=True, ax = ax2, xlim=(-0.4,1.), color=cs) # #343e33

  # redo the plot's elements to style it
  new_patches = []
  for patch in reversed(ax.patches):
    bb = patch.get_bbox()
    color=patch.get_facecolor()

    # the fancy bbox patch module gives us additional ways to customize
    p_bbox = FancyBboxPatch((bb.xmin, bb.ymin),
                        abs(bb.width) / 1.2, abs(bb.height)/2.6,
                        boxstyle="round,pad=-0.0015,rounding_size=0.010",
                        ec="none", fc=color,
                        mutation_aspect= 4
                        )
    patch.remove()
    new_patches.append(p_bbox)
  for patch in new_patches:
    ax.add_patch(patch)

  lpos = [-0.07,-0.017,0.04,0.01]
  # set the ylabel and ylabel position
  ax.set_ylabel(lsb[i], color="white", fontsize=24, rotation=0, position=(0,0))
  ax.yaxis.set_label_coords(lpos[i],-0)
  ax.yaxis.set_label_position("left")

  plt.text(1.05,-0.3, str(int(scores[i])), fontsize=36, color="white")

  # remove frame
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['bottom'].set_visible(False)
  ax.spines['left'].set_visible(False)

  # remove frame
  ax2.spines['top'].set_visible(False)
  ax2.spines['right'].set_visible(False)
  ax2.spines['bottom'].set_visible(False)
  ax2.spines['left'].set_visible(False)

  # hide the ticks and tick labels
  plt.setp( ax.get_xticklabels(), visible=False)
  plt.setp( ax2.get_xticklabels(), visible=False)
  plt.setp( ax.get_yticklabels(), visible=False)
  plt.setp( ax2.get_yticklabels(), visible=False)
  plt.xticks([])
  plt.yticks([])

# + [markdown] id="j84ncZjZ8Do3"
# This plot gives us a simple and visually appealing way to visualize summary statistics for a patient's glucose levels, allowing us to easily identify which scores are considered bad and which are good depending on color coding.

# + [markdown] id="xS9JMLrpidwo"
# ## 7.3 Glucose Summary

# + [markdown] id="ZLFqsRey8wNJ"
# The following is a box plot summarizing the daily glucose statistics. The text on the green rectangle gives the `Mean / Standard Deviation` and the caps represent the maximum/minimum.
#
# The weekly is compared with the daily in this graph

# + [markdown] id="vE2H6Y9s4DyM"
# <img src="https://i.imgur.com/X6lXdk7.png"/>

# + [markdown] id="yn46sK7G9ZL7"
# For this graph, the data we need will all come from the statistics variable we extracted at the start of this notebook. Begin by choosing a date to plot summary statistics for.

# + id="3MiCmV-NmwFA"
#@title Glucose Summary Date
start_date = "2022-06-17" #@param {type:"date"}

import pandas as pd
from scipy.stats import tstd

datelist = pd.date_range(start_date, periods=2)
start = datelist[0]
end = datelist[-1]

from datetime import datetime, timedelta
import copy

# convert string to date
def strToD(s):
  c = s[:19]
  return datetime.strptime(c, "%Y-%m-%dT%H:%M:%S")

dta = copy.deepcopy(data)

# extract the necessary data. notice we must convert
# the dates in the dataframe from string to actual datetime object
dta['time'] = dta['time'].apply(strToD)
dta = dta[dta['time'] >= start]
dta = dta[dta['time'] < end]
x = list(dta['time'])

cp = copy.deepcopy(dta)

Y = np.array(cp['level'])

first = {"min": 70.0, "max": 140.0, "__typename": "Range"}
second = {"min": min(Y), "max": max(Y), "__typename": "Range"}

low, high = min(Y), max(Y)
median = np.median(Y)
std = tstd(Y)
q1, q3 = (np.quantile(Y, [0.25, 0.75])).round(1)
greater = 70.0 < np.array(Y)
less = np.array(Y) < 140.0
condition = greater & less
timeWithinRange = float(len(np.extract(condition, Y)))
avg = np.average(Y)

stat = {
    "healthyRange": first,
    "range": second,
    "timeWithinRange": timeWithinRange,
    "min": low,
    "max": high,
    "mean": avg,
    "median": median,
    "standardDeviation": std,
    "q1": q1,
    "q3": q3,
    "score": 0.0,
    "__typename": "Stat",
}

s = [stat, statistics["average"]][::-1]

# + [markdown] id="9y7yPlo39lIU"
# Since matplotlib's default boxplot looks a farcry from the beautiful plot featured, we have some extra work to do!
#
# Since we are plotting this chart straight from precalculated statistics, we will be using the `bxp` function rather than the standard `boxplot`.

# + id="kqIz512AOYKo" colab={"base_uri": "https://localhost:8080/", "height": 390} outputId="6871409d-9d55-4a71-fdb1-14e840864b86"
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import warnings

# ignore unecessary warnings
warnings.filterwarnings("ignore")

# boxplot for daily and weekly
# bottom line is healthy range
# daily is min and max

# plt.boxplot()
figsize = (12, 4)

# healthy range:
lbound, rbound = 70.0, 140.0

# vars
labels = ["average", "today"]
medianprops = {"linestyle":'none'}
whiskerprops = {"color": "#a6a8a7","linewidth":2.2}
capprops = {"color": "white","linewidth":2.2}

stat_data = []
for i in range(len(s)):
  d = s[i]
  mn, mx = d["min"], d["max"]
  avg, sd = d["mean"], d["standardDeviation"]
  q1, q3 = d["q1"], d["q3"]

  stat_data.append({'med': avg, 'q1': q1, 'q3':q3, 'whislo': mn, 'whishi': mx, 'label': labels[i]})

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize, facecolor="#1d2525")
ax.yaxis.grid(linewidth='2', ls=":", dashes=(1,3,1,3), color="#7c7d7d")
ax.set_axisbelow(True)

ax.tick_params(axis='y',colors='white', labelrotation=90, labelsize=14, pad=10)

# might want to change below into a self drawn patch tick
ax.tick_params(axis='x',colors='red', width=4.0, length=10.0, labelsize=12, pad=10, bottom=100)


ax.set_yticklabels(["Weekly", "Daily"], rotation=90, ha='center', rotation_mode='anchor', weight="bold")
ax.set_xticklabels([lbound,rbound], ha='center', rotation_mode='anchor', weight="bold", color="#a6a8a7")
plt.tick_params(left = False)

bplot = ax.bxp(
    stat_data,
    showfliers=False,
    vert=False,
    patch_artist=True,
    medianprops=medianprops,
    whiskerprops=whiskerprops,
    capprops=capprops,
    )

caps = bplot['caps']
for cap in caps:
  cap.set(ydata=cap.get_ydata() + (-0.035,+0.035))

new_patches = []

for patch in bplot['boxes']:
  bb = patch.get_path().get_extents()
  p_bbox = FancyBboxPatch((bb.xmin, bb.ymin),
                        abs(bb.width), abs(bb.height),
                        boxstyle="round,pad=0,rounding_size=0.2",
                        ec="#a9c180", fc="#a9c180",
                        mutation_aspect=0.1)
  patch.remove()
  new_patches.append(p_bbox)

for i in range(len(new_patches)):
  patch = new_patches[i]
  ax.add_patch(patch)
  l, r = patch.get_x(), patch.get_x() + patch.get_width()
  h = patch.get_y() + patch.get_height()
  plt.text((l+r)/2-3, h+0.04, str(int(s[i]['mean']))+"/"+str(int(s[i]['standardDeviation'])), color="#a6a8a7", fontweight='semibold', fontsize=14)
  plt.text(s[i]['min']-1.,h+0.04, str(int(s[i]['min'])), color="#a6a8a7", fontweight='semibold', fontsize=14)
  plt.text(s[i]['max']-1.6,h+0.04, str(int(s[i]['max'])), color="#a6a8a7", fontweight='semibold', fontsize=14)

plt.xlim(60.0, max(s[0]['max'], s[1]['max'])+10)
plt.xticks([lbound, rbound])

# set colors
ax.set_facecolor("#1d2525")

# remove frame
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set(color="#a6a8a7", linewidth=2.0)
ax.spines['left'].set_visible(False)

# add the inner side to the ticks
ax2 = ax.twiny()
ax2.axis('off')

ax4 = ax2.twiny()
ax4.tick_params(axis="x",direction="out", pad=-15, bottom = True, top=False)
ax4.spines['bottom'].set(color="#a6a8a7", linewidth=2.0)
ax4.tick_params(axis='x',colors='red', width=4.0, length=10.0, labelsize=12, pad=10, bottom=100)
ax4.xaxis.set_ticklabels([])
ax4.set_xlim(ax.get_xlim())
ax4.set_xticks([lbound,rbound])

ax3 = ax2.twiny()
ax3.tick_params(axis="x",direction="in", pad=-15, bottom = True, top=False)
ax3.spines['bottom'].set(color="#a6a8a7", linewidth=2.0)
ax3.tick_params(axis='x',colors='red', width=4.0, length=10.0, labelsize=12, pad=10, bottom=100)
ax3.xaxis.set_ticklabels([])
ax3.set_xlim(ax.get_xlim())
ax3.set_xticks([lbound,rbound])

ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.spines['bottom'].set_visible(False)
ax3.spines['left'].set_visible(False)

ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.spines['bottom'].set_visible(False)
ax4.spines['left'].set_visible(False)

# + [markdown] id="GGvJv2ec-0FO"
# This graph is helpful because it gives a quick look at how the participant's daily glucose level statistics match up to their overall weekly trend. It also gives us a view of the summary statistics of the glucose levels.

# + [markdown] id="vQGsyH-EgpKY"
# # 8. Outlier Detection and Data Cleaning

# + [markdown] id="ToUoxMQsfzGU"
# **NOTICE:** If you are using synthetically generated data, the analyses may yield unintuitive results due to the randomly generated nature of the data

# + [markdown] id="MTh8cTaefz5S"
# In this section, we will detect outliers in our extracted data.
#
# Since there are currently no outliers (by construction, since it is simulated to have none), we will manually inject a couple into our general sessions dataframe (the method for finding outliers here will work for any glucose levels dataframe).

# + id="kJhhL_H-ZuSy" colab={"base_uri": "https://localhost:8080/", "height": 424} outputId="e9794d4a-6448-4ce8-80c6-02e3ad6353ed"
import pandas as pd
from datetime import datetime, timedelta
import copy

dToStr = lambda x: datetime.strftime(x,"%Y-%m-%dT%H:%M:%S")

last = list(data['time'])[len(data)-1]
last, apd = last[:19], last[19:]

ctime = datetime.strptime(last, "%Y-%m-%dT%H:%M:%S")
t1, t2 = dToStr(ctime + timedelta(minutes=15))+apd, dToStr(ctime + timedelta(minutes=30)) + apd

outliers = pd.DataFrame({'time': ['01:11:52', '01:11:53'], 'level': [240, 20]})

odata = copy.deepcopy(data)
random_indices = np.random.randint(0, len(data), size=len(outliers))
# Insert each entry of the outliers dataframe at random indices in the larger dataframe
for i, row in outliers.iterrows():
  nrow = pd.DataFrame([row])
  odata = pd.concat([data.iloc[:random_indices[i]], nrow, data.iloc[random_indices[i]:]], ignore_index = True)

display(data)

# + [markdown] id="y1j2EjM9N6UU"
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
# One intuitive idea is that the glucose levels should not vary too much from one second to the next. To capitalize on this, we can improve our analysis by first calculating the distance each glucose level sample is away from neighboring glucose level samples. We can then use the z-scores to determine which glucose levels differ from their neighbors by an unusually large margin. These will likely be our outliers.

# + id="_U42-CwLN5t0"
import math
import pandas as pd

nx = odata["level"]

distances = []

f = lambda x: x**2

#take the current count, subtract it by the points to its left and right some distance, then
#square each of these differences, add, then sqrt
for l1, l2, m, r1, r2 in zip(nx[:-4],nx[1:-3],nx[2:-2],nx[3:-1],nx[4:]):
  difference = math.sqrt(f(m-l1)+f(m-l2)+f(m-r1)+f(m-r2))
  distances.append(difference)

# + [markdown] id="8NbGzHxUOHm4"
# Now we can calculate our z-scores for the glucose levels data in one training session, and identify those data points that seem like outliers. Luckily, we can save some time by using the [z-score function](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.zscore.html) from scipy's statistics library, which will give us a z-score calculation for all data points.

# + id="hJZklD3uOJm-" colab={"base_uri": "https://localhost:8080/"} outputId="4dc5d270-b14c-4828-f6a8-419d95ad0836"
from scipy import stats
import pandas as pd
import numpy as np

threshold = 3 #@param{type: "integer"}
z_scores = np.abs(stats.zscore(nx))
odata['z'] = z_scores
lcs = list((odata.loc[odata['z'] > threshold]).index)
print((odata.loc[odata['z'] > threshold]))

cx = list(odata["level"].values)
for idx in odata.index[odata['z'] > threshold].tolist():
  vals = cx[idx-3:idx-2]+cx[idx-2:idx-1]+cx[idx+1:idx+2]+cx[idx+2:idx+3]
  mean_val = np.mean(vals)
  odata.loc[idx, 'level'] = mean_val


# + [markdown] id="ea-5LSSkOelC"
# It looks like the code was able to successfully identify the two outliers!
#
# We can also visualize the two outliers by locating them in a graph of the glucose levels. Run the cell below to check it out!

# + id="aperup6jb7YA" colab={"base_uri": "https://localhost:8080/", "height": 564} outputId="977cf766-7309-43eb-ba26-540834f1798c"
# Plot glucose data with conditional outliers highlighted (Plot adapted from the Biostrap notebook: https://colab.research.google.com/github/Stanford-Health/wearable-notebooks/blob/main/notebooks/biostrap_evo.ipynb#scrollTo=ysL4wqBcGC7j)
plt.figure(figsize=(10, 6))
plt.plot(odata['level'], label='level data', alpha=0.7)
plt.scatter(random_indices, outliers['level'], color='r', label='Conditional Outliers')
plt.legend()
plt.title('Glucose Data with Conditional Outliers Highlighted')
plt.xlabel('Time Index')
plt.ylabel('Glucose Level')
plt.show()

# + [markdown] id="2sHttKpIgs1j"
# # 9. Statistical Data Analysis

# + [markdown] id="Buc3V0bDGA33"
# ## 9.1: Blood glucose level vs. time of day (day vs. night)

# + [markdown] id="4AXQBfN4KDre"
# Since people (generally) sleep at night and eat during the day, one hypothesis is that glucose values will be different during the day compared to the night. Let's see if this is true. First, we will get the glucose values for each day and separate them into day time and night time values. We define day time as 9AM to 12AM (midnight) and night time as 12AM (midnight) to 9 am here, although these values can be adjusted as dayStart and dayEnd in the code.
#
# As a note, our implementation here examines all of our extracted data, so the visualization presented here may span multiple days or even weeks.

# + id="VWfrRegdLCje"
from datetime import time
import scipy.stats as stats

df = data

dayStart = time(9, 00, 00)
dayEnd = time(0, 00, 00)

allTimes = pd.to_datetime(df.loc[:,'time']).dt.time

# create a mask for the day/night
if dayStart < dayEnd:
    mask = (allTimes >= dayStart) & (allTimes <= dayEnd)
else:
    mask = (allTimes >= dayStart) | (allTimes <= dayEnd)

# separate dataframe into day and night using mask
df["Time of Day"] = mask
df["Time of Day"] = df["Time of Day"].map({True: 'Day', False: 'Night'})

# + [markdown] id="Twi_M1rbhCAA"
# Let's use [seaborn](https://seaborn.pydata.org/) to generate a scatter plot to take an initial look.

# + id="InuS5ksQhDSR" colab={"base_uri": "https://localhost:8080/", "height": 523} outputId="f5ef6e58-5a85-4e1e-cc43-430a0393d798"
import seaborn as sns

sns.catplot(x="Time of Day", y="level", data=df, palette=sns.color_palette('pastel'))

# + [markdown] id="nUmscDzxhEbw"
# Now, since we're comparing two means, we could use a one-way ANOVA (analysis of variance). For this to be a valid analysis, we have to ensure the data is [independent, normally distributed, and homoscedastic](https://www.statisticssolutions.com/free-resources/directory-of-statistical-analyses/anova/).
#
# Let's check normality first.

# + id="bfgmAx-uhGVQ" colab={"base_uri": "https://localhost:8080/", "height": 927} outputId="4e4f6a55-b672-4300-e89c-7b5638138105"
import matplotlib.pyplot as plt

# plot histogram for datapoints during the day to verify normality
plt.hist(df.loc[df["Time of Day"] == 'Day']['level'])
plt.title("Day Time")
plt.xlabel("Level")
plt.ylabel("Number of Observations")
plt.show()

# plot histogram for datapoints during the night to verify normality
plt.hist(df.loc[df["Time of Day"] == 'Night']['level'], color="orange")
plt.title("Night Time")
plt.xlabel("Level")
plt.ylabel("Number of Observations")
plt.show()

# + [markdown] id="nMoqa31e3AxD"
# Since the data do not look normally distributed, we can use a [Kruskal-Wallis test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html#scipy.stats.kruskal) instead of an ANOVA.

# + id="47JoWn9K3Bjp" colab={"base_uri": "https://localhost:8080/"} outputId="c2dc6a80-5d20-4d84-888a-b39e56126bc9"
from scipy import stats

stats.kruskal(df.loc[df["Time of Day"] == 'Day']['level'],df.loc[df["Time of Day"] == 'Night']['level'])

# + [markdown] id="JxiYBSWq3PAK"
# Thus we can reject the null hypothesis that the population medians do not significantly differ (p<\0.05), and that night time values are different from day time values.

# + [markdown] id="crrhB9ZNGVm4"
# ## 9.2: Blood glucose level after change of behavior
#
# Does a patient change their eating habits throughout the course of the study When a patient changes their eating habits in order to keep their glucose levels in check, does it work? One analysis we could do is, given the date at which the patient started implementing changes in eating habits (like eating less sweets), determine if there is a significant difference in the blood glucose levels throughout the day (140 mg/dL).
#
# For this type of question, we will use student's [T-Test](https://www.statisticshowto.com/probability-and-statistics/t-test/), a statistical test used to compare and determine if there exists a meaningful difference between the means of some value in two separate groups. Here our first group will be the set of data before the patient changed their eating habits, and the second group will be the data after the patient changed their eating habits.
#
# We will thus separate our extracted glucose levels data into our two groups based on the date of behavior change, and then perform a T-Test across the means of the two groups of data. This analysis will allow us to understand how effective a change in behavior was on a participant's glucose levels.
#
# The date of behavioral change below can be modified as needed.

# + id="UdY_alRYUfJl" cellView="form"
#@title Enter date of eating habit change

date_of_change = "2022-03-30T12:00:00" #@param {type:"string"}

# + id="IMpQSV4c7STd" colab={"base_uri": "https://localhost:8080/"} outputId="c15da611-e3f3-4d43-c8f8-bc962bc77746"
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
from datetime import timedelta, datetime
import re

df = data

pat = date_of_change + "*(.+)"

# find the index of behavior change to split thed ata into two groups
split = list(df["time"].str.match(pat).values)
split = split.index(True)


# this function splits the data into f (first), and s (second), representing the two groups
def differ(df):
  rows = len(df.index)
  f = df.iloc[range(split)]["level"]
  s = df.iloc[range(split,rows)]["level"]
  return ttest_ind(f,s)

print(differ(df))

# + [markdown] id="0jFtWMZl74UY"
# Since the t-test returned a positive value, this means the sample mean in the first half of the data is greater than the sample mean in the second half of the data. This might lead us to hypothesize that the patient has indeed changed their eating habits for the better! But is this the case?
#
# Examining the pvalue < 0.05 implies that the probability of this result occuring by under the assumption the patient did not change behaviors is less than 5%. This implies our result was statistically significant and that we should accept our hypothesis. We can conclude then that the patient did make a behavior change at the specified date!
