# clawdfrancois Project Setup Documentation

## Overview

The clawdfrancois project has been set up with comprehensive branding and avatar integration. This document explains all the places where the logo/avatar is used and how to maintain consistency.

## What Was Set Up

### 1. **Project Logo** ✓
- **Location**: `assets/logo.png`
- **Dimensions**: 200x200px (red lobster with blonde hair)
- **Format**: PNG with transparency
- **Usage**: Primary branding asset

### 2. **Favicon** ✓
- **Location**: `assets/favicon.png`
- **Purpose**: Browser tab icon for web interface
- **Integration**: Referenced in HTML templates as `<link rel="icon">`

### 3. **Project Documentation** ✓
- **README.md**: Logo displayed at top, branding explained
- **assets/BRANDING.md**: Comprehensive logo usage guidelines
- **pyproject.toml**: Project metadata with proper configuration

### 4. **Web Interface Templates** ✓
- **Location**: `assets/templates/index.html`
- **Features**:
  - Responsive design with logo in header
  - Mobile-friendly chat interface
  - Gradient background matching clawdfrancois branding
  - Status indicator for connection state
  - Ready for backend integration

### 5. **Development Guidelines** ✓
- **CLAUDE.md**: Updated with project technologies and structure
- **pyproject.toml**: Complete Python project configuration

## Where the Logo Appears

| Location | Purpose | Format |
|----------|---------|--------|
| README.md | Project identification | Markdown image link |
| assets/logo.png | Primary asset storage | PNG 200x200 |
| assets/favicon.png | Browser tab icon | PNG |
| assets/templates/index.html | Web interface branding | HTML/CSS |
| Web interface header | Main navigation branding | Static image |
| Future: PyPI package | Package distribution page | Metadata reference |
| Future: Docker builds | Container metadata | LABEL directive |
| Future: GitHub pages | Project documentation | Markdown/HTML |

## Integration Checklist

### For Web Interface Development
- [ ] Place logo SVG or PNG in `assets/` for dynamic loading
- [ ] Reference favicon in all HTML templates
- [ ] Use logo dimensions 120px × 120px for header display
- [ ] Maintain white border around logo on colored backgrounds
- [ ] Test responsiveness on mobile devices (320px - 768px widths)

### For Telegram Bot
- [ ] Set bot profile picture to clawdfrancois logo via [@BotFather](https://t.me/botfather)
- [ ] Use logo in welcome messages
- [ ] Include logo in command help text (if supported)

### For API/Backend
- [ ] Serve static assets from `/static/` endpoint
- [ ] Include logo URL in API responses (optional)
- [ ] Add CORS headers if needed for external access

### For CI/CD Pipeline
- [ ] Include assets in build artifacts
- [ ] Verify static file serving in deployment tests
- [ ] Ensure favicon is properly cached

### For Future Package Distribution
- [ ] Add logo reference to PyPI package metadata
- [ ] Include `assets/` directory in `MANIFEST.in`
- [ ] Update package classifiers if needed

## Color Scheme

From the clawdfrancois logo:
- **Primary Red**: `#FF0000` (vibrant red lobster)
- **Accent Gold**: `#FFD700` (blonde hair)
- **Background**: Can use white, light gray, or gradient (purple gradient used in templates)

## Asset References in Code

### Python - Serving Static Files (Example)
```python
# Flask
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('assets', path)

# FastAPI
app.mount("/static", StaticFiles(directory="assets"), name="static")
```

### HTML - Logo Image Tag
```html
<img src="/static/logo.png" alt="clawdfrancois Logo" width="120" height="120">
```

### HTML - Favicon
```html
<link rel="icon" type="image/png" href="/static/favicon.png">
```

## Maintenance Notes

1. **Logo Updates** - If the logo is updated:
   - Replace both `assets/logo.png` and `assets/favicon.png`
   - Update `assets/BRANDING.md` with any dimension changes
   - Test all references throughout the project

2. **Responsive Design** - When adding new pages/templates:
   - Logo should scale responsively
   - Minimum size on mobile: 80px (squeezed layouts)
   - Normal size on desktop: 120px - 200px

3. **Accessibility** - Always include:
   - `alt` attribute on all `<img>` tags
   - Proper contrast ratios for text overlaid on logo
   - ARIA labels for decorative logos

4. **Performance** - Consider:
   - Optimize PNG files (use TinyPNG if needed)
   - Serve favicon with appropriate cache headers
   - Use WebP format for modern browsers (future enhancement)

## Files Modified/Created

```
✓ assets/logo.png              # Main logo (copied from Downloads)
✓ assets/favicon.png           # Favicon version
✓ assets/BRANDING.md           # Branding guidelines
✓ assets/templates/            # Web templates directory
✓ assets/templates/index.html  # Chat interface with logo
✓ assets/templates/README.md   # Template documentation
✓ README.md                    # Updated with logo and setup info
✓ pyproject.toml              # Python project configuration
✓ This file                    # Setup documentation
```

## Next Steps

1. **Telegram Bot Setup** 
   ```bash
   # Set: /setuserpic [upload logo.png] in @BotFather
   ```

2. **Web Server Integration** - Connect any Flask/FastAPI backend to serve templates

3. **CI/CD Integration** - Add asset validation to your build pipeline

4. **Mobile Testing** - Test web interface on various mobile devices

5. **Documentation** - Update team wiki/docs with logo guidelines

## Questions & Support

For logo usage questions, refer to:
- `assets/BRANDING.md` - Official branding guide
- `CLAUDE.md` - Development guidelines
- Template files - Reference implementations

---

**Setup completed on**: April 14, 2026  
**Avatar**: clawdfrancois (Red Lobster Mascot)  
**Status**: ✅ Ready for development
