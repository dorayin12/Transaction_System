import xlrd
import MySQLdb
import datetime


book = xlrd.open_workbook('/home/wsang/book.xls')
sheet = book.sheet_by_name("book")
#sheet = book.sheet_by_index(0)
                        
database = MySQLdb.connect (user="root", host="localhost", db="oldsales")
cursor = database.cursor()

#Read all values in column 4
c      = sheet.col(4) 

#Change date into MySQL format
##for c in range(1, sheet.nrows):
##         cell               = sheet.cell(c, 4)

def cellval(cell, datemode):
    if cell.ctype == xlrd.XL_CELL_DATE:
        datetuple = xlrd.xldate_as_tuple(cell.value, datemode)
        if datetuple[3:] == (0, 0, 0):
            return datetime.date(datetuple[0], datetuple[1], datetuple[2])
        return datetime.date(datetuple[0], datetuple[1], datetuple[2], datetuple[3], datetuple[4], datetuple[5])
    if cell.ctype == xlrd.XL_CELL_EMPTY:    return None
    if cell.ctype == xlrd.XL_CELL_BOOLEAN:  return cell.value == 1
    return cell.value

##c      = sheet.col(4)

#Create a For loop to interate through each row in the XLS file, starting at ros 2 to skip the headers
for r in range(1, sheet.nrows): #1 stands for the 2nd row
         username            = sheet.cell(r,0).value
         email               = sheet.cell(r,1).value
         departmentaccount   = sheet.cell(r,2).value
         subaccount          = sheet.cell(r,3).value
         objcode             = sheet.cell(r,5).value
         subobjcode          = sheet.cell(r,6).value
         software            = sheet.cell(r,7).value
         itemtype            = sheet.cell(r,8).value
         quantity            = sheet.cell(r,9).value
         price               = sheet.cell(r,10).value
         total               = sheet.cell(r,11).value
         product             = sheet.cell(r,12).value
         productfamily       = sheet.cell(r,13).value
         item_profam         = sheet.cell(r,14).value
         c                   = sheet.cell(r, 4)
         date_soldon         = cellval(c, 0)


#Assign values from each row (it should be in the loop)
         cursor.execute('INSERT IGNORE INTO users (user_name, email) VALUES (%s, %s)', (username, email) )
         cursor.execute('select distinct id_user from users where email = %s', (email))
         userid = cursor.fetchall()
#         cursor.execute('INSERT INTO accounts (id_user, account_number, sub_account) VALUES (%s, %s, %s)',
#                        (userid, departmentaccount, subaccount))
         cursor.execute('INSERT INTO orders (date_soldon, item_title, obj_code, sub_objcode, item_type, quantity, price_per_copy,\
                        total_cost, product, product_family, item_number, id_user) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',\
                        (date_soldon, software, objcode, subobjcode, itemtype, quantity, price, total, product, productfamily, item_profam, userid))
      

cursor.close()
database.commit()
database.close()
print ""
print "All Done!"
print ""
columns = str(sheet.ncols)
rows = str(sheet.nrows)
print "You have successfully imported " + columns + " columns and " + rows + " rows to MySQL."
