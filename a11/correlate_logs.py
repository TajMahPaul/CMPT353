import sys
from pyspark.sql import SparkSession, functions, types, Row
import re
import math
spark = SparkSession.builder.appName('correlate logs').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

assert sys.version_info >= (3, 5) # make sure we have Python 3.5+
assert spark.version >= '2.3' # make sure we have Spark 2.3+

line_re = re.compile(r"^(\S+) - - \[\S+ [+-]\d+\] \"[A-Z]+ \S+ HTTP/\d\.\d\" \d+ (\d+)$")


def line_to_row(line):
    """
    Take a logfile line and return a Row object with hostname and bytes transferred. Return None if regex doesn't match.
    """
    m = line_re.match(line)
    if m:
        return Row(host=m.group(1), bytes=m.group(2))
    else:
        return None


def not_none(row):
    """
    Is this None? Hint: .filter() with it.
    """
    return row is not None


def create_row_rdd(in_directory):
    log_lines = spark.sparkContext.textFile(in_directory)
    rows = log_lines.map(line_to_row)
    return rows.filter(not_none)

def main(in_directory):
    logs = spark.createDataFrame(create_row_rdd(in_directory))
    grouped = logs.groupBy(logs['host'])
    grouped = grouped.agg(
        functions.count(logs['host']).alias('x'),
        functions.sum(logs['bytes']).alias('y')
    )
    
    n = grouped.count()
    summedGroup = grouped.groupBy()
    
    x = summedGroup.agg(functions.sum(grouped['x'])).first()[0]
    y =  summedGroup.agg(functions.sum(grouped['y'])).first()[0]
    xy = summedGroup.agg(functions.sum(grouped['x'] * grouped['y'])).first()[0]
    x2 = summedGroup.agg(functions.sum(grouped['x'] * grouped['x'])).first()[0]
    y2 = summedGroup.agg(functions.sum(grouped['y'] * grouped['y'])).first()[0]
    r =  ((n*xy) - ( x*y )) / (math.sqrt( n*x2 - x**2 ) * math.sqrt( n*y2 - y**2 ))
    print("r = %g\nr^2 = %g" % (r, r**2))


if __name__=='__main__':
    in_directory = sys.argv[1]
    main(in_directory)
