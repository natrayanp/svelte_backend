from fastapi import APIRouter, Depends, Request, HTTPException, status, Header


from ..apivalidator.apivalidators import TokenUserDetail, get_current_active_user, get_user_with_email

from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional



from ..mydb import dbfunc  as db
from ..common import commonfunc as cf
router = APIRouter()

@router.get("/test",status_code=status.HTTP_400_BAD_REQUEST)
async def path(request: Request):
    return {"message": "Hello World", "root_path": request.scope.get("root_path")}
    

@router.get("/userregchk")
async def UserRegChk(
    current_user: TokenUserDetail = Depends(get_current_active_user)    
): 
    print("inside userregchk")
    #return "Good"
    return current_user
    #return [{"item_id": "Foo", "owner": current_user.userid}]



SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str

class UserAuthDBData(BaseModel):
    userid: str
    username: str
    password: str

class UserAuthData(BaseModel):
    userid: str
    password: str

#* User profile information, visible only to the 
# Firebase project's apps.
class UserInfo (BaseModel):
    uid: str
    displayName: str = None
    email: str = None
    photoURL: str = None
    phoneNumber: str = None    
    providerId: str
    emailverified: bool = False 
    token: str = None

class AuthRespModel (BaseModel):
    userdetails: UserInfo
    sessionid: str
    #status: str
    status_code: str
    natjwt: str
    tokenClaims: dict = {}
    #message: str

class supemailResp(BaseModel):
    useremail:str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
  

def get_user_id(userid):
    salt = 'username'
    print(userid)
    print(salt)
    return hashlib.sha256(salt.encode() + userid.encode()).hexdigest()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password):
    return pwd_context.hash(password)

async def authenticate_user( form_data: UserAuthData, myhd: cf.MyHeaderData ):
    data = {"username": form_data.userid,**myhd }    
    try:
        print(data)
        try:
            userdb = await db.qry_excute(db.queries.ownlogin_user_chk,data)
        except Exception:
            raise
        print("----user")    
        print(userdb)
        print(len(userdb))
        if len(userdb) == 1:
            user = dict(userdb[0])
            print(user)
        else: 
            if(len(userdb)>1):
                raise Exception("multiple users") 
            elif (len(userdb)==0):
                raise Exception("Not registered user")  
        print(user)
        print(user["userid"])
        if not user:
            return False
        if not verify_password(form_data.password, user["userpassword"]):
            return False
    except Exception as e:   
        print("ejdjejeje")     
        print(e)
        raise
    
    return user

async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    #seccdid = db.queries.secretcode()
    try:
        skd = await db.qry_excute(db.queries.secretcode)
        print(skd)
        print(len(skd))
    except Exception:
        print("Failed due to Technical issue")
        raise
    if len(skd) == 1:
        skdr = dict(skd[0])
        print(skdr)
    else: 
        raise Exception("multiple users")    
    print(skdr)
    #to_encode.update({"skd": seccdid})
    to_encode.update({"skd": skdr["seccdid"]})    
    to_encode.update({"uid": to_encode["sub"]})    
    encoded_jwt = jwt.encode(to_encode, skdr["secretcode"], algorithm=ALGORITHM)
    return encoded_jwt


async def get_user_active_session(user: str, myhd: cf.MyHeaderData) -> str:
    sess = None
    print(myhd)
    data ={"userid": user,**myhd}
    try:
        sessdb = await db.qry_excute(db.queries.chk_session_exists,data)         
    except Exception as e:
        print (e)
        print("get session fun")
        raise
    print("Got session")
    print(sessdb)
    if sessdb !=None:        
        sess = sessdb["sessionid"]
    return sess





@router.post("/token", response_model=AuthRespModel)
async def login_for_access_token(
    form_data: UserAuthData, 
    myhd: cf.MyHeaderData = Depends(cf.get_header_data)):

    status_code = None
    new_sessid = None
    ec = "Unknow Issue.  Failed due to Technical issue"
    try:
        print("---start")
        try:
            user = await authenticate_user(form_data, myhd)
        except Exception as e:
            print(e)            
            ec = str(e)
            raise

        print("token")
        print(user)
        if not user:
            ec = "Incorrect username or password"
            raise Exception(ec)

        print(user)

        try:
            print("session")
            old_sessid = await get_user_active_session(user["userid"], myhd)
        except Exception as e:
            print(e)
            ec = str(e)
            #ec = "Session Fetch.  Failed due to Technical issue",
            raise

        try:
            print("user ")
            new_sessid = await cf.create_user_session(user["userid"],myhd)
        except Exception as e:
            print(e)
            ec = str(e)
            #ec = "Session creation.  Failed due to Technical issue"
            raise

        if old_sessid:
            status_code = 'sessionexists'

   
        userdetails = {"displayname":"","email":"","phonenumber":"","photourl":"","providerId":"nat","uid":user["userid"]}
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        try:
            access_token = await create_access_token(
                data={"sub": user["userid"],"email":user["useremail"],"name":user["username"]}, expires_delta=access_token_expires
            )
        except Exception as e:
            print(e)
            ec = str(e)
            #ec = "Token creation.  Failed due to Technical issue",
            raise

    except Exception:
        print("Final excel")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= ec,
            #detail="Session creation.  Failed due to Technical issue",
            headers={"WWW-Authenticate": "Bearer"},
        )            

    return {"userdetails":userdetails, "sessionid": new_sessid,"status_code":status_code ,"natjwt": access_token, "tokenClaims": {}}


@router.post("/salone_singup", response_model=AuthRespModel)
async def standalone_singup(
    form_data: UserAuthData, 
    myhd: cf.MyHeaderData = Depends(cf.get_header_data) ):
    print("inside stanaldone")
    print(myhd)
    data = {"username": form_data.userid, **myhd}
    print(data) 
    ed = ''
    usr_chk = await db.qry_excute(db.queries.ownlogin_user_chk,data)
    print(usr_chk)    
    print(len(usr_chk))  
    try:
        if len(usr_chk) == 0:
            #usr_cnt = dict(usr_chk[0])
            #usr_cnt = usr_cnt["count"]                
            #if usr_cnt["username"] == form_data["userid"]:
            hash_pass = await get_password_hash(form_data.password)
            print(hash_pass)      
            print("hash_pass")
            userid = get_user_id(form_data.userid)
            print(userid)
            print("userid")
            data = {"userid":userid, 
                    "username":form_data.userid, 
                    "useremail":form_data.userid, 
                    "userpassword":hash_pass, 
                    "userstatus":'A', 
                    **myhd}
            print(data)
            try:
                dbs = await db.qry_excute(db.queries.create_usr,data)
                print(dbs)
            except Exception:
                ed = "Failed due to Technical issue"    
                raise
        else:
            ed = "Already a registered users"
            raise Exception("Already a registered users")    
        #else: 
            #ed = "Incorrect query resuts"
            #raise Exception("Incorrect query resuts")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=ed,
            headers={"WWW-Authenticate": "Bearer"},
        )

    userdetails = {"displayname":"","email":data["useremail"],"phonenumber":"","photourl":"","providerId":"nat","uid":userid}
    return {"userdetails":userdetails, "sessionid":"","status_code":"","natjwt": "", "tokenClaims": {}}



@router.post("/signuptoken")
async def thirparty_singup(
    #form_data: UserAuthData, 
    request: Request,
    current_user: TokenUserDetail = Depends(get_current_active_user),
    myhd: cf.MyHeaderData = Depends(cf.get_header_data) 
    ):
    #current_user: TokenUserDetail = cur_cur(oprtype = 'singup'),
    ed = ''
    try:
        if not current_user.reg_status:
            print(current_user)
            print("inside thirdparty signup")
            print('base url - ',request.base_url)
            print('url - ',request.url)
            print('client - ',request.client)
            print(myhd)
            data = {"userid":current_user.id, 
                    "username":current_user.name, 
                    "useremail":current_user.email, 
                    "userpassword":'', 
                    "userstatus":'A', 
                    **myhd}
            print(data)
            try:
                dbs = await db.qry_excute(db.queries.create_usr,data)
                print(dbs)
            except Exception:
                ed = "Failed due to Technical issue"    
                raise
            except Exception:                            
                    raise
        else:
            ed = "Already a registered users"
            raise Exception("Already a registered users")    

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail= {'error':True,'message': current_user.email + ' : ' + str(ed)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    #userdetails = {"displayname":"","email":data["useremail"],"phonenumber":"","photourl":"","providerId":"nat","uid":current_user.id}    
    tt =  'Registration successful for ' + data["useremail"] + '. Verify your email before login.'
    return {'detail':{'error':False,'message': tt}}


@router.post("/signupemail")
async def signupemail(
        request: Request,
        useremail: supemailResp,
        myhd: cf.MyHeaderData = Depends(cf.get_header_data),         
        ):
    print('base url - ',request.base_url)
    print('url - ',request.url)
    print('client - ',request.client)
    print("going inside signupemail")
    data = {"useremail":useremail.useremail, 
            **myhd}
    
    try:
        try:        
            userdb = await db.qry_excute(db.queries.reg_chk_with_email,data)
            print(userdb)
            print("--done")
            
            if(len(userdb)>1):                    
                raise Exception("Already a registered user [TM: Multiple users]") 
            elif (len(userdb)==1):
                raise Exception("Already a registered user")                 
        except Exception:            
            raise
        
        # No users with the email exists so proceeding to register in DB
        #   step 1 : Get user data from FB        
        #   step 2 : Save in DB

        # step 1
        try:
            userdet = await get_user_with_email(useremail.useremail)
        except Exception:
            raise
        
        #step 2
        print(myhd)
        print(userdet)
        print("--done 1")
        data = {"userid":userdet.uid, 
                "username":userdet.display_name,
                "useremail":userdet.email, 
                "userpassword":'', 
                "userstatus": 'D' if userdet.disabled else 'A',
                **myhd}
        print(data)
        try:
            dbs = await db.qry_excute(db.queries.create_usr,data)
            print(dbs)
        except Exception:
            #ed = "Failed due to Technical issue"    
            raise

    except Exception as e:
        print("Final excel")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= {'error':True,'message':useremail.useremail + ' : ' + str(e)},
            #detail="Session creation.  Failed due to Technical issue",
            headers={"WWW-Authenticate": "Bearer"},
        )            
    tt =  'Registration successful for ' + useremail.useremail + '. Verify your email before login.'
    return {'detail':{'error':False,'message': tt}}












@router.get("/test1")
async def login_for_access_token():
    #await db.qry_initialise()
    try:
        dd = await db.qry_excute(db.queries.secretcode)
    except Exception as a:
        print("outside")
        print(a)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Technical error",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"success":"result"}


@router.get("/test2")
async def login_for_access_token1():
    #await db.qry_initialise()
    try:
        dd = await db.qry_excute(db.queries.secretcode)
    except Exception as a:
        print("outside")
        print(a)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Technical error",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"success":"result"}

@router.get("/trantest")
async def login_for_access_token1():
    #await db.qry_initialise()
    try:       
        
        print("cleanup table")
        dd = await db.qry_excute(db.queries.testing.trantesttablecleanup)  
        print(dd)
        print("-----------------------------------------------")
        con,tr = await db.db_tran_start()
        print("--came out")
        print("starting a update")
        dd = await db.tran_excute(tr,con,db.queries.testing.beforerollbackinsert)
        print(dd)        
        dd = await db.tran_excute(tr,con,db.queries.testing.selecttrantest)
        print(dd)
        print("select data in table")
        print("rollback imulation")
        print("select data in table")
        try:
            dd = await db.tran_excute(tr,con,db.queries.testing.selecttrantestfail)
            print(dd)
        except Exception as e:
            print(e)
        print("table should be empty")
        dd = await db.qry_excute(db.queries.testing.selecttrantest)
        print(dd)
        print("-----------------------------------------------")
        #Commit test start        
        con,tr = await db.db_tran_start()
        print("--came out")
        print("starting a update")
        dd = await db.tran_excute(tr,con,db.queries.testing.beforecommitinsert)
        print(dd)        
        dd = await db.tran_excute(tr,con,db.queries.testing.selecttrantest)
        print(dd)
        print("committing")
        dd = await db.db_tran_end(tr,con)
        print("table should not be empty")
        dd = await db.qry_excute(db.queries.testing.selecttrantest)
        print(dd)
        print("-----------------------------------------------")
    except Exception as a:
        print("outside")
        print(a)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Technical error",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"success":"result"}