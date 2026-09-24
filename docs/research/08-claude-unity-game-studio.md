# Araştırma 08 — IdoCohen560/claude-unity-game-studio

Kaynak: https://github.com/IdoCohen560/claude-unity-game-studio · Lisans: MIT · 22 yıldız, 4 fork, ~3 commit · İnceleme: 2026-09-24 (README)

## 1. Ne yapıyor?
Fork değil, **derleme paket**: birden çok kaynaktan parçaları bir araya getirip Unity'ye odaklı tek bir kurulum sunuyor. Kaynaklar: Donchitos (Claude Code Game Studios temeli), Nice Wolf Studio, TJ Boudreaux (cc-plugin-unity-gamedev), devdavv, Ivan Murzak (Unity-MCP).

## 2. Yapı
```
game-studios-template/     49 agent, 72 skill, 12 hook, 11 kural  (Donchitos şablonu)
unity-knowledge-skills/    35 Unity API skill'i (95 dosya, 44.500+ satır)
unity-middleware-skills/   21 middleware skill (VContainer, UniTask, Wwise, Addressables, NavMesh, Behavior Designer…)
unity-ai-workflow/         9 kısa komut (uw-cmd-*: kurulum, beyin fırtınası, uygulama, test, debug, cila) + 13 workflow skill
unity-mcp/                 C# plugin + MCP sunucusu (Unity editörü ile çift yönlü köprü)
```
Ek Unity agent'ları: `unity-specialist`, `unity-shader-specialist`, `unity-ui-specialist`, `unity-dots-specialist`, `unity-addressables-specialist`.

## 3. Değerlendirme
- **Özgün katkısı düşük**: çoğu içerik diğer repolardan (rapor 01, 09, IvanMurzak MCP). 44.500 satırlık Unity bilgi skill'leri bağlam maliyeti yüksek; resmî Unity plugin'i (rapor 03) bu alanı artık kapsıyor.
- Çok az commit ve topluluk; bakım belirsiz.
- Değerli olan tek şey **fikir**: "stüdyo şablonu + Unity bilgi + MCP köprüsü + kısa komut katmanı" birleşiminin tek pakette sunulması. Kısa komut katmanı (`uw-cmd-*`) büyük sistemin üstüne basit giriş noktaları koyma örneği.

## 4. v3'e alınacaklar
| Fikir | v3'te nereye |
|---|---|
| Büyük skill setinin üstüne **az sayıda kısa giriş komutu** | v3 zaten bunu hedefliyor (`/start-task`, `/design-system`, `/design-level`, `/playtest`) — teyit |
| Kaynak atıfını açıkça listeleme | F6 paketleme README'sinde kullandığımız fikirlerin kaynak listesi |
Başka bir şey alınmayacak; asıl kaynaklar ayrı raporlarda incelendi.
