import aiosql
import asyncpg
import asyncio
import warnings


ENV = 0
# 0 - DEV
# 1- HEROKU
# 2 - UAT
# 3 - PROD
CON_STR = [{'host':'127.0.0.1', 'database': 'postgres','user':'postgres','password':'password123'},
            #"host='tantor.db.elephantsql.com' dbname='vizbcyai' user='vizbcyai' password='wtN1QNGIjImJTUIEc7h14oi72C7jXoAt'",
            "host='ec2-184-72-247-70.compute-1.amazonaws.com' dbname='dcvpcbdidm2qi3' user='gneloudcsniiwt' password='ef1a64d9ff9818e190a8ab931710e7c0b984f2c93b69120f84a42d3d01f06ddf'",
            "",
            "host='assetscube.c5eo06dso01d.ap-south-1.rds.amazonaws.com' dbname='nawalcube' user='nawalcube' password='Nirudhi1!'"
          ]

#mycon: asyncpg.Connection
queries =  aiosql.from_path("/home/nirudhi/projects/svelte_backend/assetscube/apis/v1/mydb/sqlqueries","asyncpg")

mypool: asyncpg.pool

async def qry_initialise(): 
    global queries    
    try:
        queries
    except NameError:
        try:
            queries = aiosql.from_path("/home/natrayan/projects/fseed_backend/assetscube/apis/v1/mydb/sqlqueries","asyncpg")
        except Exception as e:            
            raise

async def get_connection():    
    #global mycon
    try:        
        mycon
    except NameError:
        #print("con not defined so assigning as null")        
        try:
            conn_string = CON_STR[ENV]
            #mycon = await asyncpg.connect("postgresql://postgres:password123@127.0.0.1/postgres")
            mycon = await asyncpg.connect(**conn_string)
        except Exception as e:
            print("unable to connect")
            print(e)
            raise    
    return mycon

async def get_connection_from_Pool():    
    global mypool
    try:
        mypool
    except NameError:
        print("pool not defined so assigning as null")       
        try:
            conn_string = CON_STR[ENV]
            #mycon = await asyncpg.connect("postgresql://postgres:password123@127.0.0.1/postgres")
            mypool = await asyncpg.create_pool(**conn_string)
        except Exception as e:
            print("unable to create mypool")
            print(e)
            raise
        else:
            mycon = await mypool.acquire()            
    else:
        mycon = await mypool.acquire()

    return mycon


async def tran_excute(tr, conn, fn, data: dict = None):
    try:
        res = await my_excute(fn, data, conn,tr)
    except Exception as e:
        raise
    else:
        return res

async def qry_excute(fn, data: dict = None):
    print(data)
    print(fn)
    try:
        res = await my_excute(fn, data)
    except Exception as e:
        print('i am herer')
        print(e)
        raise
    else:
        return res

async def my_excute(fn, data = None, trconn = None, tr = None):
    fun_con = None
    
    if trconn == None:
        try:
            await qry_initialise()
            #await get_connection()
            fun_con = await get_connection_from_Pool()
        except Exception as e:
            print("inside preparing")
            print(e)
            raise
    else:
        try:
            await qry_initialise()
            #await get_connection()
            fun_con = trconn
        except Exception as e:
            print("inside preparing")
            print(e)
            raise

    print(fun_con)
    print(data)
    try:
        if data:
            res = await fn(fun_con,**data) 
        else:
            res = await fn(fun_con) 
        print (res)
    except Exception as e:
        if trconn == None:
            print("inside execute exception")
            print(e)
            raise
        else:
            print("inside execute exception & rollback")
            await tr.rollback()       
            await release_conn_to_pool(fun_con)     
            raise
    finally:
        if trconn == None:            
            print("--releasing connection")
            await release_conn_to_pool(fun_con)

    return res
    
async def db_tran_start():
    try:
        #conn = await get_connection()
        conn = await get_connection_from_Pool()
        tr = conn.transaction()
        await tr.start()
    except Exception as e:
        print(e)
        raise
    else:
        return conn, tr
    
async def db_tran_end(tr,conn):
    try:        
        await tr.commit()        
    except Exception as e:
        print(e)
        await tr.rollback()
        raise
    finally:
        await release_conn_to_pool(conn)
    return True


async def release_conn_to_pool(conn):
    if not conn.is_in_transaction():
        print("releasing the conn")
        await mypool.release(conn)
    else:
        warnings.warn('Connection not released to pool after transaction end') 