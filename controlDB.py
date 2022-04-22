import sqlite3
def setmoney():

    conn = sqlite3.connect('data/field_db.db')
    cursor = conn.cursor()

    id = int(input("Enter Discord id :"))
    newamount = int(input("Enter new amount : "))

    cursor.execute("""SELECT hashfield FROM users WHERE id = ?""", (id,))
    l = list(cursor.fetchone())
    data = []
    for i in l:
        data.append(i)
    hashfield = data[0]
    print(hashfield)
    cursor.execute("""UPDATE fieldsdetails SET money = ? WHERE hashfield = ?""", (newamount, hashfield))
    conn.commit()
    print("Done.")

term = True
while term:

    print("0 - Exit")
    print("1 - Set money of a user")

    choix = int(input("cmd > "))

    if choix == 0:
        term = False

    elif choix == 1:
        setmoney()