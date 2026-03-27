import os
import subprocess
from subprocess import PIPE

def run_python_file(working_directory, file_path, args=None):
    try:
        abs_working_dir = os.path.abspath(working_directory)
        abs_file_path = os.path.normpath(os.path.join(abs_working_dir, file_path))
        if os.path.commonpath([abs_working_dir, abs_file_path]) != abs_working_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(abs_file_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'
            
        command = ["python", abs_file_path]
        if not args==None:
            command.extend(args)
        result = subprocess.run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, timeout=30)
        
        if result.returncode != 0:
            return "Process exited with code X"
        elif result.stdout or result.stderr == None:
            return "No output produced"
        else:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
        #return result.text
    except Exception as e:
        return f"Error: executing Python file: {e}"
        