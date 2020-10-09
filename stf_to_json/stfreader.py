import io
import numpy as np
import json
from os import walk, path, chdir
from pathlib import Path

class STFReader:
    def __init__(self):
        self.buffer = None
        self.value_array = {}
        self.key_array = {}
        self.char = ""

    def read_byte(self, num_bytes):
        buffer = self.buffer.read(num_bytes)

        dt = np.dtype(np.int32)
        dt = dt.newbyteorder('<')
        bytes = np.frombuffer(buffer, dtype=dt)
        return bytes

    def read_stf(self, file_data):

        self.buffer = io.BytesIO(file_data)

        self.buffer.read(9)
        row_count = self.read_byte(4)
        rows = []

        for i in range(row_count[0]):
            row_number = self.read_byte(4)
            self.read_byte(4)
            character_count = self.read_byte(4)

            for i in range(character_count[0]):
                character = chr(self.buffer.read(2)[0])
                self.char = self.char + character

            self.value_array[row_number[0]] = self.char
            self.char = ""
            rows.append(row_number)

        for i in range(row_count[0]):
            row_number = self.read_byte(4)
            character_count = self.read_byte(4)

            for i in range(character_count[0]):
                character = chr(self.buffer.read(1)[0])
                self.char = self.char + character

            self.key_array[row_number[0]] = self.char
            self.char = ""

        data = {}
        for i in rows:
            value = ""
            key = self.key_array[i[0]]
            value = self.value_array[i[0]]
            data[i[0]] = [key, value]

        return data

for root, _, filenames in walk('string'):
    for filename in filenames:
        reader = STFReader()
        filesize = path.getsize(path.join(root, filename))
        if filesize == 0:
            continue
        with open(path.join(root, filename), 'rb') as f:
            contents = f.read()
            data = reader.read_stf(contents)

        outpath = path.join(root, filename)[:-4]
        Path(path.join('json_out', root)).mkdir(parents=True, exist_ok=True)

        with open(path.join('json_out', outpath) + '.json', 'a') as f:
            f.write('{\n\t"stfFile":"' + outpath[10:] + '",\n\t"entries": {\n\t\t')
            i = 0
            size = len(data)
            for key in data.keys():
                k = data[key][0]
                v = data[key][1].replace('\n', ' ').replace('"', '\\"').replace('\\#', '').replace('', '')
                if v.__contains__('ATTRIBUTES\\'):
                    v = v.split('ATTRIBUTES\\')[0] + ' **NOTICE**: TRUNCATED ATTRIBUTES LIST DUE TO FORMATTING.'
                if i == (size - 1):
                    f.write('"' + k + '":"' + v + '"')
                else:
                    f.write('"' + k + '":"' + v + '",\t')
                i = i + 1
            f.write('\n}}')