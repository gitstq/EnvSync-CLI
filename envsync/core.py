#!/usr/bin/env python3
"""
EnvSync Core Engine - 核心引擎模块
Handles configuration parsing, file operations, encryption, and sync logic.
"""

import os
import sys
import json
import shutil
import hashlib
import base64
import tempfile
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any


class EnvSyncError(Exception):
    """Base exception for EnvSync"""
    pass


class ConfigError(EnvSyncError):
    """Configuration related errors"""
    pass


class SyncError(EnvSyncError):
    """Synchronization related errors"""
    pass


class EncryptionError(EnvSyncError):
    """Encryption related errors"""
    pass


class SimpleEncryption:
    """
    Simple XOR-based encryption for sensitive config files.
    Not for high-security use, but sufficient for basic config protection.
    """
    
    def __init__(self, key: str):
        self.key = key.encode('utf-8')
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        data_bytes = data.encode('utf-8')
        encrypted = bytearray()
        for i, byte in enumerate(data_bytes):
            encrypted.append(byte ^ self.key[i % len(self.key)])
        return base64.b64encode(bytes(encrypted)).decode('utf-8')
    
    def decrypt(self, data: str) -> str:
        """Decrypt string data"""
        try:
            encrypted = base64.b64decode(data.encode('utf-8'))
            decrypted = bytearray()
            for i, byte in enumerate(encrypted):
                decrypted.append(byte ^ self.key[i % len(self.key)])
            return bytes(decrypted).decode('utf-8')
        except Exception as e:
            raise EncryptionError(f"Decryption failed: {e}")


class ConfigTemplate:
    """
    Template engine for configuration files.
    Supports variable substitution and conditional blocks.
    """
    
    def __init__(self, template_str: str, variables: Dict[str, Any]):
        self.template = template_str
        self.variables = variables
    
    def render(self) -> str:
        """Render template with variables"""
        result = self.template
        for key, value in self.variables.items():
            placeholder = f"{{{{ {key} }}}}"
            result = result.replace(placeholder, str(value))
        
        # Handle conditional blocks: {{#if os_name == "Linux"}}...{{/if}}
        import re
        pattern = r'\{\{#if\s+(.+?)\s*==\s*"(.+?)"\}\}(.*?)\{\{/if\}\}'
        
        def replace_conditional(match):
            var_name = match.group(1).strip()
            expected = match.group(2)
            content = match.group(3)
            actual = self.variables.get(var_name, '')
            if str(actual) == expected:
                return content
            return ''
        
        result = re.sub(pattern, replace_conditional, result, flags=re.DOTALL)
        return result


class FileTracker:
    """
    Tracks file changes using hash-based comparison.
    """
    
    @staticmethod
    def compute_hash(filepath: Path) -> str:
        """Compute SHA256 hash of file"""
        h = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    
    @staticmethod
    def compute_content_hash(content: str) -> str:
        """Compute hash of string content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()


class ConfigManager:
    """
    Main configuration manager.
    Handles reading, writing, and validating envsync configuration.
    """
    
    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "name": "my-env",
        "description": "My development environment configuration",
        "created_at": "",
        "updated_at": "",
        "sync": {
            "enabled": True,
            "exclude_patterns": [
                "*.log",
                "*.tmp",
                ".DS_Store",
                "Thumbs.db",
                "node_modules/",
                "__pycache__/",
                ".git/"
            ],
            "encrypt_sensitive": True,
            "backup_before_sync": True
        },
        "files": [],
        "templates": [],
        "hooks": {
            "pre_sync": [],
            "post_sync": []
        },
        "variables": {
            "os_name": platform.system(),
            "home_dir": str(Path.home()),
            "user_name": os.getenv("USER", os.getenv("USERNAME", "unknown"))
        }
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._find_config_file()
        self.config = {}
        self.encryption = None
        self._load_config()
    
    def _find_config_file(self) -> Path:
        """Find configuration file in standard locations"""
        search_paths = [
            Path.cwd() / ".envsync.json",
            Path.cwd() / "envsync.json",
            Path.home() / ".config" / "envsync" / "config.json",
            Path.home() / ".envsync.json",
        ]
        for path in search_paths:
            if path.exists():
                return path
        return Path.cwd() / ".envsync.json"
    
    def _load_config(self):
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except json.JSONDecodeError as e:
                raise ConfigError(f"Invalid JSON in config file: {e}")
        else:
            import copy
            self.config = copy.deepcopy(self.DEFAULT_CONFIG)
            self.config["created_at"] = datetime.now().isoformat()
    
    def save(self):
        """Save configuration to file"""
        self.config["updated_at"] = datetime.now().isoformat()
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def init_project(self, name: str, description: str = ""):
        """Initialize a new EnvSync project"""
        import copy
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        self.config["name"] = name
        self.config["description"] = description or f"Environment config for {name}"
        self.config["created_at"] = datetime.now().isoformat()
        self.save()
    
    def add_file(self, source: str, target: str, encrypt: bool = False, 
                 template: bool = False, description: str = ""):
        """Add a file to sync list"""
        file_entry = {
            "source": source,
            "target": target,
            "encrypt": encrypt,
            "template": template,
            "description": description,
            "added_at": datetime.now().isoformat()
        }
        self.config["files"].append(file_entry)
        self.save()
    
    def remove_file(self, source: str):
        """Remove a file from sync list"""
        self.config["files"] = [f for f in self.config["files"] if f["source"] != source]
        self.save()
    
    def list_files(self) -> List[Dict]:
        """List all tracked files"""
        return self.config.get("files", [])
    
    def set_encryption(self, password: str):
        """Set encryption key"""
        self.encryption = SimpleEncryption(password)
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get template variable"""
        return self.config.get("variables", {}).get(name, default)
    
    def set_variable(self, name: str, value: Any):
        """Set template variable"""
        if "variables" not in self.config:
            self.config["variables"] = {}
        self.config["variables"][name] = value
        self.save()


class SyncEngine:
    """
    Synchronization engine.
    Handles backup, sync, restore, and diff operations.
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.tracker = FileTracker()
        self.results = {
            "synced": [],
            "skipped": [],
            "failed": [],
            "encrypted": [],
            "backed_up": []
        }
    
    def _should_exclude(self, filepath: Path) -> bool:
        """Check if file should be excluded"""
        patterns = self.config.config.get("sync", {}).get("exclude_patterns", [])
        name = filepath.name
        for pattern in patterns:
            if pattern.endswith('/'):
                # Directory pattern
                if filepath.is_dir() and name == pattern.rstrip('/'):
                    return True
            elif '*' in pattern:
                import fnmatch
                if fnmatch.fnmatch(name, pattern):
                    return True
            elif name == pattern:
                return True
        return False
    
    def _backup_file(self, filepath: Path) -> Optional[Path]:
        """Create backup of file before modification"""
        if not filepath.exists():
            return None
        
        backup_dir = filepath.parent / ".envsync-backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{filepath.name}.{timestamp}.backup"
        backup_path = backup_dir / backup_name
        
        shutil.copy2(filepath, backup_path)
        self.results["backed_up"].append(str(backup_path))
        return backup_path
    
    def _apply_template(self, content: str, file_entry: Dict) -> str:
        """Apply template rendering if enabled"""
        if file_entry.get("template", False):
            variables = self.config.config.get("variables", {})
            template = ConfigTemplate(content, variables)
            return template.render()
        return content
    
    def sync_out(self, dry_run: bool = False) -> Dict:
        """
        Sync files from system to envsync storage.
        'out' means from system -> envsync storage.
        """
        self.results = {
            "synced": [],
            "skipped": [],
            "failed": [],
            "encrypted": [],
            "backed_up": []
        }
        
        storage_dir = self.config.config_path.parent / ".envsync-storage"
        storage_dir.mkdir(exist_ok=True)
        
        for file_entry in self.config.config.get("files", []):
            source = Path(file_entry["source"]).expanduser()
            target = storage_dir / Path(file_entry["target"]).name
            
            if not source.exists():
                self.results["skipped"].append({
                    "source": str(source),
                    "reason": "Source file not found"
                })
                continue
            
            if self._should_exclude(source):
                self.results["skipped"].append({
                    "source": str(source),
                    "reason": "Excluded by pattern"
                })
                continue
            
            try:
                if not dry_run:
                    # Read and optionally process content
                    with open(source, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Apply template rendering
                    content = self._apply_template(content, file_entry)
                    
                    # Encrypt if needed
                    if file_entry.get("encrypt", False) and self.config.encryption:
                        content = self.config.encryption.encrypt(content)
                        self.results["encrypted"].append(str(target))
                    
                    # Write to storage
                    with open(target, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                self.results["synced"].append({
                    "source": str(source),
                    "target": str(target),
                    "size": source.stat().st_size
                })
            except Exception as e:
                self.results["failed"].append({
                    "source": str(source),
                    "error": str(e)
                })
        
        return self.results
    
    def sync_in(self, dry_run: bool = False) -> Dict:
        """
        Sync files from envsync storage to system.
        'in' means from envsync storage -> system.
        """
        self.results = {
            "synced": [],
            "skipped": [],
            "failed": [],
            "decrypted": [],
            "backed_up": []
        }
        
        storage_dir = self.config.config_path.parent / ".envsync-storage"
        
        for file_entry in self.config.config.get("files", []):
            source = storage_dir / Path(file_entry["target"]).name
            target = Path(file_entry["source"]).expanduser()
            
            if not source.exists():
                self.results["skipped"].append({
                    "target": str(target),
                    "reason": "Storage file not found"
                })
                continue
            
            try:
                if not dry_run:
                    # Backup existing file
                    if self.config.config.get("sync", {}).get("backup_before_sync", True):
                        self._backup_file(target)
                    
                    # Ensure target directory exists
                    target.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Read from storage
                    with open(source, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Decrypt if needed
                    if file_entry.get("encrypt", False) and self.config.encryption:
                        content = self.config.encryption.decrypt(content)
                        self.results["decrypted"].append(str(target))
                    
                    # Write to system
                    with open(target, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                self.results["synced"].append({
                    "source": str(source),
                    "target": str(target)
                })
            except Exception as e:
                self.results["failed"].append({
                    "target": str(target),
                    "error": str(e)
                })
        
        return self.results
    
    def diff(self) -> List[Dict]:
        """Compare system files with stored versions"""
        differences = []
        storage_dir = self.config.config_path.parent / ".envsync-storage"
        
        for file_entry in self.config.config.get("files", []):
            system_path = Path(file_entry["source"]).expanduser()
            storage_path = storage_dir / Path(file_entry["target"]).name
            
            if not system_path.exists() and not storage_path.exists():
                continue
            
            diff_entry = {
                "source": str(system_path),
                "storage": str(storage_path),
                "status": "unknown"
            }
            
            if not system_path.exists():
                diff_entry["status"] = "missing_system"
            elif not storage_path.exists():
                diff_entry["status"] = "missing_storage"
            else:
                system_hash = self.tracker.compute_hash(system_path)
                storage_hash = self.tracker.compute_hash(storage_path)
                if system_hash == storage_hash:
                    diff_entry["status"] = "identical"
                else:
                    diff_entry["status"] = "different"
            
            differences.append(diff_entry)
        
        return differences
    
    def status(self) -> Dict:
        """Get overall sync status"""
        diffs = self.diff()
        return {
            "total_files": len(diffs),
            "identical": len([d for d in diffs if d["status"] == "identical"]),
            "different": len([d for d in diffs if d["status"] == "different"]),
            "missing_system": len([d for d in diffs if d["status"] == "missing_system"]),
            "missing_storage": len([d for d in diffs if d["status"] == "missing_storage"]),
            "details": diffs
        }


class EnvSync:
    """
    Main EnvSync facade class.
    Provides high-level API for all EnvSync operations.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        path = Path(config_path) if config_path else None
        self.config = ConfigManager(path)
        self.sync = SyncEngine(self.config)
    
    def init(self, name: str, description: str = ""):
        """Initialize new project"""
        self.config.init_project(name, description)
        return f"Initialized EnvSync project: {name}"
    
    def add(self, source: str, target: str = "", encrypt: bool = False,
            template: bool = False, description: str = ""):
        """Add file to sync list"""
        target = target or Path(source).name
        self.config.add_file(source, target, encrypt, template, description)
        return f"Added: {source} -> {target}"
    
    def remove(self, source: str):
        """Remove file from sync list"""
        self.config.remove_file(source)
        return f"Removed: {source}"
    
    def list(self) -> List[Dict]:
        """List tracked files"""
        return self.config.list_files()
    
    def sync_out(self, dry_run: bool = False) -> Dict:
        """Sync system -> storage"""
        return self.sync.sync_out(dry_run)
    
    def sync_in(self, dry_run: bool = False) -> Dict:
        """Sync storage -> system"""
        return self.sync.sync_in(dry_run)
    
    def diff(self) -> List[Dict]:
        """Show differences"""
        return self.sync.diff()
    
    def status(self) -> Dict:
        """Show sync status"""
        return self.sync.status()
    
    def set_password(self, password: str):
        """Set encryption password"""
        self.config.set_encryption(password)
        return "Encryption password set"
    
    def set_var(self, name: str, value: str):
        """Set template variable"""
        self.config.set_variable(name, value)
        return f"Variable set: {name} = {value}"
