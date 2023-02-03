import json


def load_rules(path):
    with open(path, "r") as fp:
        return json.load(fp)


if __name__ == "__main__":
    pass
