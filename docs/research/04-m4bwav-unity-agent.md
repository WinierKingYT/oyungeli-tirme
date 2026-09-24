# Araştırma 04 — m4bwav/unity-agent

Kaynak: https://github.com/m4bwav/unity-agent (varsayılan branch `master`) · Lisans: MIT · İnceleme: 2026-09-24 (README, `unity-agent-workflow`, `unity-agent-mcp`, `unity-agent-headless` SKILL.md'leri)

## 1. Ne yapıyor?
AI agent'ların Unity'yi **güvenli ve doğrulanabilir** şekilde sürmesi için beş "evergreen" (kendini güncel tutan) skill. Claude Code, Copilot, Cursor, Codex. Kök: `.claude-plugin/`, `ai-docs/`, `skills/`, `tests/`, `AGENTS.md`, `CLAUDE.md`.

| Skill | Hız katmanı | İçerik |
|---|---|---|
| `unity-agent-cli` | hızlı | Resmî Unity CLI (beta, Temmuz 2026) + deneysel `com.unity.pipeline` (editörü yerel HTTP ile sürme) |
| `unity-agent-headless` | orta | Batchmode, editör açıkken **offline compile** |
| `unity-agent-mcp` | hızlı | Hangi MCP köprüsü, ne zaman MCP, istemci yapılandırması, tuzaklar, ölçülmüş bağlam maliyeti |
| `unity-agent-workflow` | orta | Doğrulama merdiveni, YAML/.meta kuralları, test hijyeni |
| `unity-agent-packages` | orta | UPM paket işlemleri (editör UI olmadan) |

Her skill'in yanında: `SKILL.md`, **`RESEARCH.md` (tarihli kaynaklar)**, `CHANGELOG.md`, **`TESTS.md` (eval baseline)**. "Evergreen": düzeltme gelirse `LEARNINGS.md` güncellenir, çelişki varsa `evergreen.json` versiyonu artırılır.

**Skill eval yöntemi:** tetikleme prompt'ları, **tetiklememesi gereken tuzak prompt'lar (decoys)**, **cevap metniyle değil trace'teki araç çağrısıyla kanıtlanan eylem vakaları**, ve baseline.

## 2. ⭐ Doğrulama merdiveni (verification ladder)
"Hatayı yakalayan **en alt basamağı** seç." Kural: *"Bir skill transkript dışındaki kanıtla geçer, kendi 'yaptım' iddiasıyla asla."*
| Basamak | Yakaladığı | Hız | Yöntem |
|---|---|---|---|
| 1 | Mantık, matematik, durum | saniye | Motorsuz C# üzerinde `dotnet test` (**Humble Object** kalıbı) |
| 2 | Tüm assembly'lerde C# hataları | **~3 sn** | `dotnet build Assembly-CSharp.csproj` offline |
| 3 | Editor API, serileştirme, play mode | dakika | `unity test --mode EditMode\|PlayMode` |
| 4 | Çalışma zamanı görünüm ve log | çağrı başı saniye | Canlı editör: yeniden derle, konsol, **ekran görüntüsü** |
| 5 | UX ve his | kullanıcının zamanı | Editörde manuel doğrulama |
Ek kural: **Başarısız test asla "zaten vardı" değildir** — düzelt ya da çıktısıyla raporla.

## 3. Güvenlik kuralları (workflow)
- Editör projeyi açıkken `.unity`, `.prefab`, `.asset`, `.controller`, `.mat` YAML'ını **elle veya regex ile düzenleme**; script, importer, menü öğesi veya `-executeMethod` kullan.
- Her `Assets/` dosyasının `.meta`'sı var; birlikte taşı/commit et. **Var olan `.meta`'yı yeniden üretmek GUID'i (asset kimliğini) yok eder.**
- Gameplay mantığı düz C#, veri enjekte edilir, çıkışlar `event Action<...>`; MonoBehaviour ince kabuk.
- **İçerik (kart, item, level) metin kaynaklarından importer ile gelir;** üretilmiş asset'i elle düzenlemek bir sonraki importta ezilir.
- Domain reload (derleme, play mode, paket) köprüleri yeniden başlatır ve static'leri temizler → **düzenlemeleri toplu yap, bir kez doğrula.**
- Serileştirilmiş alan eklemek güvenli; **yeniden adlandırmak/silmek veriyi sessizce düşürür** → hepsini işaretle.
- Sormadan asmdef, DI container, Addressables veya paket ekleme.
- Önce repo kurallarını oku (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `CODEMAP.md`, `.claude/skills`).

## 4. MCP köprüsü seçimi
Karar ağacı (en alt uygun basamak): **1) Sadece kod** (köprü yok; gameplay ve araç işi için en iyisi) → **2) CLI** (JSON çıktılı shell, config yok, boşta sunucu yok; bağlam darsa varsayılan) → **3) MCP** (shell'i iyi çalıştıramayan istemciler veya tur başına çok sahne incelemesi).
| Sunucu | Güçlü | Kısıt |
|---|---|---|
| Resmî `unity mcp` (Unity 6+) | ~150 araç, ücretsiz, resmî | Deneysel; manifest'te versiyon sabitle. Kurulum: `unity pipeline install` → `unity mcp configure <client>` |
| CoplayDev/unity-mcp (2021.3–6.x) | En yaygın, 47 araç, eski Unity desteği | Python 3.10+ + uv; HTTP köprüsü domain reload'da düşer |
| IvanMurzak/Unity-MCP (Unity 6) | 70+ araç, **`[AiTool]` dekoratörü**, oyun içi (Player) çalışma | **Proje yolunda boşluk olmamalı** |
| CoderGamester/mcp-unity (6+) | WebSocket 8090 | v1.5.0+ proje başı token |
**Bağlam maliyeti:** resmî sunucu tam yüklenirse ~149 araç, **~24k token şema (~96 KB)**. Claude Code şemaları erteler (sadece isim listesi öder); Claude Desktop/Cursor tamamını öder. **Sadece proje kapsamında kaydet** (`claude mcp add --scope local`), global değil.
**Tuzaklar:** domain reload tüm köprüleri yeniden başlatır (bir kez tekrar dene) · compile hatası Pipeline sunucusunu bloklar (Safe Mode) → önce C#'ı düzelt · odaklanmamış editör tick'i durdurabilir (resmî: `set_autotick`) · modal diyaloglar her şeyi bloklar → `-automated` ile başlat · **Unity 6.0.5–6.5 + AI Assistant 2.13-pre kilitlenmesi (UUM-132096)** → sadece MCP için Assistant paketini kurma, CLI kullan.
Kurulum doğrulama: `claude mcp list` + salt okur bir araç çağrısı (editor status).

## 5. Headless
- **Offline compile:** `dotnet build` Unity'nin ürettiği `Assembly-CSharp.csproj` üzerinde ~3 sn, editör açıkken bile. SDK: sistem veya `<editor>/Editor/Data/DotNetSdk/dotnet.exe` (Unity 6'da 8.0.x). Sınır: csproj son editör senkronunun anlık görüntüsü — editör dışında eklenen yeni dosyalar görünmez.
- Batchmode: `Unity.exe -batchmode -nographics -quit -projectPath ... -executeMethod Class.Method -logFile ...`; bayraklar `-quitTimeout`, `-accept-apiupdate`, `-ignorecompilererrors`, `-stackTraceLogType Full`.
- **`-runTests` ile `-quit` verme** (testler çalışmadan çıkar).
- Testler: `-runTests -testPlatform EditMode|PlayMode -testResults ... [-testFilter "A;B;!Skip"]`; NUnit XML `<test-run total passed failed skipped>`.
- **Çıkış koduna güvenme:** `Editor.log`'da `error CS`, `Scripts have compiler errors`, `Aborting batchmode due to failure` arar; başarı işareti `Exiting batchmode successfully`. Eski sürümler compile hatasında bile 0 döndürüyordu.
- Tuzaklar: `Temp/UnityLockfile` varsa batchmode çalışmaz · editör kapandıktan sonraki ilk batchmode Library'yi yeniden import eder (dakikalar) · `ELECTRON_RUN_AS_NODE=1` Hub CLI'yi bozar · `net9.0` test projeleri gömülü 8.0 SDK ile derlenmez.
- Rapor formatı: **2 satır** — çalıştırılan komut + kanıt (JSON `ok` + belirleyici sayılar veya dosya/satırlı ilk hata).

## 6. Güçlü yanlar
- Pratik, ölçülmüş, tarihli; gerçek tuzaklar (bug ID'si dahil).
- Doğrulama merdiveni hız/kapsam dengesini çok iyi kuruyor; "kanıt transkript dışında" ilkesi.
- Skill eval'i (decoy + trace kanıtı) bizim eval sistemimizden daha titiz.
- Humble Object + importer yaklaşımı AI dostu içerik üretimi.

## 7. Zayıf yanlar
- Sadece teknik iş akışı; tasarım kalitesi yok.
- PowerShell script'leri Windows ağırlıklı.
- Küçük proje, topluluk belirsiz.

## 8. v3'e alınacaklar (öneri — yüksek öncelik)
| Fikir | v3'te nereye |
|---|---|
| **Doğrulama merdiveni** (5 basamak, en alt uygun basamak) | `craft-gameplay-code` §3 feedback loop'u bununla değiştir; `after_edit.py` hatırlatmasına basamak 2 (offline compile) ekle |
| Offline `dotnet build` ~3 sn compile | `/unity-test`'e "hızlı compile" modu; editör kapalıyken bile anında geri bildirim |
| Çıkış kodu yerine log işaretleri | `/unity-test` §1'i düzelt (şu an çıkış koduna dayanıyor) |
| `-runTests` + `-quit` yasağı, lockfile, ilk import gecikmesi | `/unity-test` tuzaklar bölümü |
| "Başarısız test asla 'zaten vardı' değildir" | `/unity-test` §4'teki "pre-existed → report" kuralını sıkılaştır |
| Domain reload: toplu düzenle, bir kez doğrula | `craft-level-design` MCP prosedürü + `after_edit.py` (her MCP yazmasından sonra değil, grup sonunda kontrol) |
| Alan yeniden adlandırma/silme veri kaybı uyarısı | `guard.py`/`after_edit.py`: `.cs` diff'inde `[SerializeField]` silinmesi/yeniden adlandırılması uyarısı |
| İçerik importer'la metinden | Level/veri üretiminde "kaynak metin → importer → asset" kalıbı (`craft-gameplay-code`) |
| MCP: proje kapsamı kayıt, karar ağacı (kod → CLI → MCP), bilinen tuzaklar | F1 kurulum rehberi + `STRUCTURE.md` |
| IvanMurzak: yolda boşluk olmamalı | Kurulum kontrol listesi (bizim yolumuzda Türkçe karakter var — ayrıca test edilmeli) |
| Skill eval: decoy prompt + trace kanıtı + baseline; RESEARCH.md tarihli kaynak | `evals/`'a skill tetikleme testleri; her skill'e kaynak listesi |
| LEARNINGS.md | `/feedback` + hata günlüğü ile birleştir |
