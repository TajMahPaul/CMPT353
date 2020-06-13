import sys
import pandas as pd
from difflib import get_close_matches
import numpy as np

def read_movie_rating_file(filename):
    df = pd.read_csv(filename)
    return df

def read_movie_file(filename):
    lines = open(filename).readlines()
    df = pd.DataFrame(lines, columns=['title'])
    df = df.replace('\n','', regex=True)
    return df

def main():
    assert len(sys.argv) == 4, "Wrong number of cli arguments. Usage: python3 average_ratings.py <movie_list_file> <rating_csv_file> <output_file_name>"

    move_list_txt_file_name = sys.argv[1]
    move_ratings_csv_file_name = sys.argv[2]
    output_csv_file_name = sys.argv[3]

    df_movies_list = read_movie_file(move_list_txt_file_name)
    df_movies_ratings = read_movie_rating_file(move_ratings_csv_file_name)

    df_movies_ratings['best_rep'] = df_movies_ratings.apply (lambda row: get_close_matches(row.title, df_movies_list['title'], n=1), axis=1)
    df_movies_ratings['best_rep'] = df_movies_ratings['best_rep'].map (lambda x: x[0] if len(x) > 0 else np.NaN)
    df_movies_ratings = df_movies_ratings[df_movies_ratings.best_rep.notnull()]
    df_movies_ratings = df_movies_ratings.drop(['title'], axis =1)
    df_movies_ratings = df_movies_ratings.groupby(['best_rep']).mean().round(2)
    
    df_movies_list = pd.merge(left=df_movies_list, right=df_movies_ratings, left_on='title', right_on='best_rep')
    df_movies_list.to_csv(output_csv_file_name,index=False, columns=['title', 'rating'])

if __name__ == '__main__':
    main()