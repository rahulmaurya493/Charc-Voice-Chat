import os

# requirements.txt
with open("character_chat/requirements.txt", "w") as f:
    f.write("""groq==0.9.0
streamlit==1.32.0
httpx==0.27.0
python-dotenv==1.0.1
""")

# .gitignore
with open("character_chat/.gitignore", "w") as f:
    f.write(""".env
__pycache__/
*.pyc
.DS_Store
""")

# .streamlit/config.toml
os.makedirs("character_chat/.streamlit", exist_ok=True)
with open("character_chat/.streamlit/config.toml", "w") as f:
    f.write("""[theme]
primaryColor = "#667eea"
backgroundColor = "#f7f8fc"
secondaryBackgroundColor = "#ffffff"
textColor = "#1a1a2e"
font = "sans serif"
""")

# README
with open("character_chat/README.md", "w") as f:
    f.write("""# 🎭 AI Character Chat
Chat with Iron Man, Spider-Man, Modi, SRK, Roman Reigns, Dhoni, Itachi, Madara, Gojo & Zenitsu!

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud
Add secret: `GROQ_API_KEY = "gsk_..."`
""")

print("✅ All deployment files created!")
print()
print("📁 Files to upload on GitHub:")
print("  ├── app.py")
print("  ├── characters.py")
print("  ├── requirements.txt")
print("  ├── .gitignore")
print("  ├── README.md")
print("  └── .streamlit/")
print("        └── config.toml")
