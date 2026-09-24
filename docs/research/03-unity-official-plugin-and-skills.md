# Araştırma 03 — Unity resmî: unity-agent-plugin + Unity-Technologies/skills

Kaynaklar:
- https://github.com/Unity-Technologies/unity-agent-plugin · v0.1.6-beta · 345 yıldız · Unity Companion License
- https://unity.com/blog/unity-plugin-for-claude-code · https://docs.unity.com/en-us/ai/unity-plugin/claude-code
- https://github.com/Unity-Technologies/skills · 967 yıldız · `npx skills add Unity-Technologies/skills`
İnceleme: 2026-09-24 (README'ler, blog, skill klasör listesi; tek tek SKILL.md içerikleri okunmadı)

## 1. Ne yapıyor?
Unity'nin Claude Code ve Codex için resmî plugin'i: Unity'nin belgelenmiş pratiklerine dayanan **teknik** skill'ler + Unity CLI ile editörü sürme. Kurulum:
```
/plugin marketplace add Unity-Technologies/unity-agent-plugin
/plugin install unity@unity-agent-plugin
```
Gereksinim: Unity 6+. Skill'ler `/unity:` önekiyle slash menüsünde görünür ve ilgili görev tarif edildiğinde otomatik tetiklenir. Yapı: `.claude-plugin/`, `.codex-plugin/`, `skills/`, `scripts/`, `assets/`.

## 2. Skill listesi (repo klasörleri, 31)
| Kategori | Skill'ler |
|---|---|
| Başlangıç/araç | `new-unity-project`, `unity-cli`, `unity-package-management`, `generate-editor-search-query` |
| UI/metin | `ui`, `ui-uitk`, `ui-ugui`, `ui-imgui` (bakım modunda), `optimize-text-mesh-pro`, `localization` |
| 2D | `2d-pixel-perfect`, `sprite-editor`, `sprite-segment-3x3grid`, `manage-sprite-atlas`, `tilemap-palette-create`, `tilemap-ruletile-createempty`, `tilemap-ruletile-createfromsegment` |
| Grafik | `urp-postprocessing`, `migrate-birp-to-urp`, `shader-graph-create-custom-node`, `validate-urp-render-graph-renderer-feature` |
| Ses | `audio-setup-mixers`, `optimize-audio`, `setup-vivox-voice-chat` |
| Sahne/oynanış | **`initialize-ai-navigation`**, **`physics-3d-collision`** |
| Gelir/live ops | `implement-in-app-purchases`, `levelplay-unity-integration`, `build-live-game`, `setup-multiplayer-services` |
| Platform | `optimize-web` |

`unity-cli` skill'i: terminalden, canlı editör dahil Unity'yi sürer — GameObject oluşturma/değiştirme, sahne ve asset düzenleme, hiyerarşi inceleme, **C# çalıştırma**; ayrıca editör kurulumu, lisans, build. (Bu oturumda ortamımızda da `unity-cli` skill'i yüklü.)

## 3. Unity-Technologies/skills
Ayrı ve daha genel koleksiyon: Unity CLI işlemlerini doğal dille çalıştırmaya yönelik skill'ler (sürüm kurma, proje listeleme, headless çalıştırma). 50+ agent ile uyumlu, `npx skills add` ile kurulur. Plugin'le ilişkisi README'de açık değil; muhtemelen plugin'in CLI skill'lerinin kaynağı/yakını.

## 4. Sınırlamalar (blog)
- **Gameplay kodu iskeleti yok.** Tasarım, level design, oyun hissi, denge yok.
- Beta; skill'ler zamanla eklenecek.
- Blog'un iddiası: resmî skill'ler hataları azaltır ve genel agent'a göre token verimliliği sağlar (sayı verilmemiş).

## 5. Değerlendirme
- **Güçlü:** resmî ve güncel teknik bilgi (URP, UI Toolkit, navigation, fizik, paketler); tek komutla kurulum; Codex desteği; CLI ile editör kontrolü.
- **Zayıf:** tamamen **teknik**; oyun tasarımı kalitesine dair içerik yok. Beta.

## 6. v3 için sonuç
| Karar | Gerekçe |
|---|---|
| **Unity teknik skill'lerini biz yazmayacağız; resmî plugin'i bağımlılık olarak kuracağız.** | Resmî, güncel, bakımı Unity'de. Bizim `craft-gameplay-code` sadece mimari/kalite kurallarına odaklanmalı, API rehberi olmamalı. |
| `unity-cli` + `initialize-ai-navigation` bizim F3 araçlarımızın (NavMesh, sahne işlemleri) altyapısı olabilir | `measure_critical_path` NavMesh bake adımını bu skill'e devredebilir |
| Kurulum rehberimize (F1/F6) "resmî plugin'i kur" adımı | `STRUCTURE.md` kontrol listesine eklenecek |
| v3'ün farkı net: **tasarım zanaatı + gözlem + eval + hafıza** | Resmî plugin bu alanı boş bırakıyor |
