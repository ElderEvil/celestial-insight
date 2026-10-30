# Content Provenance

Short record of where the imported content came from and the decisions made while bringing it in.

## Catalogue

- Personas and spread design were imported from `celestial-neutral/src/data/`.
- Every mentor row in `mentors/fixtures/mentor_data.json` carries a `content_source` field naming the prototype source file and asset it came from.

## Intentionally not imported

- `mimi.jpg` exists in the prototype's `assets/mentors/` directory but is intentionally **not** imported, because no persona references it. Do not add a persona just to justify an unused asset.

## Spelling: `Judgement` vs `Judgment`

- The insight fixture already uses `Judgement`.
- The prototype's `Judgment` spelling exists only in its card-meaning source (`celestial-neutral/src/data/tarot_cards.py`), which is out of scope.
- This is a verified no-op, not a migration: no rename was performed and none is required.

## Fixture loading

- `tarot/fixtures/tarot_data.json` is a mixed fixture: 5 `tarot.suit`, 78 `tarot.card`, 22 `tarot.reading` and 78 `tarot.readingcard` entries. It must not be edited.
- `load_catalog` is the only supported loader. It deliberately filters to `tarot.suit` and `tarot.card` entries so historical readings are never imported. That filter is load-bearing and is pinned by `tarot/tests/test_load_catalog.py`.
