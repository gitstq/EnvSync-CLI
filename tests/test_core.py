#!/usr/bin/env python3
"""
EnvSync Core Unit Tests
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from envsync.core import (
    EnvSync, ConfigManager, SyncEngine,
    SimpleEncryption, ConfigTemplate,
    EnvSyncError, ConfigError
)


class TestSimpleEncryption:
    """Test encryption functionality"""
    
    def test_encrypt_decrypt(self):
        """Test basic encryption and decryption"""
        enc = SimpleEncryption("test_password_123")
        original = "Hello, World! This is sensitive data."
        encrypted = enc.encrypt(original)
        decrypted = enc.decrypt(encrypted)
        
        assert encrypted != original
        assert decrypted == original
    
    def test_encrypt_empty_string(self):
        """Test encryption of empty string"""
        enc = SimpleEncryption("key")
        encrypted = enc.encrypt("")
        decrypted = enc.decrypt(encrypted)
        assert decrypted == ""
    
    def test_different_keys(self):
        """Test that different keys produce different results"""
        enc1 = SimpleEncryption("key1")
        enc2 = SimpleEncryption("key2")
        text = "test data"
        
        assert enc1.encrypt(text) != enc2.encrypt(text)


class TestConfigTemplate:
    """Test template engine"""
    
    def test_basic_substitution(self):
        """Test variable substitution"""
        template = ConfigTemplate(
            "Hello {{ name }}, your home is {{ home }}",
            {"name": "Alice", "home": "/home/alice"}
        )
        result = template.render()
        assert result == "Hello Alice, your home is /home/alice"
    
    def test_conditional_block(self):
        """Test conditional rendering"""
        template = ConfigTemplate(
            "{{#if os_name == \"Linux\"}}Linux config{{/if}}{{#if os_name == \"Windows\"}}Windows config{{/if}}",
            {"os_name": "Linux"}
        )
        result = template.render()
        assert "Linux config" in result
        assert "Windows config" not in result


class TestConfigManager:
    """Test configuration manager"""
    
    def setup_method(self):
        """Setup temporary directory for tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / ".envsync.json"
    
    def teardown_method(self):
        """Cleanup temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_project(self):
        """Test project initialization"""
        cm = ConfigManager(self.config_path)
        cm.init_project("test-project", "Test description")
        
        assert cm.config["name"] == "test-project"
        assert cm.config["description"] == "Test description"
        assert self.config_path.exists()
    
    def test_add_file(self):
        """Test adding file to sync list"""
        cm = ConfigManager(self.config_path)
        cm.init_project("test")
        cm.add_file("~/.bashrc", ".bashrc", encrypt=True)
        
        files = cm.list_files()
        assert len(files) == 1
        assert files[0]["source"] == "~/.bashrc"
        assert files[0]["encrypt"] == True
    
    def test_remove_file(self):
        """Test removing file from sync list"""
        cm = ConfigManager(self.config_path)
        cm.init_project("test")
        cm.add_file("~/.bashrc", ".bashrc")
        cm.remove_file("~/.bashrc")
        
        assert len(cm.list_files()) == 0
    
    def test_set_variable(self):
        """Test setting template variable"""
        cm = ConfigManager(self.config_path)
        cm.init_project("test")
        cm.set_variable("custom_var", "custom_value")
        
        assert cm.get_variable("custom_var") == "custom_value"


class TestSyncEngine:
    """Test sync engine"""
    
    def setup_method(self):
        """Setup temporary directories"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / ".envsync.json"
        self.system_dir = Path(self.temp_dir) / "system"
        self.system_dir.mkdir()
        
        # Create test file
        self.test_file = self.system_dir / "test.txt"
        self.test_file.write_text("Hello, World!")
    
    def teardown_method(self):
        """Cleanup"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_sync_out(self):
        """Test syncing system to storage"""
        cm = ConfigManager(self.config_path)
        cm.init_project("test")
        cm.add_file(str(self.test_file), "test.txt")
        
        engine = SyncEngine(cm)
        results = engine.sync_out()
        
        assert len(results["synced"]) == 1
        
        storage_dir = self.config_path.parent / ".envsync-storage"
        assert (storage_dir / "test.txt").exists()
    
    def test_sync_in(self):
        """Test syncing storage to system"""
        cm = ConfigManager(self.config_path)
        cm.init_project("test")
        cm.add_file(str(self.test_file), "test.txt")
        
        engine = SyncEngine(cm)
        engine.sync_out()
        
        # Modify system file
        self.test_file.write_text("Modified content")
        
        # Sync back
        results = engine.sync_in()
        
        assert len(results["synced"]) == 1
        assert self.test_file.read_text() != "Modified content"
    
    def test_diff(self):
        """Test diff functionality"""
        cm = ConfigManager(self.config_path)
        cm.init_project("test")
        cm.add_file(str(self.test_file), "test.txt")
        
        engine = SyncEngine(cm)
        engine.sync_out()
        
        diffs = engine.diff()
        assert len(diffs) == 1
        assert diffs[0]["status"] == "identical"
    
    def test_status(self):
        """Test status functionality"""
        cm = ConfigManager(self.config_path)
        cm.init_project("test")
        cm.add_file(str(self.test_file), "test.txt")
        
        engine = SyncEngine(cm)
        status = engine.status()
        
        assert status["total_files"] == 1


class TestEnvSync:
    """Test main EnvSync facade"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / ".envsync.json"
        self.test_file = Path(self.temp_dir) / "test.txt"
        self.test_file.write_text("test content")
    
    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_workflow(self):
        """Test complete workflow"""
        es = EnvSync(str(self.config_path))
        
        # Init
        result = es.init("my-project", "My project")
        assert "Initialized" in result
        
        # Add file
        result = es.add(str(self.test_file), "test.txt")
        assert "Added" in result
        
        # Sync out
        results = es.sync_out()
        assert len(results["synced"]) == 1
        
        # Status
        status = es.status()
        assert status["total_files"] == 1


def run_tests():
    """Run all tests"""
    import traceback
    
    test_classes = [
        TestSimpleEncryption,
        TestConfigTemplate,
        TestConfigManager,
        TestSyncEngine,
        TestEnvSync,
    ]
    
    total = 0
    passed = 0
    failed = 0
    
    print("=" * 60)
    print("EnvSync-CLI Unit Tests")
    print("=" * 60)
    
    for cls in test_classes:
        print(f"\n📦 {cls.__name__}")
        instance = cls()
        
        for method_name in dir(cls):
            if method_name.startswith("test_"):
                total += 1
                try:
                    if hasattr(instance, 'setup_method'):
                        instance.setup_method()
                    
                    getattr(instance, method_name)()
                    
                    if hasattr(instance, 'teardown_method'):
                        instance.teardown_method()
                    
                    print(f"  ✓ {method_name}")
                    passed += 1
                except Exception as e:
                    import traceback
                    print(f"  ✗ {method_name}: {e}")
                    traceback.print_exc()
                    failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} passed, {failed}/{total} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
