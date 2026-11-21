# Monaco Editor Interaction Guide

## Overview

OpenShift Console uses **Monaco Editor** (the same editor from VS Code) for all code/YAML editing. Monaco is NOT a standard HTML input element and requires special interaction methods.

## CRITICAL: Do NOT Use Standard Input Methods

❌ **NEVER use these methods with Monaco:**
```python
await page.fill(selector, text)  # Will timeout
await page.locator(selector).fill(text)  # Will timeout
await self.fill_input(selector, text)  # Will timeout
```

These methods work for `<input>` and `<textarea>` elements but **fail with Monaco**.

## ✅ Correct Approach: Use MonacoEditor Component

### 1. Import the Component

```python
from framework.ui_components.commons.monaco_editor import MonacoEditor
```

### 2. Compose in Page Object

```python
class YourPage(BasePage):
    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        # Compose MonacoEditor component
        self.monaco_editor = MonacoEditor(page, config)
```

### 3. Set Editor Content

```python
async def fill_yaml_editor(self, yaml_content: str) -> bool:
    """Fill Monaco YAML editor with content."""
    return await self.monaco_editor.set_content(yaml_content)
```

### 4. Get Editor Content

```python
async def get_yaml_content(self) -> str:
    """Get current content from Monaco editor."""
    return await self.monaco_editor.get_content()
```

## How MonacoEditor Works

The component uses Monaco's JavaScript API (same approach as console's Cypress tests):

```javascript
// Set content
window.monaco.editor.getModels()[0].setValue(content);

// Get content
window.monaco.editor.getModels()[0].getValue();
```

**Reference**: `frontend/packages/integration-tests/views/yaml-editor.ts`

## Locators for Monaco Editor

### ✅ Correct Locators

```python
YAML_EDITOR = ".monaco-editor"  # Container
YAML_EDITOR_MOUNTED = '[data-test="code-editor"]'  # When fully loaded
YAML_EDITOR_TEXTAREA = ".monaco-editor textarea"  # For focus/keyboard
```

### ❌ Incorrect Locators (DO NOT USE)

```python
YAML_EDITOR = 'textbox[aria-label*="Editor content"]'  # Wrong! Doesn't work
```

## Design Pattern: Composition over Duplication

**SOLID Principle Applied**: Single Responsibility + DRY

```python
# ✅ GOOD: Compose MonacoEditor
class PipelineYamlPage(BasePage):
    def __init__(self, page: Page, config: Config):
        super().__init__(page, config)
        self.monaco_editor = MonacoEditor(page, config)  # Compose

    async def fill_yaml_editor(self, content: str) -> bool:
        return await self.monaco_editor.set_content(content)  # Delegate


# ❌ BAD: Duplicate Monaco logic in every page
class PipelineYamlPage(BasePage):
    async def fill_yaml_editor(self, content: str) -> bool:
        # 100+ lines of duplicated Monaco interaction code
        await self.page.evaluate("...")  # Code duplication!
```

## Existing Pages Using MonacoEditor

These pages already use the MonacoEditor component correctly:

1. `framework/ui_components/pipelines/pipeline_yaml_page.py`
2. `framework/ui_components/pipeline_builder/yaml_view.py`
3. `framework/ui_components/tasks/task_yaml_page.py` (if exists)

**Pattern to follow**: Always check if these pages exist and reuse their implementation.

## When Generating Code

### If YAML Editor Method Exists

```bash
# Check for existing implementation
grep -r "def fill_yaml_editor" framework/ui_components/**/*.py
grep -r "def get_yaml_content" framework/ui_components/**/*.py
```

If found, **reuse the existing method**. Don't generate a new one.

### If YAML Editor Method Doesn't Exist

Generate using this pattern:

```python
from framework.ui_components.commons.monaco_editor import MonacoEditor


class NewPage(BasePage):
    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.monaco_editor = MonacoEditor(page, config)

    async def fill_yaml_editor(self, yaml_content: str) -> bool:
        """Fill Monaco YAML editor with content."""
        return await self.monaco_editor.set_content(yaml_content)

    async def get_yaml_content(self) -> str:
        """Get current content from Monaco editor."""
        return await self.monaco_editor.get_content()
```

## Console Implementation Reference

The OpenShift Console's own implementation can be found at:

- **CodeEditor Component**: `frontend/packages/console-shared/src/components/editor/CodeEditor.tsx`
  - Sets `data-test="code-editor"` when Monaco is fully mounted
  - Exposes global `window.monaco` object

- **Cypress Tests**: `frontend/packages/integration-tests/views/yaml-editor.ts`
  - `setEditorContent()`: Uses `monaco.editor.getModels()[0].setValue()`
  - `getEditorContent()`: Uses `monaco.editor.getModels()[0].getValue()`
  - `isLoaded()`: Waits for `[data-test="code-editor"]`

## Common Errors

### Error: "Locator.fill: Timeout 90000ms exceeded"

**Cause**: Using `fill()` on Monaco editor
**Solution**: Use `MonacoEditor.set_content()` instead

### Error: "textbox[aria-label*='Editor content'] not found"

**Cause**: Wrong locator for Monaco
**Solution**: Use `.monaco-editor` or `[data-test="code-editor"]`

### Error: "window.monaco is not defined"

**Cause**: Monaco not fully loaded yet
**Solution**: `MonacoEditor.wait_for_editor_ready()` is called automatically

## Testing

Generated test steps should use Monaco-aware methods:

```python
# ✅ GOOD
yaml_filled = await page["pipelines"].yaml.fill_yaml_editor(yaml_content)
content = await page["pipelines"].yaml.get_yaml_content()

# ❌ BAD
await page["pipelines"].yaml.fill_input(selector, yaml_content)  # Will fail!
```

## Summary Checklist

When generating code that interacts with YAML/code editors:

- [ ] Import `MonacoEditor` from `framework.ui_components.commons`
- [ ] Compose `MonacoEditor` in page object `__init__`
- [ ] Use `monaco_editor.set_content()` to fill
- [ ] Use `monaco_editor.get_content()` to read
- [ ] Use correct locators (`.monaco-editor`, `[data-test="code-editor"]`)
- [ ] Never use `fill_input()` or standard `fill()` methods

---

**Version**: 1.0.0
**Last Updated**: 2026-05-04
**Related**: [Implementation Guide](implementation-guide.md)
