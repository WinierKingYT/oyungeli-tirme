# AI Game Development OS v3

Claude Code ile Unity'de oyun geliştirirken yapay zekanın işini **daha kaliteli** yapmasını sağlayan çalışma ortamı: oyun tasarımı zanaatı, oyunu çalıştırarak doğrulama, ölçülen kalite ve sahibin zevkini öğrenen hafıza.

Bu bir onay sistemi değildir. v1.2'nin lease/seal/receipt yönetişimi `archive/v1.2/` altında ve `v1.2-final` etiketinde durur.

## Neler var
| Katman | Nerede | Ne yapar |
|---|---|---|
| Güvenlik tabanı | `.claude/hooks/guard.py`, `.claude/settings.json` | Sadece geri dönüşü zor hataları engeller: Unity `.meta`/sahne/prefab dosyalarını metin olarak düzenleme, `git push`, toplu silme. Proje ayarları için sorar. |
| Geri bildirim | `.claude/hooks/after_edit.py`, `session_context.py` | C# değişince doğrulama merdivenini hatırlatır, serileştirilmiş alan kaybını uyarır; oturum başında `memory/STATE.md`'yi yükler. |
| Oyun bağlamı | `game/` | Oyun kimliği, ölçüler, sahibin karar vereceği sorular, sistem ve level kartları. |
| Zanaat skill'leri | `.claude/skills/` | Sistem tasarımı, level design, gameplay kodu, oyun hissi; tasarım akışları (`/design-system`, `/design-level`), `/start-task`, `/unity-test`, `/playtest`, `/feedback`. |
| Eleştirmenler | `.claude/agents/` | `design-critic`, `level-critic` (taze bağlam, tavsiye niteliğinde), `eval-scorer` (kör puanlama). |
| Hafıza | `memory/` | Durum, kararlar, beğenilen/beğenilmeyen örnekler, playtest notları. |
| Ölçüm | `evals/` | Puanlama tablosu, görev seti, sonuçlar, skill geliştirme süreci. |
| Unity araçları (taslak) | `docs/v3/unity-tools/` | Ekran görüntüsü seti, sahne lint, kritik yol ölçümü, görüntü farkı, yerleşim planı doğrulama. Unity projesi kurulunca derlenecek. |

## Kurulum (Unity projesi)
Rehber: `docs/v3/unity-template/STRUCTURE.md`. Özet: Unity 6 LTS, resmî Unity plugin'i (`/plugin install unity@unity-agent-plugin`), proje kapsamlı Unity köprüsü, `.gitignore`/`.gitattributes` şablonları, bu reponun `.claude/`, `CLAUDE.md`, `game/`, `memory/`, `evals/` klasörleri. Proje yolunda ASCII olmayan karakterlerden kaçının.

## Güvenlik hakkında dürüst not
Hook'lar bir **emniyet kemeridir, güvenlik sınırı değildir**: zaman aşımında engellemez, bilinçli bir kullanıcıyı durdurmaz. Asıl güvence git'tir — ayrı branch, küçük commit'ler, push'u sahibin yapması, her şeyin geri alınabilmesi.

İnceleme seviyeleri de adıyla anılır:
| Seviye | Ne | Bağımsızlık |
|---|---|---|
| Öz-kontrol | İşi yapan agent'ın kendi kontrolü | yok |
| Taze bağlam | Aynı model ailesinden, konuşmayı görmemiş agent | kısmi (aynı model hataları paylaşabilir) |
| Farklı model | Başka model/aile | daha yüksek |
| Ölçüm | Test, lint, NavMesh, görüntü farkı gibi deterministik kontrol | yüksek |
| Sahip | Oyunu oynayan ya da kararı veren insan | en yüksek |
Kritik sistemler (kayıt, ağ, ekonomi) en az **ölçüm** veya **sahip** seviyesinde doğrulanır.

## Kanıtlanmış mı?
Henüz değil. Sıradaki iş: aynı görevleri "düz Claude + Unity köprüsü" ile ve v3 ile yaptırıp kör puanlamak (`evals/`). Sistem bundan sonra doküman yazarak değil, ölçerek geliştirilir.

## Belgeler
- Vizyon ve yol haritası: `docs/VISION-V3.md`
- Araştırma raporları: `docs/research/` (özet: `00-SUMMARY.md`)
- Taslak ve yerleşim tablosu: `docs/v3/README.md`

## Test
```
python tests/hooks_smoke.py
```
