import sys
from pyspark.sql import SparkSession, functions, types

spark = SparkSession.builder.appName('reddit relative scores').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

assert sys.version_info >= (3, 5) # make sure we have Python 3.5+
assert spark.version >= '2.3' # make sure we have Spark 2.3+

comments_schema = types.StructType([
    types.StructField('archived', types.BooleanType()),
    types.StructField('author', types.StringType()),
    types.StructField('author_flair_css_class', types.StringType()),
    types.StructField('author_flair_text', types.StringType()),
    types.StructField('body', types.StringType()),
    types.StructField('controversiality', types.LongType()),
    types.StructField('created_utc', types.StringType()),
    types.StructField('distinguished', types.StringType()),
    types.StructField('downs', types.LongType()),
    types.StructField('edited', types.StringType()),
    types.StructField('gilded', types.LongType()),
    types.StructField('id', types.StringType()),
    types.StructField('link_id', types.StringType()),
    types.StructField('name', types.StringType()),
    types.StructField('parent_id', types.StringType()),
    types.StructField('retrieved_on', types.LongType()),
    types.StructField('score', types.LongType()),
    types.StructField('score_hidden', types.BooleanType()),
    types.StructField('subreddit', types.StringType()),
    types.StructField('subreddit_id', types.StringType()),
    types.StructField('ups', types.LongType()),
    #types.StructField('year', types.IntegerType()),
    #types.StructField('month', types.IntegerType()),
])


def main(in_directory, out_directory):
    comments = spark.read.json(in_directory, schema=comments_schema)
    comments = comments.cache()
    grouped = comments.groupBy(comments['subreddit'])
    averages = grouped.agg( functions.avg(comments['score']).alias('average') )
    averages = averages.filter(averages.average >= 0)

    comments = comments.join(averages, (averages.subreddit == comments.subreddit), how='inner' ).drop(averages.subreddit)
    # comments = comments.join(functions.broadcast(averages), (averages.subreddit == comments.subreddit), how='inner' ).drop(averages.subreddit)
    comments_filtered = comments.select(
        comments['subreddit'],
        comments['author'],
        (comments['score']/comments['average']).alias('rel_score')
    )
    comments_filtered = comments_filtered.cache()

    grouped = comments_filtered.groupBy(comments_filtered['subreddit'])
    max_comments = grouped.agg( functions.max(comments_filtered['rel_score']).alias('max_rel_score') )
    comments_filtered = comments_filtered.join(max_comments, (max_comments.subreddit == comments_filtered.subreddit) & (max_comments.max_rel_score == comments_filtered.rel_score), how='inner' ).drop(max_comments.subreddit).drop(max_comments.max_rel_score)
    # comments_filtered = comments_filtered.join(functions.broadcast(max_comments), (max_comments.subreddit == comments_filtered.subreddit) & (max_comments.max_rel_score == comments_filtered.rel_score), how='inner' ).drop(max_comments.subreddit).drop(max_comments.max_rel_score)
    comments_filtered.write.json(out_directory, mode='overwrite')


if __name__=='__main__':
    in_directory = sys.argv[1]
    out_directory = sys.argv[2]
    main(in_directory, out_directory)
