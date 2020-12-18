from fastapi import Depends, FastAPI, Header, HTTPException


from assetscube.apis.v1.authentication import logout, login, signup

apiv1 = FastAPI()



#app.include_router(auths.router,prefix="/v1",)
apiv1.include_router(signup.router)
apiv1.include_router(login.router)
apiv1.include_router(
    logout.router,
    prefix="/items",
    tags=["items"]
)