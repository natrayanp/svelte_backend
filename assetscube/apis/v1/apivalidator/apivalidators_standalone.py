from datetime import datetime
import firebase_admin
from firebase_admin import credentials, auth
from ..common import serviceAccountKey as sa
from ..mydb import dbfunc as db

from fastapi import Depends, FastAPI, HTTPException, Security, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
#from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from typing import List, Optional
from datetime import datetime, timedelta



cred = credentials.Certificate(sa.SERVICEAC)
default_app = firebase_admin.initialize_app(cred) 

class TokenUserDetail(BaseModel):
    userid: Optional[str] = None
    

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    print("es")
    
    authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        print(firebase_admin._apps)
        if not firebase_admin._apps:
            cred = credentials.Certificate(sa.SERVICEAC)
            default_app = firebase_admin.initialize_app(cred)        
        decoded_token = auth.verify_id_token(token)
        payload = decoded_token
        print(payload)
        userid: str = payload.get("user_id")
        if userid is None:
            raise credentials_exception
        print(payload)
        token_data = TokenUserDetail(userid=userid)
    except (JWTError, ValidationError):
        raise credentials_exception

    return token_data


async def get_current_active_user(
    current_user: TokenUserDetail = Depends(get_current_user),    
    usertype: str = Header(None),
    ):    
    print(current_user)    
    print(usertype)
    res = db.queries.userstatus(userid=current_user.userid,usertype=usertype)    
    dd = res.fetchall()
    print(dd[0][0])
    if dd[0][0] != 1:
        raise HTTPException(status_code=401, detail="Not a registered User")
    return current_user