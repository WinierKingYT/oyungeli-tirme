# Araştırma 07 — gamedev-skills/awesome-gamedev-agent-skills

Kaynak: https://github.com/gamedev-skills/awesome-gamedev-agent-skills (branch `main`, 94 commit) · Bakımcı: Abhishek Barali · Lisans: **Apache-2.0** · ~1.1k yıldız, 97 fork · İnceleme: 2026-09-24 (README, klasör listeleri, `level-design`, `game-feel`, `create-game-assets` SKILL.md'leri)

## 1. Ne yapıyor?
10 motor için **73 taşınabilir SKILL.md** (Agent Skills açık standardı). Claude Code, Cursor, Codex, Gemini CLI, Copilot, Kiro vb. ile uyumlu; `npx skills add gamedev-skills/awesome-gamedev-agent-skills`. Skill'ler **motor sürümüne sabitlenmiş** (Unity 6.3 LTS, Godot 4.7, Unreal 5.8 …).

## 2. Yapı
```
skills/{unity,godot,unreal,web-engines,other-engines,disciplines,genres,workflows}/<skill>/SKILL.md (+ references/, scripts/, assets/, agents/)
router/SKILL.md      ana yönlendirici
docs/                yazım standartları, kurulum, uyumluluk
templates/           SKILL.md şablonu
scripts/validate-skills.py   skill doğrulayıcı
tests/               regresyon testleri
```

## 3. İçerik
- **Motor (45):** Godot 15, **Unity 8** (C# scripting, Input System, physics, animation, ScriptableObjects, tilemap, navmesh, build pipeline), Unreal 6, web 6, diğer 10.
- **Disiplin (15):** `ai-behavior-trees-utility-ai`, `audio-design`, `camera-systems`, `create-game-assets`, `dialogue-systems`, `game-ai`, **`game-feel`**, `game-ui-ux`, `input-systems`, **`level-design`**, `performance-optimization`, `physics-tuning`, `procedural-gen`, `save-systems`, `shader-programming`.
- **Tür (9):** platformer, roguelike, RPG, FPS, tower defense, card game, visual novel, survival/crafting, puzzle — "kompozisyon şablonları".
- **Workflow (4):** game jam, hızlı prototip, Steam ve itch.io yayını.

## 4. Router
`router/SKILL.md`: (1) motoru dosyalardan tespit (`project.godot`, `*.uproject`, Unity için `ProjectSettings`), (2) istekteki kavram/tür/yayın niyetini tanı, (3) önce motor skill'i, sonra ek disiplin/tür skill'lerini yükle. **Motor seçimi tekildir; disiplin, tür ve workflow üst üste eklenir.**

## 5. İncelenen disiplin skill'leri
**`level-design`** — "Level, mekân aracılığıyla sunulan **kasıtlı deneyimler dizisidir**."
1. **Önce metrikler:** zıplama yüksekliği/mesafesi, koşu hızı, erişim → sabitle.
2. Primitive'lerle doğru ölçekte blockout.
3. Kritik yol + opsiyonel dallar.
4. **Testere dişi** (sawtooth) zorluk eğrisi: yüksek/düşük yoğunluk dönüşümlü.
5. Öğret → pratik → baskı.
6. Playtest → sürtünmeyi bul → blockout'u süslemeden önce düzelt.
Kalıplar: **Metrik güdümlü geometri** — `MAX_JUMP_DIST` sabit; boşluklar **%70 (güvenli) ve %95 (zorlayıcı)** oranında. "MAX_JUMP_DIST + 1 uzaklıktaki platform imkânsızdır." · **Ritim veri olarak:** karşılaşma dizisi 0–1 yoğunluk değerleriyle; genel yükselir ama nefes aralıkları ile iner, **asla yüksekte düz kalmaz**. · **Kritik yol doğrulama:** oda bağlantı grafiği + kilit gereksinimleri (anahtar/yetenek) → **flood-fill** ile yeteneklerin elde edilme sırasına göre hedefe ulaşılabilirlik. Tuzaklar: blockout oynanmadan detay, metriği yok sayma, düz ritim, öğretmeden test, ulaşılamaz kapı kaynaklı softlock, zayıf yönlendirme.

**`game-feel`** — "Tatmin edici bir vuruş genelde **~100 ms içinde ateşlenen 5–8 küçük tepkidir**."
- İlkeler: kısa abart ve dinlenmeye dön · önemine göre ölçekle (küçük/orta/büyük olay kademeleri) · **görseli simülasyondan ayır** (sarsıntı kamerayı oynatır gövdeyi değil; hitstop time scale veya gerçek zamanlı duraklatma, oyun mantığını durdurma değil) · ease'li hareket (pop için overshoot, oturma için ease-out).
- Teknikler: **trauma decay ile ekran sarsıntısı** (trauma 0–1 birikir, kameraya **karesel** uygulanır, her karede azalır, rastgele titreme değil **yumuşak örneklenmiş gürültü**) · **hitstop ~0.08 sn, time scale 0.05**, geri dönüş **gerçek zamanlı zamanlayıcıyla** (Unity `WaitForSecondsRealtime`) · squash & stretch 1.3×/0.7× anında, **~0.18 sn** back-ease ile 1.0'a.
- Akış: olay kancalarını doğrula (`on_hit`, `on_land`, `on_pickup`) → kademe başına 2–3 kanal, okunur olana kadar ekle, sonra dur → tüm hareket ease'li tween → hitstop/sarsıntıyı yüksek etkili olaylara ayır → **motor içinde tekrar tekrar tetikle; ateşleniyor mu, sönüyor mu, mide bulandırıyor/girdiyi bloke ediyor mu doğrula.**
- Tuzaklar: oyuncu gövdesini sallamak (collision bozulur), her kare rastgele sarsıntı, scaled timer ile hitstop (hiç dönmez), her yerde lineer tween, rutin eylemlerde juice (erişilebilirlik/netlik sorunu).

**`create-game-assets`** — mevcut görsel tutarlılık önce; teknik brief (boyut, kamera, çözünürlük, palet, filtreleme, kare sayısı); görsel sistem (şekil dili, siluet, değer yapısı, palet rolleri, malzeme, ışık, detay yoğunluğu, kenar, hareket karakteri — **sanatçı adı yerine somut özellikler**); **hero asset/stil panosunu gerçek oyun ölçeğinde ve gerçek arka planda onayla**; **deterministik normalizasyon** (kırp, boyutlandır, pivot, dilimle, adlandır, sıkıştır — "üretilmiş grid, şeffaflık, dikiş, pivot, topoloji veya boyuta incelemeden güvenme"; Python ile boyut/alfa/renk sınırı kontrolü, dama tahtası üzerinde **contact sheet**); **oyun içinde yerel çözünürlükte doğrulama** (siluet, ölçek, animasyon kararlılığı, dikiş, okunabilirlik, collision uyumu, bellek, sıkıştırma artefaktı).

## 6. Değerlendirme
**Güçlü:** Somut sayılar ve teknikler (%70/%95 boşluk, 100 ms / 5–8 tepki, trauma², 0.08 sn hitstop); level design için flood-fill ulaşılabilirlik; asset üretiminde deterministik doğrulama; router kalıbı; skill doğrulayıcı ve sürüm sabitleme; Apache-2.0 (atıfla uyarlanabilir).
**Zayıf:** Motor bağımsız disiplin skill'leri kısa (her biri ~1 sayfa); Unity bölümü sadece 8 teknik skill; MCP ile gözlem/iterasyon döngüsü yok; eval/kalite ölçümü yok.

## 7. v3'e alınacaklar
| Fikir | v3'te nereye |
|---|---|
| **Boşluk %70 güvenli / %95 zorlayıcı** metrik kuralı | `METRICS.template.md` + `craft-level-design` §1.8 + `lint_scene`'e boşluk kontrolü (ileride) |
| **Ritim veri olarak** (0–1 yoğunluk dizisi, asla yüksekte düz kalmaz) | `LEVEL-CARD` intensity curve'ü 1–5 yerine 0–1 sayısal + kontrol kuralı |
| **Flood-fill ile kilit/yetenek sırasına göre ulaşılabilirlik** | `measure_critical_path`'e gating desteği (ileride) + `craft-level-design` checklist |
| game-feel sayıları ve teknikleri (100 ms / 5–8 tepki, trauma decay, hitstop, squash, ease) | F5 `craft-game-feel` — gstack `/feel-pass` teşhisiyle birleştir (teşhis + uygulama) |
| "Görseli simülasyondan ayır" | `craft-gameplay-code` kuralı |
| Hero asset'i gerçek ölçekte onayla + deterministik normalizasyon + contact sheet | İleride asset skill'i (F5+) |
| Router: motor tekil, disiplin/tür eklenir | `/start-task` sınıflandırmasına "tür" eklentisi (genre skill'leri ileride) |
| `validate-skills.py` + sürüm sabitleme | Skill'lerimiz için yapısal doğrulayıcı (eval sistemine) |
