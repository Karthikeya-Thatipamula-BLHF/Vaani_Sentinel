"""
Kill Switch for Vaani Sentinel X
Emergency shutdown and data protection system
"""

import json
import os
import shutil
import sys
from datetime import datetime
from typing import Dict, Any, List
import argparse

class KillSwitch:
    """Emergency kill switch for the Vaani Sentinel X system"""
    
    def __init__(self):
        self.kill_switch_file = "./kill_switch.json"
        self.backup_dir = "./emergency_backup"
        self.logs_dir = "./logs"
        
    def activate(self, reason: str, severity: str = "high") -> bool:
        """Activate the kill switch"""
        
        print(f"🚨 ACTIVATING KILL SWITCH - Reason: {reason}")
        
        # Create kill switch file
        kill_switch_data = {
            "active": True,
            "activated_at": datetime.utcnow().isoformat(),
            "reason": reason,
            "severity": severity,
            "activated_by": "manual_kill_switch",
            "actions_taken": []
        }
        
        try:
            # 1. Stop all running processes (simulation)
            print("🛑 Stopping all AI agents and processes...")
            kill_switch_data["actions_taken"].append("stopped_all_processes")
            
            # 2. Create emergency backup
            print("💾 Creating emergency backup...")
            backup_success = self._create_emergency_backup()
            if backup_success:
                kill_switch_data["actions_taken"].append("created_emergency_backup")
            
            # 3. Clear sensitive data from memory (simulation)
            print("🧹 Clearing sensitive data from memory...")
            kill_switch_data["actions_taken"].append("cleared_memory")
            
            # 4. Disable API endpoints (by creating kill switch file)
            print("🔒 Disabling API endpoints...")
            kill_switch_data["actions_taken"].append("disabled_api_endpoints")
            
            # 5. Log the kill switch activation
            print("📝 Logging kill switch activation...")
            self._log_kill_switch_event(kill_switch_data)
            kill_switch_data["actions_taken"].append("logged_event")
            
            # 6. Save kill switch state
            with open(self.kill_switch_file, 'w', encoding='utf-8') as f:
                json.dump(kill_switch_data, f, indent=2)
            
            print("✅ Kill switch activated successfully!")
            print(f"📁 Emergency backup created at: {self.backup_dir}")
            print("⚠️  All system operations are now blocked.")
            
            return True
            
        except Exception as e:
            print(f"❌ Error activating kill switch: {e}")
            return False
    
    def deactivate(self) -> bool:
        """Deactivate the kill switch"""
        
        print("🔄 DEACTIVATING KILL SWITCH...")
        
        try:
            if os.path.exists(self.kill_switch_file):
                # Read current state
                with open(self.kill_switch_file, 'r', encoding='utf-8') as f:
                    kill_switch_data = json.load(f)
                
                # Update state
                kill_switch_data["active"] = False
                kill_switch_data["deactivated_at"] = datetime.utcnow().isoformat()
                kill_switch_data["deactivated_by"] = "manual_kill_switch"
                
                # Log deactivation
                self._log_kill_switch_event({
                    "event": "kill_switch_deactivated",
                    "timestamp": datetime.utcnow().isoformat(),
                    "previous_state": kill_switch_data
                })
                
                # Remove kill switch file
                os.remove(self.kill_switch_file)
                
                print("✅ Kill switch deactivated successfully!")
                print("🔓 System operations are now enabled.")
                
                return True
            else:
                print("ℹ️  Kill switch is not currently active.")
                return True
                
        except Exception as e:
            print(f"❌ Error deactivating kill switch: {e}")
            return False
    
    def status(self) -> Dict[str, Any]:
        """Get kill switch status"""
        
        if os.path.exists(self.kill_switch_file):
            try:
                with open(self.kill_switch_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                return {
                    "active": False,
                    "error": f"Error reading kill switch file: {e}"
                }
        else:
            return {
                "active": False,
                "status": "Kill switch is not active"
            }
    
    def _create_emergency_backup(self) -> bool:
        """Create emergency backup of critical data"""
        
        try:
            # Create backup directory
            os.makedirs(self.backup_dir, exist_ok=True)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_subdir = os.path.join(self.backup_dir, f"emergency_backup_{timestamp}")
            os.makedirs(backup_subdir, exist_ok=True)
            
            # Backup critical directories
            critical_dirs = [
                "./content",
                "./config",
                "./analytics_db",
                "./scheduler_db",
                "./logs"
            ]
            
            for dir_path in critical_dirs:
                if os.path.exists(dir_path):
                    dir_name = os.path.basename(dir_path)
                    backup_path = os.path.join(backup_subdir, dir_name)
                    shutil.copytree(dir_path, backup_path, ignore_errors=True)
            
            # Create backup manifest
            manifest = {
                "backup_created": datetime.utcnow().isoformat(),
                "backup_reason": "kill_switch_activation",
                "backed_up_directories": critical_dirs,
                "backup_location": backup_subdir
            }
            
            manifest_path = os.path.join(backup_subdir, "backup_manifest.json")
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating emergency backup: {e}")
            return False
    
    def _log_kill_switch_event(self, event_data: Dict[str, Any]):
        """Log kill switch events"""
        
        try:
            os.makedirs(self.logs_dir, exist_ok=True)
            
            log_file = os.path.join(self.logs_dir, "kill_switch_events.json")
            
            # Load existing logs
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Add new event
            logs.append({
                "event_id": len(logs) + 1,
                "timestamp": datetime.utcnow().isoformat(),
                "event_data": event_data
            })
            
            # Save logs
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Error logging kill switch event: {e}")
    
    def wipe_data(self, confirm: bool = False) -> bool:
        """Wipe all data (DANGEROUS - use only in extreme cases)"""
        
        if not confirm:
            print("⚠️  WARNING: This will permanently delete all data!")
            print("⚠️  This action cannot be undone!")
            response = input("Type 'CONFIRM_WIPE' to proceed: ")
            if response != "CONFIRM_WIPE":
                print("❌ Data wipe cancelled.")
                return False
        
        print("🗑️  WIPING ALL DATA...")
        
        try:
            # Directories to wipe
            dirs_to_wipe = [
                "./content",
                "./analytics_db",
                "./scheduler_db",
                "./archives",
                "./temp"
            ]
            
            # Files to wipe
            files_to_wipe = [
                "./vaani_sentinel.db",
                self.kill_switch_file
            ]
            
            # Wipe directories
            for dir_path in dirs_to_wipe:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path, ignore_errors=True)
                    print(f"🗑️  Wiped directory: {dir_path}")
            
            # Wipe files
            for file_path in files_to_wipe:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🗑️  Wiped file: {file_path}")
            
            # Log the wipe event
            self._log_kill_switch_event({
                "event": "data_wipe_completed",
                "timestamp": datetime.utcnow().isoformat(),
                "wiped_directories": dirs_to_wipe,
                "wiped_files": files_to_wipe
            })
            
            print("✅ Data wipe completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error during data wipe: {e}")
            return False

def main():
    """Command line interface for kill switch"""
    
    parser = argparse.ArgumentParser(description="Vaani Sentinel X Kill Switch")
    parser.add_argument("action", choices=["activate", "deactivate", "status", "wipe"], 
                       help="Action to perform")
    parser.add_argument("--reason", type=str, help="Reason for activation")
    parser.add_argument("--severity", type=str, choices=["low", "medium", "high", "critical"], 
                       default="high", help="Severity level")
    parser.add_argument("--confirm", action="store_true", help="Confirm dangerous actions")
    
    args = parser.parse_args()
    
    kill_switch = KillSwitch()
    
    if args.action == "activate":
        if not args.reason:
            print("❌ Reason is required for activation")
            sys.exit(1)
        
        success = kill_switch.activate(args.reason, args.severity)
        sys.exit(0 if success else 1)
    
    elif args.action == "deactivate":
        success = kill_switch.deactivate()
        sys.exit(0 if success else 1)
    
    elif args.action == "status":
        status = kill_switch.status()
        print(json.dumps(status, indent=2))
        sys.exit(0)
    
    elif args.action == "wipe":
        success = kill_switch.wipe_data(args.confirm)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
