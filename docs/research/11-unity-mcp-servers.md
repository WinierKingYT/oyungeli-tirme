# Araştırma 11 — Unity MCP sunucuları (resmî, IvanMurzak, CoplayDev, CoderGamester)

İnceleme: 2026-09-24 (README'ler + rapor 04'teki karşılaştırma). Amaç: v3'ün L4 (gözlem) katmanı ve F3 araçları için köprü seçimi.

## 1. Özet tablo
| | Resmî `unity mcp` | IvanMurzak/Unity-MCP | CoplayDev/unity-mcp | CoderGamester/mcp-unity |
|---|---|---|---|---|
| Kaynak | Unity CLI + `com.unity.pipeline` (Unity 6+) | https://github.com/IvanMurzak/Unity-MCP | https://github.com/CoplayDev/unity-mcp | https://github.com/codergamester/mcp-unity |
| Lisans | Unity | Apache-2.0 | MIT | — |
| Popülerlik | resmî | ~4.3k yıldız | **~14.5k yıldız**, v10.0.0 (2026-06-30), Aura sponsorlu | — |
| Unity | 6.0+ | 6 (herhangi, plugin destekliyorsa) | **2021.3 – 6.x** | 6+ |
| Araç sayısı | **~150** (~24k token şema) | 70+ | 47 | — |
| Mimari | CLI / Pipeline HTTP | C# plugin + MCP sunucu; **editör + oyun içi (runtime)** | **Python sunucu (uv, 3.10+)** + Unity plugin | Node + Unity paketi, WebSocket 8090 |
| Özel araç | — | **`[AiTool]` attribute ile tek satır** | "Custom tools" çerçevesi | — |
| Ekran görüntüsü | var | var (Scene & Hierarchy) | var (editör ekran görüntüsü) | — |
| Testler / konsol | var | konsol, reflection ile metot çağırma, kod çalıştırma | test + profil + konsol + build | test, konsol |
| Bilinen kısıt | Deneysel; versiyonu sabitle; Unity 6.0.5–6.5 + AI Assistant 2.13-pre kilitlenmesi (UUM-132096) | **Proje yolunda boşluk olmamalı** | HTTP köprüsü domain reload'da düşer | v1.5.0+ proje başı token |

## 2. IvanMurzak/Unity-MCP — özel araç örneği
```csharp
[AiToolType]
public class CustomTools
{
    [AiTool("tool-id", Title = "Description")]
    [Description("Help text for LLM")]
    public string MyTask(string input)
    {
        return MainThread.Instance.Run(() => { /* Unity code */ });
    }
}
```
Kurulum: `.unitypackage`, `npm install -g unity-mcp-cli && unity-mcp-cli install-plugin`, veya `openupm add com.ivanmurzak.unity.mcp`. Runtime modu (`UnityMcpPluginRuntime`) derlenmiş oyunda AI kullanımına izin verir (canlı debug, NPC).

## 3. CoplayDev/unity-mcp
Kurulum: Package Manager git URL veya OpenUPM → `Window → MCP for Unity → Configure All Detected Clients`. En geniş Unity sürüm desteği ve topluluk. Kategoriler: sahne, script, asset, test/profil, build, özel araç, konsol, ekran görüntüsü.

## 4. Genel tuzaklar (rapor 04'ten)
- Domain reload tüm köprüleri yeniden başlatır → düzenlemeleri topla, bir kez doğrula, reload sonrası bir kez tekrar dene.
- Compile hatası köprüyü bloklar → önce C#.
- Odaklanmamış editör tick'i durdurabilir; modal diyaloglar bloklar (`-automated`).
- Claude Code MCP şemalarını erteler (sadece isim listesi) → çok araçlı sunucu bile bağlamı şişirmez; yine de **proje kapsamında kaydet** (`claude mcp add --scope local`).
- Araçlar paralel çağrılmamalı.

## 5. v3 için değerlendirme ve öneri
v3'ün ihtiyaçları: (a) konsol/compile okuma, (b) test çalıştırma, (c) **ekran görüntüsü**, (d) sahne/prefab işlemleri, (e) **kendi araçlarımızı** (`capture_review_set`, `lint_scene`, `measure_critical_path`) araç olarak kaydetme, (f) Türkçe karakterli proje yolu.

| İhtiyaç | Resmî | IvanMurzak | CoplayDev |
|---|---|---|---|
| a–d | ✓ | ✓ | ✓ |
| e: özel araç | menü/`-executeMethod`/C# çalıştırma ile dolaylı | **✓ en kolay (`[AiTool]`)** | ✓ (çerçeve) |
| f: yol | test edilmeli | boşluk yasak; Türkçe karakter test edilmeli | test edilmeli |
| Bakım güvencesi | en yüksek | orta-yüksek | yüksek (en büyük topluluk) |

**Öneri (doğrulama gerekli):**
1. Birincil: **resmî Unity CLI/MCP** + resmî plugin (rapor 03) — tek ekosistem, bakım güvencesi.
2. Özel araçlar: F3 araçlarımız zaten **menü öğesi + statik metot** olarak yazıldı → her köprüde çalışır (resmî CLI'de C# çalıştırma / `executeMethod`). Resmî yol özel araç kaydını zorlaştırırsa **IvanMurzak'ın `[AiTool]`** yolu ikinci seçenek.
3. Eski Unity sürümü gerekirse CoplayDev.
4. F1 kurulum testinde üç şeyi ölç: Türkçe karakterli yol, ekran görüntüsü kalitesi (URP), domain reload sonrası davranış.
