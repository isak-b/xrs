class ChatBot:
    def __init__(self, client, cfg: dict):
        self.client = client
        self.chat_model = cfg["chat_model"]
        self.image_model = cfg["image_model"]
        self.tools = cfg["tools"]

    def chat(self, messages: list[dict]) -> dict | list:
        response = self.client.get_tool_calls(messages=messages, model=self.chat_model, tools=self.tools)
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls is None:
            return self.create_answer(messages=messages)

        output = []
        for tool_call in tool_calls:
            if tool_call.function.name == "create_answer":
                answer_output = self.create_answer(messages=messages)
                output.append(answer_output)
            elif tool_call.function.name == "create_image":
                img_output = self.create_image(messages=messages)
                output.append(img_output)
        return output[0] if len(output) == 1 else output

    def create_answer(self, messages: list[dict]) -> dict:
        try:
            response = self.client.create_answer(
                messages=messages,
                model=self.chat_model,
            )
            output = {"role": "assistant", "content": response.choices[0].message.content}
        except Exception as e:
            output = {"role": "error", "content": e}
        return output

    def create_image(self, messages: list[dict]) -> dict:
        prompt = ""
        for msg in messages:
            prompt += f"{msg['content']}\n"
        try:
            response = self.client.create_image(
                prompt=prompt,
                model=self.image_model,
            )
            revised_prompt = response.data[0].revised_prompt
            url = response.data[0].url
            output = {"role": "assistant", "content": revised_prompt, "url": url}
        except Exception as e:
            output = {"role": "error", "content": e}
        return output
