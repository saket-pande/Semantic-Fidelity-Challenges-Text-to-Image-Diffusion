# Contributing

Thank you for helping keep this list complete. Every paper on the website and in the README comes from one file, `data/papers.json`.

## Add or fix a paper

1. Add an entry to the `papers` array in `data/papers.json` (or edit an existing one):

```json
{
  "id": 190,
  "name": "MethodName",
  "title": "Full Paper Title",
  "authors": "A. Author et al.",
  "year": 2026,
  "venue": "CVPR",
  "url": "https://arxiv.org/abs/xxxx.xxxxx",
  "url_label": "arXiv",
  "url_source": "contrib",
  "code": "https://github.com/owner/repo",
  "section": "5.4.1",
  "levels": ["object"],
  "types": ["Inference-time"],
  "cited_in": []
}
```

   - `section` is one of the subsection ids listed under `taxonomy` in the same file (for example `6.4.4` for layout-guided attribute methods).
   - `levels` can contain `object`, `attribute`, `numerical`, `relational`.
   - `types` can contain `Training-time`, `Inference-time`, `Analysis`, `Metric`, `Dataset`.
   - Papers added after the survey get an `id` above 189, so the bracketed numbers keep matching the survey's reference list.

2. Run `python scripts/build_site.py` to rebuild `README.md` and `docs/index.html`.
3. Open a pull request.

You can also [open an issue](../../issues/new?template=add-paper.md) with the paper link and we will add it.
