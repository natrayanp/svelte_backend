from fastapi import APIRouter, Depends, Request, HTTPException, status, Header
from ..apivalidator.apivalidators import TokenUserDetail, get_current_active_user, get_user_with_email
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional
import hashlib


from ..mydb import dbfunc  as db
from ..common import commonfunc as cf
router = APIRouter()

@router.post("/logintoken")
async def thirparty_singup(
    #form_data: UserAuthData,     
    current_user: TokenUserDetail = Depends(get_current_active_user),
    myhd: cf.MyHeaderData = Depends(cf.get_header_data) 
    ):
    #current_user: TokenUserDetail = cur_cur(oprtype = 'singup'),
    print("inside token login")
    print(current_user)
 
    
    ed = ''
    try:
        if current_user.reg_status:
            print(current_user)            
            print(myhd)
            data = {"userid":current_user.id, 
                    **myhd}
            try:
                userdb = await db.qry_excute(db.queries.invalidate_session,data)
                print(userdb)
            except Exception as e:
                print(e)
                ed = "Failed due to Technical issue"    
                raise
            
            try:
                print("user ")
                new_sessid = await cf.create_user_session(data["userid"],myhd)
            except Exception as e:
                print(e)
                ed = str(e)
                #ec = "Session creation.  Failed due to Technical issue"
                raise
        else:
            ed = "Not a registered users"
            raise Exception("Not a registered users")   

    except Exception:
        print('catching the error')
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail= {'error':True,'message': current_user.email + ' : ' + str(ed)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    tt =  'Auth successful'
    return {'detail':{'error':False,'message': tt,'sessionid':new_sessid}}