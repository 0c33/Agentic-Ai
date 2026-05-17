import json
import os
from langchain.chat_models import init_chat_model

class MeetingActionItemExtractor:
    def __init__(self):
        self.llm = init_chat_model(
            model_provider='openai',
            model="Qwen3.6-35B-A3B-uncensored-heretic-Native-MTP-Preserved-NVFP4-Experts-Only-Q8_0.gguf",
            api_key='None',
            base_url="http://localhost:8080/v1",
            extra_body={
                "chat_template_kwargs": {"enable_thinking": False},
            },
        )

    def extract(self, raw_text):
        result = self.llm.invoke(f"""
        You are an expert Meeting Action Item Extractor. Your task is to analyze the provided raw meeting notes or transcript text and extract every single action item mentioned. 

        For each action item, you must identify:
        1. The specific task or action.
        2. The owner (person responsible). If not explicitly stated, assign 'Unassigned'.
        3. The deadline. If not explicitly stated, assign 'TBD'.
        4. The priority. If not explicitly stated, assign 'Medium'. However, infer overrides from context (e.g., 'ASAP', 'urgent', 'high priority' should change the priority level).

        Rules:
        - Never skip any action item, even if implied.
        - Handle missing information gracefully by applying the defaults mentioned above.
        - Do not include general discussion points, only actionable tasks.

        Output Format:
        You must return ONLY a valid JSON object with the following structure:
        {{
          "meeting_metadata": {{
            "date": "YYYY-MM-DD or inferred date", 
            "participants": ["list", "of", "participants"]
          }},
          "action_items": [
            {{
              "task": "string",
              "owner": "string",
              "deadline": "string",
              "priority": "string (Low, Medium, High, or ASAP)"
            }}
          ]
        }}

        Ensure the JSON is strictly valid and contains no markdown formatting like ```json.

        Raw Text:
        {raw_text}
        """)

        try:
            r = json.loads(result.content)
            return r
        except Exception as e:
            print(f'\n\nError parsing JSON: {{e}}\n\n')
            print(result.content)
            return None

if __name__ == '__main__':
    extractor = MeetingActionItemExtractor()
    user_input = input("Enter raw meeting notes or transcript: ")
    result = extractor.extract(user_input)
    if result:
        print(json.dumps(result, indent=2))