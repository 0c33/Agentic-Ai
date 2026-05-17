from langchain.chat_models import init_chat_model
import json, os, time, subprocess, sys, tempfile

class Agentic:
    def __init__(self) -> None:
        
        self.llm = init_chat_model(
            model_provider='openai',
            model="Qwen3.6-35B-A3B-uncensored-heretic-Native-MTP-Preserved-NVFP4-Experts-Only-Q8_0.gguf",
            # model="qwen3.6-35b-a3b",
            # model="gemma-4-e4b-it",
            api_key='None',
            base_url="http://localhost:8080/v1",
            # temperature=0.4,
            # top_p=0.95,
            extra_body={
                # "top_k": 20,
                "chat_template_kwargs": {"enable_thinking": False},
            },
        )

        print("🚀 Initializing Agentic AI...")
        user_request = input("💡 Enter your request: ")

        self.define_user_request(user_request)



    def define_user_request(self, user_request):

        chat_history = ''
        print("🔄 Clarifying your idea...")

        while True:

            result = self.llm.invoke(f"""
            you will try to understand user request, ask the user until you got the idea.
            the user request will be related on building Ai Agent ( Agentic Ai (Agent who Builds Agents)).
            after you clarify user request, 'idea' will go to the Agentic Ai ( who build Agents ).
            the user will give you an idea of an agent, then you will send the idea to the Agentic Ai through 'idea' arg.
            
            you will return only json format no ```json```.
            
            ARGS:
                done_understanding: you will return True if you got the idea, otherwise False.
                question: you will return a question if 'done_understanding' is false.
                idea: you will return what user request to become full idea, otherwise null.
                user_inputs_summary: you will return all user input summaries.
                
                
            user request: {user_request}
            Chat History: {chat_history}""")
                
            try:
                r = json.loads(result.content)
                done_understanding = r['done_understanding']
                question = r['question']
                idea = r['idea']

                if 'TRUE' in str(done_understanding).upper():
                    self.Agentic_Ai(user_request, idea)
                    break

                print(f"❓ {question}")
                inp = input("📝 Your response: ")

                chat_history += f"your response: {question}\n\nUser response: {inp}\n\n\n"

            except Exception as e:
                print(f'\n\nFailed Parsing json, details: {e}\n\n\n')


    def Agentic_Ai(self, user_request, idea): # An Agentic AI that takes a high-level 'Super idea' or big project from the user and decomposes it into a list of atomic, actionable tasks for a human user. Each task should be a simple, direct action item (e.g., 'Write the intro') based strictly on the user's request, without adding extra context, prerequisites, or time estimates unless explicitly asked.

        agent_prompt = ''
        agent_result = ''
        agent_history = ''
        tries_count = 0
        user_notes = ''

        chat_history = ''
        print("🏗️ Building Agent progress...")

        while True:

            result = self.llm.invoke(f"""
            you are Agentic Ai, basically Agent builds agents.
            you will get the idea of the new agent from clarify Agent.
            you will try to build the agent, and modify it if the response is not what user request till it achieve user request.
            you will change the prompt everytime if the result is not qualified.
            if finish is True, then dont generate Agent_Nmae, Agent_Scope, Agent_Prompt and Agent_Args!!.

            example on how to build the Agent:

                ```python
                def Agent_Name(self, args):
                    result = self.llm.invoke(f'''
                    here will be the prompt
                    and you should add these:

                        you will return only json format no ```json```.

                        ARGS: 
                    ''')

                    print(result.content)

                    try:
                        r = json.loads(result.content)

                        arg1 = r['arg1']
                        arg2 = r['arg2']

                    except Exception as e:
                        print(f'\\n\\nError: {{e}}\\n\\n)

                ```
            
            you will return only json format no ```json```.
            
            ARGS: 
                Agent_Name: you will return the new Agent Name.
                Agent_Scope: you will return what the agent about and what it do and what it can do it.
                Agent_Prompt: you will return prompt for the New Agent, new prompt or updating one.
                Agent_Args: you will return data that will be used to test for the new agent.

                Finish: you will return True if the New agent results are good!! (NOTE: if the counter is 0 you will return False; counter: {tries_count}).
                
                
                
            Data:
                idea: {idea}
                user request: {user_request}
                user notes: {user_notes}
                
            New Agent Result:
                {agent_history}


            
                """)

            try:
                r = json.loads(result.content)

                Finish = r['Finish']

                if 'TRUE' in str(Finish).upper():
                    
                    print(f"\n{'='*10}\n✅ Ready to deploy:\n📛 Name: {Agent_Name}\n🎯 Scope: {Agent_Scope}\n📜 Prompt: {Agent_Prompt}\n📊 Result: {agent_result}\n{'='*10}\n")
                    user_approval = input("✅ Satisfied with this result? (Y/n): ")

                    if 'y' in user_approval.lower():

                        print("✅ Loop will break!")
                        self.BuildAgent(Agent_Name, Agent_Scope, Agent_Prompt, agent_result, user_request)
                        break

                    user_note = input("🔧 What needs improvement? ")
                    user_notes += f'User Notes: {user_note}\n\nNew Agent Result: {agent_result}\n\n\n'


                Agent_Name = r['Agent_Name']
                Agent_Scope = r['Agent_Scope']
                Agent_Prompt = r['Agent_Prompt']
                Agent_Args = r['Agent_Args']

                print(f"🔄 Attempt #{tries_count + 1} | Agent: {Agent_Name}")

                agent_prompt = Agent_Prompt
                agent_result = self.Sandbox(Agent_Prompt, Agent_Args)

                print(f"📊 Output: {agent_result[:150]}...")

                agent_history += f"""
                - Attempt #{tries_count}
                Prompt Used: {agent_prompt}
                Result: {agent_result}\n\n"""

                tries_count += 1


            except Exception as e:
                print(f'\n\nError: {e}\n\n')


    def Sandbox(self, Agent_Prompt, Agent_Args):

        result = self.llm.invoke(f"""{Agent_Prompt}\n\nData: {Agent_Args}""")

        return result.content
                

    def ReadFile(self, file):
        with open(file, 'r') as f:
            return f.read()

    def BuildAgent(self, agent_name, agent_scope, agent_prompt, example_result, user_request):

        agent_result = ''
        user_notes = ''
        notes = ''

        while True:

            result = self.llm.invoke(f"""
            you will build a new agent based on below template as a reference.
            and you can modify, add more code or remove some for enhancment.
            the agent will be in standalone file, so you have to make it ready to use.
            the agent must have input.
            you will return only json format no ```json```.


            template:
                ```python
                    def Agent_Name(self, args):
                        result = self.llm.invoke(f'''
                        here will be the prompt
                        and you should add these:

                            you will return only json format no ```json```.

                            ARGS: 
                        ''')

                        try:
                            r = json.loads(result.content)

                            arg1 = r['arg1']
                            arg2 = r['arg2']

                        except Exception as e:
                            print(f'\\n\\nError: {{e}}\\n\\n)

                    ```


            more reference:
                START REFERENCE -> [{self.ReadFile('./main.py')}] <- END REFERENCE

            ARGS:
                python_code: you will return python code ready to use.
                response: you will return your response.
                input_for_test: you will return input to try/test the code.
                input_text: you will return what the text is used by input function.

            New Agent Data:
                Name: {agent_name}
                Scope: {agent_scope}
                Prompt: {agent_prompt}
                Example Result: {example_result}


            User Request: {user_request}


            Failed Builds:
                Notes: {notes}
                agent_result: {agent_result}

            
            """)

            try:
                r = json.loads(result.content)

                python_code = r['python_code']
                response = r['response']
                input_for_test = r['input_for_test']
                input_text = r['input_text']
                

                print(f"📝 Build Response: {response}")
                print(f"🧪 Test Input: {input_for_test}")

                print("✅ Build complete!")
                rate = self.RateAgentResult(python_code, input_for_test, user_request, agent_scope, example_result, agent_name, input_text)

                if rate['Break']:
                    break

                if 'FALSE' in rate['Remake'].upper():
                    self.SaveAgent(agent_name, python_code)
                    break

                notes = rate['Notes']
                agent_result = rate['agent_result']

                
            except Exception as e:
                print(f'\n\nError: {e}\n\n') 



    def RateAgentResult(self, Agent, test_input, user_request, agent_idea, example_result, agent_name, input_text): # this will be after BuildAgent to test and return response (result)

        agent_result = ''
        user_notes = ''

        agent_result = self.TestAgent(Agent, test_input, input_text)

        result = self.llm.invoke(f"""


        you will decide if the new agent result are good or not.
        you will analyze the new Agent code, Agent Result after run and test the agent, and user request.

        you will return only json format no ```json```.

        New Agent Code: 
            START CODE -> [{Agent}] <- END CODE
            Result (After running and testing the New Agent):
            START RESULT -> [{agent_result}] <- END RESULT

            what the result supposed to be ( this is only an example ):
                START EXAMPLE -> [{example_result}] <- END EXAMPLE



        ARGS:
            Rating: you will return rating from 10
            Response: you will return on what do you think of the result.
            Result_Quality: you will return what quality the result is.
            Instruct: is the result good as user request? if yes you will return True, otherwise False.
            Notes: you will return your notes here.
            Remake: should the agent remake the code ? True if yes the code and output result are bad, otherwise False.

        Needed Data:
            User Request: {user_request}
            New Agent Idea: {agent_idea}

        User Notes and Feedback:
            {user_notes}""")


        try:
            r = json.loads(result.content)

            Rating = r['Rating']
            Response = r['Response']
            Result_Quality = r['Result_Quality']
            Instruct = r['Instruct']
            Notes = r['Notes']
            Remake = r['Remake']

            if 'TRUE' in str(Remake).upper():
                return {"Remake": True, "Notes": Notes, "Agent_Result": agent_result, 'Break': False}


            inp = input("✅ Are you happy with this? (Y/n): ")
            if 'y' in inp.lower():
                self.SaveAgent(agent_name, Agent)
                return {'Break': True}
                
            else:
                inp = input("📝 What are your notes? ")
                return {"Remake": True, "Notes": inp, "Agent_Result": agent_result, 'Break': False}

            

        except Exception as e:
            print(f'Error: {e}')

        # self.SaveAgent()

        

    def TestAgent(self, Agent, test_input, input_text):

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(Agent)
            code_file = f.name

        try:

            venv_py = os.path.join("venv", "bin", "python3.12")
            site_packages = os.path.join("venv", "lib", "python3.12", "site-packages")

            env = os.environ.copy()
            env["PYTHONPATH"] = site_packages + os.pathsep + env.get("PYTHONPATH", "")

            result = subprocess.run(
                [venv_py, code_file],
                capture_output=True, text=True, input=f'{test_input}\n', env=env
            )

            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            exit_code = result.returncode


            result = f'Result: {stdout}\n\n\nstderr: {stderr}\n\n\nExit Code: {exit_code}'
            print(f"🧪 Test Agent Output:\n{result}")

            return result

        finally:
            os.unlink(code_file)




    def SaveAgent(self, Agent_Name, Agent_Code):

        with open(f'{Agent_Name}.py', 'w') as file:
            file.write(Agent_Code)

            print(f"\n✅ Agent '{Agent_Name}' saved successfully!\n")

    


if __name__ == "__main__":
    Agentic()
