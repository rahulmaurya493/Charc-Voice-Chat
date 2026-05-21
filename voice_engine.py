import io
from gtts import gTTS

VOICE_CONFIG = {
    "Tony Stark":        {"lang": "en", "tld": "com",    "slow": False},
    "Spider-Man":        {"lang": "en", "tld": "com",    "slow": False},
    "Narendra Modi":     {"lang": "en", "tld": "co.in",  "slow": True},
    "Shah Rukh Khan":    {"lang": "en", "tld": "co.in",  "slow": False},
    "Roman Reigns":      {"lang": "en", "tld": "com",    "slow": True},
    "MS Dhoni":          {"lang": "en", "tld": "co.in",  "slow": True},
    "Itachi Uchiha":     {"lang": "en", "tld": "co.uk",  "slow": True},
    "Madara Uchiha":     {"lang": "en", "tld": "co.uk",  "slow": True},
    "Gojo Satoru":       {"lang": "en", "tld": "com.au", "slow": False},
    "Zenitsu Agatsuma":  {"lang": "en", "tld": "com",    "slow": False},
}

def text_to_speech(text: str, character_name: str) -> bytes:
    config = VOICE_CONFIG.get(character_name, {"lang": "en", "tld": "com", "slow": False})
    clean  = text.replace("*", "").replace("#", "").replace("`", "").replace("_", "")
    clean  = " ".join(clean.split())
    tts    = gTTS(text=clean, lang=config["lang"], tld=config["tld"], slow=config["slow"])
    buf    = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()
