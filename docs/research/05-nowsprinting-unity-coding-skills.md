# Araştırma 05 — nowsprinting/unity-coding-skills

Kaynak: https://github.com/nowsprinting/unity-coding-skills (branch `master`, 95 commit) · Yazar: Koji Hasegawa (Unity Test Helper paketlerinin yazarı) · Lisans: Unlicense (kamu malı) · 20 yıldız · İnceleme: 2026-09-24 (README, `unity-yaml-editing-guide`, `test-designing-guide`, `plan-feature`, `edit-scene`, `test-writing-guide`)

## 1. Ne yapıyor?
Claude Code plugin'i: Unity projesinde **test-önce** iş akışıyla otonom kodlama. Bakımı kolay testler, üretim kodundan önce. Gereksinimler: JetBrains Rider 2026.2.1+ MCP Server, "MCP Server Extension for Unity", UTF Analyzers (editör donmasını tespit), opsiyonel Test Helper ve UI Test Helper paketleri. **Not:** Unity MCP değil, **Rider'ın MCP'si** üzerinden çalışıyor (`run_method_in_unity`, `get_unity_compilation_result` araçları).

Yapı: `.claude-plugin/`, `agents/`, `skills/`.

## 2. Skill'ler (11) ve agent'lar (3)
| Skill | Görev |
|---|---|
| `plan-feature` | Plan modunda test-önce planlama orkestrasyonu |
| `fix-bug` | Test güdümlü hata teşhisi ve çözümü |
| `code-writing-guide` | Unity C# kuralları |
| `test-designing-guide` | Bakımı kolay test tasarımı |
| `test-writing-guide` | Unity Test Framework kuralları |
| `refine-tests` | Test kodunu kurallara göre gözden geçirir |
| `run-tests` | UTF testlerini çalıştırır |
| `resolve-diagnostics` | IDE uyarı/hatalarını düzeltir |
| `edit-scene` | `.unity`/`.prefab` değiştirme (Editor script ile) |
| `unity-yaml-editing-guide` | YAML asset düzenleme kuralları |
Agent'lar: `test-designer` (planlamada test vakaları), `failing-test-writer` (önce başarısız test yazıp doğrular), `test-deduplicator` (tekrarlayan testleri siler).

## 3. `plan-feature` akışı
1. Plan modu kontrolü; bug ise `/fix-bug`'a yönlendir.
2. Keşif (agent'larla kod tabanı).
3. Tasarım (Plan agent): **test edilebilirlik önce** — "üretim kodunun kullandığı aynı dikişten (seam) test et", private'ı açmaya zorlama; bağımlılıklar arayüzle enjekte; alt mantığı ancak 3+ parametre kombinasyon patlaması yaratıyorsa ayrı sınıfa çıkar; "TBD" gereksinimleri yapısal engel değilse sessizce dışarıda bırak.
4. Test tasarımı (`test-designer`): 5 katman — Editor, Unit, Integration, **Visual**, Manual. Test edilebilirlik değerlendirmesi PASS/WARN/FAIL.
5. **Test edilebilirlik geri döngüsü:** FAIL → en fazla 1 kez tasarımı revize et; ikinci FAIL'de dur, kullanıcıya 3 çözüm yolu sun.
6. Review → plan dosyası (Context | Implementation Design | Test Cases | Trade-offs | Development Workflow) → plan modundan çık.

## 4. Test tasarım ilkeleri
- Katmanlar: editor testleri (eklenti kodu, asset doğrulama) · unit (doğrudan çağrı) · integration (sahne/prefab davranışı) · **görsel doğrulama (ekran görüntüsü analizi)** · manuel (sadece öznel duyusal yargı).
- **Bir test = bir denklik bölümü = bir kesin beklenen sonuç.** Beklenen sonucu parametreleştirme; sadece aynı sonucu paylaşan vakalar tek parametreli testte birleşir.
- İsimlendirme: `<Method>_<Koşul>_<Beklenen>` (unit/editor), `<Koşul>_<Beklenen>` (integration/visual); Beklenen somut durum (`IsInteractable`), koşullu ifade değil.
- Aynı SUT'un kapsamını EditMode ve PlayMode arasında bölme.
- Spesifikasyon geçersiz girdi davranışını tanımlamıyorsa **tahmin etme, kullanıcıya sor.**
- **Gereksinim izlenebilirliği:** her gereksinimin **aynı katmanda bir tanık testi** olmalı (unit test UI gereksinimine tanık olamaz).

## 5. Test yazım kuralları (öne çıkanlar)
- Test öncesi Play Mode'u durdur; `.meta` oluşturma.
- GameObject yaratan testlerde `[CreateScene]`; test dikişleri `#if UNITY_INCLUDE_TESTS` içinde.
- Kategoriler: `Integration`, **`VisualVerification`**, `Acceptance`, `Internal`, `IgnoreCI` (zamanlama/çözünürlük hassas).
- Çok kareli testlerde sabit kare sayısı bekleme; durum makinesi bitene kadar `await Awaitable.NextFrameAsync()`.
- **UI yerleşim assert'leri** (görsel değil deterministik): `Is.WithinScreen`, `Is.FullyWithin(container)`, `Is.Not.Overlapping`, `Is.Not.TextOverflowing`; `GameObjectFinder(reachable: true)` ile raycast erişilebilirliği; önce `Canvas.ForceUpdateCanvases()` + bir kare.
- Gerçek event hattını kullanan operatörler: `UguiClickOperator`, `UguiTextInputOperator`.
- **Görsel doğrulama testi:** `[TakeScreenshot]` veya `ScreenshotHelper.TakeScreenshotAsync()` ile görüntü → `[Description("...")]` içinde **neyin doğrulanacağı** (okunabilirlik, kontrast, tipografi, render kalitesi) → `[Category("VisualVerification")]` → **Assert yok** (AI/insan görüntüyü açıklamaya göre değerlendirir).

## 6. Sahne düzenleme (`edit-scene`)
- `.unity`/`.prefab` elle düzenlenmez. Bunun yerine: `Assets/UnityCodingSkills/Editor/` altına **geçici Editor script** yaz (`public static` metot) → `run_method_in_unity` ile çalıştır → `EditorSceneManager.SaveScene()` / `PrefabUtility.SaveAsPrefabAsset()` ile kaydet ("script çıkışında kirli sahne kalmasın") → log'da `"type": "Error"` yok ve `git diff` ile doğrula → **script ve .meta'sını sil.**
- Prefab düzenleme: `LoadPrefabContents()` → değiştir → `SaveAsPrefabAsset()` → `UnloadPrefabContents()`.
- **Unity araçlarını paralel çağırma** (domain reload çakışması); Play Mode'da script çalıştırma.
- Her etkileşimli objeye test için benzersiz hiyerarşik isim.

## 7. YAML düzenleme (sınırlı izin)
- **Sadece** ScriptableObject `.asset` (class 114) ve Material `.mat` (class 21) doğrudan düzenlenebilir; `.unity`, `.prefab`, `.meta` asla.
- Başlık iki satır birebir (`%YAML 1.1`, `%TAG !u! tag:unity3d.com,2011:`); kanonik anchor (`--- !u!114 &11400000`); ScriptableObject alan sırası sabit; `m_Name` = dosya adı; referans `{fileID, guid, type}`; 2 boşluk, LF, BOM'suz UTF-8; non-ASCII `\uXXXX`.
- Sonra Unity re-import + `get_unity_compilation_result` ile doğrula.

## 8. Değerlendirme
**Güçlü:** Test tasarımında gerçek uzmanlık (denklik bölümü, aynı katman tanık testi, test edilebilirlik geri döngüsü); görsel doğrulama testlerini assert'siz, açıklamalı ekran görüntüsü olarak kurması; geçici Editor script ile sahne düzenleme kalıbı; ScriptableObject YAML'ı için güvenli, dar izin.
**Zayıf:** Rider'a bağımlı; oyun tasarımı yok; küçük topluluk.

## 9. v3'e alınacaklar
| Fikir | v3'te nereye |
|---|---|
| **Görsel doğrulama testi** (`[TakeScreenshot]` + `[Description]` + kategori, assert yok) | `craft-gameplay-code` + `/unity-test`: görsel testler çıktı klasörüne, AI Description'a göre değerlendirir — `capture_review_set` ile aynı felsefe, oyun içi testlere taşınır |
| Geçici Editor script ile sahne/prefab düzenleme (yaz → çalıştır → kaydet → sil) | `craft-level-design` MCP prosedürüne "MCP aracı yoksa" yedek yol |
| **ScriptableObject `.asset` YAML'ını dar kurallarla düzenlemeye izin** | `guard.py`'de `.asset` şu an tamamen yasak → sadece class 114 ScriptableObject'lere kurallı izin düşünülebilir (denge verisi hızlı ayarı için değerli); karar bekliyor |
| Unity araçlarını paralel çağırmama | `CLAUDE.md` Unity kuralları |
| Test tasarımı: denklik bölümü, `<Method>_<Koşul>_<Beklenen>`, aynı katman tanık testi, belirsiz girdide sor | `craft-gameplay-code` §4'e ekle |
| Test edilebilirlik PASS/WARN/FAIL + en fazla 1 geri döngü | `/design-system` → uygulama geçişinde |
| UI yerleşim assert'leri (overlap, overflow, within screen, reachable) | F5 `craft-ux-onboarding` |
| `failing-test-writer` / `test-deduplicator` agent fikri | İleride; şimdilik skill kuralı yeterli |
| Test Helper / UI Test Helper paketleri | F1 önerilen paketler listesine |
