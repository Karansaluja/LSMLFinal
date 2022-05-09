import importlib
import logging
from abc import ABC
from celery import Task
from .worker import app


class PredictTask(Task, ABC):
    """
    Abstraction of Celery's Task class to support loading ML model.
    """
    abstract = True

    def __init__(self):
        super().__init__()
        self.model = None

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        if not self.model:
            logging.info('Loading Model...')
            module_import = importlib.import_module(self.path[0])
            logging.info('module_import: {}'.format(module_import))
            logging.info('self path[0]: {} path[1]: {}'.format(self.path[0], self.path[1]))
            model_obj = getattr(module_import, self.path[1])
            self.model = model_obj()
            logging.info('Model loaded')
        return self.run(*args, **kwargs)


@app.task(ignore_result=False,
          bind=True,
          base=PredictTask,
          path=('celery_task_app.ml_model.qa_model', 'QAModel'),
          name='{}.{}'.format(__name__, 'QA'))
def get_answer(self, *args):
    """
    Essentially the run method of PredictTask
    """
    answer = self.model.predict(args[0])
    return answer

'''
@app.task()
def get_answer(req_input):
    logger.info('Got Request - Starting work ')
    output = _get_answer(req_input)
    logger.info('Work Finished ')
    return output



def load_model():
    global qa_model
    model_name = "deepset/roberta-base-squad2"
    qa_model = pipeline('question-answering', model=model_name, tokenizer=model_name)



def _get_answer(request_input):
    return qa_model(request_input)


if __name__ == "__main__":
    #load_model()
    test_request = {"question": "where is test?",
                    "context": "this is a test. It is situated in main.py file."}
    print('testing model')
    print(_get_answer(test_request))

'''