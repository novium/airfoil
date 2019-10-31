from flask import Flask, request, abort
from flask_cors import CORS
import mysql.connector
import json
import time

from tasks import celery, calculate

api = Flask(__name__)
CORS(api)

db_host = 'db'
db_user = 'root'
db_password = '123'

print("Starting API server")
while True:  # API has to wait for the database to setup before connecting
    try:
        print("Connecting to DB")
        db = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database='airfoil'
        )
        time.sleep(3)
        print("Connected to database.")
        break
    except mysql.connector.errors.ProgrammingError:
        print("Creating database.")
        db = mysql.connector.connect(host=db_host, user=db_user, password=db_password)
        cursor = db.cursor(buffered=True)

        cursor.execute('CREATE DATABASE IF NOT EXISTS airfoil')  # Create database

        # Create results table
        # DB: id | angle | status | url
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS airfoil.results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                angle FLOAT(20, 10),
                status TEXT,
                url TEXT
            )
        ''')
        print("Database created.")
    except mysql.connector.errors.InterfaceError:
        pass
    except mysql.connector.errors.DatabaseError:
        pass

cursor = db.cursor(prepared=True)


@api.route('/', methods=['GET'])
def default():
    return 'This an API to the airfoil service. Please provide an angle in your query.'

# Takes an angle and returns a url to the file(s) [TODO] (if the result has
# already been computed), or the job ID if the result hasn't been computed yet.
# The API caches valid queries in a mySQL database and looks in there first. If
# result is not in the database, create job to calculate angle, and return id.
#
# Possible job statuses:
# - 'done'
# - 'computing'
@api.route('/create_job', methods=['GET'])
def create_job():
    try:
        angle = float(request.args.get('angle'))
    except (ValueError, TypeError):
        abort(400, 'Please provide an angle between 0 and 90 degrees.')

    status = job_status('angle', angle)

    if status == 'done':  # Check in database if angle has already been computed
        cursor.execute('SELECT url FROM results WHERE angle=%s', (angle,))
        try:
            return json.dumps({
                'url': str(next(cursor)[0]),
                'status': status
            })
        except StopIteration:
            abort(
                400,
                'Result for ' + str(angle) + ' degrees has already been \
                computed, but something went wrong when fetching it.'
            )
    elif status == 'computing':
        cursor.execute('SELECT id FROM results WHERE angle=' + str(angle) + ' LIMIT 1')
        try:
            return json.dumps({
                'id': cursor.fetchall()[0][0],
                'angle': angle,
                'status': status
            })
        except StopIteration:
            abort(
                400,
                'Result for angle ' + str(angle) + ' is already being \
                computed, but something went wrong when fetching its job ID.'
            )
    else:
        # TODO: If result is not in DB, call Airfoil with `angle`
        status = 'created'
        cursor.execute(
            'INSERT INTO results (angle, status) VALUES (%s, %s);',
            (angle, status)
        )
        db.commit()

        cursor.execute('SELECT LAST_INSERT_ID()')
        id_ = next(cursor)[0]
        calculate.delay(id_, angle)

        try:
            return json.dumps({
                'id': id_,
                'angle': angle,
                'status': status
            })
        except StopIteration:
            return


#  Check status of job with `id`, return url if done, or "working on it" if
#  it's already being calculated, otherwise "not done" in JSON
@api.route('/get')
def get():
    try:
        id = int(request.args.get('id'))
    except (ValueError, TypeError):
        abort(400, 'Please provide an id.')
    status = job_status('id', id)
    if status is None:
        abort(404, 'There is currently no job with id ' + str(id))
    elif status == 'done':
        cursor.execute('SELECT url FROM results WHERE id=' + str(id) + ' LIMIT 1')
        try:
            return json.dumps({
                'url': cursor.fetchall()[0][0],
                'status': status
            })
        except (StopIteration, IndexError):
            abort(
                400,
                """Job with id %s is done, but something went wrong when
                fetching its url."""
            )
    else:
        return json.dumps({
            'url': None,
            'status': status
        })


#  Returns all running jobs and their status as a JSON formatted string
@api.route('/jobs')
def all_jobs():
    result = []
    cursor.execute('SELECT id, angle, status FROM results')
    for (id, angle, status) in cursor:
        result.append({
            'id': id,
            'status': status,
            'angle': angle
        })
    return json.dumps(result)


@api.route('/clean')
def clean_db():
    cursor.execute('DELETE FROM results')
    return 'Deleted all results.'


# Returns status of a job based on either angle or id.
# `key` should be set to either 'angle' or 'id'.
# `value` should be set to either the angle or the id of the job.
def job_status(key, value):
    cursor.execute('SELECT status FROM results WHERE ' + key + '=' + str(value) + ' LIMIT 1')
    # For some reason, using `%s` for inserting key and value doesn't work
    try:
        status_list = cursor.fetchall()
        if not status_list:
            return
        else:
            return status_list[0][0]
    except StopIteration:
        return 'failed'


if __name__ == '__main__':
    api.run(host='0.0.0.0', debug=True, port=80)
