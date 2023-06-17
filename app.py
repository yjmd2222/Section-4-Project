'''
appppppp
'''
from flask_cors import CORS
from flask import Flask, request, render_template
from helpers import get_connection

from datetime import datetime,  timedelta

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/record_stream', methods=['GET'])
def record_stream():
    'streaming video data recording page'
    return render_template('recordStream.html')

@app.route('/record_images', methods=['GET'])
def record_images():
    'image data recording page'
    # init connection
    connection = get_connection()
    cursor = connection.cursor()

    # fetch data
    sql_fetch_data = '''
    SELECT *
    FROM links
    '''
    cursor.execute(sql_fetch_data)
    link_data = cursor.fetchall()

    return render_template('recordImages.html', link_data=link_data)

@app.route('/check-posture', methods=['GET'])
def your_posture():
    'model demo'
    from labels import classes
    return render_template('checkPosture.html', classes=classes)

@app.route('/check-posture-post-endpoint', methods=['POST'])
def posture_post_endpoint():
    'get data from /posture'
    from labels import classes_eng
    movenet_output = request.json['movenet_output']
    predicted_posture = request.json['predictedPosture']
    probas = request.json['probas']
    timestamp = request.json['timestamp']
    utc9 = datetime.fromtimestamp(timestamp/1000) + timedelta(hours=9) # js는 밀리초 단위로
    utc9 = utc9.strftime(r'%Y-%m-%dT%H:%M:%SZ+0900')

    # connection
    connection = get_connection()
    cursor = connection.cursor()

    # columns
    col_names = 'nose, left eye, right eye, left ear, right ear, left shoulder, right shoulder, left elbow, right elbow, left wrist, right wrist, left hip, right hip, left knee, right knee, left ankle, right ankle'
    col_names = col_names.split(sep=', ') # list has original col names
    col_names = [i.replace(' ', '_') for i in col_names] # underscore for blank
    col_names = [col+i for col in col_names for i in ('_y', '_x')] + ['posture', 'forward_head_p', 'leaning_p', 'normal_p', 'time_9']
    col_names_and_types = [i + ' FLOAT,' for i in col_names[:34]] + [col_names[-5]+' VARCHAR(20),'] + [i+' FLOAT,' for i in col_names[-4:-1]]\
        + [col_names[-1]+' VARCHAR(25)']
    cols_string = '\n    '.join(col_names_and_types)
    col_count_ex_id = len(col_names_and_types)

    # create table
    sql_create_table = f'''
    CREATE TABLE IF NOT EXISTS classifier_predict (
        Id SERIAL PRIMARY KEY,
        {cols_string} 
    )
    '''
    cursor.execute(sql_create_table)

    # insert
    datapoint = movenet_output + [classes_eng.get(predicted_posture), *probas, utc9]
    sql_insert = f'''
    INSERT INTO classifier_predict ({', '.join(col_names).replace("'", '')}) VALUES {str(tuple([r'%s']*col_count_ex_id)).replace("'",'')}
    ''' # replace to delete quotes
    cursor.execute(sql_insert, datapoint)

    # commit and close
    connection.commit()
    cursor.close()
    connection.close()

    return 'POST from check-posture'

@app.route('/record-post-endpoint', methods=['POST'])
def record_post_endpoint():
    '''
    automatic POST from javascript
    data preprocessed through MoveNet and sent
    '''
    # connection
    connection = get_connection()

    # cur
    cursor = connection.cursor()

    # col names
    col_names = 'nose, left eye, right eye, left ear, right ear, left shoulder, right shoulder, left elbow, right elbow, left wrist, right wrist, left hip, right hip, left knee, right knee, left ankle, right ankle'
    col_names = col_names.split(sep=', ') # list has original col names
    col_names = [i.replace(' ', '_') for i in col_names] # underscore for blank
    col_names = [col+i for col in col_names for i in ('_y', '_x')] + ['posture', 'location'] # y,x coords for each col. tf lists y coords first
    col_names_and_types = [i + ' FLOAT,' for i in col_names[:-2]] + [col_names[-2]+' VARCHAR(20),',  col_names[-1]+' VARCHAR(1000)'] # sql FLOAT for all cols. posture at the end
    cols_string = '\n    '.join(col_names_and_types)
    col_count_ex_id = len(col_names_and_types)

    # create table
    sql_create_table = f'''
    CREATE TABLE IF NOT EXISTS movenet_output (
        Id SERIAL PRIMARY KEY,
        {cols_string} 
    )
    '''
    cursor.execute(sql_create_table)

    # insert data
    movenet_output = request.json['movenet_output'] # 34 or 1, 34
    posture_input = request.json['posture']
    location = request.json['location']
    point_y_list = []
    if len(movenet_output) != 1: # if not bulk which is 34
        movenet_output = [movenet_output] # make it bulk 1, 34
    for single_point in movenet_output: # for 34 in 1, 34
        single_point_y = single_point + [posture_input, location]
        point_y_list.append(single_point_y)
    sql_insert = f'''
    INSERT INTO movenet_output ({', '.join(col_names).replace("'", '')}) VALUES {str(tuple([r'%s']*col_count_ex_id)).replace("'",'')}
    ''' # replace to delete quotes
    cursor.executemany(sql_insert, point_y_list)

    # commit and close
    connection.commit()
    cursor.close()
    connection.close()

    return 'POST from record'

if __name__ == '__main__':
    app.run(debug=True)
