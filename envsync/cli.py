#!/usr/bin/env python3
"""
EnvSync CLI - 命令行接口模块
Provides interactive terminal UI and command-line interface.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional

from .core import EnvSync, EnvSyncError


class Colors:
    """Terminal color codes"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    
    @classmethod
    def disable(cls):
        """Disable colors"""
        for attr in dir(cls):
            if not attr.startswith('_') and attr != 'disable':
                setattr(cls, attr, '')


def print_banner():
    """Print application banner"""
    banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   {Colors.BOLD}🔄 EnvSync-CLI{Colors.RESET}{Colors.CYAN}  v1.0.0                                    ║
║   {Colors.DIM}Lightweight Environment Config Sync Manager{Colors.RESET}{Colors.CYAN}              ║
║   {Colors.DIM}轻量级环境配置同步管理工具{Colors.RESET}{Colors.CYAN}                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)


def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")


def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")


def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")


def print_table(headers: list, rows: list, col_widths: Optional[list] = None):
    """Print formatted table"""
    if not rows:
        print_info("No data to display")
        return
    
    if col_widths is None:
        col_widths = []
        for i in range(len(headers)):
            max_len = max(len(str(h)) for h in [headers[i]] + [row[i] for row in rows])
            col_widths.append(min(max_len + 2, 40))
    
    # Print header
    header_line = "│".join(f" {str(h):<{w-1}}" for h, w in zip(headers, col_widths))
    print(f"{Colors.CYAN}┌{'┬'.join('─' * w for w in col_widths)}┐{Colors.RESET}")
    print(f"{Colors.CYAN}│{header_line}│{Colors.RESET}")
    print(f"{Colors.CYAN}├{'┼'.join('─' * w for w in col_widths)}┤{Colors.RESET}")
    
    # Print rows
    for row in rows:
        row_line = "│".join(f" {str(c):<{w-1}}" for c, w in zip(row, col_widths))
        print(f"{Colors.CYAN}│{Colors.RESET}{row_line}{Colors.CYAN}│{Colors.RESET}")
    
    print(f"{Colors.CYAN}└{'┴'.join('─' * w for w in col_widths)}┘{Colors.RESET}")


def format_size(size_bytes: int) -> str:
    """Format byte size to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


class EnvSyncCLI:
    """Main CLI handler"""
    
    def __init__(self):
        self.envsync: Optional[EnvSync] = None
        self.config_path: Optional[str] = None
    
    def _get_envsync(self) -> EnvSync:
        """Get or create EnvSync instance"""
        if self.envsync is None:
            self.envsync = EnvSync(self.config_path)
        return self.envsync
    
    def cmd_init(self, args):
        """Initialize a new EnvSync project"""
        es = self._get_envsync()
        result = es.init(args.name, args.description)
        print_success(result)
        print_info(f"Config file: {es.config.config_path}")
    
    def cmd_add(self, args):
        """Add a file to sync list"""
        es = self._get_envsync()
        source = os.path.expanduser(args.source)
        result = es.add(
            source=source,
            target=args.target or "",
            encrypt=args.encrypt,
            template=args.template,
            description=args.description or ""
        )
        print_success(result)
    
    def cmd_remove(self, args):
        """Remove a file from sync list"""
        es = self._get_envsync()
        result = es.remove(args.source)
        print_success(result)
    
    def cmd_list(self, args):
        """List all tracked files"""
        es = self._get_envsync()
        files = es.list()
        
        if not files:
            print_warning("No files tracked yet. Use 'envsync add <file>' to add files.")
            return
        
        print(f"\n{Colors.BOLD}📋 Tracked Files ({len(files)}):{Colors.RESET}\n")
        
        rows = []
        for f in files:
            encrypt_flag = "🔒" if f.get("encrypt") else ""
            template_flag = "📄" if f.get("template") else ""
            rows.append([
                f.get("source", ""),
                f.get("target", ""),
                f"{encrypt_flag} {template_flag}".strip() or "-",
                f.get("description", "")[:30]
            ])
        
        print_table(
            ["Source", "Target", "Flags", "Description"],
            rows,
            [30, 20, 10, 30]
        )
    
    def cmd_sync_out(self, args):
        """Sync files from system to storage"""
        es = self._get_envsync()
        
        if args.dry_run:
            print_info("🔍 Dry run mode - no changes will be made")
        
        print(f"\n{Colors.BOLD}📤 Syncing system -> storage...{Colors.RESET}\n")
        
        results = es.sync_out(dry_run=args.dry_run)
        
        if results["synced"]:
            print(f"{Colors.GREEN}✓ Synced {len(results['synced'])} files:{Colors.RESET}")
            for item in results["synced"]:
                print(f"  {Colors.GREEN}→{Colors.RESET} {item['source']}")
        
        if results["encrypted"]:
            print(f"\n{Colors.MAGENTA}🔒 Encrypted {len(results['encrypted'])} files{Colors.RESET}")
        
        if results["skipped"]:
            print(f"\n{Colors.YELLOW}⚠ Skipped {len(results['skipped'])} files:{Colors.RESET}")
            for item in results["skipped"]:
                print(f"  {Colors.YELLOW}→{Colors.RESET} {item['source']} ({item['reason']})")
        
        if results["failed"]:
            print(f"\n{Colors.RED}✗ Failed {len(results['failed'])} files:{Colors.RESET}")
            for item in results["failed"]:
                print(f"  {Colors.RED}→{Colors.RESET} {item['source']} - {item['error']}")
    
    def cmd_sync_in(self, args):
        """Sync files from storage to system"""
        es = self._get_envsync()
        
        if args.dry_run:
            print_info("🔍 Dry run mode - no changes will be made")
        
        print(f"\n{Colors.BOLD}📥 Syncing storage -> system...{Colors.RESET}\n")
        
        results = es.sync_in(dry_run=args.dry_run)
        
        if results["synced"]:
            print(f"{Colors.GREEN}✓ Restored {len(results['synced'])} files:{Colors.RESET}")
            for item in results["synced"]:
                print(f"  {Colors.GREEN}→{Colors.RESET} {item['target']}")
        
        if results["decrypted"]:
            print(f"\n{Colors.MAGENTA}🔓 Decrypted {len(results['decrypted'])} files{Colors.RESET}")
        
        if results["backed_up"]:
            print(f"\n{Colors.BLUE}💾 Backed up {len(results['backed_up'])} files{Colors.RESET}")
        
        if results["skipped"]:
            print(f"\n{Colors.YELLOW}⚠ Skipped {len(results['skipped'])} files{Colors.RESET}")
        
        if results["failed"]:
            print(f"\n{Colors.RED}✗ Failed {len(results['failed'])} files:{Colors.RESET}")
            for item in results["failed"]:
                print(f"  {Colors.RED}→{Colors.RESET} {item['target']} - {item['error']}")
    
    def cmd_status(self, args):
        """Show sync status"""
        es = self._get_envsync()
        status = es.status()
        
        print(f"\n{Colors.BOLD}📊 Sync Status:{Colors.RESET}\n")
        
        total = status["total_files"]
        identical = status["identical"]
        different = status["different"]
        missing_sys = status["missing_system"]
        missing_sto = status["missing_storage"]
        
        # Summary
        print(f"  {Colors.CYAN}Total files:{Colors.RESET}     {total}")
        print(f"  {Colors.GREEN}✓ Identical:{Colors.RESET}     {identical}")
        print(f"  {Colors.YELLOW}⟳ Different:{Colors.RESET}     {different}")
        print(f"  {Colors.RED}✗ Missing (system):{Colors.RESET}  {missing_sys}")
        print(f"  {Colors.BLUE}? Missing (storage):{Colors.RESET} {missing_sto}")
        
        # Progress bar
        if total > 0:
            sync_pct = (identical / total) * 100
            bar_width = 30
            filled = int(bar_width * sync_pct / 100)
            bar = "█" * filled + "░" * (bar_width - filled)
            print(f"\n  {Colors.BOLD}Sync Progress:{Colors.RESET}")
            print(f"  [{Colors.GREEN}{bar}{Colors.RESET}] {sync_pct:.1f}%")
        
        # Details
        if args.verbose and status["details"]:
            print(f"\n{Colors.BOLD}📋 Details:{Colors.RESET}")
            for detail in status["details"]:
                icon = {
                    "identical": f"{Colors.GREEN}✓{Colors.RESET}",
                    "different": f"{Colors.YELLOW}⟳{Colors.RESET}",
                    "missing_system": f"{Colors.RED}✗{Colors.RESET}",
                    "missing_storage": f"{Colors.BLUE}?{Colors.RESET}"
                }.get(detail["status"], "?")
                print(f"  {icon} {detail['source']} [{detail['status']}]")
    
    def cmd_diff(self, args):
        """Show differences between system and storage"""
        es = self._get_envsync()
        diffs = es.diff()
        
        if not diffs:
            print_info("No tracked files to compare")
            return
        
        print(f"\n{Colors.BOLD}📊 File Differences:{Colors.RESET}\n")
        
        for diff in diffs:
            status = diff["status"]
            icon = {
                "identical": f"{Colors.GREEN}✓{Colors.RESET}",
                "different": f"{Colors.YELLOW}⟳{Colors.RESET}",
                "missing_system": f"{Colors.RED}✗{Colors.RESET}",
                "missing_storage": f"{Colors.BLUE}?{Colors.RESET}"
            }.get(status, "?")
            
            print(f"  {icon} {diff['source']}")
            if status == "different":
                print(f"     {Colors.YELLOW}Files are out of sync{Colors.RESET}")
            elif status == "missing_system":
                print(f"     {Colors.RED}File exists in storage but not on system{Colors.RESET}")
            elif status == "missing_storage":
                print(f"     {Colors.BLUE}File exists on system but not in storage{Colors.RESET}")
    
    def cmd_set_password(self, args):
        """Set encryption password"""
        es = self._get_envsync()
        result = es.set_password(args.password)
        print_success(result)
    
    def cmd_set_var(self, args):
        """Set template variable"""
        es = self._get_envsync()
        result = es.set_var(args.name, args.value)
        print_success(result)
    
    def cmd_config(self, args):
        """Show current configuration"""
        es = self._get_envsync()
        config = es.config.config
        
        print(f"\n{Colors.BOLD}⚙️  Configuration:{Colors.RESET}\n")
        print(f"  {Colors.CYAN}Name:{Colors.RESET}        {config.get('name', 'N/A')}")
        print(f"  {Colors.CYAN}Description:{Colors.RESET} {config.get('description', 'N/A')}")
        print(f"  {Colors.CYAN}Version:{Colors.RESET}     {config.get('version', 'N/A')}")
        print(f"  {Colors.CYAN}Config file:{Colors.RESET} {es.config.config_path}")
        print(f"  {Colors.CYAN}Created:{Colors.RESET}     {config.get('created_at', 'N/A')}")
        print(f"  {Colors.CYAN}Updated:{Colors.RESET}     {config.get('updated_at', 'N/A')}")
        
        # Variables
        variables = config.get("variables", {})
        if variables:
            print(f"\n{Colors.BOLD}🔧 Template Variables:{Colors.RESET}")
            for name, value in variables.items():
                print(f"  {Colors.CYAN}{name}:{Colors.RESET} {value}")


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog="envsync",
        description="EnvSync-CLI - Lightweight Environment Config Sync Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  envsync init my-project                    Initialize a new project
  envsync add ~/.bashrc                      Add .bashrc to sync list
  envsync add ~/.ssh/config --encrypt        Add with encryption
  envsync sync-out                           Sync system -> storage
  envsync sync-in                            Sync storage -> system
  envsync status                             Show sync status
  envsync diff                               Show file differences
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        help="Path to configuration file",
        default=None
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="EnvSync-CLI v1.0.0"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # init
    init_parser = subparsers.add_parser("init", help="Initialize a new EnvSync project")
    init_parser.add_argument("name", help="Project name")
    init_parser.add_argument("--description", "-d", help="Project description", default="")
    
    # add
    add_parser = subparsers.add_parser("add", help="Add a file to sync list")
    add_parser.add_argument("source", help="Source file path")
    add_parser.add_argument("--target", "-t", help="Target name in storage", default="")
    add_parser.add_argument("--encrypt", "-e", action="store_true", help="Encrypt this file")
    add_parser.add_argument("--template", action="store_true", help="Enable template processing")
    add_parser.add_argument("--description", help="File description", default="")
    
    # remove
    remove_parser = subparsers.add_parser("remove", help="Remove a file from sync list")
    remove_parser.add_argument("source", help="Source file path to remove")
    
    # list
    subparsers.add_parser("list", help="List all tracked files")
    
    # sync-out
    sync_out_parser = subparsers.add_parser("sync-out", help="Sync files from system to storage")
    sync_out_parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would be synced")
    
    # sync-in
    sync_in_parser = subparsers.add_parser("sync-in", help="Sync files from storage to system")
    sync_in_parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would be synced")
    
    # status
    status_parser = subparsers.add_parser("status", help="Show sync status")
    status_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed status")
    
    # diff
    subparsers.add_parser("diff", help="Show differences between system and storage")
    
    # set-password
    pw_parser = subparsers.add_parser("set-password", help="Set encryption password")
    pw_parser.add_argument("password", help="Encryption password")
    
    # set-var
    var_parser = subparsers.add_parser("set-var", help="Set template variable")
    var_parser.add_argument("name", help="Variable name")
    var_parser.add_argument("value", help="Variable value")
    
    # config
    subparsers.add_parser("config", help="Show current configuration")
    
    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.no_color:
        Colors.disable()
    
    if not args.command:
        print_banner()
        parser.print_help()
        sys.exit(0)
    
    cli = EnvSyncCLI()
    cli.config_path = args.config
    
    try:
        command_map = {
            "init": cli.cmd_init,
            "add": cli.cmd_add,
            "remove": cli.cmd_remove,
            "list": cli.cmd_list,
            "sync-out": cli.cmd_sync_out,
            "sync-in": cli.cmd_sync_in,
            "status": cli.cmd_status,
            "diff": cli.cmd_diff,
            "set-password": cli.cmd_set_password,
            "set-var": cli.cmd_set_var,
            "config": cli.cmd_config,
        }
        
        handler = command_map.get(args.command)
        if handler:
            handler(args)
        else:
            print_error(f"Unknown command: {args.command}")
            sys.exit(1)
            
    except EnvSyncError as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n")
        print_warning("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
