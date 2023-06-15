from flask_cors import CORS, cross_origin
from flask import Flask, request, render_template
from flask_test.my_secrets import DB_HOST_NAME, DB_USER_NAME, DB_PASSWORD, DB_NAME
from flask_test.get_image_links import get_image_links
import json

app = Flask(__name__)
CORS(app)

@app.route('/record_stream', methods=['GET'])
def record_stream():
    'streaming video data recording page'
    return render_template('stream.html')

@app.route('/record_images', methods=['GET'])
def record_images():
    links = 'will have links'.split() * 100
    return render_template('images.html', links=links)

@app.route('/image-get-endpoint', methods=['GET'])
def image_get_endpoint():
    '''whatthefuck'''
    import psycopg2

    # connection info
    host = DB_HOST_NAME
    user = DB_USER_NAME
    password = DB_PASSWORD
    database = DB_NAME

    # conn
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    # cur
    cursor = connection.cursor()

    # look up table
    sql_fetch_data = f'''
    SELECT Link
    FROM TABLE Links;
    '''
    cursor.execute(sql_fetch_data)

    # get links
    links = cursor.fetchall()

    return render_template('images.html', links=links)

@app.route('/record-post-endpoint', methods=['POST'])
def record_post_endpoint():
    '''
    automatic POST from javascript
    data preprocessed through MoveNet and sent
    '''
    import psycopg2

    # connection info
    host = DB_HOST_NAME
    user = DB_USER_NAME
    password = DB_PASSWORD
    database = DB_NAME

    # conn
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    # cur
    cursor = connection.cursor()

    # col names
    col_names = 'nose, left eye, right eye, left ear, right ear, left shoulder, right shoulder, left elbow, right elbow, left wrist, right wrist, left hip, right hip, left knee, right knee, left ankle, right ankle'
    col_names = col_names.split(sep=', ') # list has original col names
    col_names = [i.replace(' ', '_') for i in col_names] # underscore for blank
    col_names = [col+i for col in col_names for i in ('_y', '_x')] + ['posture'] # y,x coords for each col. tf lists y coords first
    col_names_and_types = [i + ' FLOAT,' for i in col_names[:-1]] + [col_names[-1] + ' VARCHAR(20),'] # sql FLOAT for all cols. posture at the end
    cols_string = '\n    '.join(col_names_and_types)[:-1] # exclude comma at end
    col_count_ex_id = len(col_names_and_types)

    # create table
    sql_create_table = f'''
    CREATE TABLE IF NOT EXISTS test (
        Id SERIAL PRIMARY KEY,
        {cols_string} 
    )
    '''
    cursor.execute(sql_create_table)

    # insert data
    positions_output = request.json['movenet_output'] # 1, 1, 17, 3
    single_point = positions_output[0][0] # 17, 3
    y_point = [row[0] for row in single_point]
    x_point = [row[1] for row in single_point]
    posture_input = request.json['posture']
    flatten = y_point + x_point + [posture_input]
    sql_insert = f'''
    INSERT INTO test ({', '.join(col_names).replace("'", '')}) VALUES {str(tuple([r'%s']*col_count_ex_id)).replace("'",'')}
    ''' # replace to delete quotes
    print(sql_insert)
    cursor.execute(sql_insert, flatten)

    # commit and close
    connection.commit()
    cursor.close()
    connection.close()

    return 'POST from stream'

if __name__ == '__main__':
    app.run(debug=True)