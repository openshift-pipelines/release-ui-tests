# Troubleshooting

**Q: Skill says method exists but generates duplicate**
**A**: Method signature might differ. Review the analysis report for details.

**Q: Generated YAML fails in cluster**
**A**: Tekton version mismatch. Provide more specific intent or manually fix YAML.

**Q: Tests timeout during execution**
**A**: Increase `APP_TIMEOUT` in `.env` or add explicit waits in step definitions.

**Q: Feature file has duplicate examples**
**A**: Test data files must have unique names. Skill derives resource names from filenames.
