from datetime import datetime
import firebase_admin
from firebase_admin import credentials, auth
from ..common import serviceAccountKey as sa
from ..mydb import dbfunc as db
from ..common import commonfunc as cf

from fastapi import Depends, FastAPI, HTTPException, Security, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
#from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from typing import List, Optional
from datetime import datetime, timedelta

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

cred = credentials.Certificate(sa.SERVICEAC)
default_app = firebase_admin.initialize_app(cred) 

class TokenUserDetail(BaseModel):
    id: str
    name: str = None
    email: str   
    reg_status:bool = False
    

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")

'''
async def get_current_user(
    token: str = Depends(oauth2_scheme),    
    myhd: cf.MyHeaderData = Depends(cf.get_header_data),    
    ) -> TokenUserDetail:
    print("es")
    
    authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        if myhd["logintype"] == "T":
            print(firebase_admin._apps)
            if not firebase_admin._apps:
                cred = credentials.Certificate(sa.SERVICEAC)
                default_app = firebase_admin.initialize_app(cred)        
            decoded_token = auth.verify_id_token(token)
            payload = decoded_token
            print(payload)
            #userid: str = payload.get("user_id")    
        elif myhd["logintype"] == "S":
            sktid = jwt.get_unverified_header(token)
            #seckey = db.get_secret(sktid.skd)
            #res = db.queries.secretcodef(sktid=sktid.skd)
            data = {"sktid":sktid.skd}
            seckey = db.qry_excute(db.queries.secretcodef,data)
            print("----res")
            print(seckey)            
            #print(res.fetchall())
            #seckey = res.fetchall()[0][0]

            payload = jwt.decode(token, seckey, algorithms=[ALGORITHM])
            print(payload)
            #username: str = payload.get("sub")
        else:
            raise HTTPException(status_code=401, detail="Looks like an invalid token")    
        
         
        userid: str = payload.get("sub")
        username: str = payload.get("name")
        useremail: str = payload.get("email")
        if userid is None:
            raise credentials_exception
        print(payload)
        token_data = TokenUserDetail(id=userid,email=useremail,name=username)
    except (JWTError, ValidationError):
        raise credentials_exception

    return token_data
'''

async def get_current_active_user(
    token: str = Depends(oauth2_scheme),    
    #current_user: TokenUserDetail = Depends(get_current_user),        
    myhd: cf.MyHeaderData = Depends(cf.get_header_data),    
    ):
    try:
        print("es")
        print(myhd)
        authenticate_value = f"Bearer"
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )
        ss = False if 'logintype' in myhd.keys() else True
        print(ss)
        try:
            if ss:
            #if myhd["logintype"] == "T":
                print(firebase_admin._apps)
                if not firebase_admin._apps:
                    cred = credentials.Certificate(sa.SERVICEAC)
                    default_app = firebase_admin.initialize_app(cred)        
                decoded_token = auth.verify_id_token(token)
                payload = decoded_token
                print(payload)
                print('token done')
                #userid: str = payload.get("user_id")    
            elif myhd["logintype"] == "S":
                sktid = jwt.get_unverified_header(token)
                data = {"sktid":sktid.skd}
                seckey = db.qry_excute(db.queries.secretcodef,data)
                print("----res")
                print(seckey)
                seckey = "wrong"

                payload = jwt.decode(token, seckey, algorithms=[ALGORITHM])
                print(payload)
                #username: str = payload.get("sub")
            else:
                raise HTTPException(status_code=401, detail="Looks like an invalid token")    
            print('token done start')
            userid: str = payload.get("sub")
            username: str = payload.get("name")
            useremail: str = payload.get("email")
            print(userid)
            if userid is None:
                raise credentials_exception
            print(payload)
            print('after token_data befpre')
            try:
                token_data = TokenUserDetail(id=userid,email=useremail,name=username,reg_status=False)
            except Exception as e:
                print(e)
                print('exception during assignment')
                raise
            print('after token_data')
            print(token_data)
        except (JWTError, ValidationError):
            raise credentials_exception
        print('starting db')
        current_user = token_data
        print(current_user)  
        #res = db.queries.userstatus(userid=current_user.userid,usertype=usertype)
        data = {"userid": current_user.id, **myhd} 
        try:
            userdb = await db.qry_excute(db.queries.trdlogin_user_chk,data)
            print(userdb)
            print('starting db done')
        except Exception:
            print('starting db done except')
            raise Exception("User Fetch.  Failed due to Technical issue")

        if len(userdb) == 1:
            user = dict(userdb[0])
            print(user)
            if user["userstatus"] == 'I':
                raise Exception("Inactive user") 
            else:                
                current_user.reg_status = True
        elif(len(userdb)>1):
            raise Exception("multiple users") 
        elif (len(userdb)==0):            
            current_user.reg_status = False
            #raise Exception("Not a registered user") 

    except Exception as e:
        print("insdie this exce")
        print(e)
        raise e
        '''
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
        '''
    print('returning')
    print(current_user)
    return current_user


async def get_user_with_email(email):
    try:
        print(firebase_admin._apps)
        if not firebase_admin._apps:
            cred = credentials.Certificate(sa.SERVICEAC)
            default_app = firebase_admin.initialize_app(cred)        
        userdet = auth.get_user_by_email(email)
        print(userdet)
    except (ValueError,firebase_admin.exceptions.FirebaseError,Exception) as e:
        print(e)
        raise Exception("Technical error happened") 
    except UserNotFoundError:
        raise Exception("User not registered")

    print('---------')
    print(userdet.uid)

    return userdet

