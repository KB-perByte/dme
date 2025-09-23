# Changelog Management Guide

This collection uses [`antsibull-changelog`](https://github.com/ansible-community/antsibull-changelog) for changelog management, following Ansible community standards.

## Overview

- **Changelog files**: `CHANGELOG.md` and `CHANGELOG.rst` (auto-generated)
- **Fragment directory**: `changelogs/fragments/`
- **Configuration**: `changelogs/config.yaml`
- **Release data**: `changelogs/changelog.yaml`

## Workflow for Contributors

### 1. Adding Changes

When making changes that should be noted in the changelog, create a fragment file:

```bash
# Create a new fragment file
cat > changelogs/fragments/your-change-description.yml << EOF
---
# Choose appropriate sections:
major_changes:
  - Description of major change

minor_changes:
  - Description of minor change

breaking_changes:
  - Description of breaking change

deprecated_features:
  - Description of deprecated feature

removed_features:
  - Description of removed feature

security_fixes:
  - Description of security fix

bugfixes:
  - Description of bug fix

known_issues:
  - Description of known issue
EOF
```

### 2. Fragment File Naming

Use descriptive names for fragment files:

- `add-new-module.yml`
- `fix-authentication-bug.yml`
- `deprecate-old-parameter.yml`
- `breaking-change-api.yml`

### 3. Fragment File Format

```yaml
---
# Release summary (only for major releases)
release_summary: |
  Brief description of the release.

# Major changes (new features, significant improvements)
major_changes:
  - Added support for new DME API endpoints
  - Implemented advanced authentication methods

# Minor changes (small features, improvements)
minor_changes:
  - Improved error messages for better debugging
  - Added validation for configuration parameters

# Bug fixes
bugfixes:
  - Fixed issue with connection timeout handling
  - Resolved authentication token refresh problem

# Breaking changes
breaking_changes:
  - Changed default timeout from 30s to 60s
  - Removed deprecated 'old_parameter' option

# Security fixes
security_fixes:
  - Fixed potential credential exposure in debug logs

# Deprecated features
deprecated_features:
  - The 'legacy_mode' parameter is deprecated and will be removed in v2.0.0

# Known issues
known_issues:
  - SSL verification may fail with older Python versions
```

## Workflow for Maintainers

### Creating a Release

1. **Ensure all fragments are ready**:

   ```bash
   ls changelogs/fragments/
   ```

2. **Create the release**:

   ```bash
   # Install dependencies if needed
   pip install antsibull-changelog ansible-core

   # Create release (replace X.Y.Z with actual version)
   export PATH="$HOME/.local/bin:$PATH"
   python3 -m antsibull_changelog release --version X.Y.Z
   ```

3. **Review generated files**:

   - `CHANGELOG.md` - Markdown format for GitHub
   - `CHANGELOG.rst` - ReStructuredText format for docs
   - `changelogs/changelog.yaml` - Machine-readable changelog data

4. **Update galaxy.yml version**:

   ```yaml
   version: X.Y.Z
   ```

5. **Commit and tag**:
   ```bash
   git add .
   git commit -m "Release v X.Y.Z"
   git tag v X.Y.Z
   git push origin main --tags
   ```

### Pre-release Testing

Test changelog generation without creating a release:

```bash
# Generate preview
python3 -m antsibull_changelog generate --reload-plugins
```

## Configuration Options

The changelog behavior is configured in `changelogs/config.yaml`:

```yaml
# Key configuration options:
title: Cisco.Dme # Collection name in changelog
use_fqcn: true # Use fully qualified collection names
keep_fragments: false # Remove fragments after release
changelog_nice_yaml: false # YAML formatting style
sanitize_changelog: true # Clean up formatting

# Output formats
output:
  - file: CHANGELOG.rst
    format: rst
  - file: CHANGELOG.md
    format: md

# Change categories
sections:
  - [major_changes, Major Changes]
  - [minor_changes, Minor Changes]
  - [breaking_changes, Breaking Changes / Porting Guide]
  - [deprecated_features, Deprecated Features]
  - [removed_features, Removed Features (previously deprecated)]
  - [security_fixes, Security Fixes]
  - [bugfixes, Bugfixes]
  - [known_issues, Known Issues]
```

## Best Practices

### Fragment Guidelines

1. **Be descriptive**: Clearly explain what changed and why
2. **User-focused**: Write for end users, not developers
3. **Action-oriented**: Use active voice ("Added", "Fixed", "Changed")
4. **Categorize correctly**: Choose the most appropriate section
5. **One change per fragment**: Keep fragments focused on single changes

### Examples of Good Fragments

**Good**:

```yaml
bugfixes:
  - Fixed authentication failure when using special characters in passwords
```

**Bad**:

```yaml
bugfixes:
  - Fixed bug in auth
```

**Good**:

```yaml
major_changes:
  - Added support for DME v2.0 API with enhanced security features
```

**Bad**:

```yaml
minor_changes:
  - Updated API
```

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **Major (X.0.0)**: Breaking changes, major new features
- **Minor (X.Y.0)**: New features, backwards compatible
- **Patch (X.Y.Z)**: Bug fixes, backwards compatible

### Release Timing

- **Patch releases**: As needed for critical bug fixes
- **Minor releases**: Monthly or when significant features are ready
- **Major releases**: Quarterly or when breaking changes are necessary

## Troubleshooting

### Common Issues

1. **Command not found**: Ensure `antsibull-changelog` and `ansible-core` are installed
2. **Path issues**: Add `$HOME/.local/bin` to your PATH
3. **Permission errors**: Use `pip install --user` for user installations
4. **Invalid YAML**: Validate fragment files with `yamllint`

### Validation

```bash
# Check fragment syntax
yamllint changelogs/fragments/*.yml

# Test changelog generation
python3 -m antsibull_changelog generate --reload-plugins
```

## Integration with CI/CD

Consider adding changelog validation to your CI pipeline:

```yaml
# Example GitHub Actions step
- name: Validate changelog fragments
  run: |
    pip install antsibull-changelog yamllint
    yamllint changelogs/fragments/
    python3 -m antsibull_changelog generate --reload-plugins
```

## Resources

- [antsibull-changelog documentation](https://github.com/ansible-community/antsibull-changelog)
- [Ansible changelog standards](https://docs.ansible.com/ansible/devel/community/development_process.html#changelogs)
- [Semantic Versioning](https://semver.org/)
