import json


def extract_unicode_strokes(text):
    stroke_dict = {}
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) >= 3 and parts[1] == 'kTotalStrokes':
            unicode_char = parts[0]
            strokes = parts[2]
            stroke_dict[unicode_char] = strokes
    return stroke_dict


with open("Unihan_IRGSources.txt", "r", encoding="utf-8") as f:
    text = f.read()

    # result =
with open("unicode_Strokes_data.txt", "w", encoding="utf-8") as f:
    json.dump(extract_unicode_strokes(text), f)