import psycopg2
try:
    connect_str = "dbname='quotes' user='pyuser' host='localhost' password='password'"
    conn = psycopg2.connect(connect_str)
    cursor = conn.cursor()
    cursor.execute("""insert into test_py(text,num) values ('{1a,a2,a3}',7)""")
    cursor.execute("""select * from test_py""")
    rows = cursor.fetchall()
    print(rows)
    conn.commit()
    conn.close()
except Exception as e:
    print("Uh oh, can't connect. Invalid dbname, user or password?")
    print(e)