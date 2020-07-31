import sys
from pyspark.sql import SparkSession, functions, types

spark = SparkSession.builder.appName('reddit averages').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

assert sys.version_info >= (3, 5) # make sure we have Python 3.5+
assert spark.version >= '2.3' # make sure we have Spark 2.3+

wiki_schema = types.StructType([
    types.StructField('lang',  types.StringType()),
    types.StructField('page', types.StringType()),
    types.StructField('times_requested', types.LongType()),
    types.StructField('bytes',  types.LongType())
])

def get_date(string):
    file_name = string[string.rfind('/'): -1]
    date = file_name[file_name.find('-') + 1:file_name.rfind('-') + 3]
    return date

udf = functions.UserDefinedFunction(lambda x: get_date(x), types.StringType())

def main(in_directory, out_directory):
    wiki_data = spark.read.csv(in_directory, sep=" ", schema=wiki_schema).withColumn('filename', functions.input_file_name())
    
    wiki_data = wiki_data.withColumn('date', udf(wiki_data.filename))
    wiki_data = wiki_data.filter(wiki_data.lang.eqNullSafe('en'))
    wiki_data = wiki_data.filter(~wiki_data.page.eqNullSafe("Main_Page"))
    wiki_data = wiki_data.filter(~wiki_data.page.startswith("Special:"))
    # wiki_data = wiki_data.cache()

    wiki_data_grouped = wiki_data.groupBy(wiki_data['date']).agg( functions.max(wiki_data['times_requested']).alias('max'), functions.first("page").alias('page'))
    # wiki_data_grouped =wiki_data_grouped.cache()
    wiki_final = wiki_data_grouped.join(wiki_data, (wiki_data.times_requested == wiki_data_grouped.max) & (wiki_data.date == wiki_data_grouped.date)).drop(wiki_data.date).drop(wiki_data.page)
    wiki_final = wiki_final.cache()
    wiki_final = wiki_final.select(
         wiki_final['date'],
         wiki_final['page'],
         wiki_final['max']
    ).orderBy('date','page').write.csv(out_directory + '-wiki', mode='overwrite')


if __name__=='__main__':
    in_directory = sys.argv[1]
    out_directory = sys.argv[2]
    main(in_directory, out_directory)