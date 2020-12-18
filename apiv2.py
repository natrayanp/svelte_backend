from fastapi import Depends, FastAPI, Header, HTTPException

from assetscube.apis.v2.authentication import logout, login

apiv2 = FastAPI()

#app.include_router(auths.router,prefix="/v1",)
apiv2.include_router(login.router)
apiv2.include_router(
    logout.router,
    prefix="/items",
    tags=["items"]
)