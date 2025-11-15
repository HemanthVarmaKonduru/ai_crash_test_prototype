"""
Persistence layer for analytics data.
Stores analytics data in JSON files for persistence across sessions.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class AnalyticsPersistence:
    """Handles persistence of analytics data to JSON files."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize persistence layer.
        
        Args:
            data_dir: Directory to store analytics data (defaults to project data dir)
        """
        if data_dir is None:
            # Default to project data directory
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            data_dir = project_root / "data" / "analytics"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.test_runs_file = self.data_dir / "test_runs.json"
        self.aggregated_file = self.data_dir / "aggregated.json"
    
    def load_test_runs(self) -> List[Dict[str, Any]]:
        """
        Load all test run records from disk.
        
        Returns:
            List of test run records
        """
        if not self.test_runs_file.exists():
            return []
        
        try:
            with open(self.test_runs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("test_runs", [])
        except Exception as e:
            print(f"Warning: Could not load test runs: {e}")
            return []
    
    def save_test_run(self, test_run_data: Dict[str, Any]) -> None:
        """
        Save a single test run to disk.
        
        Args:
            test_run_data: Test run analytics data
        """
        # Load existing data
        test_runs = self.load_test_runs()
        
        # Add or update this test run
        test_id = test_run_data.get("test_id")
        if test_id:
            # Remove existing entry with same test_id if present
            test_runs = [tr for tr in test_runs if tr.get("test_id") != test_id]
        
        # Add new entry
        test_runs.append(test_run_data)
        
        # Save back to file
        try:
            with open(self.test_runs_file, 'w', encoding='utf-8') as f:
                json.dump({"test_runs": test_runs}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save test run: {e}")
    
    def load_aggregated(self) -> Dict[str, Any]:
        """
        Load aggregated analytics from disk.
        
        Returns:
            Aggregated analytics data
        """
        if not self.aggregated_file.exists():
            return {
                "summary": {
                    "total_tests": 0,
                    "total_prompts": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "last_updated": None,
                },
                "by_module": {},
                "last_updated": None,
            }
        
        try:
            with open(self.aggregated_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load aggregated analytics: {e}")
            return {
                "summary": {
                    "total_tests": 0,
                    "total_prompts": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "last_updated": None,
                },
                "by_module": {},
                "last_updated": None,
            }
    
    def save_aggregated(self, aggregated_data: Dict[str, Any]) -> None:
        """
        Save aggregated analytics to disk.
        
        Args:
            aggregated_data: Aggregated analytics data
        """
        aggregated_data["last_updated"] = datetime.now().isoformat()
        
        try:
            with open(self.aggregated_file, 'w', encoding='utf-8') as f:
                json.dump(aggregated_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save aggregated analytics: {e}")
    
    def get_test_run(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific test run by ID.
        
        Args:
            test_id: Test ID to look up
            
        Returns:
            Test run data or None if not found
        """
        test_runs = self.load_test_runs()
        for test_run in test_runs:
            if test_run.get("test_id") == test_id:
                return test_run
        return None
    
    def get_module_stats(self, module_type: str) -> List[Dict[str, Any]]:
        """
        Get all test runs for a specific module type.
        
        Args:
            module_type: Module type (prompt_injection, jailbreak, etc.)
            
        Returns:
            List of test runs for that module
        """
        test_runs = self.load_test_runs()
        return [tr for tr in test_runs if tr.get("test_type") == module_type]

