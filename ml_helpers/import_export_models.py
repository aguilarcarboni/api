from transformers import AutoTokenizer, AutoModelForCausalLM

def savePretainedModel(path, url, modelType):
    model = modelType.from_pretrained(url, trust_remote_code=True)
    model.save_pretrained(path, from_pt=True)
    return path

def loadLocalModel(path, modelType):
    model = AutoModelForCausalLM.from_pretrained(path)
    return model

savePretainedModel('C:/Desktop','models/functionary', AutoModelForCausalLM)