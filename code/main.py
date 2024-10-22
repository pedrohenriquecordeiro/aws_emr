# Import necessary libraries
from os.path import abspath  # Imports the absolute path (not used in the code, but useful for referencing paths)
from pyspark.sql import SparkSession  # Imports SparkSession to create the Spark session
from pyspark.sql.functions import *  # Imports all available functions from PySpark (useful for transformations)

# Creates a Spark session for the application
spark = SparkSession \
    .builder \
    .appName("job-1-spark")  # Defines the name of the Spark application
    .getOrCreate()  # Initializes or retrieves the Spark session

# Sets the logging level of the application. Here it's set to "ERROR" to avoid too many logs in production.
# For development, you can use "INFO" to see more process details.
spark.sparkContext.setLogLevel("ERROR")

# Reading CSV files from the raw zone of the Data Lake
df = spark.read.format("csv")\  # Specifies the format as CSV
    .option("header", "True")\  # Defines that the CSV contains headers
    .option("inferSchema","True")\  # Enables automatic schema inference (data types)
    .csv("s3://stack-test-app/*.csv")  # Reads all CSV files in the specified directory in S3

# Print the data read from the Data Lake (raw zone)
print("\nPrinting the data read from the landing zone:")
print(df.show())  # Displays the first few rows of the DataFrame

# Print the schema (structure of columns and data types) of the DataFrame
print("\nPrinting the schema of the DataFrame read from the raw zone:")
print(df.printSchema())  # Displays the schema inferred from the CSV files

# Converting the read data to Parquet format
print("\nWriting the data read from the raw zone to Parquet in the processing zone...")
df.write.format("parquet")\  # Specifies the write format as Parquet
    .mode("overwrite")\  # Sets the write mode to 'overwrite', to overwrite existing data
    .save("s3a://stack-test-processing/df-parquet-file.parquet")  # Path to save the Parquet files in the processing zone in S3

# Reading the Parquet files saved in the processing zone
df_parquet = spark.read.format("parquet")\  # Specifies the read format as Parquet
    .load("s3a://stack-test-processing/df-parquet-file.parquet")  # Reads the Parquet files from the processing zone in S3

# Print the data read in Parquet format
print("\nPrinting the data read in Parquet from the processing zone")
print(df_parquet.show())  # Displays the first few rows of the Parquet DataFrame

# Create a temporary view of the Parquet DataFrame to allow SQL queries
df_parquet.createOrReplaceTempView("view_df_parquet")  # Creates a temporary view for SQL queries

# Processing the data using a SQL query to calculate sums and averages based on business rules
df_result = spark.sql("""
    SELECT BNF_CODE as Bnf_code,
           SUM(ACT_COST) as Total_Act_cost,  # Sum of action cost (ACT_COST)
           SUM(QUANTITY) as Total_Quantity,  # Sum of quantity (QUANTITY)
           SUM(ITEMS) as Total_Items,  # Sum of items (ITEMS)
           AVG(ACT_COST) as Avg_Act_cost  # Average of action cost (ACT_COST)
    FROM view_df_parquet
    GROUP BY bnf_code  # Group the results by BNF code
""")

# Print the result of the processed DataFrame
print("\n========= Printing the result of the processed DataFrame =========\n")
print(df_result.show())  # Displays the first few rows of the processed DataFrame

# Writing the processed data to Parquet format in the curated zone
print("\nWriting the processed data to the Curated Zone...")

df_result.write.format("parquet")\  # Specifies the write format as Parquet
    .mode("overwrite")\  # Overwrites existing data if present
    .save("s3a://stack-test-curated/df-result-file.parquet")  # Path to save the processed Parquet file in the curated zone in S3

# Writing the processed data to a Delta table in the curated zone
print("\nWriting the processed data to the Delta table in the Curated Zone...")

df_result.write.format("delta")\  # Specifies the write format as Delta
    .mode("overwrite")\  # Overwrites existing data in the Delta table if present
    .save("s3a://stack-test-curated/delta-table")  # Path to save the Delta table in the curated zone in S3

# Stop the Spark session
spark.stop()  # Stops the Spark application and releases resources
