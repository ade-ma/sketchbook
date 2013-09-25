import pandas as pd
import numpy as np
import datetime as dt
import astral as al

from matplotlib import pyplot as plt

b = al.Astral()["Boston"]

# use precise coords from SOS
print b
(b.longitude, b.latitude) = (-70.9662135, 42.3177747)

d = pd.read_csv("./209789.csv").replace(to_replace=-9999, value=np.nan)

d['TMAX'] *= 0.1
d['TMIN'] *= 0.1
d['DATE'] = pd.date_range('1/1/1983', periods=d['DATE'].count())

# calculate total hours daylight as sunset-sunrise
daylight = map(lambda x: (x['sunset'] - x['sunrise']).total_seconds()/(60*60), map(lambda x: b.sun(x.to_datetime()), d['DATE']))
elevation = map(lambda x: b.solar_elevation(x['noon']), map(lambda x: b.sun(x.to_datetime()), d['DATE']))

plt.plot(d['DATE'], pd.rolling_mean(d['TMIN'], 30), label="tmin (degC)")
plt.plot(d['DATE'], pd.rolling_mean(d['TMAX'], 30), label="tmax (degC)")
plt.plot(d['DATE'], daylight, label="daylight (hrs)")
plt.plot(d['DATE'], elevation, label="elevation (deg)")
plt.legend(loc="best")
plt.show()
