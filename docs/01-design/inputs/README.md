# Game document inputs

Status: `DISCOVERY_INPUT` folder. Nothing here is authority.

Put the project owner's game documents here (vision, design notes, references, feature lists, sketches exported as text or images). Project discovery (`DISCOVERY-001`) reads this folder and turns what it finds into proposed GDD, core-loop, and system-specification drafts for the owner to approve.

## Rules

- Anything here ranks as conversation-level input until the owner approves a derived document. It never overrides accepted ADRs, systems, or the constitution.
- Do not put secrets, keys, tokens, or personal data here.
- Keep large binaries (video, big images, archives) out of this folder; link to them or store them with Git LFS once that is decided (`docs/02-architecture/UNITY-REPO-HYGIENE.md`).
- Any text format is fine (Markdown, plain text, PDF, exported Docs). Name files so their order or topic is obvious. If a document is old or contested, say so in its first lines.
- Contradictions between documents are surfaced as `AUTHORITY_CONFLICT`, not resolved silently.
