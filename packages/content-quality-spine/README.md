# content-quality-spine

Portable SourceA shared content-quality spine. Install from Git:

```bash
pip install "content-quality-spine @ git+https://github.com/Noetfield-Systems/SourceA@<sha>#subdirectory=packages/content-quality-spine"
```

Evaluate:

```bash
python3 -m content_quality_spine evaluate \
  --artifact artifact.json \
  --adapter adapter.json \
  --rules rules.json \
  --output ./receipts
```
