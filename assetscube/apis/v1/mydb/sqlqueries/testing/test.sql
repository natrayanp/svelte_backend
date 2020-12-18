--name: trantesttable#
CREATE TABLE ac.trantest (
    testvalue	               varchar(100) NOT NULL,
    octime			           date NOT NULL
	);

-- name: trantesttablecleanup!
DELETE FROM ac.trantest;

-- name: beforerollbackinsert!
INSERT INTO ac.trantest VALUES ('Rollbacktest',CURRENT_DATE);

-- name: beforecommitinsert!
INSERT INTO ac.trantest VALUES ('committest',CURRENT_DATE);

-- name: selecttrantest
SELECT * FROM ac.trantest ;

-- name: selecttrantestfail
SELECT * FROM unihot.trantest ;