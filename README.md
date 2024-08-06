---
class: DATASCI210, Summer-24-Section 01
author: Amiya Ranjan , Mandy Korphi, Ana Zapata 
---
UC Berkeley
===========
Masters in Information and Data Science (MIDS)
===========
DATASCI210 - Capstone
===========

===========


# UCB-MIDS-AvalancheGuard
UC Berkeley MIDS Program Capstone project - AvalancheGuard

## AvalancheGuard

Avalanche forecasts save lives. They enable those who travel, live, work, or recreate in the backcountry to make informed decisions in snowy mountain environments.

Forecasters rely on weather reports, snowpit data, and avalanche event observations to assess daily avalanche risk. However, forecasters and avalanche center directors agree that more reports on when, where, and what types of avalanches people see are essential. Increased reporting would lead to more accurate, localized avalanche forecasts, enhancing public safety and decision-making for backcountry travelers.

Backcountry travelers say that they currently don’t contribute pictures to existing observation platforms because they are unsure how to caption them. They also don’t realize that their contributions could help keep everyone safe.

To address this need, we’ve developed AvalancheGuard, an app that allows recreational skiers, riders, snowmobilers, and anyone traveling through snowy mountains to easily upload pictures of any avalanche activity they see. Our app automatically captions pictures with the avalanche type, simplifying the observation submission process for backcountry travelers. These crowd-sourced observations are summarized on our platform, providing valuable data for forecasters to analyze when developing their avalanche risk forecasts.

## How to deploy and run this application

The overall AvalancheGuard application consists of multiple components. Please follow this
guide to deploy each component.


* First clone this repository to your local machine

### Deploying and running the API server on your local environment
* You must configure the following in the AvaGuardServer's security configuraiton at
```console
/AvaGuardServer/src/AvaGuardHelpers/security-configuration.py
```


```python
AWS_ACCESS_KEY = 'YOUR AWS ACCESS KEY'
AWS_SECRET_KEY = 'YOUR AWS SECRET KEY'
AWS_SESSION_TOKEN = ""
AWS_REGION_NAME = "YOUR AWS REGION"
AWS_S3_BUCKET_NAME = "YOU AWS S3 BUCKET FOR UPLOADING IMAGES"

origins = [
    "YOU LIST OF URLS THAT SHOULD ALLOW TO ACCESS THE API SERVER"

]


PASSWORD_ENCRYPTION_SECRET_KEY = "A PASSWORD ENCRYPION KEY FOR OAUTH2"

```
* Install the necessary packages 
```console
cd UCB-MIDS-AvalancheGuard/AvaGuardServer
poetry install
```
* Then start the API server
```console
poetry run uvicorn src.main:app
```

### Deploying and running the Angular Web App on your local environment
* Serve the angular app 
```console
cd UCB-MIDS-AvalancheGuard/AvaGuardApp
ng serve --open --configuration=development
```

### Deploying the models to AWS Sagemaker

Our CV models are trained on AWS Sagemaker environment. They are available in directory:  
```console
/Jupyter-Notebooks/models
```


You can make use of the model deployment notebooks available in directory

```console
/Jupyter-Notebooks/deploy-models
```

to deploy the models to Sagemaker endpoints.

* List of models:
* *  Model 1 (Snowy terrain or Not) : snowTerrain_orNOT_best_model_wlandscape
* *  Model 2 (Avalanche or Not) : avi_noAvi_best_model_3
* *  Model 3 (Segmentation) : This model has not been developed yet.
* *  Model 4 (Avalanche Classification) : EfficientNetV2S_best_model_2

### Configuring S3 Bucket for image storage

You will need to configure an S3 bucket for storing image. 

Please change the values in security configuration file of 
```console
/AvaGuardServer/src/AvaGuardHelpers/security-configuration.py
```










