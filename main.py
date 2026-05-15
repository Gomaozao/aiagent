import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from call_function import available_functions
from prompts import system_prompt


def main():
    parser = argparse.ArgumentParser(description="Process user input")
    parser.add_argument(
        "user_prompt",
        type=str,
        help="gives answer to whatever question the user gives to gemini",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError("Could not retrieve GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )

    if response.usage_metadata is None:
        raise RuntimeError("Failed Request to API")

    if response.function_calls is not None:
        for function_call in response.function_calls:
            print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print(f"{response.text}")

    # if args.verbose:
    #    print(f"{response.text}")
    #    print(f"User prompt: {args.user_prompt}")
    #    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    #    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    # else:
    #    print(f"{response.text}")


if __name__ == "__main__":
    main()
