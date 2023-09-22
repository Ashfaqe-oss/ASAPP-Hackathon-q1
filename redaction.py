import zlib

def redactortext(text,rep):
    map = {}
    hash = []
    for e in rep:
        hash.append([e,generate_hash(e)])
        map[generate_hash(e)] = e
    print(hash)
    return replace_entities(text,map,hash,rep)

def replace_entities(input_str,map, entity_hash_pairs,rep):
    entity_hash_pairs = sorted(entity_hash_pairs,reverse=True)
    for entity, hash_value in entity_hash_pairs:
        input_str = input_str.replace(entity, f"{rep[entity]['entity_type']}[{hash_value}]")
    return {
        "str" : input_str,
        "map" : map
    }

def generate_hash(input_string):
    input_bytes = input_string.encode('utf-8')
    crc32_checksum = zlib.crc32(input_bytes)
    if crc32_checksum < 0:
        crc32_checksum = crc32_checksum & 0xFFFFFFFF
    crc32_hex_string = hex(crc32_checksum)[2:]
    return crc32_hex_string