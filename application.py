from app import app, db
import time

@app.route('/time')
def get_current_time():
    return {'time': time.time()}
