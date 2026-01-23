# SSRN Automation - Quick Start Guide

## Generate a Paper in One Command

```bash
cd /home/ubuntu/SSRN-AUTOMATION
python3 run_automation.py "your paper topic here"
```

## Example

```bash
python3 run_automation.py "behavioral biases in cryptocurrency markets"
```

## What Happens Automatically

1. ✅ Generates paper with contra-suggestive title
2. ✅ Writes content in authentic human academic voice
3. ✅ Removes all AI watermarks and artifacts
4. ✅ Creates properly formatted PDF
5. ✅ Names file: `Walter_Evans_[ShortTitle]_[YYYYMMDD].pdf`
6. ✅ Runs quality checks
7. ✅ Extracts metadata and keywords
8. ✅ Uploads to Google Drive
9. ✅ Backs up to GitHub
10. ✅ Generates submission info

## Output Locations

- **PDF**: `/home/ubuntu/SSRN-AUTOMATION/output/Walter_Evans_*.pdf`
- **Metadata**: `/home/ubuntu/SSRN-AUTOMATION/metadata/`
- **Logs**: `/home/ubuntu/SSRN-AUTOMATION/logs/`
- **Google Drive**: Folder ID `1qVmicFsMOLngIoRIAkeVZNreVblXbLic`
- **GitHub**: `midnghtsapphire/SSRN_Whitepapers`

## Manual Steps (If Needed)

### Generate Only
```bash
python3 scripts/generate_paper.py "topic"
```

### Quality Check Only
```bash
python3 scripts/quality_checker.py path/to/paper.pdf path/to/text.txt
```

### Upload Only
```bash
python3 scripts/upload_and_backup.py path/to/paper.pdf path/to/metadata.json
```

## Naming Convention Enforcement

**MANDATORY FORMAT**: `Walter_Evans_[ShortTitle]_[YYYYMMDD].pdf`

✅ Correct:
- `Walter_Evans_Quantum_Cognition_20260123.pdf`
- `Walter_Evans_Market_Efficiency_20260124.pdf`

❌ Incorrect:
- `Complete_Paper_Final.pdf`
- `Paper_20260123.pdf`
- `Evans_Quantum_20260123.pdf`

## Quality Requirements Checklist

- ✅ Filename starts with `Walter_Evans_`
- ✅ Abstract ≤200 words
- ✅ No AI watermarks or mentions
- ✅ No author name in body text
- ✅ Human academic writing style
- ✅ SEO-optimized keywords
- ✅ JEL classification codes
- ✅ All required sections present

## Troubleshooting

### Check Logs
```bash
cat logs/automation_$(date +%Y%m%d).log
```

### Verify Google Drive
```bash
rclone ls manus_google_drive:1qVmicFsMOLngIoRIAkeVZNreVblXbLic --config /home/ubuntu/.gdrive-rclone.ini
```

### Verify GitHub
```bash
cd /home/ubuntu/SSRN_Whitepapers && git log --oneline -5
```

## Support Files

- **Configuration**: `config.json`
- **Full Documentation**: `README.md`
- **Metadata Tracking**: `metadata/papers_log.csv`

## Author Information

**Audrey Evans**  
ORCID: 0009-0005-0663-7832  
Email: angelreporters@gmail.com
