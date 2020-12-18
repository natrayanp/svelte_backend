from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

#from assetscube.apis.v1.authentication import logout, login
from apiv2 import apiv2 as a
from apiv1 import apiv1
#import assetscube.apis.v1.authentication as auths

#app = FastAPI()
app = a

origins = [
    "http://localhost:4200",
    "http://localhost:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#app.include_router(login.router,prefix="/v1",)
'''app.include_router(
    logout.router,
    prefix="/v1/items",
    tags=["items"]
)
'''

app.mount("/v1", apiv1)
#app.mount("/v2", apiv2)