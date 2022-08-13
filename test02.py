
import matplotlib.pyplot as plt
import numpy as np

sauceKey = ["abc",
    "def",
    "hij"]

for wrd in sauceKey:
    print(wrd)


x = np.linspace(0,20,100)
plt.plot(x,np.sin(x))
plt.show()