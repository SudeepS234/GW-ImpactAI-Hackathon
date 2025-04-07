from transformers import pipeline

qg_pipeline = pipeline("text2text-generation", model="iarfmoose/t5-base-question-generator")
output = qg_pipeline("generate questions: Mitochondria is the powerhouse of the cell.")
print(output)
