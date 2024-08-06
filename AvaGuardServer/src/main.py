# ***************************************************************************
# Imports for main
# ***************************************************************************
# --------------------------------------------------------------------------
# for file handling
# --------------------------------------------------------------------------
import os
from pathlib import Path

import shutil
import requests
import io
import matplotlib

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from textwrap import wrap
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import json
import aiofiles
import numpy as np

# --------------------------------------------------------------------------
# Standard imports
# --------------------------------------------------------------------------
from mpl_toolkits.basemap import Basemap
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from tempfile import NamedTemporaryFile
# datetime and time
from datetime import datetime, timezone, timedelta
import time
# from time import sleep
# others
from fastapi.security import OAuth2PasswordRequestForm
from uuid_extensions import uuid7, uuid7str
import base64
# import logging


# --------------------------------------------------------------------------
# fastapi related
# --------------------------------------------------------------------------
from fastapi import FastAPI, File, UploadFile, Form, Request, Response, \
    BackgroundTasks, HTTPException, status, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.datastructures import FormData
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

import jwt
from typing import Annotated
from jwt.exceptions import InvalidTokenError

from pydantic import BaseModel
from typing import Annotated

# redis
# from redis import asyncio
# from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

import asyncio

# for  async
from contextlib import asynccontextmanager

# --------------------------------------------------------------------------
# aws
# --------------------------------------------------------------------------
import boto3
import logging
from botocore.exceptions import ClientError
# import sagemaker


# --------------------------------------------------------------------------
# for image processing
# --------------------------------------------------------------------------
from PIL import Image
# import io

# --------------------------------------------------------------------------
# for models
# --------------------------------------------------------------------------
# from pydantic import BaseModel, Extra
# from pydantic import BaseModel, Extra, ValidationError
# from typing import Dict
from typing import Optional

# --------------------------------------------------------------------------
# Avaguard helper
# --------------------------------------------------------------------------
from src.AvaGuardHelpers.avaguard_models import Token, User, TokenData, Observation, PredictionOfImage, TokenAndUser
import src.AvaGuardHelpers.mongoAtlasHelper as mongo
import src.AvaGuardHelpers.userHelper as userhelper
import src.AvaGuardHelpers.observationHelper as obshelper
import src.AvaGuardHelpers.commonHelper as cmnhelper
import src.AvaGuardHelpers.security_configurations as secConfig

matplotlib.use('AGG')
##########################################################################################################
##########################################################################################################
# Initial Code to run when started
##########################################################################################################
##########################################################################################################
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)

app = FastAPI()

AWS_ACCESS_KEY = secConfig.AWS_ACCESS_KEY
AWS_SECRET_KEY = secConfig.AWS_SECRET_KEY
AWS_SESSION_TOKEN = secConfig.AWS_SESSION_TOKEN
AWS_REGION_NAME = secConfig.AWS_REGION_NAME
AWS_S3_BUCKET_NAME = secConfig.AWS_S3_BUCKET_NAME

aws_sagemaker_client = boto3.client(
    'sagemaker-runtime',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION_NAME

    # aws_session_token=AWS_SESSION_TOKEN
)
aws_s3 = boto3.resource("s3",
                        aws_access_key_id=AWS_ACCESS_KEY,
                        aws_secret_access_key=AWS_SECRET_KEY,
                        region_name=AWS_REGION_NAME
                        )

mongodb = mongo.init_mangodb_connection()

origins = secConfig.origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instanitiate the userhelper object
usrhlpr = userhelper.UserHelper(mongodb)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = secConfig.PASSWORD_ENCRYPTION_SECRET_KEY

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


##########################################################################################################
##########################################################################################################
# Lifespan
##########################################################################################################
##########################################################################################################

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    HOST_URL = os.environ.get("REDIS_URL", LOCAL_REDIS_URL)
    logger.debug(HOST_URL)


##########################################################################################################
##########################################################################################################
# Health and Hello APIs
##########################################################################################################
##########################################################################################################

@app.get("/health")
async def health():
    return {"status": "healthy"}


# Raises 422 if bad parameter automatically by FastAPI
@app.get("/hello")
async def hello(name: str):
    return {"message": f"Hello {name}"}


'''
used in register obsrvation - do not delete
'''


async def get_body(request: Request):
    content_type = request.headers.get('Content-Type')
    # print("In Get_body, content_type is..", str(content_type))
    if content_type is None:
        raise HTTPException(status_code=400, detail='No Content-Type provided!')
    elif (content_type == 'application/x-www-form-urlencoded' or
          content_type.startswith('multipart/form-data')):
        try:
            # print("In Get_body, retiurning form..")
            return await request.form()
        except Exception:
            raise HTTPException(status_code=400, detail='Invalid Form data')
    else:
        raise HTTPException(status_code=400, detail='Content-Type not supported!')


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

###################################################################################
## Authentication related
###################################################################################
'''
verifies a provided plain text password to previously hashed password
'''


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


'''
hashes a plain text password to hash
'''


def get_password_hash(password):
    return pwd_context.hash(password)


'''
authenticates a user (accept username and plain text password)
'''


def authenticate_user(username: str, password: str):
    # print("Authentic user=", username, password)
    user = usrhlpr.get_user(username)
    if not user:
        return False
    else:
        if not hasattr(user, 'hashed_password') or user.hashed_password == "":
            user.hashed_password = get_password_hash(user.password)
        if not verify_password(password, user.hashed_password):
            return False
    return user


'''
creates an access token which is valid for timedelta duration

'''


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


'''
gets the current user
'''


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = usrhlpr.get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


##########################################################################################################
##########################################################################################################
# User Login and Registration Related APIs
##########################################################################################################
##########################################################################################################


@app.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # print("tokenanduser=", user)

    return Token(access_token=access_token, token_type="bearer", user=user)


@app.get("/users/me", response_model=User)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)],
):
    # print("current_user:", current_user)
    return current_user


# Raises 422 if bad parameter automatically by FastAPI
@app.get("/login")
async def login(username: str, password: str):
    print("login:", username, password)
    print(username, password)
    _username = username
    _password = password

    uh = userhelper.UserHelper(mongodb)
    _userdoc = uh.get_user(_username)

    print("login", _userdoc)
    # if user not found
    if _userdoc is None:
        return None
        # return {"status": False, "message":"Username not found, please try again", "userDoc": None}
    # if password is wrong
    if _password != _userdoc["password"]:
        return None
        # return {"status": False, "message": "Wrong password entered, please try again", "userDoc": None}
    if not _userdoc["active"]:
        return None
        # return {"status": False, "message": "User is inactive, Login not allowed.", "userDoc": None}

    # all good
    return _userdoc
    # return {"status": True, "message": f"Welcome {_userdoc['username']} to AvalancheGuard", "userDoc": _userdoc}


@app.post('/users/register')
def register(p_user: User
             ):
    # Check if the user already exist and if so , return error response
    print(f"registering user ..{p_user}...")
    print(f"registering user ..{type(p_user)}...")
    uh = userhelper.UserHelper(mongodb)
    rslt, msg = uh.create_user(p_user)

    return {"status": rslt, "message": msg}


@app.get('/users')
def users(current_user: Annotated[User, Depends(get_current_active_user)], ):
    # Check if the user already exist and if so , return error response
    print(f"Getting users..")
    uh = userhelper.UserHelper(mongodb)
    rslt, users_list = uh.get_all_users()

    if current_user.admin_user_flag:
        rslt, users_list = uh.get_all_users()
    else:
        users_list = []
        _user = uh.get_user(current_user.username)
        if not _user.hashed_password:
            _user.hashed_password = get_password_hash(_user.password)
        users_list.append(_user)
    return users_list


@app.get('/users/get_user')
def get_user(username: str, current_user: Annotated[User, Depends(get_current_active_user)], ):
    # Check if the user already exist and if so , return error response
    print(f"Getting users..")
    uh = userhelper.UserHelper(mongodb)
    _user = uh.get_user(username)
    if not _user.hashed_password:
        _user.hashed_password = get_password_hash(_user.password)
    return _user


@app.post('/users/update')
def update_user(user: User, current_user: Annotated[User, Depends(get_current_active_user)], ):
    _user = user
    if current_user.admin_user_flag:
        _user.admin_user_flag = user.admin_user_flag
    else:
        _user.admin_user_flag = False

    uh = userhelper.UserHelper(mongodb)
    _userdoc = uh.get_user(_user.username)
    print(_userdoc)
    # if user not found
    if _userdoc is None or _userdoc == False:
        return None
    # all good
    _userdoc = uh.update_user(_user)

    return _userdoc


@app.delete('/users/delete_user')
def delete_user(username: str, current_user: Annotated[User, Depends(get_current_active_user)], ):
    print(f"Getting Users for deletion..")
    uh = userhelper.UserHelper(mongodb)
    user_doc = uh.delete_user(username)

    return user_doc


##########################################################################################################
##########################################################################################################
# Avalanche Guard APIs
##########################################################################################################
##########################################################################################################
@app.get('/observations')
def observations(current_user: Annotated[User, Depends(get_current_active_user)], ):
    print(f"Getting observations..")
    obsh = obshelper.ObservationHelper(mongodb)
    if current_user.admin_user_flag:
        rslt, obss_list = obsh.get_all_observations("ALL_USERS")
    else:
        rslt, obss_list = obsh.get_all_observations(current_user.username)

    # for o in obss_list:
    #    print(o)

    # print("api call , rslt = ", rslt)

    return obss_list


@app.get('/observations/get_observation')
def get_observation(observation_id: str, current_user: Annotated[User, Depends(get_current_active_user)], ):
    print(f"Getting observations..")
    obsh = obshelper.ObservationHelper(mongodb)
    obs_doc = obsh.get_observation(observation_id)

    return obs_doc


@app.delete('/observations/delete_observation')
def delete_observation(observation_id: str, current_user: Annotated[User, Depends(get_current_active_user)], ):
    print(f"Getting observation for deletion..")
    obsh = obshelper.ObservationHelper(mongodb)
    obs_doc = obsh.delete_observation(observation_id)

    return obs_doc


# ------------------------------------------------------------------
# API : SubmitObservation
# Desc: Accepts data from WebApp and
# a. saves the observation in Amazon S3.
# b. After saving, it uses Model01 : Terrain or Not and if not a terrain, deletes the uploaded image
# c. And returns back that the image uploaded was not a terrain
# d. If the uloaded images is a terrain, it saves the data in MongoDB
#

@app.post("/observations/register_observation_json", response_model=str)
async def register_observation_json(par_obs: dict, current_user: Annotated[User, Depends(get_current_active_user)]):
    print(par_obs)
    p_obs = Observation.parse_obj(par_obs)

    submitted_user: str = p_obs.submitted_user
    avalanche_triggered: bool = p_obs.avalanche_triggered
    avalanche_observed: bool = p_obs.avalanche_observed
    avalanche_experienced: bool = p_obs.avalanche_experienced
    cracking: bool = p_obs.cracking
    collapsing: bool = p_obs.collapsing
    elevation_type: str = p_obs.elevation_type
    datetime_taken_UTC: datetime = p_obs.datetime_taken_UTC
    observation_notes = p_obs.observation_notes
    lat = p_obs.lat
    lng = p_obs.lng
    general_location = p_obs.general_location
    # print("submitted data ", submitted_user)
    # print('obs notes:', observation_notes)

    # Now save the record in MOngoDB
    _obs = Observation()
    _obs.observation_id = p_obs.observation_id

    _obs.imagefile_url = p_obs.imagefile_url
    _obs.observation_notes = p_obs.observation_notes
    _obs.datetime_taken_UTC = p_obs.datetime_taken_UTC.isoformat()
    _obs.timestamp_saved = str(datetime.now())
    _obs.lat = lat
    _obs.lng = lng
    _obs.general_location = general_location
    if avalanche_triggered == 'true':
        _obs.avalanche_triggered = True
    else:
        _obs.avalanche_triggered = False
    if avalanche_observed == 'true':
        _obs.avalanche_observed = True
    else:
        _obs.avalanche_observed = False
    if avalanche_experienced == 'true':
        _obs.avalanche_experienced = True
    else:
        _obs.avalanche_experienced = False

    if _obs.avalanche_experienced or _obs.avalanche_observed or _obs.avalanche_triggered:
        _obs.avalanche_flag = True
    else:
        _obs.avalanche_flag = False
    _obs.cracking = cracking
    _obs.collapsing = collapsing
    _obs.elevation_type = elevation_type

    _obs.submitted_user = submitted_user
    _obs.marked_for_deletion = ""
    _obs.terrain_prediction_score = ""
    _obs.avalanche_prediction_score = ""
    _obs.avalanche_category_prediction = ""
    _obs.segmented_image_url = ""

    temp_imagefilepath = os.path.dirname(os.path.realpath(__file__)) + "/temp/temp_" + _obs.observation_id + ".jpg"
    temp_imagefileFolder = os.path.dirname(os.path.realpath(__file__)) + "/temp"

    temp_imagefilepath = download(_obs.imagefile_url, dest_folder=temp_imagefileFolder,
                                  dest_file=_obs.observation_id + ".jpg")
    print(f"saved to filepath = {temp_imagefilepath}")

    print("*****************************************************************************************")
    prob1, pred_model1 = sagemaker_endpoint(temp_imagefilepath, 1)
    _obs.terrain_prediction_score = pred_model1
    print(_obs.terrain_prediction_score)
    # print(json.loads(_obs.terrain_prediction_score))
    if prob1 > 55:

        prob2, pred_model2 = sagemaker_endpoint(temp_imagefilepath, 2)
        _obs.avalanche_prediction_score = pred_model2

        prob4, pred_model4 = sagemaker_endpoint(temp_imagefilepath, 4)
        if prob2 > 50:
            _obs.avalanche_category_prediction = pred_model4
        else:
            _obs.avalanche_category_prediction += '**Unsure**'
    else:
        _obs.terrain_prediction_score += '*To be deleted*'

    # _obs_str = str(vars(_obs))
    # _obs_str = _obs_str.replace("False", "'false'").replace("True", "'true'").replace("null", "None")
    # print("_obs_str", _obs_str)

    _obs_dict = _obs.asdict()
    print("_obs_dict:", _obs_dict)
    print(f"_obs_dict[daetime_taken_utc] = {_obs_dict['datetime_taken_UTC']}  ")
    print("******************")

    obs_json = _obs_dict  # json.dumps(_obs_dict, indent=4)

    obsh = obshelper.ObservationHelper(mongodb)
    insert_result = obsh.create_observation(obs_json)

    print("returned inser_result:", insert_result)
    print("ret _obs_dict", _obs_dict)

    # clean up
    os.remove(temp_imagefilepath)

    return str(_obs_dict)


@app.post("/observations/register_observation", response_model=str)
async def register_observation(current_user: Annotated[User, Depends(get_current_active_user)],
                               body=Depends(get_body)
                               ):
    print("********************************************************************************************")
    print("body:  ", str(body)[:1000])
    print("body type:", type(body))
    body_dict = vars(body)
    print("body dict:", str(body_dict)[:1000])
    print("body getlist", body.getlist('items'))
    print("********************************************************************************************")
    submitted_user: str = body_dict["_dict"]["submitted_user"]
    # avalanche_indicator_list: str = body_dict["_dict"]["avalanche_indicator_list"]
    avalanche_triggered: bool = body_dict["_dict"]["avalanche_triggered"]
    avalanche_observed: bool = body_dict["_dict"]["avalanche_observed"]
    avalanche_experienced: bool = body_dict["_dict"]["avalanche_experienced"]
    cracking: bool = body_dict["_dict"]["cracking"]
    collapsing: bool = body_dict["_dict"]["collapsing"]
    elevation_type: str = body_dict["_dict"]["elevation_type"]
    datetime_taken_UTC: datetime = (body_dict["_dict"]["datetime_taken_UTC"])
    observation_notes = body_dict["_dict"]["observation_notes"]
    lat = body_dict["_dict"]["lat"]
    lng = body_dict["_dict"]["lng"]
    general_location = body_dict["_dict"]["general_location"]
    upload_file = body_dict["_dict"]["file"]
    imagefile_url = body_dict["_dict"]["imagefile_url"]
    print("----------------------------------------------------------------------------")
    print("----------------------------------------------------------------------------")
    print("body_dict=", body_dict["_dict"])
    print("----------------------------------------------------------------------------")
    print("----------------------------------------------------------------------------")
    print("submitted data ", submitted_user)
    print("-------------------------------")
    print("Elevation ", elevation_type)
    print("-------------------------------")

    if isinstance(body, FormData):  # if Form/File data received
        msg = body.get('msg')
        items = body.getlist('items')
        files = body.getlist('files')  # returns a list of UploadFile objects
        if files:
            for file in files:
                print(f'Filename: {file.filename}. Content (first 15 bytes): {await file.read(15)}')
            upload_file = files[0]
    ####print("Items:   ", str(items)[:400])
    ### return "OK"
    ###print("body.:", str(vars(body))[:400])
    ###upload_file = body["file"]

    print('obs notes:', observation_notes)

    # get Unique ID
    imgId = uuid7str()
    # get upload file extension
    print("Upload File:", str(upload_file)[:400])
    if not hasattr(upload_file, 'name'):
        file_extension = ".jpg"
        # upload_file = upload_file.
    else:
        file_extension = os.path.splitext(upload_file.name)[1]
    ##file_extension = os.path.splitext(upload_file.filename)[1]
    # build file name
    new_file_name = imgId + file_extension
    # build temp file name
    temp_imagefilepath = os.path.dirname(os.path.realpath(__file__)) + "/temp/temp_" + new_file_name
    print("temp_imagefilepath", temp_imagefilepath)

    # write temp file to folder
    async with aiofiles.open(temp_imagefilepath, 'wb') as out_file:
        while content := await upload_file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk

    try:
        suffix = Path(upload_file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        upload_file.file.close()
    # now save it on AWS S3
    uploadfile_s3(temp_imagefilepath, AWS_S3_BUCKET_NAME, "avaguardapp/uploaded-images", new_file_name)

    print(f"was going to remove {temp_imagefilepath}")

    key_name = "avaguardapp/uploaded-images/" + new_file_name
    bucket_location = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                                   aws_secret_access_key=AWS_SECRET_KEY,
                                   region_name=AWS_REGION_NAME).get_bucket_location(Bucket=AWS_S3_BUCKET_NAME)
    object_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
        bucket_location['LocationConstraint'],
        AWS_S3_BUCKET_NAME,
        key_name)

    # Now save the record in MOngoDB
    _obs = Observation()
    _obs.observation_id = imgId

    _obs.imagefile_url = object_url
    _obs.observation_notes = observation_notes
    _obs.datetime_taken_UTC = datetime_taken_UTC
    _obs.timestamp_saved = str(datetime.now())
    _obs.lat = lat
    _obs.lng = lng
    _obs.general_location = general_location
    if avalanche_triggered == 'true':
        _obs.avalanche_triggered = True
    else:
        _obs.avalanche_triggered = False
    if avalanche_observed == 'true':
        _obs.avalanche_observed = True
    else:
        _obs.avalanche_observed = False
    if avalanche_experienced == 'true':
        _obs.avalanche_experienced = True
    else:
        _obs.avalanche_experienced = False

    if _obs.avalanche_experienced or _obs.avalanche_observed or _obs.avalanche_triggered:
        _obs.avalanche_flag = True
    else:
        _obs.avalanche_flag = False
    _obs.cracking = cracking
    _obs.collapsing = collapsing
    _obs.elevation_type = elevation_type

    _obs.submitted_user = submitted_user
    _obs.marked_for_deletion = ""
    _obs.terrain_prediction_score = ""
    _obs.avalanche_prediction_score = ""
    _obs.avalanche_category_prediction = ""
    _obs.segmented_image_url = ""
    print("*****************************************************************************************")
    prob1, pred_model1 = sagemaker_endpoint(temp_imagefilepath, 1)
    _obs.terrain_prediction_score = pred_model1
    print(_obs.terrain_prediction_score)
    # print(json.loads(_obs.terrain_prediction_score))
    if prob1 > 55:

        prob2, pred_model2 = sagemaker_endpoint(temp_imagefilepath, 2)
        _obs.avalanche_prediction_score = pred_model2

        prob4, pred_model4 = sagemaker_endpoint(temp_imagefilepath, 4)
        if prob2 > 50:
            _obs.avalanche_category_prediction = pred_model4
        else:
            _obs.avalanche_category_prediction += '**Unsure**'
    else:
        _obs.terrain_prediction_score += '*To be deleted*'

    _obs_str = str(vars(_obs))
    _obs_str = _obs_str.replace("False", "'false'").replace("True", "'true'").replace("null", "None")
    print("_obs_str", _obs_str)
    _obs_dict = _obs.asdict()
    print("_obs_dict:", _obs_dict)
    print("******************")

    obs_json = _obs_dict  # json.dumps(_obs_dict, indent=4)

    obsh = obshelper.ObservationHelper(mongodb)
    insert_result = obsh.create_observation(obs_json)

    print("returned inser_result:", insert_result)
    print("ret _obs_dict", _obs_dict)

    # clean up
    os.remove(temp_imagefilepath)
    return str(_obs_dict)


# ----------------------------------------------------------------------------------------------------------------------
# Raises 422 if bad parameter automatically by FastAPI
@app.get("/curworkdir")
async def getcurworkdir(current_user: Annotated[User, Depends(get_current_active_user)], ):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return {"message": f"Current Working Directory is {dir_path}"}


##########################################################################################################
##########################################################################################################
# Avalanche Guard Helpers
##########################################################################################################
##########################################################################################################


###########################################################################################################
# Amazon Sagemaker based Endpoint (this is where our Avalanche Guard model will be hosted
###########################################################################################################
def infer_image_from_sagemaker_endpoint_model1(client, endpointname, image_filename):
    label = ""
    prob = None
    image_size = (224, 224)
    print(f"img file={image_filename}")

    if os.path.isfile(image_filename):
        # Load the image
        img = Image.open(image_filename)
        # Resize the image while maintaining the aspect ratio
        img.thumbnail(image_size)
        # Convert the image to a byte array
        img_byte_array = np.expand_dims(img, 0)  # Create batch axis
        body = json.dumps(img_byte_array.tolist())
        content_type = 'application/json'
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(f"endpoint = {endpointname}, contenttype = {content_type}, body = {str(body)[:100]}")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        ioc_response = client.invoke_endpoint(
            EndpointName=endpointname,
            Body=body,
            ContentType=content_type,
        )
        print(f"Model={endpointname}, {ioc_response}")
        response = json.loads(ioc_response['Body'].read())
        prediction_score_raw = list(response["predictions"])[0][0]
        ### !!!! prediction_score = 1 / (1 + np.exp(-prediction_score_raw)) # wrong!! no need to softmax!!!
        prediction_score = round(prediction_score_raw, 2)

        if prediction_score >= 0.6:
            label = 'Yes'
            prob = prediction_score * 100
        elif prediction_score < 0.45:
            label = 'No'
            prob = prediction_score * 100
        else:
            label = 'Unsure'
            prob = prediction_score * 100
        prob = round(prob, 1)
    return label, prob


def infer_image_from_sagemaker_endpoint_model2(client, endpointname, image_filename):
    label = ""
    prob = None
    image_size = (224, 224)
    print(f"img file={image_filename}")

    if os.path.isfile(image_filename):
        # Load the image
        img = Image.open(image_filename)
        # Resize the image while maintaining the aspect ratio
        # img.thumbnail(image_size)
        img = img.resize(image_size)
        # Convert the image to a byte array
        img_byte_array = np.expand_dims(img, 0)  # Create batch axis
        body = json.dumps(img_byte_array.tolist())
        content_type = 'application/json'
        ioc_response = client.invoke_endpoint(
            EndpointName=endpointname,
            Body=body,
            ContentType=content_type,
        )
        print("image=", img_byte_array[:10])
        print(f"Model={endpointname}, {ioc_response}")
        response = json.loads(ioc_response['Body'].read())
        prediction_score_raw = list(response["predictions"])[0][0]
        ## !! prediction_score = 1 / (1 + np.exp(-prediction_score_raw)) ## Wrong no need to softmax !!!
        prediction_score = round(prediction_score_raw, 2)

        if prediction_score >= 0.55:
            label = 'Yes'
            prob = prediction_score * 100
        elif prediction_score < 0.45:
            label = 'No'
            prob = prediction_score * 100
        else:
            label = 'Unsure'
            prob = prediction_score * 100
        prob = round(prob, 1)
    return label, prob


def infer_image_from_sagemaker_endpoint_model4(client, endpointname, image_filename):
    label = ""
    prob = None
    others = ""
    image_size = (224, 224)
    print(f"img file={image_filename}")

    if os.path.isfile(image_filename):
        # Load the image
        img = Image.open(image_filename)
        # Resize the image while maintaining the aspect ratio
        # img.thumbnail(image_size)
        img = img.resize(image_size)
        # Convert the image to a byte array
        img_byte_array = np.expand_dims(img, 0)  # Create batch axis
        body = json.dumps(img_byte_array.tolist())
        content_type = 'application/json'
        ioc_response = client.invoke_endpoint(
            EndpointName=endpointname,
            Body=body,
            ContentType=content_type,
        )
        print(f"Model={endpointname}, {ioc_response}")
        response = json.loads(ioc_response['Body'].read())
        prediction_score_raw = list(response["predictions"])[0]
        glide = round(prediction_score_raw[0] * 100, 1)
        loose = round(prediction_score_raw[1] * 100, 1)
        slab = round(prediction_score_raw[2] * 100, 1)

        ind = 0
        max_element = prediction_score_raw[0]
        for i in range(1, len(prediction_score_raw)):  # iterate over array
            if prediction_score_raw[i] > max_element:  # to check max value
                max_element = prediction_score_raw[i]
                ind = i

        if ind == 0:
            avlType = 'Glide'
        elif ind == 1:
            avlType = 'Loose'
        elif ind == 2:
            avlType = 'Slab'
        label = avlType
        prob = round(100 * prediction_score_raw[ind], 1)

        others = f"All Values [Glide Loose Slab]={prediction_score_raw}"
        print(
            f"Avalanche Type={avlType}, {100 * prediction_score_raw[ind]:.2f}%, All Values [Glide Loose Slab]={prediction_score_raw}%")

    return label, prob, others


def sagemaker_endpoint(image_filename, model_number: int):
    label = ""
    prob = 0
    others = ""
    print("model number = ", model_number)
    if model_number == 1:
        ENDPOINT_NAME = 'tensorflow-inference-2024-08-05-06-14-21-104'
        label, prob = infer_image_from_sagemaker_endpoint_model1(aws_sagemaker_client, ENDPOINT_NAME, image_filename)
        output = f"Predicted: {label} (Prob = {prob})"
    if model_number == 2:
        ENDPOINT_NAME = 'tensorflow-inference-2024-08-05-06-24-06-679'
        label, prob = infer_image_from_sagemaker_endpoint_model2(aws_sagemaker_client, ENDPOINT_NAME, image_filename)
    if model_number == 4:
        ENDPOINT_NAME = 'tensorflow-inference-2024-08-05-06-30-40-683'
        label, prob, others = infer_image_from_sagemaker_endpoint_model4(aws_sagemaker_client, ENDPOINT_NAME,
                                                                         image_filename)

    print(f"label={label}, prob={prob}, others= {others}")
    if model_number == 1:
        output = label  # '{"Snowy Terain?": ' + f'"{label}"' + ',"Prob" = ' + f"{prob}" + ' }'
    elif model_number == 2:
        output = label  # '{"Avalanche?": ' + f'"{label}"' + ',"Prob" = ' + f"{prob}" + ' }'
    elif model_number == 4:
        output = f'{label} ({prob}%)'
    else:
        return f"Invalid Model"

    return prob, output


##########################################################################################################
##########################################################################################################
# AWS s3 helper
##########################################################################################################
##########################################################################################################
def uploadfile_s3(localfilepath, bucket_name, folder_name, file_name):
    bucket = aws_s3.Bucket(bucket_name)
    try:
        response = bucket.upload_file(localfilepath, f"{folder_name}/{file_name}")
    except ClientError as e:
        logging.error(e)
        return False

    return True


##########################################################################################################
##########################################################################################################
# Summary
##########################################################################################################
##########################################################################################################
def create_img():
    plt.rcParams['figure.figsize'] = [7.50, 3.50]
    plt.rcParams['figure.autolayout'] = True
    plt.plot([1, 2])
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    plt.close()
    return img_buf

    def create_table_from_pd(df, chartnum: int, mainArea: str):
        return img_buf


def create_table_from_pd(df, chartnum: int, mainArea: str):
    if chartnum == 1:

        img_buf = io.BytesIO()
        # Define the width for wrapping text
        cell_width = 30
        cell_height = 0.05

        fig, ax = plt.subplots()
        fig.set_size_inches(9, 7)
        ax.axis('tight')
        ax.axis('off')

        # Wrap text in DataFrame
        wrapped_data = [[('\n'.join(wrap(str(cell), width=cell_width))) for cell in row] for row in df.values]

        table = ax.table(cellText=wrapped_data, colLabels=df.columns, cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(6)
        # Set cell height
        for key, cell in table.get_celld().items():
            cell.set_height(cell_height)

        plt.savefig(img_buf, format='png')
        plt.close()
        return img_buf
    elif chartnum == 2:
        img_buf = io.BytesIO()
        plot = sns.catplot(data=df, x="Area", y="Count", hue="Category", kind="bar")
        plot.set_xticklabels(rotation=90)
        plot.set_xticklabels(fontsize=8)
        plot.savefig(img_buf, format='png')
        return img_buf
    elif chartnum == 3:
        import geopandas as gpd
        from shapely.geometry import Point
        import contextily as ctx

        img_buf = io.BytesIO()

        areadict = cmnhelper.mainAreaToLangLatMapList()
        subAreaDict = cmnhelper.areaToLangLatMapList()
        mainArea = str(df["Area"].iloc[0]).split("/")[0]
        print(f"Mainarea = {mainArea}")

        points = [{'lat': areadict[mainArea][0][0], 'lon': areadict[mainArea][0][1], 'name': ''},
                  {'lat': areadict[mainArea][1][0], 'lon': areadict[mainArea][1][1], 'name': ''},
                  ]

        df = df.reset_index()  # make sure indexes pair with number of rows
        for index, row in df.iterrows():
            print(row['MainArea'], row['Area'], row['general_lat'], row['general_lng'], row['Count'])
            points.append({'lat': subAreaDict[row['Area']][0], 'lon': subAreaDict[row['Area']][1],
                           'name': str(row['Area']).split("/")[1] + "=" + str(row['Count'])})

        # Create a GeoDataFrame from the points
        gdf_points = gpd.GeoDataFrame(
            points,
            geometry=[Point(p['lon'], p['lat']) for p in points],
            crs="EPSG:4326"
        )

        # Convert the GeoDataFrame to Web Mercator (EPSG:3857) for compatibility with contextily
        gdf_points = gdf_points.to_crs(epsg=3857)

        # Create a plot
        fig, ax = plt.subplots(figsize=(12, 9))

        # Plot the points
        gdf_points.plot(ax=ax, color='black', markersize=50)

        # Add the labels for each point
        for x, y, label in zip(gdf_points.geometry.x, gdf_points.geometry.y, gdf_points['name']):
            plt.text(x, y, label, fontsize=15, ha='right', color='blue')

        # Add a basemap using contextily
        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom=7)

        # Set plot limits to focus on the area of interest
        ax.set_xlim(gdf_points.total_bounds[[0, 2]])
        ax.set_ylim(gdf_points.total_bounds[[1, 3]])

        # Show the plot
        plt.title(
            f"Recent Counts of Avalanches in {mainArea} - Markers denote a general area only (not the exact position)")
        plt.savefig(img_buf, format='png')
        plt.close()
        return img_buf

    elif chartnum == 31:
        import matplotlib.image as mpimg
        img_buf = io.BytesIO()

        '''
        # Sample data in a pandas DataFrame
        data = {
            'longitude': [-74.0060, -118.2437, -87.6298],  # Example longitudes
            'latitude': [40.7128, 34.0522, 41.8781]  # Example latitudes
        }
        df = pd.DataFrame(data)
        '''

        # Create a new figure
        # fig = plt.figure(figsize=(12, 12))  # Adjust figure size for higher resolution
        # Load the background image
        image = mpimg.imread('~/MIDS_DATASCI_210/AvaGuardServer/src/Alps.PNG')  # Replace with your image path

        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(1072 / 10, 712 / 10))

        ((llclat, llclng), (urclat, urclng)) = ((24, -125), (50, -66))
        ((llclat, llclng), (urclat, urclng)) = cmnhelper.mainAreaToLangLatMapList()[mainArea]
        # Display the image in the background

        if mainArea != "Unknown":
            m = Basemap(projection='merc',  # Mercator projection
                        llcrnrlat=llclat, urcrnrlat=urclat,  # Latitude limits for the continental USA
                        llcrnrlon=llclng, urcrnrlon=urclng,  # Longitude limits for the continental USA
                        resolution='l')  # High resolution
            # 38°00'00.0"N+119°00'00.0"W/@39.1380029,-120.2826346,8.42z/data=!4m4!3m3!8m2!3d38!4d-119?entry=ttu
        else:
            # Create a Basemap instance for the USA with high resolution
            m = Basemap(projection='merc',  # Mercator projection
                        llcrnrlat=24, urcrnrlat=50,  # Latitude limits for the continental USA
                        llcrnrlon=-125, urcrnrlon=-66,  # Longitude limits for the continental USA
                        resolution='l')  # low resolution

        # Get the extent of the map in map projection coordinates
        map_extent = [m.xmin, m.xmax, m.ymin, m.ymax]
        ax.imshow(image, extent=map_extent, origin='upper', zorder=0, alpha=0.5)

        # Draw map features with high resolution
        m.drawcoastlines()
        m.drawcountries()
        m.drawstates()
        # m.bluemarble()
        # m.drawparallels(range(24, 51, 6), labels=[1, 0, 0, 0])  # Draw latitude lines
        # m.drawmeridians(range(-120, -60, 10), labels=[0, 0, 0, 1])  # Draw longitude lines

        # Extract latitude and longitude from DataFrame
        lons = df['general_lng'].values
        lats = df['general_lat'].values

        # Convert latitude and longitude to map projection coordinates
        x, y = m(lons, lats)

        # Plot points on the map
        m.scatter(x, y, color='red', marker='x', s=70, label='Avalanche Observations', alpha=.9, zorder=5)

        # Annotate counts on the map
        # for (lat, lon), count in location_counts.items():
        #    x, y = m(lons, lats)
        #    plt.text(x, y, str(count), fontsize=12, ha='center', va='center', color='red', zorder=5)

        # Add a legend
        plt.legend()
        # Add a title
        plt.title(f'Recent Avalanche Observations {m.llcrnrlat},{m.llcrnrlon},{m.urcrnrlat},{m.urcrnrlon}')

        # Show the plot
        plt.savefig(img_buf, format='png')
        plt.close()

        return img_buf
    elif chartnum == 5:
        img_buf = io.BytesIO()

        import geopandas as gpd
        from shapely.geometry import Point
        import contextily as ctx

        # Create a DataFrame with point data
        data = {
            'name': ['Downtown Manhattan', 'East Village', 'Times Square'],
            'lat': [40.7128, 40.730610, 40.758896],
            'lon': [-74.0060, -73.935242, -73.985130]
        }
        df = pd.DataFrame(data)

        # Create a GeoDataFrame from the DataFrame
        gdf_points = gpd.GeoDataFrame(
            df,
            geometry=[Point(xy) for xy in zip(df['lon'], df['lat'])],
            crs="EPSG:4326"
        )

        # Convert the GeoDataFrame to Web Mercator (EPSG:3857) for compatibility with contextily
        gdf_points = gdf_points.to_crs(epsg=3857)

        # Create a plot
        fig, ax = plt.subplots(figsize=(12, 9))

        # Plot the points
        gdf_points.plot(ax=ax, color='blue', markersize=50)

        # Add the labels for each point
        for x, y, label in zip(gdf_points.geometry.x, gdf_points.geometry.y, gdf_points['name']):
            plt.text(x, y, label, fontsize=12, ha='right', color='blue')

        # Add a basemap using contextily
        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

        # Set plot limits to focus on the area of interest
        ax.set_xlim(gdf_points.total_bounds[[0, 2]])
        ax.set_ylim(gdf_points.total_bounds[[1, 3]])

        # Show the plot

        # Save the plot to an image buffer
        buffer = io.BytesIO()
        plt.title("Detailed Map of New York City with Points")
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close(fig)
        buffer.seek(0)
        # Show the plot
        plt.savefig(img_buf, format='png')
        plt.close()
        return buffer.seek(0)
    elif chartnum == -1:
        img_buf = io.BytesIO()
        # Create a figure and an axis
        fig, ax = plt.subplots()
        # Hide the axis
        ax.axis('off')
        # Set the text
        text = "** No Data Found **"
        plt.text(0.5, 0.5, text, fontsize=24, ha='center', va='center')

        # Display the chart
        plt.savefig(img_buf, format='png')
        plt.close()
        return img_buf

    else:
        img_buf = io.BytesIO()
        # Create a figure and an axis
        fig, ax = plt.subplots()
        # Hide the axis
        ax.axis('off')
        # Set the text
        text = "Not Implemented"
        plt.text(0.5, 0.5, text, fontsize=20, ha='center', va='center')

        # Display the chart
        plt.savefig(img_buf, format='png')
        plt.close()
        return img_buf


@app.get('/summary')
async def get_img(background_tasks: BackgroundTasks,
                  current_user: Annotated[User, Depends(get_current_active_user)], ):
    img_buf = create_img()
    # get the entire buffer content
    # because of the async, this will await the loading of all content
    bufContents: bytes = img_buf.getvalue()
    background_tasks.add_task(img_buf.close)
    headers = {'Content-Disposition': 'inline; filename="out.png"'}
    return Response(bufContents, headers=headers, media_type='image/png')


@app.get('/summary1')
async def summary1(daysold: int, mainArea: str, chartnum: int,
                   background_tasks: BackgroundTasks,
                   current_user: Annotated[User, Depends(get_current_active_user)], ):
    # Get all observations
    print(f"**************** {daysold} ************** {mainArea} *******************")
    obsh = obshelper.ObservationHelper(mongodb)
    if current_user.admin_user_flag:
        rslt, obss_list = obsh.get_all_observations("ALL_USERS")
    else:
        rslt, obss_list = obsh.get_all_observations(current_user.username)
    df = pd.DataFrame.from_dict(obss_list)
    df["datetime_taken_UTC"] = pd.to_datetime(df["datetime_taken_UTC"], format='mixed')
    df["lat"] = pd.to_numeric(df["lat"], errors='coerce')
    df["lng"] = pd.to_numeric(df["lng"], errors='coerce')

    # map the general area to lat long
    print("map is :", cmnhelper.areaToLangLatMapList())
    df["general_lat"] = df.apply(lambda x: cmnhelper.areaToLangLatMapList()[x["general_location"]][0], axis=1)
    df["general_lng"] = df.apply(lambda x: cmnhelper.areaToLangLatMapList()[x["general_location"]][1], axis=1)

    df["avalanche_category_prediction"] = df["avalanche_category_prediction"].astype(str)
    # remove the % from categorization
    df['avalanche_category_prediction'] = df['avalanche_category_prediction'].str.split(' ').str[0]

    df["main_area"] = df.apply(lambda x: str(x["general_location"]).split('/')[0].strip(), axis=1)

    df = df.rename(columns={'main_area': 'MainArea',
                            'general_location': 'Area',
                            'avalanche_prediction_score': 'Avalanche',
                            'avalanche_category_prediction': 'Category',
                            'lat': 'latitude',
                            'lng': 'longitude'
                            })

    print(df[['MainArea', 'Area', 'Avalanche',
              'Category', 'latitude', 'longitude', 'general_lat', 'general_lng', 'datetime_taken_UTC']
          ])

    # print("df before filter and grouping:", df)
    print("df before filter and grouping count:", df.shape[0])

    # Filter for daysold
    startDatetime = datetime.now() - timedelta(days=daysold)
    df = df.loc[df['datetime_taken_UTC'] > startDatetime]
    df = df.loc[df['MainArea'] == mainArea]
    df = df.query('Avalanche == "Yes"')
    print("df after filter and before grouping count:", df.shape[0])
    print(f"filter are calcStartDate = {startDatetime}, mainAreea= {mainArea}, daysold={daysold} Ava=Yes")

    if chartnum in [1, 2]:
        smrydf = df.groupby(['Area', 'Avalanche',
                             'Category']).size().to_frame(name='Count').reset_index()
    elif chartnum in [3]:
        smrydf = df.groupby(['MainArea', 'Area', 'general_lat', 'general_lng']).size().to_frame(
            name='Count').reset_index()

    elif chartnum in [31, 5]:
        smrydf = df.groupby(['general_lat', 'general_lng', 'Category']).size().to_frame(name='Count').reset_index()
    else:
        smrydf = df.groupby(['Area', 'Avalanche',
                             'Category']).size().to_frame(name='Count').reset_index()

    # If no records then print no records else run the chart
    print("summary df is ", smrydf.shape[0])
    if smrydf.shape[0] == 0:
        img_buf = create_table_from_pd(smrydf, -1, mainArea)
    else:
        img_buf = create_table_from_pd(smrydf, chartnum, mainArea)
    # time.sleep(10)
    # get the entire buffer content
    # because of the async, this will await the loading of all content
    bufContents: bytes = img_buf.getvalue()
    background_tasks.add_task(img_buf.close)
    headers = {'Content-Disposition': 'inline; filename="out.png"'}
    return Response(bufContents, headers=headers, media_type='image/png')


#########################################################################################
#
#########################################################################################
def download(url: str, dest_folder: str, dest_file: str):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    if dest_file == "":
        filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    else:
        filename = dest_file
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))

    return file_path
