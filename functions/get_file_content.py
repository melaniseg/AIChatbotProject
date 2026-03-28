import os
from config import *
from google.genai import types

def get_file_content(working_directory, file_path):
    try:
       working_dir_abs =  os.path.abspath(working_directory)
       abs_filepath = os.path.normpath(os.path.join(working_dir_abs, file_path))
       valid_path = os.path.commonpath([working_dir_abs, abs_filepath]) == working_dir_abs
       #print(f"this is the abs filepath : {abs_filepath}")
       if not valid_path:
           print(f'Error: Cannot read "{file_path}" as it is outside the permitted working directory')
           
       if not os.path.isfile(abs_filepath):
           print(f'Error: File not found or is not a regular file: "{file_path}"')
       else:
           with open(abs_filepath, 'r') as f:
               content = f.read(MAX_CHARS)
               print(f"length: {len(content)}")
       # After reading the first MAX_CHARS...
               if f.read(1):
                   content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
                   #print(content[-60:])
           return content

    except Exception as e:
        print(f"Error: {e}")
        
        
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Prints out the contents of the file after truncation at MAX_CHARS",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file whose content should be read, relative to the working directory",
            ),
        },
        required = ["file_path"]
    ),
)