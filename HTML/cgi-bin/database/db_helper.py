
import sqlite3
from time import strftime


def write_user(ip):
    with sqlite3.connect("cgi-bin/database/users.db") as conn:
        cursor = conn.cursor()
        val = "VALUES ('{}', '{}')".format(ip, strftime("%H:%M %d.%m.%Y"))
        cursor.execute(
            "INSERT INTO users (ip_address, date)" + val
        )
    conn.close()


def read_users():
    with sqlite3.connect("cgi-bin/database/users.db") as conn:
        cursor = conn.cursor()
        cursor.execute('select * from users')
        val = cursor.fetchall()
    conn.close()
    return val

if __name__ == "__main__":
    print "Content-type:text/html\r\n\r\n"
    print """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
    <pre>
    """
    print "<strong>{:30s}{:30s}{:30s}</strong>".format("User", "IP", "Date")
    for row in read_users():
        format_row = "{:<29d} {:30s}{:30s}".format(row[0], row[1], row[2])
        print format_row
    print """
    </pre>
</body>
</html>
"""
