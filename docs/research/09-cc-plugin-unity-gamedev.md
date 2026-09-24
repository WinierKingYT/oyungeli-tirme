# Araştırma 09 — tjboudreaux/cc-plugin-unity-gamedev

Kaynak: https://github.com/tjboudreaux/cc-plugin-unity-gamedev · Lisans: MIT · 9 yıldız, 1 fork, tek commit · İnceleme: 2026-09-24 (README)

## 1. Ne yapıyor?
Claude Code için 21 Unity skill'i; çoğu üçüncü parti kütüphane ve middleware bilgisi.

## 2. Skill'ler (21)
`eng-unity-mobile-optimization` (bellek, pil, ısı, performans) · `tools-unity-addressables` · `tools-unity-animation` (Animancer, durum makineleri) · `tools-unity-behavior-designer` · `tools-unity-cinemachine` · `tools-unity-flowcanvas` · `tools-unity-gameplay-ability-system` (yetenek, efekt, attribute, tag) · `tools-unity-memorypack` (binary serileştirme, versiyonlama) · `tools-unity-navmesh` · `tools-unity-object-pooling` · `tools-unity-physics` (karakter kontrolcü, tunneling önleme) · `tools-unity-primetween` · `tools-unity-profiling` (ProfilerMarker, FrameTimingManager, performans bütçesi) · `tools-unity-scriptable-objects` · `tools-unity-sentry` · `tools-unity-state-machine` (hiyerarşik durum, async geçiş, temizlik güvenliği) · `tools-unity-test-framework` · `tools-unity-ugui` (Canvas optimizasyonu, liste sanallaştırma) · `tools-unity-unitask` · `tools-unity-vcontainer` · `tools-unity-wwise`.

## 3. Değerlendirme
- Tamamen teknik/kütüphane odaklı; tasarım kalitesi yok.
- Tek commit, bakım yok; claude-unity-game-studio (rapor 08) bunu içine almış.
- Resmî Unity plugin'i ve awesome-gamedev-agent-skills'in Unity bölümü çekirdek alanları kapsıyor; bu repo sadece belirli middleware kullanılırsa (VContainer, UniTask, MemoryPack, Wwise) referans olabilir.

## 4. v3'e alınacaklar
| Fikir | v3'te nereye |
|---|---|
| `tools-unity-profiling`: ProfilerMarker + FrameTimingManager + bütçe | F5 performans kontrolü (C6) için referans okunacak |
| `tools-unity-state-machine`, `tools-unity-object-pooling` | `craft-gameplay-code` kalıp kütüphanesi (B4) için referans |
Doğrudan kopyalanacak içerik yok; ihtiyaç halinde ilgili skill projeye ayrı kurulabilir.
