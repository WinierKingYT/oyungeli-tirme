# Araştırma 12 — Akademik çalışmalar ve benchmark'lar

İnceleme: 2026-09-24 (arXiv özetleri ve repo README'leri; tam makaleler okunmadı).

## A. "LLMs May Not Be Human-Level Players, But They Can Be Testers" (arXiv 2410.02829)
Yazarlar: Chang Xiao, Brenda Z. Yang · https://arxiv.org/abs/2410.02829
- **Yöntem:** basit, genel prompt teknikleriyle LLM agent'ları oyun oynatan genel test çerçevesi; Wordle ve Slay the Spire.
- **Bulgu:** LLM performansı ile **insanların bildirdiği zorluk arasında istatistiksel olarak anlamlı, güçlü korelasyon** — LLM'ler ortalama insandan kötü oynasa bile **zorluk ölçer** olarak kullanılabiliyor.
- **v3:** `playtest_bot` / denge simülasyonu fikrini destekliyor. Mutlak başarı değil, **göreli zorluk** ölçümü için kullan (level A vs. B hangisi daha zor; değişiklik zorluğu artırdı mı).

## B. "Large Language Models and Games: A Survey and Roadmap" (arXiv 2402.18659, IEEE ToG 2024)
https://arxiv.org/abs/2402.18659
- LLM'lerin oyunlardaki rollerini (oyuncu, NPC, tasarım asistanı, içerik üretici, test vb.) sınıflayan tarama. Sohbetle level düzenleme editörü **LLMaker** örneği (istekleri geçerli fonksiyon çağrılarına çevirir, tutarlılığı korur).
- **v3:** Tam makale okunmadı; ileride tasarım asistanı rolü ve açık problemler için okunmalı.

## C. OpenGame (CUHK MMLab)
https://github.com/leigest519/OpenGame
- Doğal dilden uçtan uca **web oyunu** üreten agent çerçevesi. **Game Skill = Template Skill** (motor seçimi + iskelet) **+ Debug Skill** (sandbox'ta çalıştır, entegrasyon hatalarını bul, sistematik onar).
- **Execution-grounded feedback:** oyunu gerçekten çalıştırıp dosyalar arası tutarsızlıkları ve kırık sahne bağlantılarını yakalar.
- **OpenGame-Bench** üç eksen: **Build Health** (derleme/çalışma kararlılığı), **Visual Usability** (ekran görüntüsü analiziyle render/UI tutarlılığı), **Intent Alignment** (oynanış istemle uyuşuyor mu) — headless tarayıcı + **VLM yargıcı**.
- GameCoder-27B: oyun korpusunda sürekli ön eğitim + SFT + **oynanabilirlik sinyaliyle RL**.
- **v3:** Eval'imize doğrudan eşlenir: RUBRIC'e "Build health / Visual usability / Intent alignment" üçlüsünü uygulama görevleri için ekle; "niyet uyumu"nu ekran görüntüsü + kart karşılaştırmasıyla (C1) ölç.

## D. GamingAgent (ICLR 2026, lmgame-org)
https://github.com/lmgame-org/GamingAgent
- LLM/VLM'leri Sokoban, Tetris, 2048, Candy Crush, Pokemon Red, Super Mario Bros, Ace Attorney üzerinde Gymnasium arayüzüyle değerlendirir; **harness'lı (agentic) vs. harness'sız** karşılaştırma, paralel değerlendirme, bölüm loglarından **replay video**, liderlik tablosu.
- **v3:** Oyun oynatan agent için "harness" (algı + hafıza + akıl yürütme) farkının büyük olduğu mesajı; kendi playtest botumuz için basit harness yeterli (NavMesh + kurallı hareket), VLM oynatma ileride.

## E. Diğer (sadece not)
- Unity ML-Agents (https://github.com/Unity-Technologies/ml-agents): RL ile ajan eğitimi — otomatik playtest için ağır ama güçlü seçenek; şimdilik kapsam dışı.
- LLMUnity, EastWorld: oyun **içinde** LLM karakterler — v3 kapsamı dışı (geliştirme aracı değil).

## Çıkarımlar
1. **Çalıştırarak doğrulama (execution-grounded)** kalite için belirleyici — OpenGame ve m4bwav aynı sonuca varıyor. v3 L4 katmanı doğru yönde.
2. **VLM ile ekran görüntüsü yargısı** artık benchmark standardı (Visual Usability, Intent Alignment).
3. LLM'ler **göreli zorluk ölçer** olarak güvenilir; mutlak "eğlenceli mi" yargısı için değil.
