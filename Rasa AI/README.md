# RasaAI — No-LLM Local Prototype

RasaAI is a local casting-support prototype. This edition does **not** use an LLM, cloud AI API, API key, or remote inference service.

## What it does
- Accepts pasted screenplay text or a text-based screenplay PDF.
- Detects likely screenplay character cues from ALL-CAPS standalone lines and accepts manually entered character names.
- Searches for a small, explicit set of performance-related keywords and suggests audition exercises.
- Uploads an actor audition clip and uses OpenCV + MediaPipe to sample about one frame per second.
- Reports observable pose/movement measurements, timestamps, pose detection rate and a JSON export.

## Limitations
- Traditional rules do not understand a full story semantically. Character detection works best with screenplay-formatted text; prose stories may require manually entering character names.
- Keyword cues are screenplay-wide, not reliably character-specific. Verify every cue and audition requirement manually.
- Video features are approximate and affected by framing, camera angle, lighting, clothing and visibility. They are not validated measures of acting ability, emotion, personality or role suitability.
- No audio/dialogue analysis, face-expression classifier, automated actor ranking, OCR for scanned PDFs, or cloud integration is included.

## Requirements
- Windows 10/11, Python 3.11 recommended (Python 3.12 may work depending on available MediaPipe wheels).
- Internet only for initial installation/downloads. App processing is local after setup.

## Windows setup
Extract the ZIP, open PowerShell in the extracted folder, then run:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate the environment again.

## Suggested test
1. Paste a short screenplay with character cues on their own ALL-CAPS lines, e.g. `MAYA`, then dialogue beneath it.
2. Click **Parse screenplay with rules**.
3. Upload a short consented MP4 audition clip.
4. Click **Analyze visible movement locally**.
5. Review and download the JSON reports.

## Privacy
Uploaded text and video are processed in the local Streamlit process and are not intentionally sent to a cloud service by this application. Use only media you have permission to analyze. Keep human casting professionals responsible for casting decisions.
