import os
import json
from collections import OrderedDict

class LoadPrompts:
    """
    A custom node to load prompts and pass them through.
    """

    def __init__(self):
        self.json_file = os.path.join(os.path.dirname(__file__), 'ai_prompts.json')

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (["append", "rewrite", "clear"], {"default": "append"}),
            },
            "optional": {
                "Que": ("STRING", {"forceInput": True, "multiline": True}),
                "Res": ("STRING", {"forceInput": True, "multiline": True}),
                "Neg": ("STRING", {"forceInput": True, "multiline": True}),
                "load_index": (("INT", {"default": 0, "min": 0})),
                "Positive": ("STRING", {"default": "", "multiline": True}),
                "Negative": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("Question", "Positive", "Negative")
    FUNCTION = "load_prompts"
    OUTPUT_NODE = False
    CATEGORY = "ArteMoon"

    def load_prompts(self, mode, Que="", Res="", Neg="",load_index=None, Positive="", Negative=""):
        if mode == "clear":
            self.clear_json()
            return ("", "", "")

        existing_data = self.load_json()

        if Que or Res or Neg:
            data = {
                "question": Que,
                "response": self.remove_duplicates(Positive + (',' if Positive and Res else '') + Res),
                "negative": self.remove_duplicates(Negative + (', ' if Negative and Neg else '') + Neg)
            }

            if mode == 'append':
                data['index'] = len(existing_data)
                existing_data.append(data)
            else: 
                data['index'] = 0
                existing_data = [data]

            self.save_json(existing_data)

        elif load_index is not None and 0 <= load_index < len(existing_data):
            data = existing_data[load_index]
            Que = data["question"]
            Res = data["response"]
            Neg = data["negative"]

        elif existing_data:
            data = existing_data[-1]
            Que = data["question"]
            Res = data["response"]
            Neg = data["negative"]

        else:
            Que = ""
            Res = ""
            Neg = ""

        Positive_output = self.remove_duplicates(f"{Positive},{Res}" if Positive else Res)
        Negative_output = self.remove_duplicates(f"{Negative}, {Neg}" if Negative else Neg)

        return (Que, Positive_output, Negative_output)

    def clear_json(self):
        with open(self.json_file, 'w') as f:
            json.dump([], f, indent=4)

    def load_json(self):
        if os.path.exists(self.json_file):
            with open(self.json_file) as f:
                return json.load(f)
        return []

    def save_json(self, data):
        with open(self.json_file, 'w') as f:
            json.dump(data, f, indent=4)

    def remove_duplicates(self, input_string):
        items = [item.strip() for item in input_string.replace(',', '.').split('.')]
        unique_items = list(OrderedDict.fromkeys(items))
        return ', '.join(unique_items)