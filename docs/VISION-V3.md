# AI Game Development OS v3 — Vizyon ve Birleşik Plan

Durum: `PROPOSED` · Tarih: 2026-09-24 · Sahip: proje sahibi

Bu doküman iki planı tek yerde birleştirir: (1) mevcut sistemin değerlendirmesi ve teknik temizlik planı, (2) yapay zekanın oyun geliştirme **kalitesini** artırma planı. Önceki plandan yalnızca gerekli olanlar alınmıştır.

---

## 1. Neden değişiyoruz?

v1.2 bir **onay sistemi** olarak büyüdü: AI bir şey yapar, test edilir, kaydedilir, onaylanır. Güvenliği iyi ama AI'ın ürettiği işin kalitesini artırmıyor. Ölçülen maliyet: 21 satırlık bir değişiklik için ~12 adım, 4 doküman, 2 review, ~7 sahip terminal adımı. Hiç gerçek Unity projesinde kullanılmadı.

v3'ün amacı farklı:

> **AI'ı, oyun geliştiren kişinin (tek başına ya da ekipte) yanında çalışan iyi bir oyun tasarımcısı, level designer ve gameplay mühendisi gibi çalıştırmak.** Kalite; bağlam, zanaat bilgisi, tasarım süreci, oyunu görerek iterasyon ve hafıza ile artar — onay kapılarıyla değil.

### Başarı ölçütü
Aynı görevi "düz Claude + Unity MCP" ile ve "Claude + Unity MCP + v3" ile yaptırıp kör puanlandığında v3 çıktısı, puanlama tablosunda (bölüm 4) belirgin şekilde daha yüksek olmalı. Olmuyorsa ilgili katman değiştirilir veya atılır.

---

## 2. AI oyun işinde neden vasat kalıyor? (çözülecek problemler)

| # | Problem | Belirti | v3 katmanı |
|---|---|---|---|
| P1 | Oyunun kimliğini bilmiyor | Jenerik, "her oyuna uyan" çözümler | L1 Bağlam |
| P2 | Zanaat bilgisi yüzeysel | Level = koridor + düşman; ekonomi = rastgele sayılar | L2 Zanaat |
| P3 | Tek seferde cevap veriyor | Alternatif yok, eleştiri yok | L3 Süreç |
| P4 | Sonucu görmüyor | "Yaptım" diyor ama oynanışta çalışmıyor | L4 Gözlem |
| P5 | Hafızası yok | Aynı hataları tekrar ediyor, önceki kararları unutuyor | L5 Hafıza |
| P6 | Projeyi kırabiliyor | `.meta`/GUID, ProjectSettings, save formatı bozulması | L0 Güvenlik |

---

## 3. Mimari: 6 katman

```
L5 Hafıza      ─ playtest notları, kararlar, iyi/kötü örnekler
L4 Gözlem      ─ Unity MCP: ekran görüntüsü, metrik, bot, simülasyon
L3 Süreç       ─ /design-* akışları: çeşitlendir → puanla → eleştir → düzelt
L2 Zanaat      ─ disiplin skill'leri: sistem, level, gameplay kodu, his, UI/UX
L1 Bağlam      ─ oyun kimliği, sistem/level kartları, sözlük
L0 Güvenlik    ─ hafif deny kuralları + compile/test döngüsü (onay YOK)
```

### L0 — Güvenlik ve teknik taban (önceki plandan kalanlar)
Amaç: sadece geri dönüşü zor hataları önlemek; akışı yavaşlatmamak.
- **Deny kuralları** (settings.json permissions, basit hook): `.meta` dosyasına elle yazma, `.unity`/`.prefab` YAML'ına metin düzenleme (MCP kullan), `git push`, `ProjectSettings/**` değişikliğinde kullanıcıya sor.
- **Otomatik geri bildirim döngüsü:** `.cs` yazılınca compile hataları (MCP konsol / Editor.log) AI'a geri verilir; `/unity-test` batchmode EditMode/PlayMode çalıştırır ve özetler.
- **Git güvenliği:** her iş kendi branch'inde / worktree'de; küçük commit'ler; sahip merge eder. Kötü bir AI oturumu tek komutla geri alınır.
- **Unity repo şablonu:** `.gitignore`, `.gitattributes` (LF + LFS + UnityYAMLMerge), Force Text serileştirme, asmdef iskeleti (`_Project`, `_Prototype`, `Tests.EditMode`, `Tests.PlayMode`).
- **Kaldırılanlar:** lease, seal, hash'li READY/ACCEPT receipt'leri, zorunlu bağımsız onay, 136 dokümanlık süreç seti. Git geçmişinde ve `archive/` altında durur.

### L1 — Oyun bağlamı
Her işte otomatik yüklenen, kısa ve keskin bilgi. Uzun doküman değil, **yoğun kart**.
- `game/IDENTITY.md` (≤1 sayfa): vizyon cümlesi, 3–5 tasarım sütunu, hedef his (fantezi), hedef oyuncu, referans oyunlar ve neyi onlardan aldığımız, **yapmayacaklarımız**.
- `game/systems/<SYS>.md` kart: amaç, oyuncu fantezisi, girdiler/çıktılar, ayar parametreleri, bağlı sistemler, açık sorular.
- `game/levels/<LVL>.md` kart: amaç, öğretilen/sınanan mekanik, ritim eğrisi, kritik yol, önemli anlar.
- `game/GLOSSARY.md`: oyuna özel terimler (AI ve ekip aynı dili konuşsun).
- Ekip modu: kartlar ortak "tek doğru kaynak"; her kartın sahibi var.

### L2 — Zanaat skill'leri (kalitenin çekirdeği)
Her skill: **ilkeler + kontrol listesi + anti-pattern'ler + iyi örnekler + çıktı formatı.**

| Skill | İçerik (özet) |
|---|---|
| `craft-system-design` | Core loop ve alt döngüler, kaynak kaynakları/yutakları (sources/sinks), pozitif/negatif geri besleme, anlamlı seçim, dominant strateji avı, sistem etkileşim matrisi, ayar parametreleri tablosu |
| `craft-level-design` | Kritik yol ve dallanma, ritim (gerilim/dinlenme), yönlendirme (ışık, çizgi, renk, işaret), görüş hattı ve kapanma, öğret → sına → birleştir → ustalaş, blockout önce/sanat sonra, geri dönüş/kestirme yolları, metrik ölçüleri (zıplama, koridor genişliği) |
| `craft-gameplay-code` | Unity'de veri odaklı tasarım (ScriptableObject), bileşen ayrımı, event'ler, ayarlanabilir parametreler inspector'da, test edilebilir saf C# mantık, performans bütçesi |
| `craft-game-feel` | Girdi tepkisi, anticipation/impact/recovery, ekran sarsıntısı, hitstop, ses zamanlaması, kamera |
| `craft-ux-onboarding` | Diegetik UI, bilgi hiyerarşisi, öğretici tasarımı, erişilebilirlik temel listesi |
| `craft-economy-balance` | Fiyat/kazanç eğrileri, enflasyon, zaman-değer, simülasyonla doğrulama |

Kaynak: kanonik oyun tasarımı bilgisi (ör. Schell'in lensleri, MDA çerçevesi, level design metrikleri) — skill'lere **özetlenerek ve kendi sözlerimizle** yazılır.

### L3 — Tasarım süreci (tek cevap yerine tasarımcı gibi düşünme)
Eleştiri bir onay kapısı değildir; tasarımı iyileştiren iterasyondur ve kullanıcıyı beklemez.

`/design-system`, `/design-level`, `/design-feature` akışları:
1. **Netleştir:** hedef, kısıtlar, IDENTITY'deki hangi sütuna hizmet ettiği (eksikse 1–3 soru sor).
2. **Çeşitlendir:** birbirinden gerçekten farklı 3 yaklaşım.
3. **Puanla:** rubrik (bölüm 4) + sütun uyumu; gerekçeli.
4. **Seç ve detaylandır:** kart formatında.
5. **Eleştir:** ayrı `design-critic` agent'ı (kıdemli tasarımcı rolü) — dominant strateji, sıkıcı an, kırılma noktası, kapsam riski arar.
6. **Düzelt** ve kararları + reddedilen alternatifleri L5'e yaz.
7. **Uygula ve gözlemle** (L4) → gerekiyorsa 5'e dön.

Agent'lar: `design-critic`, `level-critic`, `playtester` (bot/metrik raporunu oyuncu gözüyle yorumlar), `gameplay-engineer`.

### L4 — Gözlem: oyunu görerek iterasyon (Unity MCP)
- **Görsel:** level/sahne sonrası üstten plan görünümü + oyuncu gözünden birkaç ekran görüntüsü; AI kendisi inceler (okunabilirlik, yönlendirme, boş alan).
- **Uzamsal metrikler:** NavMesh ile kritik yol uzunluğu, ulaşılamayan alanlar, sıkışma noktaları, düşman/ödül yoğunluğu ısı haritası.
- **Otomatik oyuncu:** basit bot leveli dolaşır; süre, ölüm, takılma noktaları raporlanır.
- **Sistem simülasyonu:** ekonomi/denge mantığı saf C# olduğu için N oturum hızlı simüle edilir; dengesizlik sayılarla görünür.
- **Telemetri (playtest):** oyun içi olay kaydı → oturum sonu özet → L5.

### L5 — Öğrenen proje hafızası
- `memory/DECISIONS.md`: karar, neden, reddedilen alternatifler (kısa ADR).
- `memory/PLAYTESTS/`: notlar ve metrik özetleri.
- `memory/EXAMPLES/`: sahibin beğendiği çıktılar ("böyle olsun") ve beğenmedikleri ("böyle olmasın") — skill'ler bunlara referans verir.
- `memory/STATE.md`: ≤1 sayfa oturum devri (ne yapıldı, sıradaki, açık sorular). Uzun HANDOFF dokümanlarının yerine.

---

## 3A. MCP ile çalışırken kalite artırıcılar (ayrıntılı)

MCP AI'a "el" verir; aşağıdakiler o elin **usta** gibi çalışmasını sağlar. Her madde bir skill, agent, hook veya özel MCP aracı olarak uygulanır.

### A. İşe başlamadan: doğru hazırlık
| # | Ekleme | Ne yapar | Uygulama |
|---|---|---|---|
| A1 | **Görev bağlam paketi** | İşin türüne göre (sistem/level/UI/kod) otomatik yüklenen dosya seti: IDENTITY, ilgili kartlar, ilgili kararlar, iyi örnekler | `/start-task` skill + hook |
| A2 | **Sahne/proje keşfi** | AI değişiklik yapmadan önce MCP ile hiyerarşiyi, mevcut prefab'ları, script'leri, ScriptableObject'leri tarar; "zaten var olanı yeniden yazma" | `scene-scout` skill (salt okuma MCP) |
| A3 | **Varlık kataloğu** | Projedeki prefab/materyal/ses/animasyon listesi, etiketleri ve ölçüleri; AI "küp koymak" yerine doğru prefab'ı seçer | `catalog/ASSETS.md` otomatik üretilir (Editor script) |
| A4 | **Referans ve moodboard** | Referans oyun ekran görüntüleri + "neyi alıyoruz" notları; AI hedef görünüm ve hissi bilir | `game/references/` + skill'lerde referans adımı |
| A5 | **Ölçü standardı (metrics)** | Karakter boyu, zıplama yüksekliği/mesafesi, kapı/koridor genişliği, merdiven eğimi, kamera FOV; level ve prefab bunlara uyar | `game/METRICS.md` + level lint |
| A6 | **Görev ayrıştırma** | Büyük iş → küçük, doğrulanabilir adımlar; her adımın "bitti" gözlemi tanımlı | `/design-*` akışının 0. adımı |

### B. Yaparken: doğru yöntem
| # | Ekleme | Ne yapar | Uygulama |
|---|---|---|---|
| B1 | **MCP çalışma protokolü** | Sahne düzenlerken sıra: blockout → ölçü kontrolü → oynanış → ışık → süsleme; her adımda ekran görüntüsü | `craft-level-design` içinde prosedür |
| B2 | **Yüksek seviye özel MCP araçları** | AI'ın tek tek obje koyması yerine: `place_along_path`, `scatter_in_area`, `build_room(w,h,doors)`, `snap_to_grid`, `align_to_ground` | Özel Editor araçları (Unity MCP'ye özel tool olarak) |
| B3 | **Veri odaklı üretim** | Denge değerleri kodda değil ScriptableObject'te; AI tabloyu düzenler, kod değişmez | `craft-gameplay-code` kuralı + şablon |
| B4 | **Hazır kalıp kütüphanesi** | Sık kullanılan gameplay kalıpları (etkileşim, envanter, durum makinesi, kamera, kaydetme) test edilmiş şablon olarak | `templates/unity/` + skill referansı |
| B5 | **Adlandırma ve hiyerarşi düzeni** | Sahne kökleri (`_Env`, `_Gameplay`, `_Lighting`, `_UI`), prefab ve script isimlendirme | `unity.md` kuralı + lint |
| B6 | **Küçük adım + ara kontrol** | Her MCP yazma işleminden sonra konsol hatası ve görsel kontrol; hata varsa devam etmez | PostToolUse hook (mcp yazma araçları) |

### C. Yaptıktan sonra: doğru doğrulama (kendi kendini kontrol)
| # | Ekleme | Ne yapar | Uygulama |
|---|---|---|---|
| C1 | **Niyet ↔ sonuç kontrolü** | Kartta yazan amaç ile ekran görüntüsü karşılaştırılır: "Oyuncu kapıyı buradan görebiliyor mu?" | `level-critic` agent, görsel inceleme |
| C2 | **Çoklu kamera görüntüsü** | Üstten plan, oyuncu gözü (kritik yol üzerinde 5–10 nokta), giriş anı, hedef anı | Özel MCP aracı `capture_review_set` |
| C3 | **Önce/sonra karşılaştırma** | Değişiklik öncesi ve sonrası görüntüler yan yana; AI farkı yorumlar | Görüntüleri `reviews/<tarih>/` altına kaydet |
| C4 | **Level lint** | Ölçü ihlalleri, ulaşılamaz alan, collider'sız obje, kayıp referans, üst üste binmiş obje, ışıksız bölge | Editor script + MCP aracı `lint_scene` |
| C5 | **Veri lint** | ScriptableObject değer aralıkları, eksik referans, dominant seçenek (bir silah her açıdan üstünse) | `lint_data` aracı |
| C6 | **Performans kontrolü** | Draw call, tris, batch, GC alloc, frame süresi bütçeye göre | MCP profiler okuma + `PERFORMANCE` bütçesi |
| C7 | **Oynanış botu** | Kritik yolu NavMesh ile yürür; süre, takılma, düşme noktası raporu | `playtest_bot` aracı |
| C8 | **Denge simülasyonu** | Saf C# mantık üzerinde 1000 oturum; kaynak eğrisi, bitirme süresi, strateji dağılımı | EditMode test + rapor |
| C9 | **Altın sahneler (regresyon)** | Önemli sahnelerin referans görüntü ve metrikleri; değişiklik bunları bozarsa uyarı | `golden/` + batchmode karşılaştırma |

### D. Disipline özel kalite paketleri
| Disiplin | Eklenecek kontrol ve bilgi |
|---|---|
| Sistem tasarımı | Sistem etkileşim matrisi, kaynak akış diyagramı, "oyuncu bunu neden umursar?" testi, istismar (exploit) avı |
| Level design | Ritim grafiği (gerilim eğrisi), yönlendirme kontrol listesi (ışık/renk/çizgi/hareket), öğret-sına-ustalaş haritası, kestirme/geri dönüş |
| Gameplay kodu | Test edilebilir mantık/görünüm ayrımı, event akışı, ayar parametreleri inspector'da, null/edge case testleri |
| Oyun hissi | Girdi gecikmesi ölçümü, anticipation/impact/recovery kontrolü, geri bildirim katmanları (görsel+ses+kamera+titreşim) |
| Işık ve atmosfer | Okunabilirlik (oyuncu yolu aydınlık mı), renk paleti uyumu, gece/gündüz senaryoları |
| Ses | Olay → ses eşlemesi tablosu, eksik ses tespiti, mesafe/öncelik |
| UI/UX | Bilgi hiyerarşisi, diegetik mi değil mi, erişilebilirlik (kontrast, yazı boyutu, renk körlüğü) |
| Animasyon | Animator durum grafiği kontrolü, geçiş süreleri, root motion tutarlılığı |

### E. Kullanıcıyla birlikte çalışma kalitesi
| # | Ekleme | Ne yapar |
|---|---|---|
| E1 | **Tasarım özeti ekranı** | Her iş sonunda: ne yapıldı, neden, alternatifler, görüntüler, açık sorular — tek sayfa |
| E2 | **Hızlı geri bildirim etiketleri** | Kullanıcı "👍 böyle / 👎 böyle değil + neden" der; otomatik `memory/EXAMPLES/`'a gider |
| E3 | **Ayar paneli** | Önemli denge parametreleri Editor penceresinde; kullanıcı elle dener, AI sonucu okur |
| E4 | **Tasarım tartışma modu** | Kod yazmadan önce AI kullanıcıyla 3 seçenek üzerinden kısa beyin fırtınası yapar |
| E5 | **Ekip modu** | Kart sahipliği, "kim neyi değiştirdi" özeti, çakışan tasarım kararları uyarısı |

### F. Sürekli iyileşme
- **Hata günlüğü:** AI'ın yaptığı ve kullanıcının düzelttiği hatalar kategorize edilir; tekrar edenler ilgili skill'e kural olarak eklenir.
- **Skill eval'i:** her skill değişikliği eval setinden geçer (bölüm 4).
- **Aylık gözden geçirme:** hangi skill/araç kullanılıyor, hangisi kullanılmıyor → kullanılmayan atılır.

### Önceliklendirme (etki / emek)
| Öncelik | Maddeler |
|---|---|
| **Hemen (F1–F2)** | A1, A2, A5, B3, B6, C1, C2, C4, E1, E2 |
| **Sonra (F3–F4)** | A3, A4, B1, B2, C3, C5, C7, C8, E3 |
| **İleride (F5+)** | B4, C6, C9, D paketlerinin tamamı, E4, E5, F |

---

## 4. Kalite ölçümü

### Rubrik (her çıktı 1–5)
- **Sütun uyumu:** oyunun kimliğine hizmet ediyor mu?
- **Anlamlı seçim / derinlik:** oyuncuya ilginç kararlar veriyor mu?
- **Netlik / okunabilirlik:** oyuncu ne yapacağını anlıyor mu?
- **Uygulanabilirlik:** kapsam, Unity'de yapılabilirlik, ayarlanabilirlik.
- **Yenilik:** jenerik mi, özgün mü?
- **Teknik doğruluk:** derleniyor, testleri geçiyor, performans bütçesinde.

### Kıyas düzeneği (eval)
- `evals/` altında sabit görev seti (ör. "gemi kargo ağırlık sistemi", "ilk ada limanı leveli", "yakıt ekonomisi").
- Her görev: düz Claude vs. v3; çıktılar anonimleştirilip puanlanır (sahip + ayrı değerlendirici agent).
- Her yeni skill/akış bu setle ölçülür; iyileştirmeyen değişiklik geri alınır.

---

## 5. Mevcut repodan ne alınır?

| Alınır | Değiştirilerek | Arşive |
|---|---|---|
| `.claude/rules/unity.md` | `security.md`, `architecture.md` → L0 ve `craft-gameplay-code` içine | lease/seal script'leri, `.ai-governance/`, policy_lib |
| Agent/skill altyapısı | `code-reviewer`, `qa-reviewer` → tavsiye veren rollere | READY/ACCEPT şablonları, receipt'ler |
| Ship-game baseline (örnek proje olarak) | `validate_os.py` → pytest ile yeni yapının doğrulayıcısı | 16 mimari standart, 14 şablon, OWNER-POLICY/DEBT-FIX patch'leri |
| Anti-pattern fikri | GDD/pillars → `game/IDENTITY.md` | HANDOFF-001 |

Arşivleme silme değildir: `git tag v1.2-final` + `archive/v1.2/`.

---

## 6. Yol haritası

| Faz | İçerik | Çıktı / Bitti ölçütü |
|---|---|---|
| **F0 Temizlik** | Bekleyen değişiklikleri commit, `v1.2-final` tag, v1.2'yi `archive/`'a taşı, yeni klasör yapısı, `.gitattributes` | Temiz repo; yeni `CLAUDE.md` ≤60 satır |
| **F1 Taban (L0+L1)** | Deny kuralları, Unity şablonu, compile/test döngüsü, `IDENTITY` + kart şablonları, `STATE.md` | Örnek Unity projesinde AI script yazınca hatayı kendisi görüp düzeltiyor |
| **F2 Sistem tasarımı dikey dilimi (L2+L3)** | `craft-system-design`, `/design-system`, `design-critic`, rubrik, ilk 3 eval görevi | Eval'de v3 > düz Claude (ortalama ≥ +1 puan) |
| **F3 Level design + gözlem (L2+L4)** | `craft-level-design`, `/design-level`, MCP ekran görüntüsü + NavMesh metrikleri, `level-critic` | Blockout level'ı AI kendi ekran görüntüsü ve metrikleriyle en az 1 tur iyileştiriyor |
| **F4 Hafıza (L5)** | DECISIONS, EXAMPLES, PLAYTESTS; skill'lerin bunları okuması | Yeni oturum, önceki kararlara aykırı öneri yapmıyor |
| **F5 Genişleme** | game-feel, economy (simülasyon), UX skill'leri; ekip modu (kart sahipliği) | Her yeni skill eval'den geçiyor |
| **F6 Paketleme** | Başka bir Unity projesine 10 dakikada kurulum (`init` script), README | Temiz projeye kurulup çalışıyor |

Her faz sonunda: eval seti çalışır, sonuç `evals/RESULTS.md`'ye yazılır.

---

## 7. Kapsam dışı (bilinçli olarak yapılmayacaklar)
- Onay kapıları, hash'li receipt'ler, lease/seal.
- Her değişiklik için zorunlu doküman.
- Kendi MCP sunucumuzu yazmak (resmî Unity MCP veya CoplayDev/unity-mcp kullanılır; gerekirse küçük özel araçlar eklenir).
- Unreal desteği (motor profili Unity; çekirdek fikirler motordan bağımsız yazılır ama uygulanmaz).

## 8. Açık sorular
1. Hangi Unity MCP: resmî `com.unity.ai.assistant` mı, CoplayDev/unity-mcp mi? (F1'de kısa karşılaştırma)
2. Deneme projesi: ship-game mi, daha küçük bir test oyunu mu?
3. Ekip modu ne zaman gerekli? (F5'e kadar tek kişi varsayımı)
4. Zanaat skill'lerinin dili: Türkçe mi, İngilizce mi? (Öneri: skill içerikleri İngilizce — model performansı; kullanıcıya yanıtlar Türkçe)

## 9. Not: `design-system` skill'i
Ortamdaki `design-system` skill'i UI görsel tutarlılığı (renk, tipografi, bileşen) içindir. v3'ün çekirdeği için gerekli değil; F5'te `craft-ux-onboarding` ile oyun arayüzü stil rehberi hazırlanırken kullanılabilir.
