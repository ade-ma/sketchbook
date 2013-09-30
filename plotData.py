import pandas as pd
import numpy as np
import datetime as dt
import astral as al

from matplotlib import pyplot as plt

b = al.Astral()["Boston"]

# use precise coords from SOS
(b.longitude, b.latitude) = (-70.9662135, 42.3177747)

d = pd.read_csv("./209789.csv").replace(to_replace=-9999, value=np.nan)

d['TMAX'] *= 0.1
d['TMIN'] *= 0.1
d['DATE'] = pd.date_range('1/1/1983', periods=d['DATE'].count())

yr = d['DATE'][0:365]

# calculate total hours daylight as sunset-sunrise
daylight = map(lambda x: (x['sunset'] - x['sunrise']).total_seconds()/(60*60), map(lambda x: b.sun(x.to_datetime()), d['DATE']))

# http://www.pveducation.org/pvcdrom/properties-of-sunlight/air-mass
# equation from "Revised optical air mass tables and approximation formula / Fritz Kasten and Andrew T. Young / Applied Optics, Vol. 28, Issue 22, pp. 4735-4738 (1989)"
# airmass equation incorporates earth curvature
airMass = lambda ZA: 1.0/(np.cos(np.radians(ZA)) + (0.50572 * (96.07995 - ZA)**-1.6364))
# 0.7 -> atmospheric attenuation
# 0.678 -> emperical fit
# 1.353 -> solar flux constant (kw/m**2)
solarFlux = lambda AM: 1353 * 0.7**(AM**0.678)

dates = map(lambda x: b.sun(x.to_datetime()), d['DATE'])

from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA

host = plt.subplot()
par1 = host.twinx()
par2 = host.twinx()
par3 = host.twinx()

par2.plot(yr, daylight[0:365], "k-", label="hours of daylight")

for date in dates[0:365]:
	intervals = np.array(map(lambda x: x.to_datetime(),
		pd.date_range(start=date['sunrise'], end=date['sunset'], freq='5Min')))
	powerDensities = np.array(map(lambda x: solarFlux(airMass(90 - b.solar_elevation(x))),
		intervals))
	# multiply power densities by 300 seconds (5 minutes), sum results - forward euler integration
	host.plot(intervals[0], sum(np.array([300]*len(intervals)) * powerDensities) , '.k')

powerDensityNoon = np.array(map(lambda x:
	solarFlux(airMass(90-b.solar_elevation(x['noon']))), dates))

par1.plot(yr, powerDensityNoon[0:365], label="noontime power density")


tmin = list(pd.rolling_mean(d['TMIN'], 2))
tmax = list(pd.rolling_mean(d['TMAX'], 2))

par3.fill_between(yr, tmin[0:365], tmax[0:365], alpha=0.7)
#plt.plot(d['DATE'], daylight, label="daylight (hrs)")
par1.legend(loc='lower left')
par2.legend(loc='lower center')
par3.legend(loc='lower right')
plt.show()
