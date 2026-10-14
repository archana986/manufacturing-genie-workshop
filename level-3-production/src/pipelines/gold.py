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


@dlt.table(comment="Work orders used by the maintenance metric view")
def maintenance_work_orders():
    return (
        spark.range(800)
        .withColumn("wo_id", F.concat(F.lit("WO-"), F.col("id").cast("string")))
        .withColumn("line_id", F.concat(F.lit("LN-0"), (F.col("id") % 6 + 1).cast("string"), F.lit("-0"), (F.col("id") % 4 + 1).cast("string")))
        .withColumn("wo_type", F.when(F.col("id") % 4 == 0, F.lit("unplanned")).otherwise(F.lit("planned")))
        .withColumn("opened_date", F.expr("date_sub(current_date(), CAST(id % 80 AS INT))"))
        .withColumn("mttr_minutes", (F.lit(15) + (F.col("id") % 240)).cast("int"))
        .drop("id")
    )
