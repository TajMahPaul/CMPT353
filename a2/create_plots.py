import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def main():
    filename1 = sys.argv[1]
    filename2 = sys.argv[2]

    File1CSV = pd.read_csv(filename1, sep=' ', header=None, index_col=1,names=['lang', 'page', 'views', 'bytes'])
    data1 = File1CSV.sort_values(by=['views'], ascending = False)

    File2CSV = pd.read_csv(filename2, sep=' ', header=None, index_col=1,names=['lang', 'page', 'views', 'bytes'])
    data2 = File2CSV.sort_values(by=['views'], ascending = False)
    
    data1['views2'] = data2['views']

    plt.figure(figsize=(10, 6)) # change the size to something sensible
    plt.subplot(1, 2, 1) # subplots in 1 row, 2 columns, select the first
    plt.plot(data1['views'].values) # build plot 1
    plt.title("Popularity Distribution")
    plt.xlabel("Rank")
    plt.ylabel("Views")
    plt.subplot(1, 2, 2) # ... and then select the second
    plt.scatter(data1['views'], data1['views2']) # build plot 2
    plt.title("Daily Correlation")
    plt.xlabel("Day 1 views")
    plt.ylabel("Day 2 views")
    plt.xscale('log')
    plt.yscale('log')
    # plt.show()
    plt.savefig('wikipedia.png') 

if __name__ == '__main__':
    main()

# python3 create_plots.py pagecounts-20190509-120000.txt pagecounts-20190509-130000.txt
 
# REFERENCED:
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.sort_values.html