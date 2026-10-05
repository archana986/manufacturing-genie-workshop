import dlt
from pyspark.sql import functions as F


@dlt.table(comment="Shift-grain gold used by Apex metric views")
def fct_line_shift():
    return (
        spark.range(24)
        .withColumn("line_id", F.concat(F.lit("LN-0"), (F.col("id") % 6 + 1).cast("string"), F.lit("-0"), (F.col("id") % 4 + 1).cast("string")))
        .withColumn("shift_date", F.expr("date_sub(current_date(), 1)"))
        .withColumn("shift_name", F.lit("Morning"))
        .withColumn("planned_seconds", F.lit(28800).cast("bigint"))
        .withColumn("run_seconds", (F.lit(20000) + (F.col("id") % 5000)).cast("bigint"))
        .withColumn("units", (F.lit(900) + (F.col("id") % 120)).cast("bigint"))
        .withColumn("good_units", (F.lit(850) + (F.col("id") % 110)).cast("bigint"))
        .withColumn("ideal_cycle_seconds", F.lit(12.0))
        .drop("id")
    )
