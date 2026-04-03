# Lead Finder v1.2

## This upgrade adds
- Multi-search-source collection: DuckDuckGo + Bing + Google parser layer
- Company name extraction from page title / meta / H1 / domain
- Email quality filter with `high / medium / low`
- More personalized letters using `company_name`, `country`, `keyword`, and business hint
- Expanded keyword library for glass beads / road marking / traffic safety buyers
- Improved Excel / CSV output fields
- Master database dedupe still based on `(website, email)`

## Important production note
This version includes parser support for public Google / Bing / DuckDuckGo result pages.
Because search engine HTML and anti-bot behavior can change at any time, production use is more stable when later switched to API, proxy, or browser automation.

## Main output files
- `leads.csv`
- `leads.xlsx`
- `letters.txt`
- `followup.csv`
- `due_followups.csv`
- `leads_master.csv`

## New lead fields
- `company_name`
- `email_quality`
- `email_quality_reason`
- `search_source`
- `source_count`
- `score`
- `score_reason`

## Suggested usage order
1. Update `keywords.txt`
2. Fill your sender info in `config.py`
3. Test `python3 main.py`
4. Check `leads.xlsx` and `letters.txt`
5. Only then consider enabling SMTP auto send

## Email auto-send safety
Keep these OFF until your templates and SMTP are fully tested:
- `AUTO_SEND_EMAILS = False`
- `SEND_INITIAL_EMAILS = False`
- `SEND_FOLLOWUP_EMAILS = False`

## macOS daily schedule
1. Open Terminal in this project folder
2. Copy the plist:
   `cp com.leadfinder.daily.plist ~/Library/LaunchAgents/`
3. Load it:
   `launchctl load ~/Library/LaunchAgents/com.leadfinder.daily.plist`
4. Check status:
   `launchctl list | grep leadfinder`
