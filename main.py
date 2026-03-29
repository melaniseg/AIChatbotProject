import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from functions.call_function import available_functions, call_function

def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    #verbose = "--verbose" in sys.argv
    if not api_key:
       raise RuntimeError("API Key cannot be found")
    client = genai.Client(api_key=api_key)
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    response = client.models.generate_content(model='gemini-2.5-flash', 
    contents=messages, config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),)
    if response.usage_metadata is None:
       raise RuntimeError("Failed API request")
    if args.verbose:
       print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
       print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
       print(f"User prompt: {args.user_prompt}")
    #print(response.text)
    #print(f"Calling function: {response.function_calls.name}({response.function_calls.args})")
    if response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call
        function_call_result = call_function(function_call)
        if function_call_result.parts == []:
            raise Exception("Function call parts list is empty")
        if function_call_result.parts[0].function_response == None:
            raise Exception("Function Call has no FunctionResponse")
        if function_call_result.parts[0].function_response.response == None:
            raise Exception("No function result detected")
        print(f"-> {function_call_result.parts[0].function_response.response}")
        #print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print(response.text)
    
    generate_content_loop(client, messages, args.verbose)
    


def generate_content_loop(client, messages, verbose, max_iterations=20):
    for iteration in range(max_iterations):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], system_instruction=system_prompt
                ),
            )
            if verbose:
                print("Prompt tokens:", response.usage_metadata.prompt_token_count)
                print("Response tokens:", response.usage_metadata.candidates_token_count)

            # Add model response to conversation
            if response.candidates:
                for candidate in response.candidates:
                    if candidate.content:
                        messages.append(candidate.content)

            # Check if we have a final text response
            if response.text:
                print("Final response:")
                print(response.text)
                break

            # Handle function calls
            if response.function_calls:
                function_responses = []
                for function_call_part in response.function_calls:
                    function_call_result = call_function(function_call_part, verbose)
                    if (
                        not function_call_result.parts
                        or not function_call_result.parts[0].function_response
                    ):
                        raise Exception("empty function call result")
                    if verbose:
                        print(f"-> {function_call_result.parts[0].function_response.response}")
                    function_responses.append(function_call_result.parts[0])
                if function_responses:
                    messages.append(types.Content(role="user", parts=function_responses))
                else:
                    raise Exception("no function responses generated, exiting.")
        except Exception as e:
            print(f"Error: {e}")
            break
    else:
        print(f"Reached maximum iterations ({max_iterations}). Agent may not have completed the task.")

if __name__ == "__main__":
    main()

