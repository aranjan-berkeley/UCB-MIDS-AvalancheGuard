from pydantic import BaseModel, Extra
from typing import Optional
from datetime import datetime


# --------------------------------------------------
# User Login and Registration Related Models
# --------------------------------------------------


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str
    password: str
    hashed_password: Optional[str] = ""
    active: bool = True
    firstName: str
    lastName: str
    timestamp_lastlogged: Optional[datetime] = None
    admin_user_flag: bool = False


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User


class TokenAndUser(BaseModel):
    token: Token
    user: User


class UserInDB(User):
    hashed_password: str


# --------------------------------------------------
# Observation Related Models
# --------------------------------------------------
# define observation
class Observation(BaseModel, extra=Extra.forbid):
    observation_id: Optional[str] = None
    datetime_taken_UTC: Optional[datetime] = None
    timestamp_saved: Optional[datetime] = None
    imagefile_url: Optional[str] = None
    observation_notes: Optional[str] = None
    avalanche_triggered: Optional[bool] = None
    avalanche_observed: Optional[bool] = None
    avalanche_experienced: Optional[bool] = None
    avalanche_flag: Optional[bool] = None
    cracking: Optional[bool] = None
    collapsing: Optional[bool] = None
    elevation_type: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    general_location: Optional[str] = None
    submitted_user: Optional[str] = None
    marked_for_deletion: Optional[bool] = None
    terrain_prediction_score: Optional[float] = None
    avalanche_prediction_score: Optional[float] = None
    avalanche_category_prediction: Optional[str] = None
    segmented_image_url: Optional[str] = None

    def asdict(self):
        return {"observation_id": self.observation_id,
                "datetime_taken_UTC": self.datetime_taken_UTC,
                "timestamp_saved": self.timestamp_saved,
                "imagefile_url": self.imagefile_url,
                "observation_notes": self.observation_notes,
                "avalanche_triggered": self.avalanche_triggered,
                "avalanche_observed": self.avalanche_observed,
                "avalanche_experienced": self.avalanche_experienced,
                "avalanche_flag": self.avalanche_flag,
                "cracking": self.cracking,
                "collapsing": self.collapsing,
                "elevation_type": self.elevation_type,
                "lat": self.lat,
                "lng": self.lng,
                "general_location": self.general_location,
                "submitted_user": self.submitted_user,
                "marked_for_deletion": self.marked_for_deletion,
                "terrain_prediction_score": self.terrain_prediction_score,
                "avalanche_prediction_score": self.avalanche_prediction_score,
                "avalanche_category_prediction": self.avalanche_category_prediction,
                "segmented_image_url": self.segmented_image_url
                }


class PredictionOfImage(BaseModel):
    terrian: bool
    classification: str


# Use pydantic.Extra.forbid to only except exact field set from client.
# This was not required by the lab.
# Your test should handle the equivalent whenever extra fields are sent.
class House(BaseModel, extra=Extra.forbid):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float


class ListHouses(BaseModel, extra=Extra.forbid):
    houses: list[House]


class UserPassword(BaseModel):
    username: str
    password: str
