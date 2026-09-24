# v3 taslak içerikleri

Bu klasör, [VISION-V3.md](../VISION-V3.md) F1–F2 içeriğinin taslaklarıdır. Hook'lar devre dışı bırakıldığında (F0) hedef konumlarına taşınır.

> **2026-09-24 (F0):** Unity projesi gerektirmeyen tüm taslaklar hedef konumlarına taşındı. Burada yalnızca `unity-tools/` ve `unity-template/` kaldı; bunlar Unity projesi kurulunca (F1/F3) yerleştirilecek.

| Taslak | Hedef konum | Faz |
|---|---|---|
| `game/IDENTITY.template.md` | `game/IDENTITY.md` | F1 |
| `game/SYSTEM-CARD.template.md` | `game/systems/_TEMPLATE.md` | F1 |
| `game/LEVEL-CARD.template.md` | `game/levels/_TEMPLATE.md` | F1 |
| `game/METRICS.template.md` | `game/METRICS.md` | F1 |
| `memory/STATE.template.md` | `memory/STATE.md` | F1 |
| `skills/craft-system-design.md` | `.claude/skills/craft-system-design/SKILL.md` | F2 |
| `skills/design-system-flow.md` | `.claude/skills/design-system/SKILL.md` | F2 |
| `agents/design-critic.md` | `.claude/agents/design-critic.md` | F2 |
| `evals/RUBRIC.md` | `evals/RUBRIC.md` | F2 |
| `evals/TASKS.md` | `evals/TASKS.md` | F2 |
| `agents/eval-scorer.md` | `.claude/agents/eval-scorer.md` | F2 |
| `evals/RESULTS.template.md` | `evals/RESULTS.md` | F2 |
| `memory/EXAMPLE.template.md` | `memory/EXAMPLES/_TEMPLATE.md` | F4 |
| `memory/PLAYTEST.template.md` | `memory/PLAYTESTS/_TEMPLATE.md` | F4 |
| `skills/playtest.md` | `.claude/skills/playtest/SKILL.md` | F4 |
| `skills/feedback.md` | `.claude/skills/feedback/SKILL.md` | F4 |
| `memory/DECISIONS.template.md` | `memory/DECISIONS.md` | F1 |
| `skills/start-task.md` | `.claude/skills/start-task/SKILL.md` | F1 |
| `skills/craft-gameplay-code.md` | `.claude/skills/craft-gameplay-code/SKILL.md` | F1 |
| `skills/craft-level-design.md` | `.claude/skills/craft-level-design/SKILL.md` | F3 |
| `skills/design-level-flow.md` | `.claude/skills/design-level/SKILL.md` | F3 |
| `unity-tools/Runtime/*.cs` | `Assets/_Project/Scripts/Tools/` | F3 |
| `unity-tools/Editor/*.cs` | `Assets/_Project/Scripts/Editor/` | F3 |
| `agents/level-critic.md` | `.claude/agents/level-critic.md` | F3 |
| `unity-template/gitignore.txt` | `<UnityProject>/.gitignore` | F1 |
| `unity-template/gitattributes.txt` | `<UnityProject>/.gitattributes` | F1 |
| `unity-template/STRUCTURE.md` | kurulum rehberi (F6 init script'inin girdisi) | F1 |
| `skills/unity-test.md` | `.claude/skills/unity-test/SKILL.md` | F1 |
| `hooks/guard.py` | `.claude/hooks/guard.py` | F0 |
| `hooks/after_edit.py` | `.claude/hooks/after_edit.py` | F0 |
| `hooks/settings.draft.json` | `.claude/settings.json` (replaces v1.2) | F0 |
| `CLAUDE.draft.md` | `CLAUDE.md` (replaces v1.2 router) | F0 |
| `hooks/session_context.py` | `.claude/hooks/session_context.py` | F0 |
| `skills/_quality-preamble.md` | `.claude/skills/_quality-preamble.md` | F1 |
| `game/JUDGMENT-GAPS.template.md` | `game/JUDGMENT-GAPS.md` | F1 |
| `skills/craft-game-feel.md` | `.claude/skills/craft-game-feel/SKILL.md` | F3 (F5'ten öne alındı) |
| `evals/triggers/` (F2'de yazılacak) | `evals/triggers/<skill>.md` | F2 |
| `skills/<skill>.reference/*.md` | `.claude/skills/<skill>/reference/*.md` (SKILL.md içindeki `reference/...` bağlantıları bu hedefe göre yazıldı) | skill'le aynı |
| `evals/SKILL-DEVELOPMENT.md` | `evals/SKILL-DEVELOPMENT.md` | F2 |

Skill ve agent içerikleri İngilizce yazılır (model performansı); kullanıcıya yanıt dili Türkçedir.

## Performans araştırması sonrası (2026-09-24, rapor 13)
| # | Değişiklik | Dosyalar |
|---|---|---|
| 1 | Skill'ler inceltildi: kısa ana akış + `reference/` dosyaları | `craft-level-design`, `craft-game-feel`, `craft-system-design`, `craft-gameplay-code` (+ `.reference/`) |
| 2 | Açıklamalar yönlendirme kuralı: 3. şahıs, ne + ne zaman + Türkçe/İngilizce tetikleyiciler | tüm skill frontmatter'ları |
| 3 | CLAUDE.md "Unity gotchas" odaklı; Unity kuralları tek yerde, iş akışı listesi kaldırıldı (skill açıklamaları yönlendiriyor) | `CLAUDE.draft.md` |
| 4 | Görsel yargı kuralları: odaklı tek soru + kart, ölçülebilen koda, `inferred-visual` etiketi | `craft-level-design` ref, `level-critic`, `_quality-preamble`, CLAUDE |
| 5 | Görüntü farkı aracı | `unity-tools/Editor/ImageDiff.cs` |
| 6 | Plan → doğrula → uygula (layout.json) | `unity-tools/Editor/LayoutPlan.cs`, `craft-level-design` |
| 7 | Yargıç ayrımı: alternatifleri taze bağlamlı critic puanlar (Mode A) | `design-system-flow`, `design-level-flow`, critic'ler, `_quality-preamble` |
| 8 | Model yönlendirme: critic'ler `opus`, scorer `sonnet` | agent frontmatter'ları |
| 9 | Denge araması (hedef fonksiyon + parametre taraması + LLM oyuncu sınırı) | `craft-system-design` ref |
| 10 | Önce eval + Claude A/B + model testi süreci | `evals/SKILL-DEVELOPMENT.md` |
| 11 | Önbellek dostu: sabit içerik sabit, STATE hook ile | `SKILL-DEVELOPMENT.md`, CLAUDE |
| 12 | Best-of-N sadece Full modda (akışlarda 3 alternatif + bağımsız puanlama) | akışlar |

## Araştırma sonrası işlenen değişiklikler (2026-09-24)
Kaynak: [docs/research/00-SUMMARY.md](../research/00-SUMMARY.md)
| # | Değişiklik | Dosyalar |
|---|---|---|
| 1 | Doğrulama merdiveni, offline compile, log işaretleri, batchmode tuzakları | `craft-gameplay-code`, `unity-test`, `after_edit.py` |
| 2 | Oynanabilirlik rubriği (6 boyut /12), zaman çizelgesi, zorlayıcı sorular, hipotez, regresyon | `playtest` |
| 3 | `craft-game-feel` (teşhis /14 + teknikler + doğrulama) | yeni skill |
| 4 | Ortak kalite ilkeleri (dalkavukluk yok, gözlem/çıkarım, durum satırı) | `_quality-preamble`, critic'ler, CLAUDE |
| 5 | Level sayıları: %70/%95, 0–1 yoğunluk dizisi, kilit sırasına göre ulaşılabilirlik | `craft-level-design`, `LEVEL-CARD`, `METRICS` |
| 6 | Formüller (değişken tablosu), uç durumlar, kabul kriterleri, tek kaynak, NO DATA, ADD/KEEP/DEFER/CUT, Twist | `SYSTEM-CARD`, `craft-system-design`, `IDENTITY` |
| 7 | Script rolleri, sahne sözleşmesi | `craft-gameplay-code`, `LEVEL-CARD` |
| 8 | Test tasarımı, görsel doğrulama testleri, geçici Editor script | `craft-gameplay-code`, `unity-test` |
| 9 | Eval: build health / visual usability / intent alignment, level kriterleri, skill tetikleme testleri | `RUBRIC`, `eval-scorer` |
| 10 | Quick varsayılan, kritik sistemler full | `design-system-flow`, `IDENTITY` |
| 11 | Karar boşlukları dosyası | `JUDGMENT-GAPS.template.md` |
| 12 | MCP seçimi, resmî plugin, yol testi, köprüden bağımsız araçlar | `STRUCTURE.md`, `unity-tools/README.md` |
| 13 | SessionStart (STATE enjekte, kartsız kod, açık karar boşluğu) + PreCompact hook | `session_context.py`, `settings.draft.json` |
| 14 | Teknik Unity API içeriği resmî plugin'e bırakıldı | `craft-gameplay-code`, CLAUDE |
