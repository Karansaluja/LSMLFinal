from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline


class QAModel:

    """ Wrapper for loading and serving pre-trained model"""

    def __init__(self):
        self.model_name = "deepset/roberta-base-squad2"
        self.model = pipeline('question-answering', model=self.model_name, tokenizer=self.model_name)

    def predict(self, data):
        return self.model(data)