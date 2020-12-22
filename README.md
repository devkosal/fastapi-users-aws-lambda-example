# FastAPI Users + AWS Lambda Example

Note: this example mostly leverages other tutorials to create a users database API with FastAPI Users and AWS Lambda. 

## 0. Prerequesites

- Python 3.7+
- Docker

## 1. Create Users API 

This API is configured following `FastAPI Users` documentation starting [here](https://frankie567.github.io/fastapi-users/installation/). The SQLAlchemy [full example](https://frankie567.github.io/fastapi-users/configuration/full_example/) was modified to create `app/lambda_function.py`

Next, create a file named `config.py` in the `app` directory:

`touch app/config.py`

Define the following variables as per your needs:

```python
testing = False # set this to True to test on a local sqlite db
SECRET = "SECRET"    
PROJECT_NAME = "My Users API"
STAGE_NAME = "/dev" # remember this so you set the correct stage name in AWS API settings later
DB_USERNAME = "username"
DB_PASSWORD = "password"
DB_ADDRESS = "1.1.1.1" #  db host name/address
DB_NAME = "db_name"
root_response = {"Hello": "Welcome to my users API. Visit /docs route for documentation."}

# remember this so you set the correct stage name in AWS API settings later.
# if you are doing local testing, set this to be an empty string
STAGE_NAME = "/dev" 
```

## 2. Deploy the API with AWS Lambda

Given the modifications below, follow instructions [here](https://towardsdatascience.com/fastapi-aws-robust-api-part-1-f67ae47390f9) to complete this step.

####  Modifications: 
- For the AWS lambda layer creation step ([steps 1 and 4 in TDS article](https://towardsdatascience.com/fastapi-aws-robust-api-part-1-f67ae47390f9)), you can alternatively use the zip file created via `create_aws_layer` i.e. `fastapi-mysql.zip`:

    - Command: `sh create_aws_layer`
    - This step loads all your python dependencies into one place. 
    - If your zip file is < 10 MB, you can forego the S3 step as well and upload the zip directly. If > 10 MB, you can use `copy_zip_to_s3 AWS_BUCKET_NAME` command to upload the zip file to S3. You will need AWS CLI set up to use the `copy_zip_to_s3` script. 
    - Note that a docker container is used to create the dependencies' zip file because linux binaries are required to run them smoothly in lambda. 

- Only upload the contents of `app/` to your root AWS lambda function directory.

- If you want to take advantage of `/docs` FastAPI route, you must speicify the `openapi_prefix` in `lambda_function.py` which is tied to `STAGE_NAME` in `app/config.py`. See [this issue from fastapi-aws-lambda-example](https://github.com/iwpnd/fastapi-aws-lambda-example/issues/2) for more details. 

## Notes

- This specific tutorial only supports Mac/Linux. 
- This example uses MySQL as the database but this repo can be easily adapated to use other backends (e.g. postgres, sqlite etc.) See [FastAPI Users Documentation](https://frankie567.github.io/fastapi-users/installation/) for more details. 





