---
name: extract-page-structure
description: Navigate to a page and extract its DOM structure for POM generation.
Use when asked to scrape, inspect, or extract elements from a page.
disable-model-invocation: true
allowed-tools: Bash(npx playwright *) mcp__playwright__browser_navigate mcp__playwright__browser_snapshot mcp__playwright__browser_screenshot
---

Navigate to $ARGUMENTS using Playwright MCP and extract the full page structure:

1. Navigate to the URL with `browser_navigate`
2. Take a screenshot for visual reference
3. Get the accessibility tree snapshot with `browser_snapshot`
4. From the snapshot, identify and list ALL interactive elements:
   - Inputs (text, email, password, checkbox, radio, select, file)
   - Buttons and links
   - Forms and their fields
   - Tables and data grids
   - Modals and dialogs
   - Navigation menus
5. For each element, record:
   - Element type
   - ARIA role
   - Visible label / placeholder / aria-label
   - data-testid or data-cy attribute if present
   - CSS class or ID if no testid exists
   - Whether it is inside a specific section/region
6. Output this as a structured JSON block with this shape:
   {
     "page_name": "<inferred from URL or title>",
     "url": "<url>",
     "sections": [
       {
         "name": "<section name>",
         "elements": [
           {"type": "...", "role": "...", "label": "...", "locator": "...", "locator_strategy": "testid|aria|css"}
         ]
       }
     ]
   }
