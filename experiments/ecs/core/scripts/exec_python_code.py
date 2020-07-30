def script_exec_python_code(event=None, *args, **kwargs):

    # Get the body of the script from the arguments
    script_body = kwargs.get("script_body", '')

    # Execute the script
    exec(script_body)

    # Return success
    return 0
