import boto3
import logging
import json
import requests
import os
import io
import docx
import PyPDF2
import openpyxl
import tiktoken
import embed

logger = logging.getLogger()
logger.setLevel(logging.INFO)
lambda_client = boto3.client('lambda')


def chunk_text(paragraphs, max_tokens=1024, model_name="gpt-3.5-turbo"):
    """
    Join paragraphs into chunks, each no more than `max_tokens` tokens.
    """
    enc = tiktoken.encoding_for_model(model_name)
    chunks = []
    current_chunk = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = len(enc.encode(para))
        if para_tokens > max_tokens:
            # long paragraphs become individual chunks
            chunks.append(para)

        if current_tokens + para_tokens > max_tokens:
            # Finalize current chunk
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = []
            current_tokens = 0

        current_chunk.append(para)
        current_tokens += para_tokens

    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks


def get_file_url(file_key):
    payload = json.dumps(
        {
            'FileKey': file_key
        }
    )

    response = lambda_client.invoke(
        FunctionName="ChatRAG-GetDocument",
        InvocationType='RequestResponse',  # Use 'Event' for async invocation
        Payload=payload
    )

    response_payload = response['Payload'].read().decode('utf-8')
    response = json.loads(response_payload)
    if response['statusCode'] != 200:
        raise Exception(response_payload)

    response_body = json.loads(response['body'])
    url = response_body['file_url']
    return url


def get_file_content(url):
    file_response = requests.get(url)
    if file_response.status_code != 200:
        raise Exception(f"Failed to fetch file content: {file_response.status_code}")

    return file_response.content


def parse_file_content(file_name, file_bytes):
    ext = os.path.splitext(file_name)[-1].lower()

    if ext == '.txt' or ext == '.md':
        # Treat as UTF-8 encoded text and split into paragraphs by blank lines
        content = file_bytes.decode('utf-8')
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        return paragraphs

    elif ext == '.docx':
        doc = docx.Document(io.BytesIO(file_bytes))
        return [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    elif ext == '.pdf':
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        paragraphs = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                paragraphs.extend([p.strip() for p in text.split('\n') if p.strip()])
        return paragraphs

    elif ext == '.xlsx':
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        paragraphs = []
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                line = '\t'.join([str(cell) if cell is not None else '' for cell in row]).strip()
                if line:
                    paragraphs.append(line)
        return paragraphs

    else:
        raise Exception(f"Unsupported file type: {ext}")


def parse(file_key):
    logger.warning(f'parse {file_key}')
    url = get_file_url(file_key)
    content = get_file_content(url)
    paragraphs = parse_file_content(file_key, content)
    chunks = chunk_text(paragraphs)

    for i, chunk in enumerate(chunks):
        escaped_chunk = chunk.replace('\n', '\\n')
        embedding = embed.embed_text(chunk)
        logger.warning(f"chunk{i}: {escaped_chunk}, embedding={embedding}")
