# AI Game Development OS v1.2

Bu paket, Claude Code veya başka coding agent'ları “tek prompt ile oyun yaptırma” yaklaşımından çıkarıp kanıta dayalı, sınırları belirlenmiş bir üretim sürecine sokar.

Paketin varsayılan durumu güvenlidir: proje `PLAN` modunda açılır ve production dosyalarına yazma yetkisi aktif değildir. Bu paket kuruldu diye hiçbir oyun sistemi `READY`, `ACCEPTED` veya `PRODUCTION READY` sayılmaz.

## Ne sağlar?

- `AGENTS.md`: vendor-neutral ortak çalışma sözleşmesi.
- `CLAUDE.md`: Claude Code yönlendiricisi; kısa ve kalıcı kurallar.
- `.claude/rules/`: konu ve dosya yoluna göre kurallar.
- `.claude/agents/`: araştırmacı, mimar, implementer ve bağımsız reviewer rolleri.
- `.claude/skills/`: discovery, spec, implementation, verification ve closure iş akışları.
- `.claude/settings.json`: başlangıçta plan modu ve hook kayıtları.
- `.claude/hooks/`: Git-bound lease olmadan production yazımını ve varsayılan olarak MCP kullanımını engelleyen, hata halinde `exit 2` ile fail-closed çalışan denetim.
- `docs/`: proje otoritesi, mimari, üretim, test ve kanıt kayıtları.
- `docs/templates/`: her yeni sistem ve milestone için tekrar kullanılabilir şablonlar.

## Hızlı kurulum

1. Paketin içeriğini Git oyun reposunun köküne kopyala.
2. `python --version` ile Python 3.10+ olduğunu doğrula.
3. `python scripts/doctor.py --require-claude` çalıştır; runtime ve adversarial doğrulama tamamen geçmeden Claude oturumu açma.
4. `docs/00-project/` ve `docs/01-design/` içindeki bootstrap alanlarını gerçek projeye göre doldur.
5. Claude Code'u repo kökünde aç ve `/context` ile `CLAUDE.md` ile rules dosyalarının yüklendiğini doğrula.
6. İlk iş olarak `/project-discovery` çalıştır. Doğrudan implementation başlatma.

## Implementation nasıl açılır?

Agent önce `docs/05-production/tasks/` altında bir task contract hazırlar. Bağımsız reviewer, task’in exact SHA-256 değerine bağlı ayrı bir READY receipt üretir. Task ve receipt commit’lenmiş, worktree temiz olmalıdır. Bundan sonra terminali **Claude dışında** açıp şunu çalıştır:

```bash
python scripts/activate_lease.py docs/05-production/tasks/TASK-ID.md
```

Script sana task ID, base HEAD/branch, izinli dosya yolları ve izinli komutları gösterir; exact task ID ve `ACTIVATE` yazmadan lease oluşmaz. Lease varsayılan olarak sekiz saat sonra biter. HEAD veya branch değişirse lease geçersiz olur. Claude'un kendi Bash aracı bu scripti çalıştıramaz.

Implementation bittiğinde insan operatör exact diff’i mühürler:

```bash
python scripts/seal_implementation.py
```

Seal, lease dışındaki değişmiş yolları reddeder; tracked binary diff’i ve untracked dosyaları SHA-256 ile bağlar; lease’i `SEALED` yaparak sonraki agent yazımlarını kapatır.

İş bittiğinde veya durdurmak istediğinde yine Claude dışında:

```bash
python scripts/deactivate_lease.py
```

Aktif lease yalnızca contract içindeki `allowed_paths` alanlarına yazım izni verir. Task contract, READY receipt, HEAD veya branch değişirse izin kapanır. Pipe, redirection, command substitution veya birleşik shell komutları hiçbir zaman otomatik onaylanmaz. MCP araçları exact-name policy ile yönetilir; bilinmeyen MCP çağrısı lease yokken reddedilir, lease varken insan onayı ister.

## Önemli güvenlik sınırı

Hook'lar güçlü bir proje-içi kontrol katmanıdır fakat işletim sistemi sandbox'ı değildir. Hook runtime hiç başlatılamazsa Claude Code bunu tek başına fail-closed saymaz; bu yüzden paket Plan Mode, auto/bypass mode yasağı, `doctor.py`, CI ve branch protection katmanlarını birlikte kullanır. `ConfigChange` oturum içi settings/skill gevşetmesini bloke eder; ancak işletim sistemi ve Claude dışı programlar yine ayrı güven sınırıdır. Ayrıntılar `docs/00-project/SECURITY-THREAT-MODEL.md` içindedir.

## İlk proje durumu

Bu dağıtımın initial state'i:

- Process: `BOOTSTRAPPED`
- Project discovery: `NOT_STARTED`
- Current milestone: `UNAPPROVED`
- Current implementation task: `NONE`
- Implementation lease: `INACTIVE`
- Accepted systems: `0`

Gemi oyunu için bilinen ürün kararları `examples/ship-game/` altında discovery girdisi olarak bulunur. Bunlar repo ve motor gerçekliği incelenmeden frozen architecture sayılmaz.

Mevcut v1.1 kurulumu yükseltiliyorsa `MIGRATION-v1.1-to-v1.2.md` dosyasını uygula. Schema-2 lease’ler v1.2’de bilerek geçersizdir.

## v1.2 repository-bound attestation özeti

- Lease, temiz repository root + exact base HEAD + branch’e bağlı schema 3 authority’dir.
- Human-only implementation seal exact changed-path listesi ve diff SHA-256 üretip yazma yetkisini kapatır.
- Tüm `mcp__*` araçları deny-by-default policy hook’una girer.
- `ConfigChange` project/user/local settings ve skill değişikliklerini mevcut oturumda bloke eder.
- R4 task’ları OpenSSH public-key allowlist ile doğrulanan imzalı READY receipt gerektirir.
- Saldırı korpusu; dirty-tree activation, branch drift, MCP gate, post-seal denial ve signature tampering testleri içerir.

## Devralınan v1.1 hardening

- Hook iç hataları `exit 2` ile bloklanır.
- Pipe/redirection/compound/substitution shell kaçışları adversarial test edilir.
- `/usr/bin/git push`, `git -C . push`, quoted subcommand ve nested shell varyantları yakalanır.
- READY kararı task hash’ine bağlı bağımsız receipt gerektirir.
- Acceptance receipt evidence-pack hash’i ve implementation revision’a bağlanır.
- Her hook kararı `.ai-governance/audit.log` içine JSONL olarak kaydedilir.
- Auto ve bypass permission modları project settings seviyesinde devre dışıdır.
- CI workflow ve runtime doctor eklenmiştir.
