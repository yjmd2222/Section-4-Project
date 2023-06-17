'''
download database to csv
'''
from helpers import get_connection
import csv

connection = get_connection()
cursor = connection.cursor()

def export_to_csv(cursor, *args):
    '*args: table names'
    for arg in args:
        sql_columns = f'''
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{arg}';
        '''
        sql_select = f'SELECT * FROM {arg}'
        with open(arg+'.csv', 'w') as file:
            writer = csv.writer(file)

            cursor.execute(sql_columns)
            header = cursor.fetchall()
            header = [i[0] for i in header]
            writer.writerow(header)

            cursor.execute(sql_select)
            writer.writerows(cursor.fetchall())

    cursor.close()

export_to_csv(cursor, 'movenet_output', 'classifier_predict')

connection.close()
