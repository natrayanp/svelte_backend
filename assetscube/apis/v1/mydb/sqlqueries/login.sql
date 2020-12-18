-- name: ownlogin_user_chk
SELECT userid,username,useremail,userpassword,userstatus FROM ac.userlogin
WHERE username = :username 
AND logintype = :logintype AND usertype = :usertype AND siteid = :siteid
AND userstatus NOT IN ('D');

-- name: trdlogin_user_chk
SELECT userid,username,useremail,userpassword,userstatus FROM ac.userlogin
WHERE userid = :userid 
AND  siteid = :siteid
AND userstatus NOT IN ('D');


-- name: create_usr!
INSERT INTO ac.userlogin (userid, username, useremail, userpassword, userstatus, siteid, userstatlstupdt, octime, lmtime) 
VALUES (:userid, :username, :useremail, :userpassword, :userstatus, :siteid, CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);


--name: chk_session_exists^
SELECT userid,sessionid FROM ac.loginh
WHERE userid = :userid AND logoutime IS NULL 
AND logintype = :logintype AND usertype = :usertype AND siteid = :siteid;

--name: create_session!
INSERT INTO ac.loginh (userid, ipaddress, sessionid, siteid, logintime) 
VALUES (:userid, :ipaddress, :sessionid, :siteid ,CURRENT_TIMESTAMP);
                            
--name: invalidate_session!
UPDATE ac.loginh SET logoutime = CURRENT_TIMESTAMP
WHERE userid = :userid 
AND siteid = :siteid
AND logoutime IS NULL


--name: reg_chk_with_email
SELECT userid,username,useremail,userpassword,userstatus FROM ac.userlogin
WHERE useremail = :useremail 
AND siteid = :siteid
AND userstatus NOT IN ('D');