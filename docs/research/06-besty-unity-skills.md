# Araştırma 06 — Besty0728/Unity-Skills

Kaynak: https://github.com/Besty0728/Unity-Skills (branch `main`) · Lisans: MIT (+ SIL OFL CJK font) · ~1.8k yıldız, 165 fork · Unity 2022.3+ · İnceleme: 2026-09-24 (README, kök `SKILL.md`, skill klasör listesi, `perception`, `scene-contracts`, `script-roles` modülleri)

## 1. Ne yapıyor?
Unity Editor içinde çalışan bir **HTTP (REST) sunucusu** + agent'a nasıl kullanacağını anlatan SKILL.md'ler. MCP değil: agent, Python istemcisi (`scripts/unity_skills.py`) veya doğrudan HTTP ile yerel sunucuya istek atar. 56 C# dosyası → **~805 REST skill, 54 kategori**; ayrıca eylemsiz **danışma (advisory) modülleri** (`*-design`, `manual-*` vb.). Domain reload'dan sonra 15 dk'ya kadar oturum sürekliliği.

Kurulum: UPM `https://github.com/Besty0728/Unity-Skills.git?path=/SkillsForUnity`; editörde `Window > UnitySkills > AI Config` ile Claude Code, Codex, Cursor, OpenCode vb. için tek tık kurulum.

## 2. Yapı
```
SkillsForUnity/                       UPM paketi (com.besty.unity-skills)
  unity-skills~/SKILL.md              ana protokol
  unity-skills~/scripts/unity_skills.py  istemci
  unity-skills~/skills/<modül>/SKILL.md  modül dokümanları
  Editor/Skills/SkillsHttpServer.cs, SkillRouter.cs, WorkflowManager.cs, [50+ kategori]
  Editor/UI/                          editör paneli
docs/SETUP_GUIDE.md, OPERATING_MODES.md
```

## 3. Kategoriler (örnek sayılar)
GameObject 19, Component 14, Prefab 11, Scene 10, **Perception 18**, **Validation 16**, **Workflow 40** (snapshot/undo/batch), NavMesh 10, Physics 12, Camera 12 (ekran görüntüsü), Light 11, Material 21, ProBuilder 22, Terrain 10, **Smart 10** (SQL benzeri sorgu, otomatik yerleşim, snapping), Test 13, Console 10, Debug 11, Profiler 10, Optimization 10, Cleaner 10, ScriptableObject 13, Script 12, Animator 10, Timeline 12, Cinemachine 34, UI Toolkit 31, Netcode 39, ShaderGraph 23, DOTween 21, YooAsset 40, XR 22, Addressables 8, Package 11 …

## 4. Danışma modülleri (gerçek klasör adları)
`architecture`, `patterns`, `scriptdesign`, **`script-roles`**, `testability`, `asmdef`, `async`, `adr`, `blueprints`, **`scene-contracts`**, **`project-scout`**, `performance`, `inspector`, `yaml-editing`, `manual-component`, `manual-gameobject`, `manual-material`, `manual-scene`, `addressables-design`, `dotween-design`, `netcode-design`, `primetween-design`, `qframework-design`, `shadergraph-design`, `unitask-design`, `yooasset-design`, `pico-design`. (README'deki "28 advisory module" sayısı bu listeyle kabaca örtüşüyor; README özetindeki başka isimli liste doğrulanamadı.)

Örnekler:
- **`script-roles`:** "AI her şeyi MonoBehaviour yapmasın diye" script listesini açık rollere çevirir: MonoBehaviour köprüsü, ScriptableObject config/veri, saf C# domain/servis, presenter/controller, durum makinesi düğümü, installer/bootstrap. Korkuluklar: her şeyi MonoBehaviour yapma; geçici runtime durumunu ScriptableObject'e zorlama. Her rol için gerekçe (sorumluluk, bağımlılıklar, alternatif neden uymaz).
- **`scene-contracts`:** sahne kompozisyonunu açık kurallara bağlar: hangi kök objeler olmalı, hangi bileşenler, hangi bağlantı Inspector'da/kodda, sahneyi kim başlatır, runtime'da ne spawn edilir, erken doğrulama varsayımları. İlke: **"Runtime Find zincirleri yerine açık sahne bağlantısı."** Çıktı: sahne obje sözleşmesi, bootstrap sırası, Inspector bağlantı listesi, doğrulama kuralları, gizli bağımlılık riskleri.
- **`perception`** (salt okur): `scene_summarize` (hızlı özet), `scene_analyze` (bulgu + öneri), `scene_health_check` (eksik script, derin hiyerarşi, boş düğüm), `scene_context` (AI için yapılandırılmış hiyerarşi/bileşen/referans), `hierarchy_describe`, `scene_export_report`, `scene_dependency_analyze`, `script_dependency_graph` (N adım), `project_stack_detect` (pipeline, UI, paketler, klasör yapısı), **`scene_spatial_query`** (koordinat/obje yakınındaki objeler).

## 5. Ana protokol (SKILL.md) — öne çıkanlar
- **El sıkışma:** `GET /health` → mod (approval/auto/bypass), `surfaceProfile` (full/guide/noSceneAuthoring), proje adı doğrulama; oturumda bir kez `GET /skills/meta`.
- **En ucuzdan keşif:** `GET /skills/recommend?intent=...` (4–14 KB) → kategori şeması (~32 KB) → tüm özet (~143 KB). `?wire=v2` ile sıkıştırılmış format.
- **Üç kutsal kural:** (1) emin olmadığın çağrıdan önce **`?mode=dryRun`** — parametreyi isimden tahmin etme; (2) **yazmaları toplu yap** (`POST /skills/batch`, 50 adıma kadar, `continueOnError`, adımlar arası `$ref`, hatada otomatik geri alma, `?diff=1` net değişim raporu); (3) **yanıt yankısına değil, okuma skill'leriyle editörde doğrula.**
- Güvenlik: Approval (ilk yazmada kullanıcı izni) / Auto (yüksek riskli işlemler otomatik bloklanır) / Bypass. **Denetim günlüğü** `Library/UnitySkillsAudit.jsonl`. Domain reload'a dayanıklı 5 tür **snapshot**, `workflow_undo_task` ile tek işlem geri alma.
- Hata kodları: `MODE_RESTRICTED`, `SURFACE_EXCLUDED` (konfigürasyon, hata değil), `MISSING_PARAM`, `TARGET_NOT_FOUND`.

## 6. Değerlendirme
**Güçlü:** Çok geniş editör otomasyonu; dryRun + batch + transaction + snapshot/undo gerçekten güvenli; bağlam maliyetini düşüren "recommend" keşfi; salt okur algı (perception) araçları ve uzamsal sorgu; `script-roles` ve `scene-contracts` gibi AI'ın tipik hatalarını hedefleyen danışma modülleri.
**Zayıf:** MCP değil (kendi REST protokolü); 805 skill bakım ve güven riski; oyun tasarımı kalitesi yok (teknik/mimari odaklı); Çin ekosistemi paketlerine (YooAsset, HybridCLR, QFramework) ağırlık.

## 7. v3'e alınacaklar
| Fikir | v3'te nereye |
|---|---|
| **`script-roles`**: kod yazmadan önce her script'e rol ata | `craft-gameplay-code` §1'e "rol tablosu" adımı (MonoBehaviour köprü / SO config / saf C# / presenter / state / bootstrap) |
| **`scene-contracts`**: sahne sözleşmesi, Find yerine açık bağlantı | `LEVEL-CARD`'a "Scene contract" bölümü + `lint_scene`'e "beklenen kök/bileşen" kontrolü |
| **Perception önce** (özet, sağlık kontrolü, `scene_context`) | `/start-task` scout adımı: hangi MCP'yi seçersek seçelim eşdeğer salt okur araçları kullan |
| `scene_spatial_query` | `craft-level-design` metrik geçişi ("bu noktanın 2 m yakınında ne var?") |
| dryRun → batch → okuyarak doğrula | Tüm MCP yazma işlemleri için genel kural (`CLAUDE.md`) |
| Snapshot/undo, denetim günlüğü | MCP işlemleri öncesi git commit / sahne yedeği kuralı (F3) |
| "En ucuzdan keşif" bağlam stratejisi | `/start-task` bağlam bütçesi ilkesiyle aynı; teyit |
| Alternatif köprü olarak değerlendirme | MCP seçiminde aday (özellikle editör otomasyonu genişliği için) |
