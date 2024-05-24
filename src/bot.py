from copy import deepcopy
import json


class ChatBot:
    def __init__(self, client, cfg: dict):
        self.client = client
        self.tool_caller = cfg["tool_caller"]
        self.text = cfg["text"]
        self.image = cfg["image"]
        self.tools = cfg["tools"]

    def chat(self, messages, **kwargs) -> list[dict]:
        if self.text["active"] is True and self.image["active"] is True:
            return self.call_tools(messages, **kwargs)
        elif self.text["active"] is True:
            return [self.create_text(messages, **kwargs)]
        elif self.image["active"] is True:
            return [self.create_image(messages, **kwargs)]
        else:
            return [{"role": "assistant", "content": "Please select a tool"}]

    def call_tools(self, messages: list[dict], history_size: int = 10) -> list[dict]:
        output = []
        chat_messages = deepcopy(messages) if history_size is None else deepcopy(messages)[-history_size:]
        try:
            response = self.client.create_text(messages=chat_messages, model=self.tool_caller, tools=self.tools)
            tool_calls = response.choices[0].message.tool_calls
            if tool_calls is None:
                return [self.create_text(messages=messages)]

            for tool_call in tool_calls:
                call_messages = deepcopy(messages)
                func = self.__getattribute__(tool_call.function.name)
                revised_prompt = json.loads(tool_call.function.arguments).get("revised_prompt")
                if revised_prompt is not None:
                    call_messages = call_messages[:-1] + [{"role": "user", "content": revised_prompt}]
                output.append(func(messages=call_messages))
        except Exception as e:
            output.append({"role": "assistant", "content": e})
        return output

    def create_text(self, messages: list[dict], history_size: int = 10) -> dict:
        text_messages = deepcopy(messages) if history_size is None else deepcopy(messages)[-history_size:]
        try:
            response = self.client.create_text(
                messages=text_messages,
                model=self.text["model"],
            )
            answer = response.choices[0].message.content
            output = {"role": "assistant", "content": answer}
        except Exception as e:
            output = {"role": "system", "content": e}
        return output

    def create_image(self, messages: list[dict], history_size: int = 10) -> dict:
        image_messages = deepcopy(messages) if history_size is None else deepcopy(messages)[-history_size:]
        prompt = ""
        for msg in image_messages:
            prompt += f"{msg['role']}: {msg['content']}\n\n"
        try:
            response = self.client.create_image(
                prompt=prompt,
                model=self.image["model"],
            )
            revised_prompt = response.data[0].revised_prompt
            url = response.data[0].url
            output = {"role": "assistant", "content": revised_prompt, "url": url}
        except Exception as e:
            output = {"role": "system", "content": e}
        return output
