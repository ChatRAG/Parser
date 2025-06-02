import boto3
import time
import logging
import json
import parse

logger = logging.getLogger()
logger.setLevel(logging.INFO)
sqs = boto3.client('sqs')
queue_url = 'https://sqs.ap-southeast-2.amazonaws.com/698446905433/chatrag-parse-queue'


def poll_messages():
    logger.warning('Start polling messages...')
    while True:
        resp = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20  # long polling
        )

        messages = resp.get('Messages', [])
        if not messages:
            continue

        logger.warning(f'Received message: {resp}')

        for message in messages:
            body = json.loads(message['Body'])
            file_key = body.get('FileKey')
            file_name = body.get('FileName')
            if file_key is not None and file_name is not None:
                try:
                    parse.parse(file_key, file_name)
                except Exception as e:
                    logger.error(f'parse {file_key} failed, error: {e}')


if __name__ == '__main__':
    poll_messages()
