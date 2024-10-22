import boto3  # AWS SDK for Python, used to interact with AWS services
import json   # Used to format and print JSON responses

from dotenv import load_dotenv
load_dotenv()

var_Ec2KeyName = 'ec2_name'
var_script_extract = 's3://stack-app-project-1/app/extract_files.sh'
var_role_service  = 'EMR_DefaultRole'
var_instance_role = 'EMR_EC2_DefaultRole'
var_subnet_id = 'subnet-0b8956b74ba993948'

# Initialize a Boto3 client for EMR (Elastic MapReduce)
client = boto3.client(
    'emr',  # The EMR service we're interacting with
    aws_access_key_id = os.getenv('access_key_id'),
    aws_secret_access_key = os.getenv('secret_access_key'),
    region_name='us-east-1'  # Specify the AWS region where the EMR cluster will be launched
    # Credentials are now fetched automatically from environment variables or AWS credentials configuration
)

# Define the job flow (EMR cluster configuration) and submit the request to create the cluster
response = client.run_job_flow(
    Name="Emr-Cluster-Stack",  # Name of the EMR cluster
    ReleaseLabel='emr-6.3.0',  # EMR version to use (this is the software bundle version)
    LogUri='s3://aws-logs-562248030452-us-east-1/elasticmapreduce/',  # S3 bucket to store logs
    
    # Applications to install in the EMR cluster
    Applications=[
        {'Name': 'Hadoop'},  # Hadoop is the backbone of EMR
        {'Name': 'Spark'},   # Spark for big data processing
        {'Name': 'Hive'}     # Hive for SQL-like querying of data
    ],
    
    # Instance configuration for the cluster
    Instances={
        'InstanceGroups': [
            {
                'Name': "Master nodes",  # Name for the master node group
                'Market': 'ON_DEMAND',   # Purchase type: On-demand instance
                'InstanceRole': 'MASTER',  # Role: Master node, manages the cluster
                'InstanceType': 'r5.2xlarge',  # Instance type for the master node
                'InstanceCount': 1,  # Number of master nodes (usually 1)
            },
            {
                'Name': "Slave nodes",  # Name for the slave (core) node group
                'Market': 'ON_DEMAND',  # Purchase type: On-demand instances
                'InstanceRole': 'CORE',  # Role: Core node, performs data processing
                'InstanceType': 'r5.2xlarge',  # Instance type for the core nodes
                'InstanceCount': 2,  # Number of core nodes (2 in this case)
            }
        ],
        'TerminationProtected': False,  # If False, the cluster can be terminated by user actions
        'Ec2KeyName': var_Ec2KeyName,  # EC2 key pair for SSH access to the instances
    },

    # Bootstrap actions to run before the cluster is ready (e.g., custom setups)
    BootstrapActions=[
        {
            'Name': 'Download and Extract files on cluster',  # Descriptive name for the bootstrap action
            'ScriptBootstrapAction': {
                'Path': var_script_extract  # Path to the script that extracts application files on the cluster
            }
        }
    ],
    
    # Steps are tasks (like Spark jobs) that will be executed after the cluster is set up
    Steps=[
        {
            'Name': 'Run Spark App',  # Name of the step (running a Spark job)
            'ActionOnFailure': 'TERMINATE_CLUSTER',  # Action to take if the step fails (terminate the cluster)
            'HadoopJarStep': {
                'Args': ['sudo', 'spark-submit', '/home/hadoop/job-1-spark.py'],  # Command to submit the Spark job
                'Jar': 'command-runner.jar'  # EMR's default JAR to run commands on the cluster
            }
        }
    ],

    # IAM roles to allow EMR to access AWS resources
    VisibleToAllUsers=True,  # Whether the cluster is visible to all users in the AWS account
    ServiceRole=var_role_service,  # IAM role that EMR uses to access AWS services on your behalf
    JobFlowRole=var_instance_role,  # IAM role that the EC2 instances in the cluster use to access AWS services
)

# Print the response from AWS, which includes the cluster's ID and other details
print(json.dumps(response, indent=4, sort_keys=True, default=str))
