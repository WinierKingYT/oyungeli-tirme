# Araştırma 10 — Küçük/ikincil repolar

İnceleme: 2026-09-24 (README'ler). Üç repo birlikte raporlandı çünkü v3'e katkıları sınırlı.

## A. HermeticOrmus/claude-code-game-development
Kaynak: https://github.com/HermeticOrmus/claude-code-game-development · MIT · 63 yıldız
- **Ne:** Claude Code ile **web tabanlı** (JS/TS, Phaser, Three.js, Babylon.js) oyun yapmak için eğitim deposu: 50.000+ kelime doküman (13 bölüm: döngü, çarpışma, fizik, render, AI, ses, ağ, UI/UX, performans, test, yayın), 10+ örnek oyun (Pong'dan RTS'e), **100+ kategorize edilmiş prompt**, 5 şablon, öğrenme yolları.
- **Değer:** Prompt kütüphanesi fikri (görev türüne göre test edilmiş prompt + varyasyon). Unity ve tasarım kalitesi yok.
- **v3:** Doğrudan alınacak yok. Eval görev setimiz (TASKS.md) büyürken "prompt + varyasyon" formatı örnek alınabilir.

## B. wanghaisheng/openagenticgame-gdd
Kaynak: https://github.com/wanghaisheng/openagenticgame-gdd (branch `master`) · 30 yıldız · lisans belirtilmemiş (kullanmadan önce kontrol)
- **Ne:** AI agent'lar için bölüm bölüm Markdown GDD şablonu (EN + ZH). 15 bölüm: telif, versiyon, **genel bakış (core thrill loop)**, oynanış/mekanik (sistem mimarisi, ticari katmanlama), hikâye/dünya/karakter, level, arayüz, AI, teknik, sanat (asset pipeline), ikincil yazılım, yönetim, ekler (asset indeksi), **14: AI destekli tasarım ("Fun Concentration Tester", tasarım kalite değerlendirmesi)**, 15: 8 oyun türüne uyarlama. CSV/JSON/MD asset şablonları. Kök: `docs/`, `examples/`, `templates/`, `ref/`, `public/`, `old/`.
- **Değer:** Her bölümün bağımsız dosya olması (AI'ın sadece ilgili bölümü yüklemesi) — v3'ün kart yaklaşımıyla aynı fikir. "Concentration theory" (konsantrasyon/odak teorisi) tabanlı eğlence testi iddiası README'de detaylandırılmıyor; doğrulanamadı.
- **v3:** Kart yaklaşımımızı teyit ediyor. İleride "tür uyarlaması" (8 tür) fikri `IDENTITY`'de tür alanı ve RUBRIC ağırlıkları için referans.

## C. davila7/claude-code-templates — `unity-game-developer` agent
Kaynak: https://github.com/davila7/claude-code-templates/blob/main/cli-tool/components/agents/game-development/unity-game-developer.md
- **Ne:** Tek bir persona agent'ı ("8+ yıl deneyimli Unity geliştirici"): motor, C#, mimari (oyuncu kontrolcü, durum, save/load, envanter, behavior tree, combat), render (URP/HDRP), mobil, çapraz platform; 7 aşamalı genel iş akışı.
- **Değer:** Düşük. Persona + yetkinlik listesi; somut kural, kontrol listesi, doğrulama yok. "Uzman gibi davran" demek kaliteyi artırmaz — v3'ün "somut ilke + kontrol listesi + anti-pattern + doğrulama" yaklaşımının neden gerekli olduğuna iyi bir karşı örnek.
- **v3:** Alınacak yok.
