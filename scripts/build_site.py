#!/usr/bin/env python3
"""Generate README.md, docs/index.html and CITATION.cff from data/papers.json.

    python scripts/build_site.py

Edit data/papers.json (add a paper, fix a link, add a code URL) and run this
script again; the README and the website are both rebuilt from that one file.
"""
import json, datetime, pathlib, html, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.load(open(ROOT / 'data/papers.json', encoding='utf-8'))
META, TAX, PAPERS = D['meta'], D['taxonomy'], D['papers']
REPO = META['repo']
TODAY = datetime.date.today().strftime('%B %Y')
LEVELS = ['object', 'attribute', 'numerical', 'relational']
LEVEL_EXAMPLE = {
    'object': ('Object', 'cubes, cat', 'The cat never appears.'),
    'attribute': ('Attribute', 'red', 'The cubes come out blue.'),
    'numerical': ('Numerical', 'two', 'Three cubes instead of two.'),
    'relational': ('Relational', 'to the left of', 'The cubes end up on the right.'),
}
GROUP_DESC = {
    'surveys': 'Earlier surveys on diffusion models, quality assessment and controllable generation.',
    'foundations': 'Diffusion, attention and conditioning, latent diffusion and the text-to-image models the survey builds on.',
    'object': 'Every entity named in the prompt should appear in the image.',
    'attribute': 'Colours, textures, shapes and styles should attach to the right object.',
    'numerical': 'The image should contain exactly the number of instances the prompt asks for.',
    'relational': 'Objects should stand in the spatial or semantic relation the prompt describes.',
    'metrics': 'How visual quality and prompt alignment are measured.',
    'datasets': 'Prompt sets and benchmarks used to evaluate semantic fidelity.',
    'beyond': 'Work on general compositionality and directions beyond the four levels.',
}


def bibtex():
    a = ' and '.join(f"{n.split()[-1]}, {' '.join(n.split()[:-1])}" for n in META['authors'])
    lines = ['@article{pandey2026semantic,',
             f"  title   = {{{META['title']}}},",
             f'  author  = {{{a}}},',
             f"  journal = {{{META['journal']}}},",
             f"  year    = {{{META['year']}}}"]
    if META.get('paper_url'):
        lines[-1] += ','
        lines.append(f"  url     = {{{META['paper_url']}}}")
    return '\n'.join(lines + ['}'])


def by_section():
    out = {}
    for p in sorted(PAPERS, key=lambda p: p['id']):
        out.setdefault(p['section'], []).append(p)
    return out


# ------------------------------------------------------------------ README
def md_escape(s):
    return s.replace('|', '\\|')


def readme():
    owner, name = REPO.split('/')
    site = f'https://{owner.lower()}.github.io/{name}/'
    secs = by_section()
    n = len(PAPERS)
    o = []
    o.append(f"<h1 align=\"center\">Semantic Fidelity in Text-to-Image Diffusion Models</h1>\n")
    o.append('<p align="center">')
    o.append(f'  <a href="https://awesome.re"><img src="https://awesome.re/badge.svg" alt="Awesome"></a>')
    o.append(f'  <a href="{site}"><img src="https://img.shields.io/badge/Website-paper%20explorer-5F7891" alt="Website"></a>')
    if META.get('paper_url'):
        o.append(f'  <a href="{META["paper_url"]}"><img src="https://img.shields.io/badge/Paper-survey-A0595F" alt="Paper"></a>')
    o.append(f'  <img src="https://img.shields.io/badge/papers-{n}-3F7C7D" alt="{n} papers">')
    o.append(f'  <a href="https://github.com/{REPO}/stargazers"><img src="https://img.shields.io/github/stars/{REPO}?style=social" alt="GitHub stars"></a>')
    o.append(f'  <a href="https://github.com/{REPO}/pulls"><img src="https://img.shields.io/badge/PRs-welcome-93762A" alt="PRs welcome"></a>')
    o.append('</p>\n')
    o.append(f"This repository collects the {n} papers reviewed in our survey **“{META['title']}”** "
             f"by {', '.join(META['authors'][:-1])} and {META['authors'][-1]} (IIT Roorkee). "
             'Papers are grouped by the survey’s taxonomy, and every entry links to the paper and, where available, its code.\n')
    o.append(f'**[Browse and search the list on the website]({site})**, with filters by fidelity level, approach and year.\n')
    o.append('> If this list helps your work, please ⭐ star the repository and [cite the survey](#citation). '
             'Missing a paper? [Open an issue or a pull request](CONTRIBUTING.md).\n')

    o.append('## The four levels of semantic fidelity\n')
    o.append('Take the prompt *“Two red cubes to the left of a cat”*. A model can get it wrong in four ways:\n')
    o.append('| Level | Prompt words at stake | Typical failure | Papers |')
    o.append('|---|---|---|---|')
    for l in LEVELS:
        lab, words, fail = LEVEL_EXAMPLE[l]
        cnt = sum(1 for p in PAPERS if l in p['levels'])
        o.append(f'| [{lab}](#{l}) | *{words}* | {fail} | {cnt} |')
    o.append('')

    o.append('## Taxonomy\n')
    o.append('```mermaid\nmindmap\n  root((Semantic fidelity))')
    for g in TAX:
        if g['id'] in LEVELS:
            o.append(f"    {g['title'].replace('-Level Fidelity', ' level')}")
            for s in g['subsections']:
                o.append(f"      {s['title'].replace('Inference: ', 'Inference, ').replace('/', 'or').replace('&', 'and')}")
    o.append('    Evaluation\n      Visual fidelity metrics\n      Semantic fidelity metrics\n      Prompt datasets and benchmarks')
    o.append('```\n')

    o.append('## Contents\n')
    for g in TAX:
        o.append(f"- [{g['title']}](#{g['id']})")
        if len(g['subsections']) > 1:
            for s in g['subsections']:
                o.append(f"  - [{s['title']}](#s-{s['id'].replace('.', '-')})")
    o.append('- [Citation](#citation)\n')

    for g in TAX:
        sec = f" (§{g['paper_section']})" if g['paper_section'] else ''
        o.append(f'<a id="{g["id"]}"></a>\n')
        o.append(f"## {g['icon']} {g['title']}{sec}\n")
        o.append(f"{GROUP_DESC[g['id']]}\n")
        for s in g['subsections']:
            items = secs.get(s['id'], [])
            if not items:
                continue
            if len(g['subsections']) > 1:
                o.append(f'<a id="s-{s["id"].replace(".", "-")}"></a>\n')
                o.append(f"### {s['title']} (§{s['id']})\n")
            o.append('| Ref | Method | Paper | Venue | Links |')
            o.append('|:-:|---|---|---|---|')
            for p in items:
                links = f"[{p['url_label']}]({p['url']})"
                if p['code']:
                    links += f" [{'Code' if 'github.com' in p['code'] else 'Project'}]({p['code']})"
                o.append(f"| [{p['id']}] | {('**' + md_escape(p['name']) + '**') if p['name'] else ''} | "
                         f"[{md_escape(p['title'])}]({p['url']}) <br><sub>{md_escape(p['authors'])}</sub> | "
                         f"{p['venue']} {p['year']} | {links} |")
            o.append('')
        o.append('<p align="right"><a href="#contents">back to top</a></p>\n')

    o.append('<a id="citation"></a>\n')
    o.append('## Citation\n')
    o.append('If you find the survey or this list useful, please cite:\n')
    o.append('```bibtex\n' + bibtex() + '\n```\n')
    o.append('## Contributing\n')
    o.append('New papers on semantic fidelity in text-to-image generation are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md); '
             'in short, add an entry to `data/papers.json` and run `python scripts/build_site.py`.\n')
    o.append('## Star history\n')
    o.append(f'[![Star History Chart](https://api.star-history.com/svg?repos={REPO}&type=Date)](https://star-history.com/#{REPO}&Date)\n')
    o.append(f'<sub>Numbers in brackets match the survey’s reference list. Links point to arXiv or the official open-access version where one exists. Last updated {TODAY}.</sub>\n')
    return '\n'.join(o)


# ------------------------------------------------------------------ website
def site():
    t = (ROOT / 'site/template.html').read_text(encoding='utf-8')
    jsonld = {
        '@context': 'https://schema.org', '@type': 'ScholarlyArticle', 'headline': META['title'],
        'name': META['title'],
        'author': [{'@type': 'Person', 'name': a,
                    'affiliation': {'@type': 'Organization', 'name': 'Indian Institute of Technology Roorkee'}}
                   for a in META['authors']],
        'keywords': 'Diffusion models, Text-to-image generation, Semantic fidelity, Compositional generation',
        'about': 'Semantic fidelity challenges in diffusion-based text-to-image models',
    }
    if META.get('paper_url'):
        jsonld['url'] = META['paper_url']
    data = json.dumps(D, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return (t.replace('__DATA__', data)
             .replace('__JSONLD__', json.dumps(jsonld, ensure_ascii=False).replace('</', '<\\/'))
             .replace('__BIBTEX__', html.escape(bibtex()))
             .replace('__REPO__', REPO)
             .replace('__N__', str(len(PAPERS)))
             .replace('__DATE__', TODAY))


def citation_cff():
    auth = '\n'.join(f"  - family-names: \"{a.split()[-1]}\"\n    given-names: \"{' '.join(a.split()[:-1])}\"\n"
                     f"    affiliation: \"Indian Institute of Technology Roorkee\"" for a in META['authors'])
    url = f"\n  url: \"{META['paper_url']}\"" if META.get('paper_url') else ''
    return f'''cff-version: 1.2.0
message: "If you use this paper list, please cite the survey below."
title: "Awesome Semantic Fidelity in Text-to-Image Diffusion Models"
repository-code: "https://github.com/{REPO}"
authors:
{auth}
preferred-citation:
  type: article
  title: "{META['title']}"
  authors:
{chr(10).join('  ' + l for l in auth.splitlines())}
  journal: "{META['journal']}"
  year: {META['year']}{url}
'''


if __name__ == '__main__':
    (ROOT / 'docs').mkdir(exist_ok=True)
    (ROOT / 'README.md').write_text(readme(), encoding='utf-8')
    (ROOT / 'docs/index.html').write_text(site(), encoding='utf-8')
    (ROOT / 'docs/.nojekyll').write_text('')
    (ROOT / 'CITATION.cff').write_text(citation_cff(), encoding='utf-8')
    print(f'Built README.md, docs/index.html and CITATION.cff with {len(PAPERS)} papers.')
