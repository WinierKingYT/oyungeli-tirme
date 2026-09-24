# Araştırma 13 — AI ile oyun geliştirmede performans ve kaliteyi artırma teknikleri

Tarih: 2026-09-24 · Soru: v3'ten daha fazla kalite ve verim nasıl alınır? · Yöntem: web araması + birincil kaynaklar (Anthropic dokümanları, arXiv makaleleri). Makalelerin tamamı değil, özetleri/HTML sürümleri okundu.

---

## 1. Bağlam mühendisliği (context engineering) — kalitenin temeli

### Bulgular
- **Claude 5 nesli daha az talimatla daha iyi çalışıyor.** Anthropic, Claude Code'un sistem prompt'unun %80'inden fazlasını gelişmiş modeller için performans kaybı olmadan kaldırmış. Aşırı talimat, tekrar ve çelişen yönergeler modele gereksiz "düşünme yükü" bindiriyor; fazla korkuluk yargıyı kısıtlıyor. ([claude.dev](https://claude.dev/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models/))
- **CLAUDE.md kısa olmalı**; dosya yapısından çıkarılabilecek şeyleri değil, **kod tabanındaki tuzakları (gotchas)** anlatmalı. Karmaşık prosedürler skill'lere.
- **Kural türüne göre doğru mekanizma:** zorunlu kural → hook/izin; bağlamsal bilgi → skill; görev devri sınırı → subagent; her zaman geçerli kısa yönlendirme → CLAUDE.md. ([Medium: Claude Code in Practice](https://medium.com/@riyaz.sarah/claude-code-in-practice-context-caching-subagents-and-skills-c565f202e778))
- **Örnek yerine arayüz tasarımı:** araç dokümanlarında uzun örnekler yerine anlamlı parametreler ve enum'lar; spesifikasyon olarak **kod ve test süiti**; doğrulayıcı agent'lar için **rubrik**.
- **Aşamalı yükleme (progressive disclosure):** başlangıçta sadece skill adı+açıklaması; skill tetiklenince SKILL.md; gerekirse referans dosyalar. Onlarca skill bağlamı şişirmeden kurulabilir.

### Skill yazım kuralları (Anthropic resmî dokümanı)
([platform.claude.com — Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices))
- **"Claude zaten çok akıllı" varsayımı:** sadece bilmediği şeyi yaz; her paragraf token maliyetini hak etmeli.
- **Serbestlik derecesi kırılganlığa göre:** açık alan (tasarım, review) → yüksek serbestlik, sezgisel ilkeler; dar köprü (dosya formatı, migration, Unity YAML) → düşük serbestlik, tam script/komut.
- **Açıklama (description) bir yönlendirme kuralıdır:** 3. şahıs, ne yapar + ne zaman kullanılır + kullanıcının gerçekten söylediği tetikleyici kelimeler; ≤1024 karakter.
- **SKILL.md gövdesi < 500 satır;** detaylar ayrı dosyalarda, **referanslar tek seviye derin** (iç içe referanslar kısmi okunur); 100+ satırlık referans dosyaya içindekiler tablosu.
- **İsimlendirme:** fiil-ing önerilir (`designing-levels`), tutarlı terminoloji.
- **İş akışı + kontrol listesi:** karmaşık süreçlerde Claude'un kopyalayıp işaretleyeceği checklist.
- **Geri bildirim döngüsü:** doğrulayıcı çalıştır → düzelt → tekrar. "Bu desen çıktı kalitesini büyük ölçüde artırır."
- **Plan → doğrula → uygula:** toplu/yıkıcı işlemlerde önce yapılandırılmış plan dosyası (ör. `changes.json`), script ile doğrula, sonra uygula. Doğrulama hataları açıklayıcı olmalı.
- **Deterministik işler için hazır script** (üretilen koddan güvenilir, token harcamaz); script hataları kendisi çözer, "sihirli sayı" yok.
- **Görsel analiz:** render edilebilen girdileri görüntüye çevirip Claude'a baktır.
- **MCP araçlarına tam nitelikli isimle** atıf (`Sunucu:araç`).
- **Önce eval, sonra doküman:** skill'siz çalıştır → eksikleri belgele → 3 senaryo → baseline → minimum talimat → yinele.
- **Claude A / Claude B yöntemi:** bir Claude skill'i yazar/düzeltir, taze bir Claude gerçek görevde kullanır; davranış gözlemlenip geri beslenir.
- **Birden çok modelle test** (Haiku yeterli rehberlik alıyor mu, Opus fazla açıklamadan rahatsız mı).
- Tetiklenmeyen dosya → gereksiz ya da kötü işaretlenmiş; sürekli okunan dosya → SKILL.md'ye taşınmalı.

### v3 için sonuç
v3 taslakları **iyi yönde ama bazı yerlerde fazla uzun ve tekrarlı** olabilir (ör. her skill'de Unity kurallarının tekrarı, `_quality-preamble` + CLAUDE.md'de aynı ilkeler). Yapılacaklar bölüm 7'de.

---

## 2. Görsel yargı (VLM) — ne kadar güvenebiliriz?

### Bulgular
- **VideoGameQA-Bench** ([arXiv 2505.15952](https://arxiv.org/html/2505.15952v2)): en iyi modeller ortalama ~%50. Güçlü: **bariz glitch tespiti** (görüntüde ~%83, videoda ~%78), **bug raporu yazma**. Zayıf: **ince sahne anlama** (görsel birim test en iyi %53, UI %40), **nesne yerleşimi/postür**, **ince anomaliler** (iç içe geçme, sağduyu ihlali), **referansla karşılaştırma / görsel regresyon (en iyi ~%45)**, videoda zamanı belirleme. **Çok yanlış pozitif** → otonom değil asistan olarak kullan.
- **İnsan + AI birlikte test** ([arXiv 2501.11782](https://arxiv.org/html/2501.11782v1)): AI yardımıyla insan kusur bulma doğruluğu **%41 → %63**; **AI + tasarım bilgisi (doküman) birlikte %64** en iyi. Ama **AI yanlış işaretleyince doğruluk ciddi düşüyor** (bir koşulda %22) → AI'ın gerekçesi görünür olmalı, insan eleştirel bakmalı.
- 2025–26 modelleri görüntüyü daha iyi işliyor (erken füzyon mimarileri) — ama yukarıdaki zayıflıklar büyük ölçüde sürüyor.

### v3 için sonuç
- Ekran görüntüsü yargısını **"sorulan soruya odaklı"** yap: "Bu görüntüde parlak/kontrastlı en belirgin öğe nedir? Kapı görünüyor mu?" gibi **tek, somut sorular**; genel "bu level iyi mi?" değil.
- **Ölçülebilir olanı koda bırak:** yerleşim, çakışma, ulaşılabilirlik, boyut → `lint_scene`, NavMesh, raycast; VLM sadece **okunabilirlik, yönlendirme, kompozisyon, his** için.
- **Referans karşılaştırmasına (önce/sonra, altın sahne) VLM ile güvenme;** piksel/metrik farkı (ör. görüntü farkı yüzdesi, obje sayısı, bounds) ile yap, VLM sadece farkı yorumlasın.
- VLM bulgularını **"inferred-visual"** olarak etiketle; sahip onaylamadan "hata" sayma. Kart (tasarım bilgisi) her zaman görsel incelemeye eklensin — çalışma bunun doğruluğu artırdığını gösteriyor.
- Birden çok açıdan görüntü + tepeden plan; tek görüntüden yargı yok.

---

## 3. Otomatik playtest ve denge

### Bulgular
- **LLM'ler zorluk ölçer olarak güvenilir** (rapor 12: insan zorluk algısıyla güçlü korelasyon), mutlak oyun becerileri düşük olsa bile.
- **RuleSmith** ([arXiv 2602.06232](https://arxiv.org/html/2602.06232v1)): LLM agent'ları kural metnini okuyup **kendi kendine oynuyor**; **Bayesyen optimizasyon** 12 boyutlu parametre uzayında dengeyi arıyor; hedef `|win_A−0.5| + |win_B−0.5| + 0.5·draw`; umut veren adaylara daha çok oyun (16→64) ayrılıyor. Dengeli konfigürasyonlara yakınsamış, birden fazla dengeli çözüm bulmuş, parametreler yorumlanabilir.
- **TITAN** gibi sistemler: ~%95 başarı, %74 kapsam, yerleştirilmiş hataların %82'si ([emergentmind özet](https://www.emergentmind.com/topics/llm-agents-as-game-testers)) — detay doğrulanmadı.
- Botlar **denge ve tempo ölçümünde** iyi; **hikâye tutarlılığı, duygusal etki, istismar keşfinde** insanın yerini tutmuyor.

### v3 için sonuç
- **Saf C# kural + ScriptableObject config** mimarimiz bunu mümkün kılıyor: kurallar Unity olmadan hızlı simüle edilebilir.
- F5 `craft-economy-balance` → **simülasyon + parametre araması** (basit grid/rastgele arama ile başla; Bayesyen optimizasyon ileride). Hedef fonksiyonu kartta yazılı olsun (ör. "sefer başına net kâr 80–120, iflas oranı < %5").
- Playtest botu (NavMesh) → süre ve takılma; **LLM oyuncu** → sadece metin/tur tabanlı sistemler (ticaret kararları gibi) için göreli zorluk.

---

## 4. Çoklu aday + seçim (best-of-N)

### Bulgular
- Aynı görevi N kez (veya N farklı yaklaşımla) üretip **bağımsız bir yargıç** ile seçmek, tek seferlik üretimden belirgin daha iyi (kod üretiminde örn. %36 → %50 pass@1). Yargıç **kendi üretmediği** çıktıları değerlendirmeli. ([hermes-agent issue](https://github.com/NousResearch/hermes-agent/issues/479), [CodeJudgeBench](https://arxiv.org/pdf/2507.10535))
- Kodda testler en iyi yargıç; tasarımda rubrikli bağımsız agent.

### v3 için sonuç
- `/design-system` ve `/design-level` zaten 3 farklı yaklaşım üretiyor → **puanlamayı aynı bağlamdaki ana agent değil, taze bağlamlı `design-critic`/`eval-scorer` yapsın** (kendi çıktısını seçme yanlılığını azaltır).
- Önemli gameplay parçaları için **2–3 alternatif uygulama** (ayrı worktree'lerde paralel) → testler + kısa oynanış görüntüsü ile seçim. Pahalı; sadece kritik sistemlerde ("Full" mod).

---

## 5. Model ve maliyet yönetimi

- Karmaşık tasarım/mimari → en güçlü model; tekrar eden kontroller (lint yorumlama, test özeti, eval puanlama) → hızlı/ucuz model (Haiku/Sonnet) alt agent'larda. Anthropic ayrıca skill'lerin her modelde test edilmesini öneriyor.
- **Prompt önbelleği:** sabit içerik (CLAUDE.md, IDENTITY, skill metinleri) başta ve değişmeden kalırsa önbellekten gelir → oturum içinde değişen içeriği (STATE) sona yakın tut; sık sık CLAUDE.md düzenlemek önbelleği bozar.
- **MCP araç şemaları** bağlamı şişirebilir (resmî Unity MCP ~24k token); Claude Code erteleyerek yükler — yine de sadece gereken sunucuları, proje kapsamında aç.
- **Subagent ile bağlam izolasyonu:** keşif, geniş okuma, eleştiri alt agent'ta → ana bağlam temiz kalır; alt agent sadece özet döndürür.
- **Script > üretilen kod** deterministik işlerde (lint, capture, path) — bizim `unity-tools` yaklaşımımız doğru.

---

## 6. Sektör ve pratik geri bildirimleri (ikincil kaynaklar, doğrulanmadı)
- Unity 2026 raporu: stüdyoların çoğu AI'ı üretim akışına almış; Claude Code kullanıcıları C#, shader, debug'da %40–60 zaman kazancı bildiriyor ([Kevuru](https://kevurugames.com/blog/using-claude-ai-in-game-development-tools-use-cases-and-industry-statistics/), [gamineai](https://gamineai.com/blog/how-ai-is-transforming-game-development-2026)) — pazarlama kaynaklı, temkinli okunmalı.
- İndie deneyimleri: **AI'ı disiplin bazında yönlendir** (her iş için doğru araç/skill), proje genel bakış dokümanı + ilk günden kodlama standartları; Claude özellikle dağınık fikirleri yapılandırılmış tasarım dokümanına çevirmede ve debug hipotezlerinde güçlü ([BigDevSoon](https://bigdevsoon.me/blog/building-games-with-ai-indie-game-dev-workflow/)).

---

## 7. v3 için öneriler (öncelik sırasıyla)

| # | Öneri | Neden | Etkilenen |
|---|---|---|---|
| 1 | **Skill'leri incelt:** her SKILL.md'yi kısa ana akış + `reference/` dosyalarına böl (ör. `craft-level-design/reference/checklists.md`, `techniques.md`); Unity kurallarını tek yerde (CLAUDE.md "gotchas") tut, skill'lerde tekrar etme | Anthropic: Claude 5 az talimatla daha iyi; tekrar/çelişki zarar | tüm skill'ler, CLAUDE.md |
| 2 | **Açıklamaları yönlendirme kuralı olarak yeniden yaz** (3. şahıs, tetikleyici Türkçe+İngilizce ifadeler: "level tasarla", "his kötü", "dengele") | Skill doğru anda tetiklensin | tüm frontmatter'lar |
| 3 | **CLAUDE.md'yi "gotchas" odaklı yap**; dosya yapısından çıkarılabilecekleri sil | Kısa, yüksek sinyal | CLAUDE.draft |
| 4 | **VLM kullanım kuralları:** odaklı tek sorular, kartla birlikte, "inferred-visual" etiketi, referans karşılaştırmasını metrikle yap | VLM zayıflıkları (ince detay, regresyon, yanlış pozitif) | `craft-level-design`, `level-critic`, `capture_review_set` |
| 5 | **Görüntü farkı aracı:** önce/sonra ve altın sahneler için piksel farkı yüzdesi + bölge ısı haritası (C# veya Python script) | VLM regresyonda ~%45 | yeni `unity-tools` aracı (F3/F4) |
| 6 | **Plan → doğrula → uygula** sahne düzenlemesi için: MCP ile toplu yerleşim öncesi `layout.json` (obje, konum, boyut) → METRICS'e göre script ile doğrula → uygula | Toplu değişikliklerde hatayı erken yakalar | `craft-level-design` §2, yeni `validate_layout` aracı |
| 7 | **Yargıç ayrımı:** 3 alternatifi ana agent değil taze `design-critic`/`eval-scorer` puanlasın | Kendi çıktısını seçme yanlılığı | `design-system-flow`, `design-level-flow` |
| 8 | **Model yönlendirme:** eval-scorer, lint/test özetleyici → hızlı model; critic'ler → güçlü model; agent frontmatter'da `model:` | Maliyet/hız | agent tanımları |
| 9 | **Denge araması:** simülasyon + parametre taraması + kartta yazılı hedef fonksiyonu; LLM oyuncu sadece tur/metin tabanlı kararlar için | RuleSmith, LLM zorluk ölçer bulguları | F5 `craft-economy-balance` |
| 10 | **Önce eval, sonra skill** + **Claude A/B yöntemi** süreç olarak | Anthropic önerisi; gereksiz içeriği önler | `evals/`, skill geliştirme rehberi |
| 11 | **Önbellek dostu düzen:** sabit içerik önce, değişen STATE sonra; CLAUDE.md'yi sık değiştirme | Maliyet ve hız | `session_context.py`, CLAUDE |
| 12 | **Çoklu uygulama adayı (best-of-N) sadece kritik sistemlerde** paralel worktree + test + görüntü ile seçim | Kalite artışı kanıtlı ama pahalı | "Full" mod |

Kaynaklar: yukarıdaki bağlantılar; ayrıca rapor 04 (doğrulama merdiveni), 11 (MCP bağlam maliyeti), 12 (LLM zorluk ölçer, OpenGame).
