"""
Configuration Loader for Behavior Intelligence Platform.
Loads settings from config.yaml and provides dot-notation access.
"""
import yaml
import os
from pathlib import Path

class ConfigLoader:
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self._config = self._load()

    def _load(self):
        root_dir = Path(__file__).parent
        path = root_dir / self.config_path
        if not path.exists():
             # Fallback for scripts running from subdirectories
             path = Path(os.getcwd()) / self.config_path
             
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found at {path}")
            
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def __getattr__(self, name):
        if name in self._config:
            val = self._config[name]
            if isinstance(val, dict):
                return ConfigDict(val)
            return val
        raise AttributeError(f"Config has no attribute '{name}'")

class ConfigDict:
    def __init__(self, data):
        self._data = data
        
    def __getattr__(self, name):
        if name in self._data:
            val = self._data[name]
            if isinstance(val, dict):
                return ConfigDict(val)
            return val
        raise AttributeError(f"Config section has no attribute '{name}'")

    def __getitem__(self, key):
        return self._data[key]
    
    def get(self, key, default=None):
        return self._data.get(key, default)

def _sync_streamlit_theme(theme_name):
    """
    Writes/Updates .streamlit/config.toml to match the YAML theme.
    Streamlit doesn't support programmatic global theme switching via st.xxx
    at runtime for the base UI, so we must use the config file.
    """
    dot_streamlit = Path(os.getcwd()) / ".streamlit"
    dot_streamlit.mkdir(exist_ok=True)
    config_toml = dot_streamlit / "config.toml"
    
    # Map 'light'/'dark' to Streamlit settings
    base = "light" if theme_name.lower() == "light" else "dark"
    
    content = f"""[theme]
base="{base}"
"""
    # Only write if different to avoid unnecessary server reloads
    if not config_toml.exists() or config_toml.read_text().strip() != content.strip():
        config_toml.write_text(content)

# Singleton instance
_cfg = ConfigLoader()

# Sync theme on load
_sync_streamlit_theme(_cfg.dashboard.theme)

# Export specific values or the whole object
app = _cfg.app
data = _cfg.data
rfm = _cfg.rfm
api = _cfg.api
actions = _cfg.actions
dashboard = _cfg.dashboard

# For backward compatibility with my recent change
CURRENCY_SYMBOL = app.currency.symbol
CURRENCY_CODE = app.currency.code
