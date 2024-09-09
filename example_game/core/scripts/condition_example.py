def script_condition_example(event, *args, **kwargs):
    print(kwargs.get("test_param", "No test param"))
    return True