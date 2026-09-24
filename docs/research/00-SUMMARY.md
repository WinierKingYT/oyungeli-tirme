# Araştırma özeti — AI ile Unity oyun geliştirme sistemleri

Tarih: 2026-09-24 · Kapsam: 15+ repo ve 4 akademik kaynak · Yöntem: README ve seçili SKILL.md dosyaları (WebFetch). Dosyaların tamamı satır satır okunmadı; sayılar repoların kendi beyanıdır.

## Raporlar
| # | Kaynak | Tür | v3 için değer |
|---|---|---|---|
| [01](01-claude-code-game-studios.md) | Donchitos/Claude-Code-Game-Studios (~25k★) | Stüdyo hiyerarşisi, 49 agent, 74 skill | Orta-yüksek: rigor düğmesi, GDD bölümleri, registry, **kendi ölçümleri: fazla doküman = daha kötü oyun** |
| [02](02-gstack-game.md) | fagemx/gstack-game | Yargı + puanlama skill'leri | **Çok yüksek:** `/feel-pass`, `/build-playability-review`, anti-sycophancy, AI yargı boşlukları |
| [03](03-unity-official-plugin-and-skills.md) | Unity resmî plugin + skills | Teknik Unity skill'leri, CLI | **Yüksek (altyapı):** teknik skill yazmayacağız, bunu kuracağız |
| [04](04-m4bwav-unity-agent.md) | m4bwav/unity-agent | Güvenli Unity iş akışı | **Çok yüksek:** doğrulama merdiveni, ~3 sn offline compile, MCP tuzakları |
| [05](05-nowsprinting-unity-coding-skills.md) | nowsprinting/unity-coding-skills | Test-önce Unity | Yüksek: görsel doğrulama testi, test tasarımı, geçici Editor script ile sahne düzenleme |
| [06](06-besty-unity-skills.md) | Besty0728/Unity-Skills (~1.8k★) | REST editör otomasyonu, 805 skill | Orta-yüksek: `script-roles`, `scene-contracts`, perception, dryRun+batch |
| [07](07-awesome-gamedev-agent-skills.md) | gamedev-skills/awesome-gamedev-agent-skills (~1.1k★) | 73 çok motorlu skill | Yüksek: level design ve game feel sayıları, flood-fill ulaşılabilirlik |
| [08](08-claude-unity-game-studio.md) | IdoCohen560/claude-unity-game-studio | Derleme paket | Düşük |
| [09](09-cc-plugin-unity-gamedev.md) | tjboudreaux/cc-plugin-unity-gamedev | Middleware skill'leri | Düşük |
| [10](10-small-repos.md) | HermeticOrmus, openagenticgame-gdd, davila7 | Eğitim, GDD şablonu, persona | Düşük |
| [11](11-unity-mcp-servers.md) | Resmî MCP, IvanMurzak, CoplayDev, CoderGamester | MCP köprüleri | **Yüksek (seçim):** resmî birincil, `[AiTool]` yedek |
| [13](13-performance-and-quality-techniques.md) | Anthropic dokümanları, VideoGameQA-Bench, insan+AI test, RuleSmith, best-of-N | Performans/kalite teknikleri | **Çok yüksek:** skill inceltme, VLM sınırları, plan→doğrula→uygula, yargıç ayrımı, denge araması |
| [12](12-academic-and-benchmarks.md) | arXiv 2410.02829, 2402.18659, OpenGame, GamingAgent | Araştırma | Yüksek: execution-grounded doğrulama, VLM yargısı, LLM = zorluk ölçer |

## Ana bulgular
1. **Kimse v3'ün tam kombinasyonunu yapmamış.** Mevcut sistemler ya (a) rol/süreç yapısı (Studios), ya (b) teknik Unity bilgisi (resmî, Besty, tjboudreaux), ya (c) yargı/puanlama (gstack-game) sunuyor. **Tasarım zanaatı + motor içinde gözlem + ölçülmüş kalite (eval) + sahibin zevkini öğrenen hafıza** birleşimi boşta.
2. **Süreç ağırlığı kaliteyi artırmıyor** — Studios'un kendi kör testi (standard rigor build'i sonuncu). v1.2'den v3'e geçiş kararımızı doğruluyor.
3. **Çalıştırarak doğrulama belirleyici** — m4bwav (merdiven, "kanıt transkript dışında"), OpenGame (execution-grounded + VLM), Studios ("parse check bir çalıştırma değildir"), gstack (build/video olmadan feel/playability yok).
4. **Kalite, çıpalı sayısal rubriklerle ölçülüyor** — gstack'in 0/1/2 tanımlı boyutları, ms eşikleri; OpenGame-Bench'in 3 ekseni.
5. **Somut sayılar kaliteyi yükseltiyor** — %70/%95 boşluk, 100 ms / 5–8 tepki, >0.5 sn ölü zaman, 90 sn onboarding, trauma² sarsıntı, 0.08 sn hitstop.
6. **AI'ın yargı boşlukları belgelenmeli** (gstack) — türe göre ağırlık, "yeterli" eşikleri sahibin kararı.
7. **Teknik Unity bilgisini yazmak gereksiz** — resmî plugin var; bizim değerimiz tasarım ve kalite katmanı.

## v3'e önerilen değişiklikler (öncelik sırasıyla)
| # | Değişiklik | Etkilenen v3 dosyaları | Kaynak |
|---|---|---|---|
| 1 | Doğrulama merdiveni (5 basamak) + offline compile + log işaretleri | `craft-gameplay-code`, `/unity-test`, `after_edit.py` | 04 |
| 2 | Oynanabilirlik rubriği (6 boyut /12, Stranger/Opposite/Retention soruları, oturum zaman çizelgesi, hipotez doğrulama) | `/playtest`, `evals/RUBRIC.md` | 02 |
| 3 | `craft-game-feel`'i öne al: hedef his, 4 vuruş zinciri, ms eşikleri, /14 rubrik, kilitli sözlük + uygulama teknikleri | yeni skill | 02, 07 |
| 4 | Anti-sycophancy ortak preamble (yasak ifadeler, "gözlem mi çıkarım mı", "teşhis et reçete yazma") | tüm craft/critic içerikleri | 02 |
| 5 | Level design sayıları: %70/%95 boşluk, 0–1 yoğunluk dizisi, flood-fill gating | `craft-level-design`, `LEVEL-CARD`, `METRICS` | 07 |
| 6 | Sistem kartına Formulas (değişken tablosu), Edge Cases (kesin çözüm), Acceptance Criteria; registry fikri | `SYSTEM-CARD`, `craft-system-design` | 01 |
| 7 | `script-roles` ve `scene-contracts` | `craft-gameplay-code`, `LEVEL-CARD`, `lint_scene` | 06 |
| 8 | Görsel doğrulama testleri (`[TakeScreenshot]` + `[Description]`) ve test tasarım kuralları | `craft-gameplay-code`, `/unity-test` | 05 |
| 9 | Eval'e OpenGame üçlüsü (Build health / Visual usability / Intent alignment) + skill tetikleme testleri (decoy + trace kanıtı) | `evals/` | 12, 04 |
| 10 | Rigor düğmesi + sistem bazlı override (minimal varsayılan) | `/design-*` Quick/Full modu | 01 |
| 11 | `docs/JUDGMENT-GAPS.md`: sahibin karar vermesi gereken yerler | yeni doküman | 02 |
| 12 | MCP seçimi: resmî birincil, F3 araçları menü+statik metot (köprüden bağımsız), IvanMurzak yedek; F1'de Türkçe yol testi | `unity-tools/README.md`, `STRUCTURE.md` | 11, 03 |
| 13 | Pre/post-compact hook ile `STATE.md` koruma; `detect-gaps` (kod var kart yok) | hooks | 01 |
| 14 | Resmî Unity plugin'ini kurulum adımı yap; teknik API içeriğini kendi skill'lerimizden çıkar | `STRUCTURE.md`, `craft-gameplay-code` | 03 |

## Kullanım ilkesi
Bu kaynaklardan yöntem ve fikir öğreniyoruz; v3 içeriklerini kendi sözlerimizle yazıyoruz, metin kopyalamıyoruz. İlham alınan kaynaklar ilgili skill'lerde "Kaynaklar" satırında anılır.
