<!-- drop your logo here -->
<br />

<div align="center"><a href="#top"></a>

<img src="https://i.postimg.cc/GmXvDNNs/raw-removebg-preview.png" alt="Logo" width="300" height="300">

<h1 align="center">Hearo</h1>

<h3 align="center">YOUR MEETING ASSISTANT</h3>

<p align="center">
Meet <b>Hearo</b> - a real-time meeting companion that transcribes speech with Whisper (via <i>faster-whisper</i>), streams smart keywords alongside your call, and turns each tap into instant answers. Click any keyword to get a bite‑size summary, the newest relevant image, and up‑to‑the‑minute news - all without leaving your meeting.
</p>
</div>

<!-- ToC: please don't edit/remove this block unless you know what you're doing -->
<details>
<summary>Table of Contents</summary>

- [ℹ Project Information](#ℹ-project-information)
  - [👨‍💻 Members](#-members)
  - [🔧 Tech Stack](#-tech-stack)
- [⚙ Installation](#-installation)
  - [📦 Prerequisites](#-prerequisites)
  - [▶️ Run with terminal](#️-run-with-terminal)
  - [📷 How to Use](#-how-to-use)
  - [🔒 Security & Privacy](#-security--privacy)
- [🖥️ Features and Interfaces](#️-features-and-interfaces)
  - [Live Transcription](#live-transcription)
  - [Smart Keywords Overlay](#smart-keywords-overlay)
  - [AI Information Panel](#ai-information-panel)
  - [Click-to-Search](#click-to-search)
- [🚀 Roadmap & Future Work](#-roadmap--future-work)
- [📝 Notes](#-notes)
</details>

---

## ℹ Project Information
<b>Hearo</b> is a real-time note‑taking and information‑lookup assistant for online meetings and classes. It helps solve the problem of <i>information overload</i> and <i>missing important points</i> while you are listening, note‑taking, and searching — all at once.

Hearo captures system audio (Zoom, Google Meet, YouTube, etc.), converts speech to text using Whisper, extracts important keywords with NLP, and shows those keywords on a floating UI so you can follow the main ideas without manual note‑taking. When you click a keyword, Hearo returns a short summary, the latest image, and related news — instantly.

---

### 👨‍💻 Members
Project by team <b>Free Five</b> 🆓5️⃣:
* Tran Xuan Bao - [23020332](mailto:tranxuanbaohtka@gmail.com)
* Nguyen Hoang Tu - [23020428](mailto:nongvandenhoc@gmail.com)
* Bui Thanh Dan - [23020342](mailto:btdan.yamm@gmail.com)
* Nguyen Duy Hai Bang - [23020335](mailto:totenhaibang@gmail.com)
* Le Vu Hieu - [23020365](mailto:levuhieu2k5@gmail.com)

---

### 🔧 Tech Stack

<p align="left">
<a href="https://www.python.org/" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/></a>
<a href="https://www.qt.io/qt-for-python" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/qt/qt-original.svg" alt="pyqt6" width="40" height="40"/></a>
<a href="https://github.com/guillaumekln/faster-whisper" target="_blank"><img src="https://avatars.githubusercontent.com/u/1335026?s=200&v=4" alt="faster-whisper" width="40" height="40"/></a>
<a href="https://github.com/bastibe/SoundCard" target="_blank"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/windows8/windows8-original.svg" alt="soundcard" width="40" height="40"/></a>
</p>

| Component                 | Technologies / Notes                                                                   |
|--------------------------|-----------------------------------------------------------------------------------------|
| UI/Overlay               | PyQt6 floating panel (glassmorphism‑style)                                             |
| Speech-to-Text           | OpenAI Whisper (via <code>faster-whisper</code>)                                       |
| NLP for Keywords         | spaCy (noun chunks & proper nouns)                                                     |
| Audio Capture            | <code>soundcard</code> (system loopback)                                               |
| Search Providers         | Images / definitions / news via external APIs             |

(<a href="#top">back to top</a>)

---
## ⚙ Installation

### 📦 Prerequisites

* Python 3.11+

* `ffmpeg` (recommended for audio/Whisper)

* Permission for system audio loopback recording (if you capture system sound)

* (Optional) Git for faster source download

### ▶️ Run with terminal

```
# Install git if you don't have it
git clone https://github.com/its6ueq/Hearo.git Hearo
cd Hearo
```

```
pip install --upgrade pip
pip install -r requirements.txt
```

```
python -m Hearo.main 
```
### 📷 How to Use

<video width="640" height="360" controls>
    <source src="https://www.dropbox.com/scl/fi/awkoc36b8ci5muh4tpwbr/demo_video-Made-with-Clipchamp.mp4?rlkey=3aeb8ccd3f4bigd6tm97ey31x&st=62mtyels&raw=1" type="video/mp4">
    Trình duyệt không hỗ trợ video.
  </video>

### 🔒 Security & Privacy
- STT and keyword extraction are processed locally with Whisper & spaCy.  
- Lookups for images/news may call external APIs: please review and accept the <i>privacy policy</i> before enabling.  
- Options to limit/hide sensitive content; do not store audio unless explicitly allowed.

(<a href="#top">back to top</a>)

---

## 🖥️ Features and Interfaces

### Live Transcription
- Near real‑time speech‑to‑text; supports Vietnamese and multilingual scenarios.  
- Maintains conversation context across the meeting.

### Smart Keywords Overlay
- Automatically extracts keywords (noun chunks / proper nouns).  
- Displays compact interactive chips.  
- Topic grouping and timeline tracking.

### AI Information Panel
- For each keyword: returns a short summary, latest images, and related news.  
- One click - zero context switching.

### Click-to-Search
- Pluggable search providers (images/definitions/news).  
- Source filters and timestamps for contextual reference.

(<a href="#top">back to top</a>)

---

## 🚀 Roadmap & Future Work

**Delivery phases**  
- Phase 1: Audio capture → Whisper → spaCy → Overlay → Search Engine pipeline.  
- Phase 2: Desktop MVP; click‑to‑lookup.  
- Phase 3: Speed optimizations for smooth near‑real‑time (CPU‑friendly).  
- Phase 4: Beta testing with students/office workers/tech learners.  
- Phase 5: Premium tier - content saving, account‑based keyword sync, context summaries.

**Additional directions**  
- Real‑time captions to support the hard‑of‑hearing community.  
- Integrations with popular online meeting/learning platforms.   
- Security hardening: least‑privilege options; opt‑out of external data sharing.

**Highlights**  
- Live, interactive keyword overlay - a novel UX approach.  
- Context‑aware grouping vs. isolated keywords.  
- Clear path to monetization: standalone app, plugins, or B2B API.

(<a href="#top">back to top</a>)

---

## 📝 Notes
- This document summarizes the system; deeper technical docs will be added when the codebase is ready.  
- Questions or suggestions? Please contact the team via the emails above.  
- <i>Made with ❤️ by Free Five.</i>
