from ninja import NinjaAPI, Schema, File
from ninja.files import UploadedFile

from django.http import FileResponse as DjangoFileResponse
from . import audioConvert
from . import fileManager
from . import streamAudio
from wsgiref.util import FileWrapper
from django.http import StreamingHttpResponse
from django.conf import settings
import os
import re
from time import time

import mutagen
from mutagen.wave import WAVE

from dotenv import load_dotenv
import os
import boto3

load_dotenv()
piperapikey = os.environ['PIPER_KEY']
AWS_ACCESS_KEY_ID=os.environ['AWS_ACCESS_KEY_ID']
AWS_ACCESS_SECRET_KEY_ID=os.environ['AWS_ACCESS_SECRET_KEY_ID']
AWS_STORAGE_BUCKET_NAME=os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_S3_REGION_LOCATION=os.environ['AWS_S3_REGION_LOCATION']

s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_ACCESS_SECRET_KEY_ID,
                  region_name=AWS_S3_REGION_LOCATION
                  )
#s3 = boto3.client('s3')
bucket_name = AWS_STORAGE_BUCKET_NAME


api = NinjaAPI() # ninja actually has its own API key security you can copy in!!!!

class Item(Schema):
    #input_text: str #must be file
    modelname: str
    userid: str
    name_file: str
    key: str

class Query(Schema):
    userid: str
    name_of_file: str
    file_id: str
    file_path: str

class UserInfo(Schema):
    userid: str
    userfolderpath: str

class FileLocate(Schema):
    userid: str
    name_of_file: str
    file_id: str
    file_path: str


def get_file_size_in_mb(file_path):
    # Get the size of the file in bytes
    file_size_in_bytes = os.path.getsize(file_path)

    # Convert bytes to megabytes (1 MB = 1024 * 1024 bytes)
    file_size_in_mb = file_size_in_bytes / (1024 * 1024)

    return file_size_in_mb

"""
No longer needs to be asynchronous as I removed the streaming call to use S3 instead.
"""
@api.post("/ttsCreate")
def text_to_speech(request, item: Item, file_input: UploadedFile = File(...)):
    #input_text = file_input.read().decode('utf-8')

    file_content = file_input.file.read()

        # Attempt to decode the bytes into a UTF-8 string
    input_text = file_content.decode('UTF-8')
    #decode = True
    #if decode == True:
    #    return (f"First 10 bytes: {file_content[:10]}")

    if item.key != piperapikey:
        return "Error:  incorrect key"
    try:
        start_time = time()
        if len(input_text) < 7200:
            # Generate the audio file using Google Text-to-Speech asynchronously
            file_path_and_nameArr = audioConvert.call_piper_gaps_and_pause(input_text, item.modelname, item.userid, item.name_file)
            waveFile = WAVE(file_path_and_nameArr[0])
            waveFile_info = waveFile.info
            lengthOfFileSeconds = int(waveFile_info.length)
            end_time = time()
            execution_time = end_time - start_time

        else:
            file_path_and_nameArr = audioConvert.callLongTextPiper(input_text, item.modelname, item.userid, item.name_file)
            waveFile = WAVE(file_path_and_nameArr[0])
            waveFile_info = waveFile.info
            lengthOfFileSeconds = int(waveFile_info.length)
            end_time = time()
            execution_time = end_time - start_time
    #s3 upload
        s3filepath = file_path_and_nameArr[0][2:]  # Key is the name of the object in S3
        s3.upload_file(file_path_and_nameArr[0], bucket_name, s3filepath)
        # return the path to client
        # should be added to database (after this
        file_sizeMB = get_file_size_in_mb(file_path_and_nameArr[0])
        ret_json = {
            "file_path":s3filepath,
            "name_of_file":file_path_and_nameArr[1],
            "lengthOfFileSeconds": lengthOfFileSeconds,
            "execution_time":execution_time,
            "file_sizeMB" : file_sizeMB,
            "bucket_name" : bucket_name
            }
        audioConvert.delete_file(file_path_and_nameArr[0])
        return ret_json #[file_path_and_nameArr, lengthOfFileSeconds, execution_time]
    except Exception as e:
        # Handle any exceptions that might occur during processing
        return {"error": str(e)}  # Return an error message

@api.post("/getPod")
def get_pod(request, query: Query):
    try:
        audio_file_path = fileManager.getFile(query.userid, query.name_of_file, query.file_id, query.file_path)
        return DjangoFileResponse(open(audio_file_path, "rb"), content_type="audio/wav")
    except Exception as e:
        # Handle any exceptions that might occur during processing
        return {"error": str(e)}  # Return an error message

@api.post("/fetchUserFileList")
def fetchFileList(request, userinfo: UserInfo):
    try:
        return fileManager.returnFileNames(userinfo.userid)
    except Exception as e:
        return {"error": str(e)}

@api.post("/deleteFile")
def deleteFile(request, fileLocate: FileLocate):
    try:
        fileManager.delete_file(f"./outputs/{fileLocate.userid}/{fileLocate.name_of_file}.wav")
        return f"deleted file at {fileLocate.userid}/{fileLocate.name_of_file}.wav"
    except Exception as e:
        return {"error": str(e)}

@api.get("/testGet")
def testGet(request):
    try:
        return "YOU GOT IT BRO! Immaculately formed GET request :)"
    except Exception as e:
        return {"error": str(e)}

# represents the regular expression pattern used to parse the Range header.
RANGE_RE = re.compile(r"bytes\s*=\s*(\d+)\s*-\s*(\d*)", re.I)

@api.post("/streamAudio")
async def stream_audio_asyc(request, fileLocate: FileLocate):
    path = f"./outputs/{fileLocate.userid}/{fileLocate.name_of_file}"
    content_type = "audio/wav"

    range_header = request.META.get("HTTP_RANGE", "").strip()
    range_match = RANGE_RE.match(range_header)
    size = os.path.getsize(path)

    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = (
            first_byte + 1024 * 1024 * 8
        )  # The max volume of the response body is 8M per piece
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        response = StreamingHttpResponse(
            streamAudio.file_iterator(path, offset=first_byte, length=length),
            status=206,
            content_type=content_type,
        )
        response["Content-Range"] = f"bytes {first_byte}-{last_byte}/{size}"

    else:
        response = StreamingHttpResponse(
            FileWrapper(open(path, "rb")), content_type=content_type
        )
    response["Accept-Ranges"] = "bytes"
    return response


@api.get("/getVoices")
def getVoices(request):
    try:
        return audioConvert.get_voices()
    except Exception as e:
        return {"error": str(e)}


@api.post("/developerspeedtest")
async def devspeedtest(request, item: Item):
    try:
        start_time = time()
        if len(item.input_text) < 7400:
            # Generate the audio file using Google Text-to-Speech asynchronously
            audio_file_path = await audioConvert.call_piper_async(item.input_text, item.modelname, item.userid, item.name_file)
            end_time = time()
            execution_time = end_time - start_time

        else:
            audio_file_path = await audioConvert.callLongTextPiper_async(item.input_text, item.modelname, item.userid, item.name_file)
            end_time = time()
            execution_time = end_time - start_time
        # return the path to client
        # should be added to database after this
        return [audio_file_path, execution_time]
    except Exception as e:
        # Handle any exceptions that might occur during processing
        return {"error": str(e)}  # Return an error message
