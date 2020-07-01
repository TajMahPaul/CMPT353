import sys
import pandas as pd
import numpy as np
from scipy import stats
OUTPUT_TEMPLATE = (

    '"Did more/less users use the search feature?" p-value: {more_users_p:.3g}\n'
    '"Did users search more/less?" p-value: {more_searches_p:.3g}\n'
    '"Did more/less instructors use the search feature?" p-value: {more_instr_p:.3g}\n'
    '"Did instructors search more/less?" p-value: {more_instr_searches_p:.3g}'
)

def run(new, old):
    old_alteast_one_search = old[old['search_count'] > 0]['search_count'].count()
    old_no_search = old[old['search_count'] <= 0]['search_count'].count()
    
    new_alteast_one_search = new[new['search_count'] > 0]['search_count'].count()
    new_no_search = new[new['search_count'] <= 0]['search_count'].count()

    chi_square_input = [[old_alteast_one_search,  old_no_search], [new_alteast_one_search, new_no_search]]

    chi2, p_chi, dof, expected = stats.chi2_contingency(chi_square_input)
    stat, p_man = stats.mannwhitneyu(new['search_count'], old['search_count'], alternative= 'two-sided')

    return (p_chi, p_man)
def main():
    
    # read the file
    searchdata_file = sys.argv[1]
    df = pd.read_json(searchdata_file,orient='records', lines=True)
    
    # seperate the population
    df_new = df[np.mod(df['uid'], 2) == 1 ]
    df_old = df[np.mod(df['uid'], 2) == 0 ]

    # run tests on population
    more_users_p, more_searches_p = run(df_new, df_old)

    # filter out non-instructors
    df_new_intr = df_new[df_new['is_instructor'] == True ]
    df_old_intr = df_old[df_old['is_instructor'] == True ]

    more_instr_p, more_instr_searches_p = run(df_new_intr, df_old_intr)

    print(OUTPUT_TEMPLATE.format(
        more_users_p=more_users_p,
        more_searches_p=more_searches_p,
        more_instr_p=more_instr_p,
        more_instr_searches_p=more_instr_searches_p,
    ))


if __name__ == '__main__':
    main()