# Araştırma 02 — gstack-game

Kaynak: https://github.com/fagemx/gstack-game · Lisans: MIT · 71 yıldız, 8 fork, 115 commit, v0.5.0 · İnceleme: 2026-09-24 (README, ETHOS.md, `docs/domain-judgment-gaps.md`, `feel-pass`, `game-review`, `build-playability-review` skill'leri; WebFetch özetleri)

## 1. Ne yapıyor?
Garry Tan'ın **gstack** (SaaS mühendislik iş akışı) metodolojisinin oyun geliştirmeye uyarlanmış hali. Kendi tanımı: *"Bir oyun üreticisi veya kod üreticisi değil; erken yaratıcı kıvılcımları korumaya, sonra hazır olduğunuzda oyun tasarımınızı ve kodunuzu yargılamaya, puanlamaya ve iyileştirmeye yardım eden yapılandırılmış destek sistemi."* Motor bağımsız. Hedef: solo indie, 2–5 kişilik ekip, tasarım öğrencisi.

**v3 ile en yakın felsefi eşleşme bu repo:** onay değil, **yargı + puanlama + iyileştirme**.

## 2. Yapı
```
skills/   29 skill (SKILL.md.tmpl şablonlarından üretiliyor)
docs/     domain-judgment-gaps.md, geliştirici rehberi
bin/      7 yardımcı script
scripts/  skill üretimi için template engine (preamble injection)
test/     24 doğrulama testi
ETHOS.md, CLAUDE.md, CONTRIBUTING.md, CHANGELOG.md
```
Kurulum: `git clone ... ~/.claude/skills/gstack-game && bun run build` (Bun gerekli). Skill listesi projenin CLAUDE.md'sine eklenir.

## 3. Skill'ler (29)
| Faz | Skill | Ne yapar |
|---|---|---|
| Yaratıcı | `/spark-lens` | Kırılgan fikri **eleştirmeden** korur |
| | `/game-import` | PDF/dokümanı standart GDD'ye çevirir |
| | `/game-ideation` | Konsepti **Fantasy / Loop / Twist** çerçevesiyle yapılandırır |
| Tasarım/strateji | `/game-direction` | Yapımcı review'u; kapsam kararı ADD/KEEP/DEFER/CUT |
| | `/game-review` | Kıdemli tasarımcı GDD review'u + sayısal Health Score |
| | `/pitch-review` | Pazar konumu, fizibilite |
| Planlama/teknik | `/game-eng-review` | Motor seçimi, mimari |
| | `/balance-review` | Ekonomi, zorluk eğrisi, **Sink/Faucet** modeli |
| | `/player-experience` | **7 persona** ile UX araştırmacısı gezintisi |
| | `/plan-design-review` | 7 geçişli uygulama planı + DESIGN.md |
| | `/prototype-slice-plan` | Önce neyin yapılacağına karar (hipotez) |
| Uygulama/kalite | `/implementation-handoff` | Tasarım niyetini build paketine çevirir |
| | `/gameplay-implementation-review` | 3 geçişli kod review (tasarım niyeti, performans, kalite) |
| | **`/feel-pass`** | 7 boyutlu oyun hissi teşhisi |
| | **`/build-playability-review`** | "Oynamaya değer mi?" değerlendirmesi |
| | `/game-qa` | 8 boyutlu test + Health Score |
| Cila/yayın | `/game-ship`, `/game-docs`, `/game-retro` | Build→test→changelog→platform |
| | `/game-debug` | **3 hak hipotez testi** ile hata ayıklama |
| | `/game-codex` | İstismar/desync için adversarial review |
| | `/game-visual-qa`, `/asset-review` | Sanat tutarlılığı, asset teknik doğrulama |
| | `/playtest` | Gözlem metrikleri ve röportaj çerçeveleri |
| Yardımcı | `/triage` | Proje durumunu tespit edip doğru skill'e yönlendirir |
| | `/careful`, `/guard`, `/unfreeze` | Yıkıcı komut uyarısı; düzenlemeyi bir klasöre kısıtlama |

## 4. gstack'ten miras alınan mekanizmalar
- **Template engine + preamble injection:** tüm skill'ler ortak bir başlangıç bloğu (kurallar, ton, yasak kelimeler) enjekte edilerek üretiliyor → tutarlılık.
- **Anti-sycophancy (dalkavukluk karşıtı) protokol.**
- **Classify-before-judge:** önce türü/aşamayı sınıfla, sonra o sınıfa uygun ölçütle yargıla.
- Her review sonucu: **Auto-fixed / Ask / Escalate** ayrımı, X.X/10 Health Score.
- Durum kodları: `DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT` + bir sonraki skill'e yönlendirme (skill zinciri).

## 5. Detaylı incelenen skill'ler

### `/feel-pass` — oyun hissi teşhisi
- **Oynanabilir build veya oynanış videosu şart.** GDD veya kod review yapmaz.
- Faz 0: **hedef his** tek cümle (ağır, çevik, akışkan…).
- Faz 1 Tepki: girdi→ilk görsel değişim gecikmesi; **>100 ms = hantal.**
- Faz 2 Geri bildirim zinciri: **ANTICIPATION → ACTION → IMPACT → RESOLUTION**; eksik kanal (görsel vuruş var ses yok = "hollow").
- Faz 3 Ritim: 30–60 sn makro akış; **>0.5 sn ölü zaman otomatik işaret**; gerilim/rahatlama döngüleri.
- Faz 4 Netlik: ne olduğunu oyuncu anlıyor mu, telegraph'lar görünür mü.
- Faz 5 Ödül/enerji: başarı çabayla orantılı mı.
- Faz 6 Zorlayıcı sorular ("bu kasıtlı mı, kazara mı?").
- Faz 7 Puan: 7 boyut × 2 = /14 — Responsiveness, Clarity, Impact, Rhythm, Payoff, Dead Time, Overload. Hüküm: **ALIVE (12–14) / BREATHING / FLAT / MUDDY / DEAD (<5)**.
- Kurallar: **teşhis et, reçete yazma** ("vuruşta ses yok" ✓, "300 Hz ses ekle" ✗); **her bulgu kanal + zamanlama içerir**; **kilitli kelime dağarcığı** (snappy, weighty, crunchy, hollow, mushy, flowing, telegraphed, readable, charged, relentless, staccato, lurching, monotonous — `references/feel-vocabulary.md`).
- <7/14 ise `/implementation-handoff`'a geri döner.

### `/build-playability-review` — oynamaya değer mi?
6 boyut × 0–2 = /12, her puan için kanıt zorunlu:
| Boyut | 2 puan tanımı (özet) |
|---|---|
| Loop Closure | Eylem → ödül → harcama/kurulum döngüsü tamamlanıyor, oyuncu görüyor |
| Session Viability | 5+ dk sürtünmesiz, oturum bilinçli |
| Onboarding | Yeni oyuncu **90 sn** içinde ne ve neden yapacağını anlıyor |
| Failure Recovery | Başarısızlıkta net sonraki adım, softlock yok |
| Retention Signal | Tekrar oynatacak **bir** an (kilit açma, yeni yetenek, hikâye) |
| Peak Moment | Hatırlanan bir an (gerilim, tatmin, keşif, gülme) |
Hüküm: PLAY-READY (10–12) / ALMOST (7–9) / NOT YET (4–6) / TECH DEMO (0–3).
- Girdi hiyerarşisi: çalışan build > video/ekran görüntüsü > dakika dakika oturum dökümü > kod + açıklama (**"çıkarım, gözlem değil"** olarak işaretlenir).
- **Oturum zaman çizelgesi tablosu:** zaman | eylem | oyuncu durumu | bayrak. >5 sn yapacak bir şey yok = ölü zaman.
- Zorlayıcı sorular: **Stranger Test** (sıfır bilgili oyuncu ilk döngüyü bitirebilir mi?), **Opposite Action** (tutorial'ı atlar/yanlış oynarsa ne bozulur?), **Retention Cliff** (5. dakikada istediği için mi, mecbur hissettiği için mi oynuyor?).
- **Hipotez doğrulama:** slice planındaki hipotez VALIDATED / INVALIDATED / INCONCLUSIVE — *"hipotezi doğrulayan 5/12, doğrulamayan 7/12'den değerlidir."*
- **Regresyon farkı:** önceki rapor varsa boyut bazında düşüş işaretlenir.
- Aşamaya uygun puanlama: alpha'da placeholder normal, kırık döngü kritik.

### `/game-review` — GDD review
- Faz 0: 5 bağlam çıpası (tür, oturum süresi, gelir modeli, kitle, sütunlar) tabloyla teyit.
- 6 bölüm: Core Loop, Progression, Economy, Player Motivation, Risk, Cross-Consistency; her biri 1–10, **oyun moduna göre ağırlıklı** (Mobile, PC/Console, Multiplayer, Narrative, Tabletop).
- Bölüm başına ≥2 zorlayıcı soru (GDD olgunluğuna göre seçilir); **"slop detection"** (stat şişirme, placeholder içerik gibi jenerik kalıplar).
- Faz 1.5: bağlamsız **ikinci görüş** alt agent'ı (öncülleri sorgular).
- Her öneri: NEDEN + 2–3 seçenek + emek tahmini + **oyuncu etkisi 1–10**.
- **Yasak dil:** "delve", "robust", "nuanced", "interesting approach", "could work", "you might consider", boş övgü, em dash.
- Çıktı: ağırlıklı GDD Health Score + **playtest gözlem rehberi**.

## 6. ⭐ `domain-judgment-gaps.md` — AI'ın nerede başarısız olduğu
Repo, AI'ın **kendi başına karar veremediği** yerleri dürüstçe listeliyor. Eksik olan veri değil, **değer çerçeveleri**: sınıflandırma sistemleri, puanlama formülleri, zorlayıcı sorular.
- GDD review: türe göre boyut ağırlıkları, önem taksonomisi, ne zaman düzelt/sor/yükselt.
- Ideation: kanıtsız övgüye kayma ("bu eğlenceli olacak!"); hayal edilen eğlence ile prototiple doğrulanmış eğlenceyi ayıramama.
- Balance: türe göre "sağlıklı" zorluk eğrisi tanımlayamama (Soulslike vs. casual zıt); enflasyon, zorluk/beceri oranı eşikleri yok.
- Kod review: frame bütçesi ihlali, serileştirme yarışları, motor bazlı kritik noktalar.
- UX: stres altında HUD okunabilirliği, kontrol şeması paritesi.
- Çapraz: **ortak sözlük**, **yasak övgü listesi + düzeltilmiş versiyonu**, **tür yönlendirmesi** (roguelike ile live-service denetim önceliği farklı), **skill zinciri çıktı formatları**.
- Olgunluk ölçeği: %70–80 tam yapı + alan teorisi; %55–65 yapı + kelime dağarcığı (çoğu skill burada); %35–40 iskelet.

## 7. ETHOS
- **Boil the Lake:** AI uygulama maliyetini düşürdüğüne göre kapsamlı çözümü yap (edge case, denge verisi, tutorial, kontrolcü desteği); "sonra dengeleriz" deme. Ama okyanusu (motor yeniden yazımı) kaynatma.
- **Search Before Building:** kanıtlanmış temeller → güncel çerçeveler → ilk ilkeler; asıl değer türün varsayımlarını sorgulayıp oyunun **Twist**'ini bulmak ("şu oyun işte...").
- **Player Time is Sacred:** zorla bekletme, atlanamaz tekrar, belirsiz hedef, satmak için grind yok.
- **Fun First:** öncelik sırası eğlenceli döngü → netlik → performans → cila → ekonomi.

## 8. Güçlü yanlar
- Kalite **sayısal ve çıpalı** rubriklerle ölçülüyor (0/1/2 tanımlı), her puan kanıt istiyor.
- Oyun hissi için ölçülebilir eşikler (100 ms, 0.5 sn, 5 sn) ve kilitli kelime dağarcığı.
- "Teşhis et, reçete yazma" ve "gözlem mi çıkarım mı" ayrımı.
- Hipotez odaklı prototip; regresyon karşılaştırması.
- Dalkavukluk karşıtı protokol + yasak kelime listesi + bağlamsız ikinci görüş.
- AI'ın sınırlarını açıkça belgelemesi.
- Skill'lerin şablondan üretilmesi (ortak preamble) ve skill zinciri durum kodları.

## 9. Zayıf yanlar
- Motor bağımsız: Unity MCP, sahne, ekran görüntüsü alma yok; oynanış kanıtını kullanıcı getirmek zorunda.
- Etkileşimli, soru-cevap ağırlıklı (her bölümden sonra bekler).
- Skill'lerin çoğu kendi ölçeğine göre %55–70 olgunlukta; eşikler uzman kalibrasyonu bekliyor.
- Küçük topluluk; Bun bağımlılığı.
- Level design için özel skill yok.

## 10. v3'e alınacaklar (öneri)
| Fikir | v3'te nereye |
|---|---|
| `/feel-pass` yapısı: hedef his, 4 vuruş zinciri, ms eşikleri, /14 rubrik, kilitli kelime dağarcığı, "teşhis et reçete yazma" | `craft-game-feel` (F5 → öne alınabilir) + MCP ile video/ekran görüntüsü kanıtı |
| `/build-playability-review` 6 boyut /12 + Stranger/Opposite/Retention soruları + oturum zaman çizelgesi | `/playtest` skill'ine sindir; `evals/RUBRIC.md`'ye oynanış rubriği olarak ekle |
| Hipotez doğrulama (VALIDATED/INVALIDATED/INCONCLUSIVE) ve "hipotez skordan önemli" | Kartlardaki "Top 3 risks → prototip testi" ile birleştir |
| Gözlem vs. çıkarım etiketi | Tüm review çıktılarında zorunlu alan |
| Anti-sycophancy + yasak ifade listesi | Ortak skill preamble'ı (tüm craft/critic içerikleri) |
| Classify-before-judge + oyun türüne göre ağırlık | `design-critic` ve RUBRIC'e tür/aşama çıpası |
| Fantasy / Loop / Twist | `IDENTITY` şablonuna "Twist" satırı |
| ADD/KEEP/DEFER/CUT kapsam kararı | `/design-*` akışı sonunda kapsam adımı |
| Önceki rapora göre regresyon farkı | Eval ve playtest raporlarında |
| Durum kodları + sonraki skill önerisi | Tüm skill çıktılarına standart son satır |
| `domain-judgment-gaps` fikri | v3'te `docs/JUDGMENT-GAPS.md`: AI'ın kendi başına karar veremediği ve sahibin karar vermesi gereken yerler |
| Fun First öncelik sırası | `IDENTITY`/CLAUDE.md ilkesi |
