import pandas as pd
import numpy as np
import datetime as dt
import astral as al

from matplotlib import pyplot as plt

_chunk = lambda l, x: [l[i:i+x] for i in xrange(0, len(l), x)]

b = al.Astral()["Boston"]

# use precise coords from SOS
(b.longitude, b.latitude) = (-70.9662135, 42.3177747)

d = pd.read_csv("./209789.csv").replace(to_replace=-9999, value=np.nan)

d['TMAX'] *= 0.1
d['TMIN'] *= 0.1
d['DATE'] = pd.date_range('1/1/1983', periods=d['DATE'].count())

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

for date in dates[0:365]:
	intervals = np.array(map(lambda x: x.to_datetime(),
		pd.date_range(start=date['sunrise'], end=date['sunset'], freq='5Min')))
	powerDensities = np.array(map(lambda x: solarFlux(airMass(90 - b.solar_elevation(x))),
		intervals))
	# multiply power densities by 300 seconds (5 minutes), sum results - forward euler integration
	plt.plot(intervals[0], sum(np.array([300]*len(intervals)) * powerDensities) , '.k')

plt.ylabel("joules/day")
plt.title("joules vs. day")

plt.figure()

powerDensityNoon = np.array(map(lambda x:
	solarFlux(airMass(90-b.solar_elevation(x['noon']))), dates))

plt.plot(d['DATE'][0:365], powerDensityNoon[0:365], label="noon")
plt.ylabel("power density @ noon")

length = len(_chunk(d['DATE'], 365)[0:-2])
tmin = sum(np.array(_chunk(d['TMIN'], 365)[0:-2]))/length
tmax = sum(np.array(_chunk(d['TMAX'], 365)[0:-2]))/length

plt.figure()

plt.fill_between(d['DATE'][0:365], tmin[0:365], tmax[0:365], alpha=0.7)
#plt.plot(d['DATE'], daylight, label="daylight (hrs)")
plt.ylabel("temp (degC)")
plt.legend(loc="best")
plt.show()
