import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key=os.getenv('ZHIPU_API_KEY')
base_url = "https://open.bigmodel.cn/api/paas/v4/"
chat_model = "glm-4-flash"

client=OpenAI(
    api_key=api_key,
    base_url=base_url
)

def get_completion(prompt):
    response=client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role":"user","content":prompt},
        ],
    )
    return response.choices[0].message.content

response=get_completion("你好，世界")
print(response)