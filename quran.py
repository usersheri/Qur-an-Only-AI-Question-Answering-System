arabic = {}
with open("quran-uthmani.txt", encoding="utf-8") as f:
    for line in f:
        s, a, text = line.strip().split("|")
        arabic[(int(s), int(a))] = text

english = {}
with open("en.sahih.txt", encoding="utf-8") as f:
    for line in f:
        s, a, text = line.strip().split("|")
        english[(int(s), int(a))] = text

quran = []
for key in arabic:
    quran.append({
        "surah": key[0],
        "ayah": key[1],
        "arabic": arabic[key],
        "english": english.get(key, "")
    })
