import os
from subprocess import run
from tempfile import mkdtemp
from threading import Thread
from uuid import uuid4

import boto3
from botocore.client import Config
import requests
# Never put credentials in your code!
from dotenv import load_dotenv
from flask import Flask, request
from flask_restful import Resource, Api, reqparse

load_dotenv()


def required_env(name):
    value = os.environ.get(name)
    if value:
        return value
    raise RuntimeError(f'Missing required environment variable: {name}')


# Keep this value mirrored in web-application/cattube/settings.py.
B2_USER_AGENT_EXTRA = 'b2-video-sharing-example (backblaze-b2-samples)'
B2_REGION = required_env('B2_REGION')
B2_STORAGE_ENDPOINT_URL = f'https://s3.{B2_REGION}.backblazeb2.com'
B2_PRIVATE_BUCKET_NAME = required_env('B2_PRIVATE_BUCKET_NAME')

# Obtain B2 S3 compatible client
s3 = boto3.client(service_name='s3',
                  region_name=B2_REGION,
                  endpoint_url=B2_STORAGE_ENDPOINT_URL,
                  aws_access_key_id=required_env('B2_APPLICATION_KEY_ID'),
                  aws_secret_access_key=required_env('B2_APPLICATION_KEY'),
                  config=Config(user_agent_extra=B2_USER_AGENT_EXTRA))

bucket_name = B2_PRIVATE_BUCKET_NAME

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('inputObject', required=True)
parser.add_argument('webhook', required=True)
parser.add_argument('token', required=True)


def transcode(inputObject, webhook, token):
    input_video = inputObject

    # Unfortunately, we can't directly stream the B2 object into ffmpeg, since
    # many video formats require ffmpeg to seek around the data to decode it
    input_file = os.path.join(mkdtemp(), str(uuid4()))

    print(f'Downloading s3://{bucket_name}/{input_video} to {input_file}')

    s3.download_file(bucket_name, input_video, input_file)

    output_file = input_file + '.mp4'
    thumbnail_file = input_file + '.jpg'
    command = (f'ffmpeg -y -i {input_file} '
               f'-c:a copy -s hd720 -preset superfast {output_file} '
               f'-ss 00:00:01.000 -vf \'scale=320:320:force_original_aspect_ratio=decrease\' -vframes 1 {thumbnail_file}')

    print(f'Running {command}', flush=True)

    # Have to run in a shell to make this work in a worker thread
    cp = run(command, shell=True)

    print(f'Exit status {cp.returncode}')

    if cp.returncode == 0:
        output_video = os.path.splitext(input_video)[0] + '.mp4'
        output_thumbnail = os.path.splitext(input_video)[0] + '.jpg'

        print(f'Uploading {output_video} to s3://{bucket_name}/{output_video}')
        s3.upload_file(output_file, bucket_name, output_video)

        print(f'Uploading {output_thumbnail} to s3://{bucket_name}/{output_thumbnail}')
        s3.upload_file(thumbnail_file, bucket_name, output_thumbnail)

        response = {
            'status': 'success',
            'inputObject': input_video,
            'outputObject': output_video,
            'thumbnail': output_thumbnail,
            'token': token
        }
    else:
        response = {
            'status': 'failure',
            'inputObject': input_video,
            'token': token
        }

    print(f'POSTing transcoder status for {input_video} to {webhook}')
    r = requests.post(webhook, json=response)
    print(f'Status code {r.status_code}')


class Videos(Resource):
    def post(self):
        if not request.is_json:
            return {'message': 'JSON payload required'}, 415
        args = parser.parse_args()
        thread = Thread(target=transcode, kwargs={**args})
        thread.start()
        return {'status': 'transcoding'}, 200


api.add_resource(Videos, '/videos')

if __name__ == '__main__':
    app.run()
