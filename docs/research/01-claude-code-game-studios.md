# Araştırma 01 — Claude Code Game Studios

Kaynak: https://github.com/Donchitos/Claude-Code-Game-Studios · Lisans: MIT · ~25.4k yıldız, ~3.6k fork · İnceleme: 2026-09-24 (README, skill listesi, `design-system`, `balance-check` skill'leri, `level-designer` agent'ı; WebFetch özetleri üzerinden — dosyaların tamamı satır satır okunmadı)

## 1. Ne yapıyor?
Tek bir Claude Code oturumunu "oyun stüdyosu" yapısına sokan bir şablon repo. Amaç: tek sohbetin yapısızlığından doğan hataları (hardcoded değer, dokümansız tasarım, kötü mimari) organizasyon hiyerarşisi ve rol uzmanlığıyla önlemek. Repo klonlanıp üzerine oyun yapılıyor (`/start` ile başlanıyor).

## 2. Yapı
```
.claude/agents/     49 agent (markdown + YAML frontmatter)
.claude/skills/     74 skill (her biri klasör)
.claude/hooks/      14 script (bash; Windows Git Bash birincil platform)
.claude/rules/      13 yol-kapsamlı kural
.claude/docs/templates/  39 şablon, workflow-catalog.yaml (7 fazlı boru hattı), effects-map.md (ayar şeması)
project.yaml        tek doğru kaynak: motor, rigor, override'lar
design/ docs/ src/ assets/ tests/ prototypes/ production/
"CCGS Skill Testing Framework/"  skill'lerin kendilerini test eden çerçeve
```

## 3. Agent hiyerarşisi (49)
- **Direktörler (3, Opus):** creative-director (vizyon), technical-director (mimari), producer (koordinasyon, çatışma çözümü).
- **Lead'ler (8):** game-designer, lead-programmer, art-director, audio-director, narrative-director, qa-lead, release-manager, localization-lead.
- **Uzmanlar (38):** gameplay/engine/ai/network/tools-programmer; systems/level/economy/ux-designer, prototyper; technical-artist, sound-designer, world-builder, ui-programmer, performance-analyst; qa-tester, accessibility, analytics, devops, security, live-ops; writer, community-manager; motor uzmanları (godot/unity/unreal-specialist).
- **Model ataması:** direktörler Opus; 16 uzman Sonnet/Haiku; kalanı oturum modeli.
- **Koordinasyon:** dikey delegasyon (direktör→lead→uzman), yatay danışma (bağlayıcı karar yok), anlaşmazlık ortak üst direktöre, disiplinler arası değişiklik `producer` + `/propagate-design-change`.
- **İşbirliği protokolü:** Sor → 2–4 seçenek sun (artı/eksi) → kullanıcı karar verir → taslak göster → onaysız yazma yok.

## 4. Skill'ler (74) — kategoriler
- Başlangıç: `start`, `help`, `project-stage-detect`, `setup-engine`, `adopt`, `settings`
- **Tasarım:** `brainstorm`, `map-systems`, `design-system`, `quick-design`, `propagate-design-change`, `review-all-gdds`
- Sanat/UX: `art-bible`, `asset-spec`, `asset-audit`, `ux-design`, `ux-review`
- Mimari: `create-architecture`, `architecture-decision`, `architecture-review`, `create-control-manifest`
- Hikaye/sprint: `create-epics`, `create-stories`, `dev-story`, `sprint-plan`, `sprint-status`, `story-readiness`, `story-done`, `estimate`
- **Review/analiz:** `design-review`, `code-review`, `balance-check`, `content-audit`, `scope-check`, `perf-profile`, `tech-debt`, `gate-check`, `consistency-check`, `security-audit`
- QA: `qa-plan`, `smoke-check`, `soak-test`, `regression-suite`, `test-setup`, `test-helpers`, `test-evidence-review`, `test-flakiness`, `skill-test`, `skill-improve`
- Üretim: `milestone-review`, `retrospective`, `bug-report`, `bug-triage`, `reverse-document`, `playtest-report`
- Yayın: `release-checklist`, `launch-checklist`, `changelog`, `patch-notes`, `hotfix`, `day-one-patch`
- Yaratıcı: `prototype`, `vertical-slice`, `onboard`, `localize`
- **Takım orkestrasyonu:** `team-combat`, `team-narrative`, `team-ui`, `team-release`, `team-polish`, `team-audio`, `team-level`, `team-live-ops`, `team-qa` (çok agent'lı özellik geliştirme)

### İncelenen skill'lerin detayı
**`design-system`** (GDD'yi bölüm bölüm yazar)
- Akış: Parse → bağlam topla → doğrula → iskelet → bölümleri yaz → review → bitir.
- 8 bölüm: Overview, Player Fantasy, Detailed Design, **Formulas**, **Edge Cases**, Dependencies, **Tuning Knobs**, **Acceptance Criteria**. Rigor'a göre 5 veya 8 zorunlu.
- Her bölüm için döngü: bağlam → sorular → seçenekler → karar → taslak → onay → yaz.
- Bölüm bazlı uzman delegasyonu: Player Fantasy → creative-director; Design/Formulas/Edge → systems-designer; Acceptance → qa-lead; görsel/ses → art/audio director.
- Kurallar: **formüller değişken tablosu olmadan yazılamaz**; **edge case'ler kesin çözümle** yazılır; **registry çakışmaları işaretlenir** (`design/registry/entities.yaml` — değerlerin tek kaynağı); **design review taze oturumda** yapılır (bağımsızlık).
- Kesinti kurtarma: `production/session-state/active.md`.

**`balance-check`**
- 6 faz: alan tespiti (Combat/Economy/Progression/Loot) → veri topla (`assets/data/`, `design/balance/`, registry) → alan özel analiz (DPS baskınlığı, kaynak akışı, ilerleme eğrisinde ölü bölge/güç sıçraması) → rapor (aykırı değer tablosu, **dejenere stratejiler**, öncelikli öneriler) → düzelt ve yeniden doğrula.
- **Kritik kapı:** veri yoksa tahminle doldurmaz, `NOT ASSESSED — NO DATA` der (sahte-temiz rapor önleme).

**`level-designer` agent**
- Soru önce; 2–4 seçenek + teoriye dayalı gerekçe; iskelet önce, bölüm bölüm onay.
- Level dokümanı: tema, tahmini süre, ASCII/düzyazı yerleşim diyagramı, kritik ve opsiyonel yol, karşılaşma listesi, **ritim grafiği**, anlatı vuruşları, ses/müzik ipuçları. Sightline ve yönlendirme analizi sorumluluklarında.
- Kapsam dışı: oyun geneli sistem tasarımı, hikaye kararları, motor uygulaması.

## 5. Hook'lar (14)
`validate-commit.sh` (hardcoded değer, TODO formatı, JSON, GDD bölümleri), `validate-push.sh` (korumalı branch uyarısı), `validate-assets.sh` (asset isim/JSON), `session-start.sh` (branch + son commit'ler), **`detect-gaps.sh`** (kod var ama tasarım dokümanı yoksa uyarır), **`pre-compact.sh` / `post-compact.sh`** (bağlam sıkıştırmada ilerleme notlarını korur, `active.md`'den geri yükletir), `notify.sh` (Windows toast), `session-stop.sh` (oturum arşivi), `log-agent*.sh` (agent denetim izi), **`validate-skill-change.sh`** (skill değişince `/skill-test` önerir). İlgisiz dosyalarda hemen `exit 0` — sürtünmesiz.

## 6. Kurallar (13, yol kapsamlı)
`src/gameplay/**` veri odaklı, delta time, UI referansı yok · `src/core/**` sıcak yolda allocation yok · `src/ai/**` performans bütçesi, debug edilebilirlik · `src/networking/**` sunucu otoriter, versiyonlu mesaj · `src/ui/**` oyun durumu sahiplenmez, lokalizasyona hazır · `design/gdd/**` zorunlu bölümler, formül formatı, edge case · `design/narrative/**` lore tutarlılığı · `assets/data/**` JSON şeması · `assets/shaders/**` · `tests/**` · **`prototypes/**` gevşek kurallar, README ve hipotez zorunlu.** Unity'de kök `Assets/`.

## 7. Ayar sistemi (`project.yaml`)
- **`modes.rigor`:** `minimal` (varsayılan) / `standard` / `full`. Alt düğmeler: `workflow`, `docs.density`, `qa.level`, `story_granularity`, `review_mode` (full/lean/solo), `team.size`.
- Kişisel override: `project.local.yaml` (gitignore) → `review_mode`, `automation` (AI ne sıklıkla durup sorar).
- **`system_overrides`:** tek bir sistemi (ör. combat) daha yüksek rigor'da tutma.
- `testing.strict`: kanıt eksikliği tür bazında hata mı uyarı mı.

## 8. Kalite kapısı
- Oyuncuya görünen değişiklik içeren story, **oyun çalıştırılıp gözlenmeden ve ekran görüntüsü `production/qa/evidence/`'a konmadan** kapanmaz. "Parse check bir çalıştırma değildir" — her rigor seviyesinde geçerli.
- Tasarım teorileri: MDA, Self-Determination Theory, Flow, Bartle tipleri.

## 9. ⭐ En değerli bulgu: kendi ölçümleri
README'de: aynı brief'ten dört oyun farklı rigor seviyeleriyle yapılmış.
| Rigor | Kod öncesi doküman | Süre |
|---|---|---|
| minimal | 1 | 0 dk |
| standard | 30 | 58 dk |
"İki kör değerlendirici ve bir insan playtest'i **standard build'i sonuncu** sıraladı — fazladan 29 doküman izlenebilirlik getirdi, daha iyi oyun değil." (Metodoloji detayı, full sonuçları ve oyun adı verilmemiş.)
→ Bu, bizim v1.2 deneyimimizi ve v3'ün "kalite dokümandan değil, zanaat + gözlem + iterasyondan gelir" tezini doğrudan destekliyor. Varsayılanı `minimal` yapmışlar.

## 10. Güçlü yanlar
- Rigor'u tek düğmeyle ayarlama ve **sistem bazlı override** (kritik sistemi sıkı, gerisini hafif tutma).
- Formül → değişken tablosu, edge case → kesin çözüm, tuning knob'ları ve kabul kriteri zorunlu bölümler.
- **Registry** (`entities.yaml`): tasarım değerlerinin tek kaynağı; tutarsızlık tespiti.
- `balance-check`'in "veri yoksa değerlendirme yapma" dürüstlüğü; dejenere strateji avı.
- `detect-gaps`, compaction hook'ları, skill'leri test eden framework (`skill-test`, `skill-improve`).
- Görünür değişiklikte ekran görüntüsü zorunluluğu.
- Review'un taze oturumda yapılması.
- Kendi yaklaşımlarını ölçmüş ve sonucu dürüstçe yayınlamışlar.

## 11. Zayıf yanlar / riskler
- 49 agent + 74 skill çok büyük; bağlam ve bakım yükü. Rol taklidi (stüdyo hiyerarşisi) kaliteyi değil süreci yapılandırıyor — kendi ölçümleri de bunu gösteriyor.
- Varsayılan protokol her bölümde kullanıcı onayı istiyor → yavaş, bizim "onay istemiyorum" hedefimize ters.
- Level design dokümana dayalı (ASCII diyagram); motor içi gözlem, ekran görüntüsüyle iterasyon, NavMesh ölçümü gibi somut doğrulama yok (story kapanışındaki ekran görüntüsü kanıt amaçlı, iterasyon amaçlı değil).
- Unity desteği tek bir `unity-specialist` agent'ından ibaret; MCP entegrasyonu yok.
- Hook'lar bash; Windows'ta Git Bash gerektiriyor.
- Kalite ölçümü tek seferlik, metodolojisi yayınlanmamış.

## 12. v3'e alınacaklar (öneri)
| Fikir | v3'te nereye |
|---|---|
| Rigor düğmesi + sistem bazlı override (minimal varsayılan) | `/design-system` Quick/Full modu → `project` ayarına bağla; kritik sistemler (save, network) için override |
| GDD bölümleri: Formulas (değişken tablosu), Edge Cases (kesin çözüm), Tuning Knobs, Acceptance Criteria | `SYSTEM-CARD` şablonuna ekle |
| Registry: tasarım değerlerinin tek kaynağı | ScriptableObject config'lerden otomatik üretilen `game/registry` + tutarlılık kontrolü |
| `balance-check` + "NO DATA" kuralı + dejenere strateji avı | `craft-economy-balance` (F5) ve `lint_data` |
| `detect-gaps` (kod var, kart yok) | `after_edit`/session-start hook'una hafif uyarı |
| Pre/post-compact hook ile durumu koruma | `memory/STATE.md`'yi compaction öncesi güncelleyen hook |
| Skill test framework (`skill-test`/`skill-improve`) | Bizim eval sistemine skill yapısal testi olarak ekle |
| Review'u taze bağlamda yapma | Zaten `design-critic` alt agent → teyit |
| Prototip klasörü: gevşek kural + hipotez zorunlu | `_Prototype` kuralı |
| Kendi ölçümleri (rigor ↑ ≠ kalite ↑) | VISION-V3 gerekçesine kaynak olarak ekle |

**Almayacaklarımız:** 49 agent'lık hiyerarşi, her bölüm için kullanıcı onayı, sprint/story/epic üretim bürokrasisi, yayın/live-ops skill'leri (şimdilik).
