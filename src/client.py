from openai import OpenAI


def check_client(client):
    if client is None:
        raise ValueError("Client is None.")
    try:
        _ = client.create_completion(model="davinci-002", prompt="This is a test.", max_tokens=5)
    except Exception as e:
        raise e
    return True


def get_client(api_type: str, api_key: str):
    client = None
    if api_type.lower() == "openai":
        client = OpenAI(api_key=api_key)
        client.query = client.chat.completions.create
        client.create_text = client.chat.completions.create
        client.create_image = client.images.generate
        client.create_completion = client.completions.create
    else:
        raise ValueError(f"{api_type=} is not supported.")
    return client
