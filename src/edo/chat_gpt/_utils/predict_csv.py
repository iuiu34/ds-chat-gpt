"""App config."""
import json
from importlib.resources import files

import fire
import pandas as pd
from edo.mkt.ml.llm import LlmBaseModel

from edo import chat_gpt


class LlmModel(LlmBaseModel):
    def __init__(self):
        package_path = files(chat_gpt)
        prompts_path = package_path.joinpath('model_configuration', 'prompts')
        filename = prompts_path.joinpath('system.tmpl')
        with open(filename) as f:
            system = f.read()

        filename = prompts_path.joinpath('prompt.tmpl')
        with open(filename) as f:
            prompt_template = f.read()

        super().__init__(
            system=system,
            prompt_template=prompt_template,
        )


def parse_string_to_dict(x):
    # input_str = input_str.replace("{", '')
    keys = ['bookingId', 'userId', 'userQuestion']
    out = x.replace(': ', '":"').replace(',', '","').replace('{', '{"').replace('}', '"}')
    out = json.loads(out)

    return out


def predict_csv(n=None):
    package_path = files(chat_gpt)
    filename = 'tmp/data.csv'
    data = pd.read_csv(filename, nrows=n)
    data['Message'] = data['Message'].apply(lambda x: x.split("---sepAiHomeQuestionSmokeTest")[1])
    data['Message'] = data['Message'].apply(lambda x: x.split("---")[0])
    # data['Message'] = data['Message'].apply(lambda x: x.replace("{", '{"').replace(": ", '": ').replace(", ", ', "').replace("}", '"}'))
    data['Message'] = data['Message'].apply(lambda x: parse_string_to_dict(x))

    data['userId'] = data['Message'].apply(lambda x: x.get('userId'))
    data['bookingId'] = data['Message'].apply(lambda x: x.get('bookingId'))
    data['userQuestion'] = data['Message'].apply(lambda x: x.get('userQuestion'))

    model = LlmModel()
    # model.predict(data)


def main():
    """Execute main program."""
    fire.Fire(predict_csv)
    print('\x1b[6;30;42m', 'Success!', '\x1b[0m')


if __name__ == "__main__":
    main()
