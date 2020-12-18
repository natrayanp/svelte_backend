-- name: userstatus1
SELECT COUNT(1) FROM ac.userlogin WHERE
userid = :userid AND usertype = :usertype
AND userstatus NOT IN ('D');

-- name: secretcode
WITH maxtime AS (SELECT MAX(secoctime) FROM ac.secrettkn)
SELECT secretcode,seccdid FROM ac.secrettkn
WHERE secoctime = (select secoctime FROM ac.secrettkn)

-- name: secretcodej
SELECT json_agg(a) FROM (
SELECT secretcode,seccdid FROM unihot.secrettkn                                 
) as a;

-- name: secretcodef$
SELECT secretcode FROM ac.secrettkn
WHERE seccdid = :sktid;

-- name: userlogin
--SELECT json_agg(a) FROM (
SELECT userid, username, userpassword FROM ac.userlogin WHERE
username = :username AND userpassword = :userpassword 
AND userstatus = 'A' 
AND logintype = :logintype AND usertype = :usertype
--) as a;