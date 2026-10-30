# Content Provenance

Short record of where the imported content came from and the decisions made while bringing it in.

## Catalogue

- Personas and spread design were imported from `celestial-neutral/src/data/`.
- Every mentor row in `mentors/fixtures/mentor_data.json` carries a `content_source` field naming the prototype source file and asset it came from.

## Card copy

- `tarot/content/cards.json` is authored for this product, not harvested. It is the canonical source for every card's description, upright meaning, reversed meaning and keywords in English and Ukrainian.
- The `description`, `upright_meaning` and `reversed_meaning` columns were empty for all 78 cards, and the 78 `description` values were scrapes of the form `"The The Fool Meaning\r\nUpright: ..."` or `"The Ace of Wands represents..."`. All were replaced.
- Copy is applied by `uv run python manage.py load_card_catalogue`. The loader only writes the copy fields, fills blanks by default, and replaces non-empty values only with `--overwrite`, so admin edits survive a re-seed.
- It is deliberately **not** a Django fixture: deserializing a partial `tarot.card` row calls `save()` with `raw=True`, which writes every field and would erase each card's name, slug, suit, number and image.
- Voice: reflective, present tense, second person. Meanings describe a field of experience to notice, never an outcome. Ukrainian uses the polite plural (ви). The reflective-language gate lives in `tarot/tests/test_card_catalogue.py`.

## Intentionally not imported

- `mimi.jpg` exists in the prototype's `assets/mentors/` directory but is intentionally **not** imported, because no persona references it. Do not add a persona just to justify an unused asset.

## Spelling: `Judgement` vs `Judgment`

- The insight fixture already uses `Judgement`, and the authored catalogue keys the card as `judgement`.
- The prototype's `Judgment` spelling exists only in its card-meaning source (`celestial-neutral/src/data/tarot_cards.py`), which is not used.
- This is a verified no-op, not a migration: no rename was performed and none is required.

## Fixture loading

- `tarot/fixtures/tarot_data.json` is a mixed fixture: 5 `tarot.suit`, 78 `tarot.card`, 22 `tarot.reading` and 78 `tarot.readingcard` entries. It must not be edited.
- `load_catalog` is the only supported loader. It deliberately filters to `tarot.suit` and `tarot.card` entries so historical readings are never imported. That filter is load-bearing and is pinned by `tarot/tests/test_load_catalog.py`.
- `load_catalog` creates missing rows and never overwrites existing ones, so re-seeding cannot erase admin edits or authored copy.
- `load_catalog` treats the fixture as structural: it creates each card with empty copy fields and never imports the fixture's scraped descriptions or keywords. Editorial copy comes only from `load_card_catalogue`.
- Card copy is loaded separately by `load_card_catalogue`, which joins on `slug`; `seed_demo` runs both.
- A database created before the authored catalogue landed keeps its legacy fixture copy. Run
  `uv run python manage.py load_card_catalogue --overwrite` once on such a database; after that, re-seeds preserve edits.
