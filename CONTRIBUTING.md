# Contributing to Warrior Dashboard

First off, thanks for considering contributing! 🎉

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Screenshots** (if applicable)
- **Environment details** (Python version, OS, browser)

### Suggesting Features

Feature requests are welcome! Please:

- **Use a clear title**
- **Provide detailed description**
- **Explain why this would be useful**
- **Include mockups** (if applicable)

### Pull Requests

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/warrior-dashboard.git
cd warrior-dashboard

# Install dependencies
pip install Flask

# Run in development mode
python app.py
```

## Coding Standards

### Python

- Follow PEP 8
- Use meaningful variable names
- Add comments for complex logic
- Keep functions under 50 lines

### JavaScript

- Use ES6+ features
- Use `const` and `let`, not `var`
- Add JSDoc comments for functions
- Keep functions focused and small

### CSS

- Use existing CSS variables
- Follow BEM naming where applicable
- Keep selectors specific but not overly nested
- Mobile-first responsive design

## Project Structure

```
warrior_dashboard/
├── app.py              # Flask backend
├── templates/
│   └── index.html      # Main page
├── static/
│   ├── css/
│   │   └── style.css   # All styles
│   └── js/
│       └── app.js      # Frontend logic
└── data/
    └── character_data.json  # User data
```

## Adding New Features

### Adding a New Activity

1. **Add checkbox in HTML** (`templates/index.html`)
2. **Add point calculation** in `app.py` (`@app.route('/api/daily-log')`)
3. **Map to stat** for XP distribution
4. **Test thoroughly**

### Adding a New API Endpoint

1. **Create route** in `app.py`
2. **Add error handling**
3. **Update API.md** documentation
4. **Add tests** (coming soon)

### Adding UI Features

1. **Add HTML structure**
2. **Style with existing CSS variables**
3. **Add JavaScript functionality**
4. **Test on mobile**

## Testing

Currently manual testing only. Automated tests coming soon!

**Test checklist:**
- [ ] Desktop Chrome, Firefox, Safari
- [ ] Mobile Chrome, Safari
- [ ] All features work
- [ ] No console errors
- [ ] Data persists correctly

## Documentation

Update these files if your PR affects them:

- `README.md` — Main documentation
- `API.md` — API reference (if adding endpoints)
- `CHANGELOG.md` — List your changes (coming soon)

## Code of Conduct

- Be respectful
- Be constructive
- Be collaborative
- Have fun!

## Questions?

Open an issue with the `question` label or reach out directly.

Thanks for contributing! ⚔️
