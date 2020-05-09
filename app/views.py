import time
from application import app

@app.route('/time')
def get_current_time():
    return {'time': time.time()}
