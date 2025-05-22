import json
import boto3
import wikipediaapi
import datetime

# Configuration to enable or disable log export
ENABLE_LOG_EXPORT = False

# S3 bucket configuration
BUCKET_NAME = 'bedrock-lambda-logging-vinicius'  # Placeholder for the S3 bucket name
s3_client = boto3.client('s3')

def export_to_s3(content, filename):
    """
    Exports given content to S3 as a JSON object if logging is enabled.

    :param content: Content to be exported
    :param filename: File name in the bucket
    """
    if not ENABLE_LOG_EXPORT:
        print("Log export is disabled. Skipping export to S3.")
        return

    try:
        s3_client.put_object(Bucket=BUCKET_NAME, Key=filename, Body=json.dumps(content))
    except Exception as e:
        print(f"Error exporting to S3: {str(e)}")

def log_to_s3(folder='unknown_agent', event=None, response=None, error=None):
    """
    Logs input event, response, or error to S3 if logging is enabled.

    :param event: The input event to log
    :param response: The response to log (optional)
    :param error: The error to log (optional)
    """
    if not ENABLE_LOG_EXPORT:
        return

    timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    try:
        if event:
            s3_input_file_name = f"{folder}/input/{timestamp}_input.json"
            export_to_s3(event, s3_input_file_name)

        if response:
            s3_output_file_name = f"{folder}/output/{timestamp}_output.json"
            export_to_s3(response, s3_output_file_name)

        if error:
            s3_error_file_name = f"{folder}/error/{timestamp}_error.json"
            export_to_s3(error, s3_error_file_name)

    except Exception as e:
        print(f"Error logging to S3: {str(e)}")

def get_wikipedia_url(celebrity_name, language='en'):
    """
    Returns the link to the Wikipedia page for a famous person, if it exists.

    :param celebrity_name: Name of the famous person
    :param language: Language of the Wikipedia page
    :return: URL to the Wikipedia page or a message indicating it was not found
    """
    user_agent = 'LambdaWikipediaLinkFinder (youremail@example.com)'
    wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language=language)
    page = wiki.page(celebrity_name)
    
    if page.exists():
        return page.fullurl
    else:
        return f"The Wikipedia page for '{celebrity_name}' was not found."

def lambda_handler(event, context):
    """
    Lambda function to find the Wikipedia link for a famous person and log the result to S3.

    :param event: Event received by the Lambda
    :param context: Lambda execution context
    :return: Response containing the Wikipedia link or error message
    """
    try:
        agent = event['agent']
        agent_name = agent.get("name", "unknown_agent")
        action_group = event['actionGroup']
        function_name = event['function']
        parameters = event.get('parameters', [])

        # Extracting parameters from the list
        celebrity_name = None
        language = 'en'  # Default language

        for param in parameters:
            if param['name'] == 'celebrity_name':
                celebrity_name = param['value']
            if param['name'] == 'language':
                language = param['value']

        # Validating if the required parameter is present
        if not celebrity_name:
            raise ValueError("Missing required parameter: celebrity_name")

        # Business logic execution
        wikipedia_url = get_wikipedia_url(celebrity_name, language)
        
        response_body = {
            "TEXT": {
                "body": wikipedia_url
            }
        }

        # Building the response
        response = {
            'actionGroup': action_group,
            'function': function_name,
            "functionResponse": {
                "responseBody": response_body
            }
        }

        function_response = {'response': response, 'messageVersion': event['messageVersion']}

        # Log input and response to S3
        log_to_s3(folder=agent_name, event=event, response=function_response)

        return function_response
    except Exception as e:
        print(f"Error executing Lambda: {str(e)}")
        error_response = {
            "errorMessage": str(e),
            "errorType": "LambdaExecutionError"
        }

        # Log input and error to S3
        log_to_s3(folder=agent_name, event=event, error=error_response)

        return error_response