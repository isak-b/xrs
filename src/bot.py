from copy import deepcopy
import json


class ChatBot:
    def __init__(self, client, cfg: dict):
        self.client = client
        self.models = cfg["models"]
        self.tools = cfg["tools"]

    def chat(self, messages: list[dict], history_size: int = 10) -> list[dict]:
        chat_messages = deepcopy(messages) if history_size is None else deepcopy(messages)[-history_size:]
        output = []
        try:
            response = self.client.query(messages=chat_messages, model=self.models["chat"], tools=self.tools)
            tool_calls = response.choices[0].message.tool_calls
            if tool_calls is None:
                return [self.text(messages=messages)]

            for tool_call in tool_calls:
                call_messages = deepcopy(messages)
                func = self.__getattribute__(tool_call.function.name)
                revised_prompt = json.loads(tool_call.function.arguments).get("revised_prompt")
                if revised_prompt is not None:
                    call_messages = call_messages[:-1] + [{"role": "user", "content": revised_prompt}]
                output.append(func(messages=call_messages))
        except Exception as e:
            output.append({"role": "system", "content": e})
        return output

    def text(self, messages: list[dict], history_size: int = 10) -> dict:
        text_messages = deepcopy(messages) if history_size is None else deepcopy(messages)[-history_size:]
        try:
            response = self.client.create_text(
                messages=text_messages,
                model=self.models["text"],
            )
            answer = response.choices[0].message.content
            output = {"role": "assistant", "content": answer}
        except Exception as e:
            output = {"role": "system", "content": e}
        return output

    def image(self, messages: list[dict], history_size: int = 3) -> dict:
        image_messages = deepcopy(messages) if history_size is None else deepcopy(messages)[-history_size:]
        prompt = ""
        for msg in image_messages:
            prompt += f"{msg['role']}: {msg['content']}\n\n"
        try:
            response = self.client.create_image(
                prompt=prompt,
                model=self.models["image"],
            )
            revised_prompt = response.data[0].revised_prompt
            url = response.data[0].url
            output = {"role": "assistant", "content": revised_prompt, "url": url}
        except Exception as e:
            output = {"role": "system", "content": e}
        return output
