import time
from implementations import all_implementations
import pandas as pd
import numpy as np

def main():

    # initalize how many random array per function there will be
    n = 50

    # initialize DataFrame
    data = pd.DataFrame()

    # iterate through all functions
    for func in all_implementations:
        
        # each function will be a coloumn in our DataFrame. Get the name of function to name our column and initialize the values to an empty array 
        values = np.empty(n)
        name_of_function = func.__name__

        # create and append times to values for each random array
        for i in range(n):
            random_array = np.random.randint(10000000, size=15000)
            start_time  = time.time()
            res = func(random_array)
            end_time  = time.time()
            total = end_time - start_time
            values[i] = total

        # create the column in the data frame
        data[name_of_function] = values

    data.to_csv('data.csv', index=False)

if __name__ == '__main__':
    main()