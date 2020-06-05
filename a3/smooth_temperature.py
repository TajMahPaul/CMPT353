import sys
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
from pykalman import KalmanFilter
import numpy as np

def main():
    # create lowess functions
    lowess = sm.nonparametric.lowess

    # retrieve file name from cli argument
    csv_file = sys.argv[1]

    # plt base data
    cpu_data = pd.read_csv(csv_file, parse_dates=['timestamp'])
    plt.figure(figsize=(12, 4))
    plt.plot(cpu_data['timestamp'], cpu_data['temperature'], 'b.', alpha=0.5)

    # plot lowess smoothed
    loess_smoothed = lowess( cpu_data['temperature'],cpu_data['timestamp'], frac=.05)
    plt.plot(cpu_data['timestamp'], loess_smoothed[:, 1], 'r-')

    # plot kalman smoothed
    kalman_data = cpu_data[['temperature', 'cpu_percent', 'sys_load_1', 'fan_rpm']]
    initial_state = kalman_data.iloc[0]
    observation_covariance = np.diag([.10, .10, .10, .10]) ** 2 # TODO: shouldn't be zero
    transition_covariance = np.diag([0.01, 0.01, 0.01, 0.01]) ** 2 # TODO: shouldn't be zero
    transition = [[0.97, 0.5, 0.2, -0.001], [0.1,0.4,2.2,0], [0,0,0.95,0], [0,0,0,1]] # TODO: shouldn't (all) be zero
    kf = KalmanFilter(
        initial_state_mean=initial_state,
        initial_state_covariance=observation_covariance,
        observation_covariance=observation_covariance,
        transition_covariance=transition_covariance,
        transition_matrices=transition
    )
    kalman_smoothed, state_cov = kf.smooth(kalman_data)
    plt.plot(cpu_data['timestamp'], kalman_smoothed[:, 0], 'g-')
    plt.show()
if __name__ == "__main__":
    main()