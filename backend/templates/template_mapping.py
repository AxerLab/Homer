"""
Template mapping for PPTX themes.
Maps theme names to their corresponding template file paths.
"""
from pathlib import Path

# Get the templates directory
TEMPLATES_DIR = Path(__file__).parent

# Available themes and their template files
AVAILABLE_THEMES = {
    "default": None,  # Will use python-pptx default blank template
    "dark": TEMPLATES_DIR / "dark.pptx",
    "light": TEMPLATES_DIR / "light.pptx",
}

def get_template_path(theme: str | None) -> str | None:
    """
    Get the template file path for a given theme name.
    
    Args:
        theme: Theme name (e.g., 'default', 'dark', 'light')
        
    Returns:
        Absolute path to template file as string, or None for default theme
    """
    if theme is None or theme not in AVAILABLE_THEMES:
        return None
    
    template_path = AVAILABLE_THEMES[theme]
    if template_path is None:
        return None
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    return str(template_path)

def get_available_theme_names() -> list[str]:
    """
    Get list of all available theme names.
    
    Returns:
        List of theme names that can be used
    """
    return list(AVAILABLE_THEMES.keys())
