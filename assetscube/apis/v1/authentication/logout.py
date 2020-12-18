from fastapi import APIRouter, HTTPException
from fastapi import Depends, FastAPI, HTTPException, status


router = APIRouter()

@router.get("/userregchk1")
async def UserRegChk(Resource):  
    return "all good"


'''        res_to_send, repp = userregchk_common(request, 'uh')

        if res_to_send == 'success' or 'fail':
            resps = repp    
            #resps = make_response(jsonify(response), 200 if res_to_send == 'success' else 400)
        else:
            raise HTTPException(status_code=404, detail="Item not found")
        #dfdfdf
        return resps
        

async def userregchk_common(request, site):
        # This is only for thirparty auth
        print("inside userregchk_common")
        s = 0
        f = None
        t = None #message to front end
        response = None
        res_to_send = 'fail'
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        dtkn = jwtf.decodetoken(request, needtkn = False)
        userid = dtkn.get("user_id", None)

            
        thirdparty = request.headers.get("thirdparty", None)
        usertype = request.headers.get("usertype", None)


        print("iamback")
        print(userid)
        print(thirdparty)
        print(usertype)

        if userid == None:
            s, f, t= errhand.get_status(s, 100, f, "No user details sent from client", t, "yes")

        if thirdparty == None:
            s, f, t= errhand.get_status(s, 100, f, "No auth method details sent from client", t, "yes")
        else:
            thirdparty = "T" if thirdparty == "true" else "S"
            
        if usertype == None:
            s, f, t= errhand.get_status(s, 100, f, "No auth method details sent from client", t, "yes")

        
        if s <= 0:
            con, cur, s1, f1 = db.mydbopncon()
            s, f, t = errhand.get_status(s, s1, f, f1, t, "no")
            s1, f1 = 0, None

        if s <= 0:
            command = cur.mogrify("""
                                    SELECT COUNT(1) FROM unihot.userlogin WHERE
                                    userid = %s AND logintype = %s AND usertype = %s
                                    AND userstatus NOT IN ('D') ;
                                """,(userid, thirdparty, usertype,) )
            print(command)
            cur, s1, f1 = db.mydbfunc(con,cur,command)
            s, f, t = errhand.get_status(s, s1, f, f1, t, "no")
            s1, f1 = 0, None
            print('----------------')
            print(s)
            print(f)
            print('----------------')
            if s > 0:
                s, f, t = errhand.get_status(s, 200, f, "User data fetch failed with DB error", t, "no")
        print(s,f)

        if s <= 0:
            user_cnt = cur.fetchall()[0][0]
            print(user_cnt)


        if s > 0:
            res_to_send = 'fail'
            response = {
                'uid' : userid,
                'sessionid' : '',
                'status': res_to_send,
                'status_code': s,
                'message': errhand.error_msg_reporting(s, t)
                }
        else:
            if user_cnt > 0:
                res_to_send = 'success'
                response = {
                            'uid' : userid,
                            'sessionid' : None,
                            'status': res_to_send,
                            'status_code': 0,
                            'message': ''
                }
            else:
                s, f, t = errhand.get_status(s, 401, f, "Not a registered user. Signup",t,"yes")
                res_to_send = 'fail'
                response = {
                    'uid' : userid,
                    'sessionid' : None,
                    'status': res_to_send,
                    'status_code': s,
                    'message': errhand.error_msg_reporting(s, t)
                    }
        print('##########')
        print(response)
        
        return (res_to_send, response)
    
'''