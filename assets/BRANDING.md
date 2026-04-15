# clawdfrancois Avatar & Branding

## Logo

The official **clawdfrancois** logo is stored in the `assets/` directory:

- **File**: `assets/logo.png`
- **Dimensions**: 200x200px (can be scaled)
- **Location**: Red lobster mascot with golden/blonde hair

## Usage Guidelines

### README.md
The logo is displayed at the top of the README for project identification.

### Web Interface
If a web-based interface is implemented (HTML/frontend), the logo should be used:
- As the page favicon (`/favicon.ico` or via favicon.png)
- As a header/branding element in the navigation bar
- In any deployed documentation

### API/Server Response
The bridge server can optionally include the logo URL or base64-encoded data in API responses for mobile clients that support displaying project branding.

### Docker/Container Images
If Docker images are created, consider using the logo as the container image metadata:
```dockerfile
LABEL maintainer="clawdfrancois"
LABEL icon="logo.png"
```

### Package Distribution
If this project is distributed via PyPI or other package managers in the future, the logo should be referenced in the package metadata through `pyproject.toml`.

## Asset Organization

```
assets/
├── logo.png           # Main project logo (200x200px)
└── [future assets]    # Screenshots, diagrams, icons, etc.
```

## Branding Standards

- **Primary Color**: Red (#FF0000 approximate)
- **Project Name**: clawdfrancois (with ç character)
- **Mascot**: Red lobster with blonde hair
- **Theme**: Playful, tech-forward coastal imagery

---

For questions about logo usage, refer to `CLAUDE.md` for development guidelines.
