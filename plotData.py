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

# calculate total hours daylight as sunset-sunrise
daylight = map(lambda x: (x['sunset'] - x['sunrise']).total_seconds()/(60*60), map(lambda x: b.sun(x.to_datetime()), d['DATE']))


# http://www.pveducation.org/pvcdrom/properties-of-sunlight/air-mass
# equation from "Revised optical air mass tables and approximation formula /Fritz Kasten and Andrew T. Young / Applied Optics, Vol. 28, Issue 22, pp. 4735-4738 (1989)"
# airmass equation incorporates earth curvature
airmass = lambda ZA: 1.0/(np.cos(np.radians(ZA)) + (0.50572 * (96.07995 - ZA)**-1.6364))
# 0.7 -> atmospheric attenuation
# 0.678 -> emperical fit
# 1.353 -> solar flux constant (kw/m**2)
solarFlux = lambda AM: 10 * 1.353 * 0.7**(AM**0.678)

elevation = map(lambda x: b.solar_elevation(x['noon']), map(lambda x: b.sun(x.to_datetime()), d['DATE']))

earthFlux = map(lambda e: solarFlux(airmass(90-e)), elevation)

plt.plot(d['DATE'], earthFlux)

tmin = list(pd.rolling_mean(d['TMIN'], 30))
tmax = list(pd.rolling_mean(d['TMAX'], 30))

plt.fill_between(d['DATE'], tmin, tmax, alpha=0.7)
plt.plot(d['DATE'], daylight, label="daylight (hrs)")
#plt.legend(loc="best")
plt.show()
