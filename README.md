# 100% Free Automated Daily YouTube Shorts Setup & Monetization Blueprint (US Audience)

Yeh guide aapko step-by-step batati hai ki kaise aap `youtube_shorts_auto_bot.py` ko **[GitHub Actions Scheduled Workflows](https://www.google.com/search?q=https%3A%2F%2Fdocs.github.com%2Fen%2Factions%2Freference%2Fworkflows-and-actions%2Fevents-that-trigger-workflows)** par **100% Free (₹0 kharch)** chala sakte hain — bina apna computer ya phone on rakhe.

## 1. Yeh Automation Bot Roz Kya Karta Hai?

| Stage | Module Name | Free Tool / API Used | Kaam Kya Hota Hai? |
| :--- | :--- | :--- | :--- |
| **Step 1** | **Viral Diagnostics Engine** | [YouTube Data API v3](https://www.google.com/search?q=https%3A%2F%2Fdevelopers.google.com%2Fyoutube%2Fv3%2Fdocs) | Aapke pichle 10 Shorts ke views, like ratio (`<3.5%` warning), aur comment rate (`<0.15%` warning) check karta hai aur diagnose karta hai ki video viral kyun nahi hua. |
| **Step 2** | **Daily US Niche & Script AI** | [Google AI Studio (Gemini API)](https://www.google.com/search?q=https%3A%2F%2Fai.google.dev%2Fgemini-api%2Fdocs%2Fapi-key) + US Google Trends RSS | Roz US trends check karke 4 high-RPM family-friendly niches (*3D What If Science*, *Animal Superpowers*, *Interactive Riddles*, *Human Body Facts*) mein se best topic chunta hai aur pichle video ki kamiyon ko sudhar kar 50-second ki 6-scene script likhta hai. |
| **Step 3** | **Free US Neural Voiceover** | [edge-tts (PyPI)](https://www.google.com/search?q=https%3A%2F%2Fpypi.org%2Fproject%2Fedge-tts%2F) | Microsoft Edge ke free US English neural voices (`en-US-ChristopherNeural` / `en-US-AriaNeural`) se crystal-clear American accent voiceover banata hai. |
| **Step 4** | **Free 3D Pixar-Style Visuals** | [Pollinations.ai API](https://www.google.com/search?q=https%3A%2F%2Fgen.pollinations.ai%2Fdocs) (`1080x1920`) | Har scene ke liye vibrant 3D animated vertical (`9:16`) visuals bina kisi API key ya paise ke generate karta hai. |
| **Step 5** | **Auto Video Editing & Captions** | [MoviePy 1.0.3](https://www.google.com/search?q=https%3A%2F%2Fpypi.org%2Fproject%2Fmoviepy%2F1.0.3%2F) + Pillow + FFmpeg | Har scene par smooth **Ken Burns Zoom-In (`1.0x -> 1.12x`)**, upar yellow curiosity badge, aur screen ke beech mein bold pop-up captions lagata hai. |
| **Step 6** | **US Peak-Time Auto Upload** | [YouTube Data API v3 Upload Guide](https://www.google.com/search?q=https%3A%2F%2Fdevelopers.google.com%2Fyoutube%2Fv3%2Fguides%2Fuploading_a_video) | Roz shaam **3:30 PM US Eastern Time (1:00 AM IST)** par video upload karta hai, `selfDeclaredMadeForKids=False` set rakhta hai taaki US views par full ad revenue mile. |

## 2. 15-Minute Free Setup Steps (Bina Paisa Lagaye)

### Step A: Free Gemini API Key Lein (₹0)
1. Apne Google account se **[Google AI Studio API Keys](https://www.google.com/search?q=https%3A%2F%2Faistudio.google.com%2Fapikey)** page par jayein.
2. **Create API Key** par click karein aur key copy kar lein (`GEMINI_API_KEY`). Free tier mein roz ke kai saare scripts bilkul muft bante hain.

### Step B: YouTube Data API v3 OAuth Credentials Lein (₹0)
1. **[YouTube Data API Registration Guide](https://www.google.com/search?q=https%3A%2F%2Fdevelopers.google.com%2Fyoutube%2Fregistering_an_application)** ke mutabiq Google Cloud Console mein ek naya project banayein aur **YouTube Data API v3** enable karein.
2. **OAuth Consent Screen** mein apna YouTube email *Test Users* mein add karein aur **Credentials -> Create OAuth Client ID (Web application)** banayein.
3. *Authorized redirect URI* mein `https://developers.google.com/oauthplayground` daalein aur apna `YT_CLIENT_ID` aur `YT_CLIENT_SECRET` copy kar lein.
4. OAuth 2.0 Playground par jaakar gear icon (Settings) mein *Use your own OAuth credentials* tick karein, `https://www.googleapis.com/auth/youtube.upload` aur `https://www.googleapis.com/auth/youtube.readonly` scopes select karke authorize karein, aur **Exchange authorization code for tokens** daba kar apna `YT_REFRESH_TOKEN` copy kar lein.

### Step C: GitHub Actions Par Free Cloud Server Chalu Karein (₹0)
1. GitHub par ek naya **Private या Public Repository** banayein.
2. Apne computer ya GitHub codespace mein `python3 youtube_shorts_auto_bot.py --init-ci` chalayein (ya `youtube_shorts_auto_bot.py` ko repo mein upload karein). Yeh command apne-aap `requirements.txt` aur `.github/workflows/daily_shorts.yml` bana degi.
3. Apne GitHub Repository ke **Settings -> Secrets and variables -> Actions -> New repository secret** mein yeh 4 secrets save karein:
   * `GEMINI_API_KEY`
   * `YT_CLIENT_ID`
   * `YT_CLIENT_SECRET`
   * `YT_REFRESH_TOKEN`
4. **Actions** tab mein jaakar workflow ko enable karein aur **Run workflow** (`workflow_dispatch`) daba kar pehla test Short abhi turant generate aur upload karein!

## 3. Viral Diagnostics & Tez Monetization Strategy

**[YouTube Partner Program (YPP)](https://support.google.com/youtube/answer/72851?hl=en&co=GENIE.Platform%3DAndroid)** ke mutabiq Shorts channel monetize karne ke liye **1,000 Subscribers + 90 din mein 10 Million Public Shorts Views** (aur **[Expanded YPP Early Access](https://support.google.com/youtube/answer/13429240?hl=en&co=GENIE.Platform%3DAndroid)** ke liye 500 Subscribers + 3 Million Shorts views) chahiye hote hain.

Hamara bot har roz upload se pehle `viral_diagnostics_log.json` banata hai aur 4 mukhya wajahon ko check karke agli video mein khud sudhar karta hai:

* **Swipe-Away Rate Fix (0–3s Hook):** Agar pichle videos ke average views `<1,500` par ruk rahe hain, toh iska matlab viewers pehle 3 second mein swipe kar rahe hain. Bot agli script ke Scene 1 mein extreme visual contrast सवाल (*"What would happen if..."*, *"Never touch this..."*) aur top yellow badge lagata hai.
* **Like-to-View Ratio Fix (`>4%` Target):** Agar Like rate `3.5%` se kam hai, toh bot 15-second mark par ek mini-twist add karta hai.
* **Comment Velocity Fix (`>0.15%` Target):** Shorts algorithm comments se video ko 100K+ seed pool mein bhejta hai. Bot har video ke **Scene 4** mein ek asaan सवाल poochta hai (*"What would you pick? Tell me in the comments!"*) jisse bache aur US viewers turant comment karte hain.
* **100%+ Retention Loop:** Scene 6 ki aakhri line Scene 1 ki pehli line se judti hai (*"...which is why scientists still ask -> What would actually happen if..."*), jisse viewer ko pata hi nahi chalta ki video kab khatam hokar dobara shuru ho gaya!
