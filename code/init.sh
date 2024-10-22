#!/bin/bash
set -e
aws s3 cp s3://stack-app-project-1/app/app_libraries.zip app_libraries.zip
tar -xzf app_libraries.zip -C /home/hadoop/
