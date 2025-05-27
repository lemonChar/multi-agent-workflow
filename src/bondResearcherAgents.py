import os
import json
import requests
from typing import Dict, List

# Qwen3 API配置
QWEN_API_URL = "https://api.qwen.com/v1/generate"
API_KEY = "your_api_key_here"

# Agent角色定义
class Agent:
    def __init__(self, role: str, prompt_template: str):
        self.role = role
        self.prompt_template = prompt_template
        
    def execute(self, context: Dict) -> str:
        """执行任务并返回结果"""
        prompt = self._generate_prompt(context)
        return self._call_qwen_api(prompt)
        
    def _generate_prompt(self, context: Dict) -> str:
        """根据模板生成提示词"""
        return self.prompt_template.format(**context)
        
    def _call_qwen_api(self, prompt: str) -> str:
        """调用Qwen3 API生成内容"""
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "qwen3",
            "prompt": prompt,
            "max_tokens": 1024,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(QWEN_API_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()["text"]
        except Exception as e:
            return f"API调用失败: {str(e)}"

# 定义各Agent的Prompt模板
director_prompt = """## Role: 研究总监

## Instruction:
你是一个专业的债券研究任务拆分专家。请根据输入的市场事件或政策背景，将研究任务分解为若干个子任务。每个子任务应包含：
1. **主题**（Topic）：如宏观经济影响、行业趋势、财务指标分析等
2. **分析维度**（Dimensions）：如利率变动、信用利差、行业增长率、偿债能力等
3. **所需数据**（Data Sources）：如国家统计局、央行公告、Wind数据、上市公司年报等
4. **预期输出**（Expected Output）：如分析报告、图表、风险评分等

## Context:
{context}

## Output Format:
请以JSON数组形式输出，每个子任务应包含以下字段：
- id: 任务唯一标识
- topic: 子任务主题
- dimensions: 分析维度列表
- data_sources: 所需数据来源
- expected_output: 预期输出形式

## Example:
[
    {
        "id": "task_001",
        "topic": "宏观经济政策对债券市场的影响",
        "dimensions": ["GDP增速", "CPI变化", "货币政策调整"],
        "data_sources": ["中国人民银行公告", "国家统计局2025年一季度数据"],
        "expected_output": "分析政策对利率曲线和信用利差的影响"
    },
    ...
]
"""

researcher_prompt = """## Role: 债券研究员

## Instruction:
你是一位专业的债券分析师，请根据以下任务要求进行深入研究：
1. **主题**：{topic}
2. **分析维度**：{dimensions}
3. **数据来源**：{data_sources}
4. **时间范围**：请使用2025年一季度及之前发布的最新数据
5. **分析要求**：
   - 使用权威来源（如Wind、央行、上市公司年报）
   - 包含定量分析（如计算财务指标）
   - 包含定性分析（如政策解读、行业趋势判断）
   - 识别并说明潜在风险因素（如信用违约、流动性风险）

## Context:
{context}

## Output Format:
请以Markdown格式输出，包含以下部分：
- 摘要（Summary）
- 数据分析（Data Analysis）
- 风险提示（Risk Factors）
- 结论（Conclusion）

## Example:
### 摘要
本报告分析了...

### 数据分析
- 利率变化：...
- 行业增长率：...

### 风险提示
- 信用风险：...
- 政策风险：...

### 结论
综上所述，...
"""

logic_checker_prompt = """## Role: 逻辑校验员

## Instruction:
你是一位专业的内容逻辑校验专家，请对以下研究报告进行逻辑审查，重点检查：
1. **数据来源可靠性**：是否引用了权威且最新的数据？
2. **推理过程合理性**：结论是否基于数据和分析逻辑得出？
3. **结论与论据一致性**：是否有推论与数据不一致的情况？

## Context:
{context}

## Output Format:
请以JSON格式输出：
- score: 评分（1-10）
- comments: 审查意见（如“逻辑连贯，但缺乏对XXX的解释”）
- suggestions: 改进建议（如“建议补充XXX数据”）

## Example:
{
    "score": 8,
    "comments": "整体逻辑清晰，但未说明XXX与YYY之间的关系",
    "suggestions": [
        "补充2025年一季度行业增长率数据",
        "增加对政策影响的量化分析"
    ]
}
"""

style_modifier_prompt = """## Role: 文字润色员

## Instruction:
你是一位专业的内容编辑，请对以下研究报告进行语言润色：
1. 使用专业术语（如“信用利差”、“久期”、“杠杆率”等）
2. 保持客观中立，避免主观判断
3. 确保段落衔接自然，逻辑清晰
4. 优化标题和小标题，使其更具信息量
5. 去除冗余内容，提升阅读体验

## Context:
{context}

## Output Format:
请以Markdown格式输出润色后的内容

## Example:
### 摘要
本报告对XXX进行了全面分析...

### 数据分析
- 利率变化：...
- 行业增长率：...
"""

quality_controller_prompt = """## Role: 质量管控员

## Instruction:
你是一位专业的内容质量评估专家，请对以下研究报告进行评分和建议：
1. **数据准确性**（20分）：是否使用了准确且最新的数据？
2. **分析深度**（20分）：是否进行了多维度、深入的分析？
3. **风险提示完整性**（20分）：是否全面覆盖了潜在风险？
4. **表达清晰度**（20分）：语言是否清晰、专业？
5. **结构合理性**（20分）：结构是否逻辑清晰、易于阅读？

## Context:
{context}

## Output Format:
请以JSON格式输出：
- total_score: 总评分（1-10）
- breakdown: 各项评分详情
- feedback: 综合反馈与改进建议

## Example:
{
    "total_score": 9,
    "breakdown": {
        "data_accuracy": 18,
        "analysis_depth": 19,
        "risk_coverage": 17,
        "expression": 19,
        "structure": 18
    },
    "feedback": "报告整体质量较高，但建议补充XXX分析以提升深度"
}
"""

# 初始化Agent
agents = {
    "director": Agent("研究总监", director_prompt),
    "researcher": Agent("债券研究员", researcher_prompt),
    "logic_checker": Agent("逻辑校验员", logic_checker_prompt),
    "style_modifier": Agent("文字润色员", style_modifier_prompt),
    "quality_controller": Agent("质量管控员", quality_controller_prompt)
}

def bond_research_pipeline(event: str) -> Dict:
    """债券研究工作流"""
    results = {}
    
    # 1. 任务拆分
    context = {"context": event}
    results["tasks"] = json.loads(agents["director"].execute(context))
    
    # 2. 并行研究
    for task in results["tasks"]:
        research_context = {
            "topic": task["topic"],
            "context": task.get("context", event)
        }
        raw_result = agents["researcher"].execute(research_context)
        
        # 3. 逻辑校验
        check_context = {"context": raw_result}
        check_result = json.loads(agents["logic_checker"].execute(check_context))
        
        # 4. 文字润色
        if check_result["score"] >= 7:
            modified = agents["style_modifier"].execute({"context": raw_result})
            results[task["id"]] = {
                "raw": raw_result,
                "modified": modified,
                "check": check_result
            }
        else:
            # 需要重做
            results[task["id"]] = {
                "raw": raw_result,
                "check": check_result,
                "status": "需要修改"
            }
    
    # 5. 质量评估
    final_context = {"context": json.dumps(results)}
    results["quality"] = json.loads(agents["quality_controller"].execute(final_context))
    
    return results

# 示例使用
if __name__ == "__main__":
    # 输入事件示例
    event = "中国人民银行决定：自2025年5月20日起，下调金融机构存款准备金率0.5个百分点"
    
    # 执行研究流程
    output = bond_research_pipeline(event)
    
    # 输出结果
    print("债券研究结果:")
    print(json.dumps(output, indent=2, ensure_ascii=False))