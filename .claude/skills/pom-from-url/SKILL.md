---
name: pom-from-url
description: Full pipeline — scrape a page and generate its POM file in one command.
disable-model-invocation: true
allowed-tools: Read Write Bash(python *) mcp__playwright__browser_navigate mcp__playwright__browser_snapshot mcp__playwright__browser_screenshot
---

Run the full POM generation pipeline for $ARGUMENTS:

1. Use the `extract-page-structure` skill steps on the URL
2. Save the extracted JSON to `tmp/page_structure.json`
3. Use the `generate-pom` skill steps to generate the POM from that JSON
4. Report: what file was created, how many locators and methods it contains
