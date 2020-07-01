import pandas as pd
import numpy as np
import sys
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import matplotlib.pyplot as plt
def main():
    # read the file
    data_file = sys.argv[1]
    df = pd.read_csv(data_file)
    partition_sort = df['partition_sort']

    print('ANOVA p-value:\n')
    f, p = stats.f_oneway(df['qs1'], df['qs2'], df['qs3'], df['qs4'], df['qs5'], df['merge1'], df['partition_sort'] )
    print(p)

    x_melt = pd.melt(df)
    posthoc = pairwise_tukeyhsd(
    x_melt['value'], x_melt['variable'],
    alpha=0.05)

    print('Adhoc Anylsis:\n')
    print(posthoc)
    fig = posthoc.plot_simultaneous()
    plt.show()


if __name__ == '__main__':
    main()