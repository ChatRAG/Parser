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

        logger.warning(f'Received message: {resp}')

        messages = resp.get('Messages', [])
        if not messages:
            continue

        for message in messages:
            body = json.loads(message['Body'])
            file_key = body.get('FileKey')
            if file_key is not None:
                try:
                    parse.parse(file_key)
                except Exception as e:
                    logger.error(f'parse {file_key} failed, error: {e}')


if __name__ == '__main__':
    poll_messages()
