<div align="center">

# 😴 Drowsy Driver Detector — كاشف نعاس السائق

**Real-time drowsiness & yawn detection with vibration + audible alerts, built on a Raspberry Pi.**
**رصدٌ للنعاس والتثاؤب في الزمن الحقيقي، بتنبيهٍ اهتزازيٍّ وصوتيٍّ، مبنيٌّ على حاسوب Raspberry Pi.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![dlib](https://img.shields.io/badge/dlib-19.x-lightgrey)](http://dlib.net/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Compatible-A22846?logo=raspberrypi&logoColor=white)](https://www.raspberrypi.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Built by [Ahmed Darwish](mailto:eahmeddarwish@gmail.com)**

[![GitHub](https://img.shields.io/badge/GitHub-Repo-181717?logo=github)](https://github.com/eahmeddarwish/drowsy-driver-detector)

</div>

---

## 🌍 Overview | نظرة عامة

**[English]**
Drowsy Driver Detector watches the driver's face through a camera and estimates two things in real time: how closed the eyes are (Eye Aspect Ratio) and how open the mouth is (yawn distance). When either crosses a threshold for several consecutive frames — not a single flicker — it triggers a vibration motor, a buzzer, and a spoken warning. Originally built as a Computer Engineering graduation project (Raspberry Pi + night-vision camera), it also runs on any laptop webcam with no hardware attached, for development, demos, or a software-only deployment path.

**[العربية]**
يراقب هذا النظام وجه السائق عبر كاميرا، ويحسب في الزمن الحقيقي مؤشرَين اثنين: مدى انغلاق العينين، عبر ما يُعرف بـ"نسبة اتساع العين" (Eye Aspect Ratio)، ومدى اتساع الفم، عبر مسافة الشفتين. فإذا تجاوز أيٌّ من هذين المؤشرين حدًّا معينًا لعدد إطاراتٍ متتاليةٍ — لا للحظةٍ عابرةٍ واحدة — يُطلِق النظام موتور اهتزاز، وجرس تنبيه، وتحذيرًا صوتيًا مسموعًا. بدأ هذا العمل مشروعَ تخرجٍ في هندسة الحاسوب، قائمًا على حاسوب Raspberry Pi وكاميرا ذات رؤيةٍ ليلية، وهو يعمل أيضًا على أي حاسوبٍ محمولٍ بكاميرا اعتيادية، من دون أي عتادٍ إضافي، لأغراض التطوير والعرض، أو كنسخةٍ برمجيةٍ بحتة.

> ⚠️ **Safety notice | تنبيهٌ بشأن السلامة:** This is a driver-assistance aid, not a certified safety device — it does not replace attentive, rested driving. / هذا النظام أداةٌ مساعدةٌ للتنبيه، وليس جهاز سلامةٍ معتمدًا، ولا يُغني بحالٍ عن القيادة اليقظة والمرتاحة.

---

## ✨ What Changed vs. the Original Project | ما الذي تغيّر مقارنةً بالنسخة الأصلية

| | Original (graduation project) / النسخة الأصلية | Rebuilt / النسخة المُعاد بناؤها |
|---|---|---|
| Code structure / بنية الكود | One file, everything mixed in (181 lines) / ملفٌ واحدٌ يضم كل شيء | 5 focused modules: config, detection, camera, alerts, main loop / خمس وحداتٍ مستقلة |
| Thresholds / العتبات | Hardcoded in the source / مُثبَّتةٌ داخل الكود | Fully env-configurable, no code edits needed / قابلةٌ للتعديل كاملةً عبر متغيرات البيئة |
| False-positive guard / مقاومة الإنذار الكاذب | None — one blink triggers a full alarm / غير مُفعَّلة؛ أي رمشةٍ تُطلِق الإنذار فورًا | Consecutive-frame debounce before any alert fires / نظام "تأكيدٍ متتالٍ" قبل إطلاق أي إنذار |
| Alert loop / حلقة التنبيه | Tight `while` loop calling TTS with no delay — pegs the CPU / حلقةٌ مضغوطة بلا إبطاء، تُرهق المعالج | One spoken call per event + a cooldown / نداءٌ واحد لكل حدث مع فترة تهدئة |
| Camera source / مصدر الكاميرا | Pi Camera only; a `--webcam` flag exists but is dead code / كاميرا Pi حصرًا؛ خيار الويب كام موجودٌ لكنه معطَّل | Works with Pi Camera **or** any laptop/USB webcam / يعمل مع كاميرا Pi **أو** أي كاميرا حاسوبٍ محمول |
| Face detector file / ملف كاشف الوجه | Assumed present locally, no download instructions / يُفترَض وجوده محليًا دون تعليمات | Uses OpenCV's bundled cascade — nothing to download / يستخدم الملف المرفق مع OpenCV، بلا تنزيلٍ منفصل |
| Landmark model / نموذج علامات الوجه | Not included, source undocumented / غير مرفق وغير موثَّق مصدره | Fetched automatically via a download script / يُنزَّل تلقائيًا عبر سكربت مخصص |
| Secrets / الأسرار | Real Wi-Fi credentials committed in project files / بيانات شبكة واي فاي حقيقية داخل ملفات المشروع | Fully scrubbed; `.gitignore` excludes anything sensitive / مُستبعَدةٌ بالكامل عبر .gitignore |

---

## 🔬 Why "Consecutive-Frame" Debouncing Matters | لماذا "التأكيد المتتالي" ضروريٌّ

**[English]**
Any vision-based system is prone to momentary noise: a glare, a natural blink, an odd head angle. If the alarm fires the instant the Eye Aspect Ratio dips below threshold, false alarms repeat constantly — and the first thing any driver does with a system like that is ignore it, or switch it off, which defeats the whole point. This version requires the metric to stay below threshold for several consecutive frames (15 by default for eye closure, 10 for yawning) before any alert fires. It's a deliberate, documented tradeoff, and it's tunable per install via environment variables alone — no code changes.

**[العربية]**
كل نظام رصدٍ بصري عرضةٌ لأخطاء لحظية: انعكاس ضوء، رمشة طبيعية، أو زاوية رأسٍ غير معتادة. وإذا كان النظام يُطلق الإنذار عند أول لحظةٍ تنخفض فيها نسبة اتساع العين دون العتبة، فسيتكرر الإنذار الكاذب باستمرار — وأول ما يفعله أي سائقٍ حينها هو تجاهل النظام كليًا أو إيقاف تشغيله، وهو ما يُبطل الغرض منه تمامًا. لهذا يشترط هذا الإصدار استمرار المؤشر دون العتبة لعدد إطاراتٍ متتالية (خمسة عشر إطارًا افتراضيًا لجفاف العين، وعشرة إطاراتٍ للتثاؤب) قبل إطلاق أي تنبيه. هذا خيارٌ مقصودٌ وموثَّق، وقابلٌ للضبط الدقيق حسب كل تركيب عبر متغيرات البيئة وحدها، دون الحاجة لتعديل الكود.

---

## 🏗️ Architecture | المعمارية

```
drowsy-driver-detector/
├── app/
│   ├── config.py     # All thresholds & pins — env-overridable
│   ├── detector.py   # EAR + yawn math (pure functions, unit-testable)
│   ├── camera.py     # PiCamera / webcam source abstraction
│   ├── alerts.py     # GPIO + TTS alert manager (daemon-fixed, cooldown-limited)
│   └── main.py        # Video loop, wires everything together
├── models/            # Downloaded via scripts/download_models.sh (not in git)
├── scripts/           # Model download + system dependency install helpers
├── systemd/            # Boot-time auto-start unit for a dedicated Pi install
└── assets/hardware/    # Circuit diagram, breadboard photo, Fritzing sketch
```

| Module / الوحدة | Role | الدور |
|---|---|---|
| `detector.py` | EAR & yawn-distance math from 68 facial landmarks | حساب نسبة اتساع العين ومسافة التثاؤب من 68 نقطة علامةٍ على الوجه |
| `camera.py` | Starts PiCamera or a webcam by index | تشغيل كاميرا Pi أو كاميرا ويب كام حسب رقمها |
| `alerts.py` | Drives GPIO + spoken alerts, debounced & rate-limited | التحكم بمنافذ GPIO والتنبيه الصوتي، مع تأخيرٍ زمني ومنع تكرارٍ مُفرط |
| `main.py` | Captures frames, runs detection, renders overlay | التقاط الإطارات، تشغيل الكشف، ورسم المؤشرات على الشاشة |

---

## 🚀 Quick Start | البدء السريع

### Option A — Raspberry Pi (hardware mode) | الخيار الأول — على جهاز Raspberry Pi (وضع العتاد الفعلي)

```bash
git clone https://github.com/eahmeddarwish/drowsy-driver-detector.git
cd drowsy-driver-detector

bash scripts/install-system-deps.sh      # build tools, espeak
pip install -r requirements.txt
pip install RPi.GPIO picamera            # Pi-only packages

bash scripts/download_models.sh          # fetches the 68-point landmark model

python3 -m app.main                      # CAMERA_SOURCE=picamera by default
```

### Option B — Any laptop (desktop / dev / demo mode, no hardware needed) | الخيار الثاني — على أي حاسوبٍ محمول (وضع التطوير والعرض، دون عتاد)

```bash
git clone https://github.com/eahmeddarwish/drowsy-driver-detector.git
cd drowsy-driver-detector

pip install -r requirements.txt
bash scripts/download_models.sh

python3 -m app.main --camera webcam
```

**[English]** On a non-Pi machine, GPIO output and speech are automatically logged instead of driven — the detection window and on-screen `DROWSINESS ALERT!` / `YAWN ALERT!` overlays still work normally.

**[العربية]** على أي جهازٍ غير Raspberry Pi، يُسجَّل مخرَج GPIO والصوت في سجل النظام تلقائيًا بدلًا من تشغيل عتادٍ فعلي، بينما تستمر نافذة الفيديو ومؤشرات "تنبيه نعاس!" و"تنبيه تثاؤب!" بالعمل كالمعتاد.

### Option C — Headless (in-vehicle, no monitor) | الخيار الثالث — تشغيلٌ بلا شاشة (للتركيب داخل المركبة)

```bash
python3 -m app.main --no-display
```

Press **q** in the video window to quit (Options A/B). / اضغط **q** داخل نافذة الفيديو للخروج (في الخيارين الأول والثاني).

---

## ⚙️ Configuration | الإعدادات

Copy `.env.example` to `.env` and adjust — no code changes needed to calibrate for a specific camera angle or driver. / انسخ ملف `.env.example` إلى `.env` وعدِّل القيم — لا حاجة لتعديل أي سطر برمجي لمعايرة النظام حسب زاوية الكاميرا أو طبيعة السائق:

| Variable / المتغير | Default / القيمة الافتراضية | Meaning / المعنى |
|---|---|---|
| `CAMERA_SOURCE` | `picamera` | `picamera` or `webcam` / إما `picamera` أو `webcam` |
| `WEBCAM_INDEX` | `0` | Which USB camera to use / رقم كاميرا الويب كام المستخدمة |
| `EYE_AR_THRESH` | `0.25` | EAR below this = eyes considered closed / ما دون هذه القيمة تُعتبر العين مغلقة |
| `EYE_AR_CONSEC_FRAMES` | `15` | Consecutive closed-eye frames before alarm fires / عدد الإطارات المتتالية قبل إنذار النعاس |
| `YAWN_THRESH` | `20.0` | Mouth-opening distance (px) above this = yawn / مسافة اتساع الفم التي تُعدّ تثاؤبًا |
| `YAWN_CONSEC_FRAMES` | `10` | Consecutive yawn frames before alarm fires / عدد الإطارات المتتالية قبل إنذار التثاؤب |
| `GPIO_VIBRATION_PIN` / `GPIO_BUZZER_PIN` | `8` / `10` | BOARD-numbered GPIO pins / منفذا GPIO بترقيم BOARD |
| `ALERT_COOLDOWN_SECONDS` | `3.0` | Gap between repeated spoken warnings / الفاصل الزمني بين تكرار التحذير الصوتي |

---

## 🔧 Hardware Used | العتاد المستخدم

| Component | المكوّن |
|---|---|
| Raspberry Pi (any model with GPIO + camera port) | Raspberry Pi (أي إصدارٍ فيه منافذ GPIO ومنفذ كاميرا) |
| 5MP night-vision-enabled Pi Camera | كاميرا Pi ليلية، دقة 5 ميجابكسل |
| Vibration motor | موتور اهتزاز |
| Buzzer | جرس تنبيه (Buzzer) |

<div align="center">
  <img src="assets/hardware/circuit-breadboard.jpg" alt="Breadboard circuit" width="420"/>
  <img src="assets/hardware/system-diagram.png" alt="System diagram" width="420"/>
</div>

Wiring reference (Fritzing source): `assets/hardware/circuit.fzz` / مرجع التوصيل الكامل (ملف Fritzing المصدري)

---

## 🔒 Security & Privacy Notes | ملاحظات الأمان والخصوصية

**[English]** All video processing happens locally and in memory — no frame is ever written to disk, uploaded, or logged. No secrets (Wi-Fi credentials, API keys) are stored in this repository; `wpa_supplicant.conf` and `.env` are git-ignored.

**[العربية]** تجري معالجة الفيديو بالكامل محليًا وفي الذاكرة فقط؛ لا يُحفَظ أي إطارٍ على القرص، ولا يُرفَع إلى أي خادم، ولا يُسجَّل بأي شكل. كما لا تحتوي هذه المستودعة على أي بياناتٍ حساسة — لا مفاتيح شبكاتٍ، ولا كلمات مرور — إذ يستبعد ملف `.gitignore` كلًّا من `wpa_supplicant.conf` و`.env` تلقائيًا.

---

## ⚠️ Honest Limitations | القيود الصادقة

**[English]**
- **No automatic per-driver calibration.** Eye shape, glasses, and seating position vary by driver, and the default thresholds may need manual tuning to reduce false positives or missed alerts for a specific person. A deliberate simplicity/speed-of-install tradeoff — auto-calibration is on the roadmap below.
- **Detection depends on a clearly visible face.** Very poor lighting, an extreme head angle, or a fully covered face can prevent the detector from finding facial landmarks at all — in which case no alert fires, since "no detection" isn't treated as "no drowsiness." A separate "face not detected for too long" alert is a sensible next step.
- **This is a driver-assistance aid, not a certified safety device.** It has not been through any formal certification (CE/FCC or equivalent automotive-safety standards) — a necessary step before any real commercial deployment.
- **Video is never recorded, by design — that's a feature, not a gap.** There's no way to review events after the fact. Anyone wanting a commercial deployment that needs an event log (not video) for fleet use should see the Roadmap.

**[العربية]**
- **لا معايرةَ تلقائية لكل سائق.** يختلف شكل العين، والنظارات الطبية أو الشمسية، ووضعية الجلوس من سائقٍ لآخر، وقد تتطلب العتبات الافتراضية تعديلًا يدويًا لتقليل الإنذارات الكاذبة أو المفوَّتة لسائقٍ بعينه. هذا خيارٌ مقصودٌ يوازن بين البساطة وسرعة التركيب؛ أما المعايرة التلقائية فمُدرَجةٌ في خطة التطوير أدناه.
- **يعتمد الكشف على وضوح الرؤية للوجه.** إضاءةٌ ضعيفةٌ جدًا، أو انحرافٌ حادٌّ لزاوية الرأس، أو غطاء وجهٍ كامل، قد يمنع الكاشف من تحديد نقاط الوجه أصلًا — وفي هذه الحالة لا يُطلَق أي إنذار، لأن غياب الكشف لا يعادل غياب النعاس. إضافة تنبيهٍ منفصل عند غياب الوجه لفترةٍ طويلة خطوةٌ منطقية تالية.
- **هذا نظام تنبيهٍ مساعد، لا جهاز سلامةٍ معتمد.** لم يخضع لأي اعتمادٍ رسمي (كمعايير CE أو FCC أو ما يعادلها في قطاع سلامة المركبات)، وهو خطوةٌ ضرورية قبل أي طرحٍ تجاريٍّ فعلي.
- **الفيديو غير مُسجَّل بتصميم النظام، وهذه ميزةٌ لا نقص.** لا توجد آلية لمراجعة الأحداث لاحقًا. من أراد استخدامًا تجاريًا يتطلب سجلَّ أحداثٍ (لا فيديو) لأغراض الأساطيل، فليراجع خطة التطوير أدناه.

---

## 🗺️ Roadmap | خطة التطوير

**[English]** Earlier prototyping by the project team explored driver-identity verification (face recognition against a known-driver profile) and push/SMS notifications to a third party on a drowsiness event. Both are natural v2 directions for a commercial deployment and are intentionally **not** included here yet (they require handling biometric data and third-party credentials responsibly — outside the scope of this public release):

**[العربية]** كشفت مراجعة تجارب الفريق السابقة عن محاولاتٍ أولية للتحقق من هوية السائق (عبر التعرف على الوجه مقابل ملفٍ معروف)، وإرسال تنبيهاتٍ فورية أو رسائل نصية لطرفٍ ثالث عند تكرار حالات النعاس. كلتا الميزتين اتجاهٌ منطقي لنسخةٍ تجاريةٍ مقبلة، وقد استُبعِدَتا عمدًا من هذا الإصدار (لأنهما تستوجبان تعاملًا مسؤولًا مع بياناتٍ بيومترية وبيانات اعتماد أطراف ثالثة، وهو خارج نطاق هذا الإصدار العلني):

- [ ] Optional driver-identity check before arming alerts / تحقق اختياري من هوية السائق قبل تفعيل التنبيهات
- [ ] Configurable push/SMS notification on repeated drowsiness events / تنبيهٌ عبر رسالةٍ نصية أو إشعارٍ فوري عند تكرار حالات النعاس
- [ ] Per-driver threshold auto-calibration (glasses, eye shape, seating position) / معايرة تلقائية للعتبات لكل سائق
- [ ] Logging of alert *events* only (timestamp/type, never video) for fleet use / تسجيل الأحداث فقط (الوقت والنوع، لا الفيديو) لأغراض إدارة الأساطيل

---

## 🎓 Academic Origin | الأصل الأكاديمي

**[English]** Originally developed as a Computer Engineering graduation project ("**Anti-Sleep Alarm for Drowsy Drivers**") at the **American University of the Middle East (AUM)**, Kuwait, under faculty supervision. This repository is a cleaned-up, hardened, and modularized version of that work, prepared for public/academic reuse and as a foundation for a possible commercial iteration.

**[العربية]** بدأ هذا العمل مشروعَ تخرجٍ في هندسة الحاسوب بعنوان **"إنذار مانع النعاس للسائقين" (Anti-Sleep Alarm for Drowsy Drivers)**، في **الجامعة الأمريكية بالشرق الأوسط**، بالكويت، تحت إشرافٍ أكاديمي. وهذه المستودعة نسخةٌ مُعاد بناؤها بالكامل، ومُحصَّنةٌ، ومُهيكَلةٌ من ذلك العمل، أُعِدَّت لإعادة الاستخدام الأكاديمي والعام، ولتكون أساسًا لتطويرٍ تجاريٍّ محتمل مستقبلًا.

---

## ⚠️ Disclaimer | إخلاء المسؤولية

> **This project is for educational and research purposes primarily.**
> It is a driver-assistance aid only — not a substitute for attentive, rested driving, and not a certified safety device.
> The driver always bears full responsibility for safe driving.

> **هذا المشروع مُعدٌّ لأغراضٍ تعليميةٍ وبحثيةٍ في الأساس.**
> هو أداةٌ مساعدةٌ للتنبيه فقط، وليس بديلًا عن القيادة اليقظة والمرتاحة، وليس جهاز سلامةٍ معتمدًا.
> يتحمّل السائق دائمًا المسؤولية الكاملة عن القيادة الآمنة.

---

## 👤 Author | المطوّر

<div align="center">

**Ahmed Darwish**

*Electrical & Computer Engineer | Python · Arduino · Raspberry Pi · AI/ML*

[![Email](https://img.shields.io/badge/Email-eahmeddarwish%40gmail.com-EA4335?logo=gmail&logoColor=white)](mailto:eahmeddarwish@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-eahmeddarwish-181717?logo=github)](https://github.com/eahmeddarwish)

</div>

---

## 📄 License | الترخيص

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details. / هذا المشروع مرخَّصٌ بموجب **رخصة MIT** — راجع ملف [LICENSE](LICENSE) للتفاصيل الكاملة.

```
MIT License — free to use, modify, and distribute with attribution.
رخصة MIT — حرة الاستخدام والتعديل وإعادة التوزيع، مع وجوب ذكر المصدر.
```

---

<div align="center">

⭐ If this project is useful, consider starring the repo! | إن كان هذا المشروع مفيدًا لك، فلا تتردد في دعمه بنجمة (Star) على GitHub

</div>
