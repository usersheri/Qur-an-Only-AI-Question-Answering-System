import json

ARABIC_FILE = "data/quran-uthmani.txt"
ENGLISH_FILE = "data/en.sahih.txt"
OUTPUT_FILE = "data/quran.py"

arabic = {}
english = {}

# Load Arabic
with open(ARABIC_FILE, encoding="utf-8") as f:
    for line in f:
        surah, ayah, text = line.strip().split("|", 2)
        arabic[(int(surah), int(ayah))] = text

# Load English
with open(ENGLISH_FILE, encoding="utf-8") as f:
    for line in f:
        surah, ayah, text = line.strip().split("|", 2)
        english[(int(surah), int(ayah))] = text

# Merge
quran = []
for key in sorted(arabic.keys()):
    if key not in english:
        raise ValueError(f"Missing English translation for {key}")

    quran.append({
        "surah": key[0],
        "ayah": key[1],
        "arabic": arabic[key],
        "english": english[key]
    })

# Final sanity check
if len(quran) != 6236:
    raise ValueError(f"Expected 6236 ayahs, got {len(quran)}")

# Write JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(quran, f, ensure_ascii=False, indent=2)

print("✅ quran.json created successfully with 6236 ayahs")
