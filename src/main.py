from smartAssistant import SmartAssistant
import os
from dotenv import load_dotenv
from openai import OpenAI
# 加载环境变量
load_dotenv()
# 从环境变量中读取API密钥
api_key = os.getenv('ZHIPU_API_KEY')
# 基础配置
base_url = "https://open.bigmodel.cn/api/paas/v4/"
chat_model = "glm-4-flash"
# 创建客户端
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)
def get_completion(prompt):
    response = client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content
# 测试调用
response = get_completion("你好，世界！")
print(response) 

if __name__ == "__main__":
    assistant = SmartAssistant(client)
    assistant.start_conversation()