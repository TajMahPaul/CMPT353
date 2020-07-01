import sys
import pandas as pd
import datetime
import numpy as np
from scipy import stats

OUTPUT_TEMPLATE = (
    "Initial (invalid) T-test p-value: {initial_ttest_p:.3g}\n"
    "Original data normality p-values: {initial_weekday_normality_p:.3g} {initial_weekend_normality_p:.3g}\n"
    "Original data equal-variance p-value: {initial_levene_p:.3g}\n"
    "Transformed data normality p-values: {transformed_weekday_normality_p:.3g} {transformed_weekend_normality_p:.3g}\n"
    "Transformed data equal-variance p-value: {transformed_levene_p:.3g}\n"
    "Weekly data normality p-values: {weekly_weekday_normality_p:.3g} {weekly_weekend_normality_p:.3g}\n"
    "Weekly data equal-variance p-value: {weekly_levene_p:.3g}\n"
    "Weekly T-test p-value: {weekly_ttest_pl:.3g}\n"
    #"Mann–Whitney U-test p-value: {utest_p:.3g}"
)

def transform(df):
    # df['log'] = np.log(df['comment_count'])
    df['sqrt'] = np.sqrt(df['comment_count'])
    # df['sqrd'] = df['comment_count']**2
    return df

def weekly(df):
    df['yearWeekTuple'] = df['date'].map(lambda val: datetime.date.isocalendar(val)[:2])
    return df.groupby('yearWeekTuple').mean()

def main():

    reddit_counts = sys.argv[1]
    counts = pd.read_json(sys.argv[1], lines=True)
    counts['date'] = pd.to_datetime(counts['date'])
    # from https://stackoverflow.com/questions/32278728/convert-dataframe-date-row-to-a-weekend-not-weekend-value
    counts['isWeekDay'] = ((pd.DatetimeIndex(counts.date).dayofweek) // 5 == 1).astype(float)
    
    counts['year'] = counts['date'].dt.year
    counts = counts[counts.year.isin( [2012, 2013])]
    counts = counts[counts['subreddit'] == 'canada']

    weekday = counts[counts['isWeekDay'] == 1.0]
    weekend = counts[counts['isWeekDay'] == 0]
    
    ttest = stats.ttest_ind(weekday['comment_count'], weekend['comment_count'])
    print(ttest.pvalue)
    initial_ttest_p = ttest.pvalue
    initial_weekday_normality_p = stats.normaltest(weekday['comment_count']).pvalue
    initial_weekend_normality_p = stats.normaltest(weekend['comment_count']).pvalue
    initial_levene_p = stats.levene(weekday['comment_count'], weekend['comment_count']).pvalue

    weekend = transform(weekend)
    weekday = transform(weekday)

    transformed_weekday_normality_p = stats.normaltest(weekday['sqrt']).pvalue
    transformed_weekend_normality_p = stats.normaltest(weekend['sqrt']).pvalue
    transformed_levene_p = stats.levene(weekday['sqrt'], weekend['sqrt']).pvalue
    
    weekend_groupby = weekly(weekend)
    weekday_groupby = weekly(weekday)
    
    weekly_weekday_normality_p=stats.normaltest(weekday_groupby['comment_count']).pvalue,
    weekly_weekend_normality_p=stats.normaltest(weekend_groupby['comment_count']).pvalue,
    weekly_levene_p=stats.levene(weekend_groupby['comment_count'], weekday_groupby['comment_count']).pvalue,
    ttest = stats.ttest_ind(weekend_groupby['comment_count'], weekday_groupby['comment_count'])
    weekly_ttest_p = ttest.pvalue
    utest = stats.mannwhitneyu(weekday['comment_count'], weekend['comment_count'], use_continuity=True, alternative=None)
    utest_p = utest.pvalue
    string = '''
        Initial (invalid) T-test p-value: {0:.3g}
        Original data normality p-values: {1:.3g} {2:.3g}
        Original data equal-variance p-value: {3:.3g}
        Transformed data normality p-values: {4:.3g} {5:.3g}
        Transformed data equal-variance p-value: {6:.3g}
        Weekly data normality p-values: {7:.3g} {8:.3g}
        Weekly data equal-variance p-value: {9:.3g}
        Weekly T-test p-value: {10:.3g}
        Mann–Whitney U-test p-value: {11:.3g}
    '''.format(initial_ttest_p, initial_weekday_normality_p, initial_weekend_normality_p, initial_levene_p,transformed_weekday_normality_p, transformed_weekend_normality_p, transformed_levene_p, weekly_weekday_normality_p[0], weekly_weekend_normality_p[0], weekly_levene_p[0], weekly_ttest_p, utest_p)
    print(string)


if __name__ == '__main__':
    main()  