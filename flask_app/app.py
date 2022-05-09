try:
    from flask import Flask, request
    import boto3
    from celery import Celery
    import pymongo
    import json
    from flask_cors import CORS, cross_origin
except Exception as e:
    print("Error  :{} ".format(e))

app = Flask(__name__)
_ = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

celery_app = Celery('celery_app',
                    broker='amqp://admin:mypass@rabbit:5672',
                    backend='mongodb://mongodb_container:27017/mydb')


@app.route('/')
@cross_origin()
def health_check():
    return "Hello from QA app"


@app.route('/get_answer', methods=["GET", "POST"])
@cross_origin()
def get_answer():
    if request.method == 'POST':
        data = request.get_json(force=True)
        result = celery_app.send_task('celery_task_app.tasks.QA', args=[data])
        response = {
            "task_id": result.id
        }
        app.logger.info(result.backend)
        return json.dumps(response)
    else:
        return "You should use only POST query"


@app.route('/get_answer/<task_id>')
@cross_origin()
def get_answer_status(task_id):
    task = celery_app.AsyncResult(task_id, app=celery_app)
    if task.ready():
        response = {
            "status": "DONE",
            "answer": task.result['answer']
        }
    else:
        response = {
            "status": "IN_PROGRESS"
        }
    return json.dumps(response)
