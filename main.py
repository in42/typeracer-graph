import sys
from fetcher import fetch_user_data
from plotter import plot

username = sys.argv[1]
fetch_user_data(username)
plot()
