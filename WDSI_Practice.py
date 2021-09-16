#random number generation
from random import random
#Autoregressive modeling(uses the previous dependant variable for next prediction) 
from statsmodels.tsa.ar_model import AR
#Graph Time series model
import matplotlib.pyplot as pyplt
#Autoregressive moving average modeling(uses the previous value and its residual error for next prediction) 
from statsmodels.tsa.arima_model import ARMA
#Exponential smoothing modeling(uses the previous value and its residual error for next prediction(difference between ARIMA and Exp smoothing is the level of 
#weight that previous values have on influenceing future values(Exp smoothing is less)))
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

#creates a psuedo dataset for time series, and graphs it using pyplot
time_series=[2*x**2 + random() for x in range(1,100) ]
pyplt.plot(time_series)
pyplt.show()

#creates a autoregressive model of time_series, and predicts the value at the end of time_series array
model=AR(time_series)
model_fit=model.fit()
x=model_fit.predict(len(time_series),len(time_series))
print(x)
#creates a autoregressive moving average model of time_series, and predicts the value at the end of time_series array
model=ARMA(time_series,order=(0,1))
model_fit=model.fit(disp=False)
y=model_fit.predict(len(time_series),len(time_series))
print(y)
#creates a Simple Exponential Smoothing model of time_series, and predicts the value at the end of time_series array
model=SimpleExpSmoothing(time_series)
model_fit=model.fit()
z=model_fit.predict(len(time_series),len(time_series))
print(z)
#provides final values of time series modeling
print("AR={}\nARMA={}\nSimpleExpSmoothing={}".format(x,y,z))
