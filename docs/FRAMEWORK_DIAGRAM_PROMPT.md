# Image Generation Prompt for Test Automation Framework

**Copy the text below and paste it into an AI image generation model (DALL-E, Midjourney, etc.)**

---

## Prompt for Image Generation Model:

Create a professional, clean technical architecture diagram showing a test automation framework with the following structure:

**Top Section - Test Definition Layer (Gherkin/BDD):**
- A box labeled "Feature Files (.feature)" containing sample text: "Given user logs in, When user creates task, Then task appears in list"
- Icon: Document with checkmarks
- Color: Light blue (#E3F2FD)

**Second Section - Test Execution Layer:**
- Box labeled "pytest-bdd" with subtitle "Test Runner & Step Matcher"
- Shows arrow connecting to Feature Files
- Icon: Gear/cog wheel
- Color: Green (#C8E6C9)

**Third Section - Step Definitions Layer:**
- Box labeled "Step Definitions (Python)" containing "test_task_crud_steps.py, test_auth_steps.py, test_navigation_steps.py"
- Arrow from pytest-bdd pointing here
- Icon: Python logo
- Color: Yellow (#FFF9C4)

**Fourth Section - Page Object Model (Core Framework):**
- Large box labeled "Page Object Model (POM)" containing 4 sub-boxes:
  1. "Page Objects" - "TasksPage, PipelinesPage, TriggersPage"
  2. "Locators" - "CSS selectors, data-test attributes"
  3. "Commons" - "Login, Navigation, Modals, Project Selector"
  4. "Helpers" - "YAML Loader, Field Extractor, CLI Wrapper"
- Icon: Layered blocks/modules
- Color: Orange (#FFE0B2)
- Arrow from Step Definitions pointing here

**Fifth Section - Browser Automation:**
- Box labeled "Playwright" with subtitle "Browser Controller"
- Shows Chrome browser icon
- Arrow from POM pointing here
- Icon: Browser window
- Color: Purple (#E1BEE7)

**Sixth Section - Application Under Test:**
- Box labeled "OpenShift Console" with subtitle "Tekton Pipelines UI"
- Shows web application interface
- Arrow from Playwright pointing here
- Icon: Web application/cloud
- Color: Red (#FFCDD2)

**Bottom Section - Supporting Infrastructure:**
Three boxes side by side:
1. "Test Data (YAML files)" - simple_task.yaml, pipeline_templates
2. "CLI Integration (oc commands)" - Project creation, Resource cleanup
3. "Fixtures & Config" - Browser setup, Login sessions, Isolated projects

**Flow Arrows:**
- Show data flow from top to bottom with clear arrows
- Add labels on arrows: "Defines Tests", "Executes Steps", "Controls UI", "Interacts With"

**Additional Visual Elements:**
- Add "SOLID Principles" badge in top-right corner
- Add "BDD Framework" label in top-left corner
- Use rounded corners for all boxes
- Add subtle shadows for depth
- Include version label at bottom: "Playwright + pytest-bdd + Page Object Model"

**Style:**
- Clean, modern, professional
- Use pastel colors for clarity
- Clear hierarchy (top-down flow)
- Suitable for management presentation
- High contrast for readability
- Grid-aligned boxes

---

## Alternative Simplified Prompt (if the above is too complex):

Create a simple flowchart diagram showing:
1. Top: "Test Scenarios (Gherkin)" in blue box
2. Arrow down to: "pytest-bdd Runner" in green box
3. Arrow down to: "Python Step Definitions" in yellow box
4. Arrow down to: "Page Object Model" in orange box (with sub-components: Pages, Locators, Helpers)
5. Arrow down to: "Playwright Browser Automation" in purple box
6. Arrow down to: "OpenShift Console (Application)" in red box

Add side boxes for:
- Left side: "Test Data (YAML)" and "CLI Tools (oc)"
- Right side: "Fixtures" and "Config"

Use rounded rectangles, clean lines, pastel colors, and professional style suitable for management presentation.

---

## Tips for Using This Prompt:

1. **DALL-E 3**: Copy the main prompt above, it handles detailed descriptions well
2. **Midjourney**: Use the simplified prompt and add `--ar 16:9 --style corporate --v 6` at the end
3. **Stable Diffusion**: Use simplified prompt with "professional technical diagram, clean style, corporate presentation"
4. **After Generation**: You may need to add text labels manually in PowerPoint/Google Slides for clarity

---

## Expected Output:

A professional architecture diagram showing:
- Clear visual hierarchy (top to bottom flow)
- Component relationships (boxes and arrows)
- Technology stack (pytest, Playwright, Page Objects)
- Test flow (Feature → Steps → POM → Browser → App)
- Supporting infrastructure (Data, CLI, Config)

Perfect for:
- Management presentations
- Architecture reviews
- Onboarding documentation
- Stakeholder updates
