# Pick sheet: drop-in values

Sheet: https://uzandigitalofficial.github.io/ace-reels/picks/

Nothing in brands/stolenvalour.json has been changed. To use a pick, paste its value over the matching key.

## Voices: set as "tts" in brands/stolenvalour.json

V1 to V4 use engine "edge", which is NOT registered in render/render5.py yet. The function is ready in render/voice/eng_edge.py. To switch it on, add `from voice.eng_edge import eng_edge` and `ENGINES["edge"] = eng_edge` in render5.py (a one-line change, left for the session that owns render5.py). V5 and V6 work as they are today. Edge voices need internet from the runner (they call Microsoft's free service; not tested from a GitHub runner).

### V1: Microsoft Ava Multilingual (16.0 s, -16.1 LUFS)
American, warm and natural. Our top pick for a real, human feel.
```json
"tts": {"engine": "edge", "voice": "en-US-AvaMultilingualNeural", "rate": "-4%"}
```

### V2: Microsoft Emma Multilingual (16.7 s, -16.0 LUFS)
American, bright and chatty. A little younger and quicker.
```json
"tts": {"engine": "edge", "voice": "en-US-EmmaMultilingualNeural", "rate": "-4%"}
```

### V3: Microsoft Sonia (17.3 s, -16.0 LUFS)
British, polished and calm. Premium and measured.
```json
"tts": {"engine": "edge", "voice": "en-GB-SoniaNeural", "rate": "-4%"}
```

### V4: Microsoft Leah (18.9 s, -16.0 LUFS)
South African English. Sounds local to your dealers.
```json
"tts": {"engine": "edge", "voice": "en-ZA-LeahNeural", "rate": "-4%"}
```

### V5: Kokoro, Heart (15.8 s, -16.1 LUFS)
American, smooth and clean. Works today, no key and no extra setup.
```json
"tts": {"engine": "kokoro", "voice": "af_heart", "lang": "a"}
```

### V6: Chatterbox, calm settings (12.3 s, -16.1 LUFS)
The voice the reels use now, tuned steadier and less sing-song.
```json
"tts": {"engine": "chatterbox", "chatterbox": {"exaggeration": 0.4, "cfg_weight": 0.5, "temperature": 0.7, "seed": 7}}
```

## Music: set as "music" in brands/stolenvalour.json

The list holds full mp3 URLs; render5.py picks one per slot. A one-track list pins that track. All six are Kevin MacLeod, CC-BY 4.0: commercial use is free, but the credit line must go in the post caption.

All six at once:
```json
"music": [
 "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Gymnopedie%20No%201.mp3",
 "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Sincerely.mp3",
 "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Lightless%20Dawn.mp3",
 "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Windswept.mp3",
 "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Fresh%20Air.mp3",
 "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Perspectives.mp3"
]
```

### M1: Gymnopedie No 1
Satie's soft solo piano. Calm, elegant, about one note a second.
```json
"music": ["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Gymnopedie%20No%201.mp3"]
```
Caption credit: "Gymnopedie No 1" Kevin MacLeod (incompetech.com). Licensed under Creative Commons: By Attribution 4.0 License. http://creativecommons.org/licenses/by/4.0/

### M2: Sincerely
Slow, warm and low. Almost nothing in the voice range.
```json
"music": ["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Sincerely.mp3"]
```
Caption credit: "Sincerely" Kevin MacLeod (incompetech.com). Licensed under Creative Commons: By Attribution 4.0 License. http://creativecommons.org/licenses/by/4.0/

### M3: Lightless Dawn
Very slow ambient piano and texture. Reflective.
```json
"music": ["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Lightless%20Dawn.mp3"]
```
Caption credit: "Lightless Dawn" Kevin MacLeod (incompetech.com). Licensed under Creative Commons: By Attribution 4.0 License. http://creativecommons.org/licenses/by/4.0/

### M4: Windswept
Airy, even ambient bed. Very steady level.
```json
"music": ["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Windswept.mp3"]
```
Caption credit: "Windswept" Kevin MacLeod (incompetech.com). Licensed under Creative Commons: By Attribution 4.0 License. http://creativecommons.org/licenses/by/4.0/

### M5: Fresh Air
The sparsest bed: long soft tones, hardly any attacks.
```json
"music": ["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Fresh%20Air.mp3"]
```
Caption credit: "Fresh Air" Kevin MacLeod (incompetech.com). Licensed under Creative Commons: By Attribution 4.0 License. http://creativecommons.org/licenses/by/4.0/

### M6: Perspectives
Gentle and even, a little more motion. Keeps a reel moving.
```json
"music": ["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Perspectives.mp3"]
```
Caption credit: "Perspectives" Kevin MacLeod (incompetech.com). Licensed under Creative Commons: By Attribution 4.0 License. http://creativecommons.org/licenses/by/4.0/
