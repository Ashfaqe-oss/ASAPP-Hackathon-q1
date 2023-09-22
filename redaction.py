import zlib


def redactortext(text):
    map = {}
    

def replace():
    original_string = "I have an apple, a banana, and a cherry."

    replacements = {
        "apple": {"replacement": "fruit", "start": 7, "end": 11},
        "banana": {"replacement": "fruit", "start": 17, "end": 23},
        "cherry": {"replacement": "fruit", "start": 31, "end": 36},
    }

    sorted_replacements = sorted(replacements.items(), key=lambda x: x[1]['start'])

    result = ""
    current_position = 0

    for word, replacement_info in sorted_replacements:

        start_index = replacement_info["start"]
        end_index = replacement_info["end"]
        replacement = replacement_info["replacement"]

        result += original_string[current_position:start_index]
        result += replacement

        current_position = end_index + 1
    result += original_string[current_position:]

    print(result)
    return result

replace()
def generate_hash(input_string):

    input_bytes = input_string.encode('utf-8')
    crc32_checksum = zlib.crc32(input_bytes)
    
    if crc32_checksum < 0:
        crc32_checksum = crc32_checksum & 0xFFFFFFFF
    
    crc32_hex_string = hex(crc32_checksum)[2:]
    return crc32_hex_string