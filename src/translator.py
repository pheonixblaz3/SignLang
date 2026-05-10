class Translator:
    def __init__(self):
        self.text = []

    def add_sign(self, sign):
        if sign and sign != 'Unknown':
            self.text.append(sign)

    def get_text(self):
        return ''.join(self.text)

    def clear(self):
        self.text = []

    def save_to_file(self, filename='decoded_text.txt'):
        with open(filename, 'w') as f:
            f.write(self.get_text())