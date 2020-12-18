from fastapi import Header
from pydantic import BaseModel
import hashlib
from datetime import datetime, timedelta

from ..mydb import dbfunc  as db


class MyHeaderData (BaseModel):
    siteid: str


def get_header_data(siteid: str = Header(None)) -> MyHeaderData:
    print(siteid)
    
    myhd = {'siteid': siteid}
    return myhd


def session_hash(password):
    salt = 'sesstkn'
    print(password)
    print(salt)
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest()


async def create_user_session(userid: str, myhd: MyHeaderData) -> str:
    sh = session_hash( userid + datetime.now().strftime("%Y%m%d%H%M%S%f"))
    data = {"userid":userid, "ipaddress":None, "sessionid":sh, **myhd}
    try:
        shdb = await db.qry_excute(db.queries.create_session,data)
        if shdb != None:
            raise Exception("Create session: DB failure")
    except Exception as e:
        print(e)
        raise Exception("Create session: DB failure")

    return sh