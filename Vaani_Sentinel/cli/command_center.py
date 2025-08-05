"""
Command Center CLI for Vaani Sentinel X
Task 2 Requirement: Simple Command Center CLI

Capabilities:
- Run any agent manually
- See process logs
- Kill or restart a pipeline
- Monitor system status
"""

import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class CommandCenter:
    """
    Command Center CLI for Vaani Sentinel X
    Task 2 requirement for manual agent control and monitoring
    """
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.logs_dir = os.path.join(self.base_dir, "logs")
        self.agents_dir = os.path.join(self.base_dir, "agents")
        
        # Ensure directories exist
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Available agents
        self.available_agents = {
            "miner": "agents.miner_sanitizer",
            "writer": "agents.ai_writer_voicegen", 
            "scheduler": "agents.scheduler",
            "security": "agents.security_guard",
            "multilingual": "agents.multilingual_pipeline",
            "analytics": "agents.analytics_collector",
            "sentiment": "agents.sentiment_tuner",
            "targeter": "agents.adaptive_targeter",
            "publisher": "agents.publisher_sim",
            "translation": "agents.translation_agent",
            "personalization": "agents.personalization_agent",
            "tts": "agents.tts_simulator",
            "strategy": "agents.strategy_recommender"
        }
        
        # Running processes
        self.running_processes = {}
        
        # Log file
        self.log_file = os.path.join(self.logs_dir, f"command_center_{datetime.now().strftime('%Y%m%d')}.log")
    
    def log_message(self, message: str, level: str = "INFO"):
        """Log message to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"

        # Handle Unicode encoding for Windows console
        try:
            print(log_entry)
        except UnicodeEncodeError:
            # Fallback to ASCII-safe version
            safe_message = message.encode('ascii', 'replace').decode('ascii')
            safe_log_entry = f"[{timestamp}] [{level}] {safe_message}"
            print(safe_log_entry)

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Failed to write to log file: {e}")
    
    def show_status(self):
        """Show system status"""
        self.log_message("=== VAANI SENTINEL X COMMAND CENTER ===")
        self.log_message(f"Base Directory: {self.base_dir}")
        self.log_message(f"Logs Directory: {self.logs_dir}")
        self.log_message(f"Available Agents: {len(self.available_agents)}")
        self.log_message(f"Running Processes: {len(self.running_processes)}")
        
        # Show available agents
        self.log_message("\n📋 AVAILABLE AGENTS:")
        for agent_name, agent_module in self.available_agents.items():
            status = "🟢 AVAILABLE" if self._check_agent_availability(agent_module) else "🔴 UNAVAILABLE"
            self.log_message(f"   {agent_name}: {status}")
        
        # Show running processes
        if self.running_processes:
            self.log_message("\n🔄 RUNNING PROCESSES:")
            for process_id, process_info in self.running_processes.items():
                self.log_message(f"   {process_id}: {process_info['agent']} (PID: {process_info.get('pid', 'N/A')})")
        else:
            self.log_message("\n💤 No processes currently running")
    
    def _check_agent_availability(self, agent_module: str) -> bool:
        """Check if agent module is available"""
        try:
            module_path = agent_module.replace(".", "/") + ".py"
            full_path = os.path.join(self.base_dir, module_path)
            return os.path.exists(full_path)
        except Exception:
            return False
    
    def run_agent(self, agent_name: str, **kwargs):
        """Run an agent manually"""
        if agent_name not in self.available_agents:
            self.log_message(f"❌ Unknown agent: {agent_name}", "ERROR")
            self.log_message(f"Available agents: {list(self.available_agents.keys())}")
            return False
        
        agent_module = self.available_agents[agent_name]
        
        self.log_message(f"🚀 Starting agent: {agent_name}")
        self.log_message(f"   Module: {agent_module}")
        
        try:
            # Import and run agent
            if agent_name == "miner":
                self._run_miner_agent(**kwargs)
            elif agent_name == "writer":
                self._run_writer_agent(**kwargs)
            elif agent_name == "scheduler":
                self._run_scheduler_agent(**kwargs)
            elif agent_name == "security":
                self._run_security_agent(**kwargs)
            elif agent_name == "multilingual":
                self._run_multilingual_agent(**kwargs)
            elif agent_name == "analytics":
                self._run_analytics_agent(**kwargs)
            elif agent_name == "sentiment":
                self._run_sentiment_agent(**kwargs)
            elif agent_name == "targeter":
                self._run_targeter_agent(**kwargs)
            elif agent_name == "publisher":
                self._run_publisher_agent(**kwargs)
            elif agent_name == "translation":
                self._run_translation_agent(**kwargs)
            elif agent_name == "personalization":
                self._run_personalization_agent(**kwargs)
            elif agent_name == "tts":
                self._run_tts_agent(**kwargs)
            elif agent_name == "strategy":
                self._run_strategy_agent(**kwargs)
            else:
                self.log_message(f"❌ Agent runner not implemented: {agent_name}", "ERROR")
                return False
            
            self.log_message(f"✅ Agent {agent_name} completed successfully")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error running agent {agent_name}: {str(e)}", "ERROR")
            return False
    
    def _run_miner_agent(self, **kwargs):
        """Run Knowledge Miner & Sanitizer agent"""
        from agents.miner_sanitizer import get_miner_sanitizer
        
        miner = get_miner_sanitizer()
        
        # Example operation
        if 'file_path' in kwargs:
            result = miner.process_csv_file(kwargs['file_path'])
            self.log_message(f"Processed file: {result}")
        else:
            self.log_message("Miner agent ready - provide file_path parameter")
    
    def _run_writer_agent(self, **kwargs):
        """Run AI Writer & Voice Generator agent"""
        from agents.ai_writer_voicegen import get_ai_writer
        
        writer = get_ai_writer()
        
        if 'content_text' in kwargs:
            result = writer.generate_platform_content(
                content_text=kwargs['content_text'],
                platforms=kwargs.get('platforms', ['twitter']),
                tone=kwargs.get('tone', 'neutral')
            )
            self.log_message(f"Generated content: {len(result.get('platform_content', {}))} platforms")
        else:
            self.log_message("Writer agent ready - provide content_text parameter")
    
    def _run_scheduler_agent(self, **kwargs):
        """Run Scheduler & Publisher Simulator agent"""
        from agents.scheduler import get_scheduler
        
        scheduler = get_scheduler()
        
        if 'content_id' in kwargs:
            result = scheduler.schedule_content(
                content_id=kwargs['content_id'],
                platforms=kwargs.get('platforms', ['twitter']),
                schedule_time=kwargs.get('schedule_time')
            )
            self.log_message(f"Scheduled content: {result}")
        else:
            self.log_message("Scheduler agent ready - provide content_id parameter")
    
    def _run_security_agent(self, **kwargs):
        """Run Security & Ethics Guard agent"""
        from agents.security_guard import get_security_guard
        
        security = get_security_guard()
        
        if 'content_text' in kwargs:
            result = security.analyze_content_safety(kwargs['content_text'])
            self.log_message(f"Security analysis: {result['safety_score']}")
        else:
            self.log_message("Security agent ready - provide content_text parameter")
    
    def _run_multilingual_agent(self, **kwargs):
        """Run Multilingual Pipeline agent"""
        from agents.multilingual_pipeline import get_multilingual_pipeline
        
        pipeline = get_multilingual_pipeline()
        
        if 'content_text' in kwargs:
            result = pipeline.process_multilingual_content(
                content_text=kwargs['content_text'],
                target_languages=kwargs.get('languages', ['hi', 'sa'])
            )
            self.log_message(f"Multilingual processing: {len(result.get('translations', {}))} languages")
        else:
            self.log_message("Multilingual agent ready - provide content_text parameter")
    
    def _run_analytics_agent(self, **kwargs):
        """Run Analytics Collector agent"""
        from agents.analytics_collector import get_analytics_collector
        
        analytics = get_analytics_collector()
        
        if 'content_id' in kwargs:
            result = analytics.generate_task3_engagement_stats(
                content_id=kwargs['content_id'],
                platform=kwargs.get('platform', 'twitter'),
                content_text=kwargs.get('content_text', 'Sample content')
            )
            self.log_message(f"Analytics generated: {result['engagement_rate']}")
        else:
            self.log_message("Analytics agent ready - provide content_id parameter")
    
    def _run_sentiment_agent(self, **kwargs):
        """Run Sentiment Tuner agent"""
        from agents.sentiment_tuner import get_sentiment_tuner
        
        sentiment = get_sentiment_tuner()
        
        if 'content_text' in kwargs:
            result = sentiment.adjust_sentiment(
                content_text=kwargs['content_text'],
                target_sentiment=kwargs.get('sentiment', 'uplifting'),
                intensity=kwargs.get('intensity', 'moderate')
            )
            self.log_message(f"Sentiment adjusted: {result['target_sentiment']}")
        else:
            self.log_message("Sentiment agent ready - provide content_text parameter")
    
    def _run_targeter_agent(self, **kwargs):
        """Run Context-Aware Platform Targeter agent"""
        from agents.adaptive_targeter import get_platform_targeter
        
        targeter = get_platform_targeter()
        
        if 'content_text' in kwargs:
            result = targeter.target_platform_content(
                content_text=kwargs['content_text'],
                platform=kwargs.get('platform', 'instagram'),
                context=kwargs.get('context')
            )
            self.log_message(f"Platform targeting: {result['platform']} - {result['context']}")
        else:
            self.log_message("Targeter agent ready - provide content_text parameter")
    
    def _run_publisher_agent(self, **kwargs):
        """Run Platform Publisher agent"""
        from agents.publisher_sim import get_multilingual_publisher_sim
        
        publisher = get_multilingual_publisher_sim()
        
        if 'content_text' in kwargs:
            result = publisher.simulate_platform_publishing(
                content_id=kwargs.get('content_id', 'cli_test'),
                content_text=kwargs['content_text'],
                platforms=kwargs.get('platforms', ['twitter'])
            )
            self.log_message(f"Publishing simulation: {len(result['platform_posts'])} platforms")
        else:
            self.log_message("Publisher agent ready - provide content_text parameter")
    
    def _run_translation_agent(self, **kwargs):
        """Run Translation agent"""
        from agents.translation_agent import get_translation_agent
        
        translator = get_translation_agent()
        
        if 'content_text' in kwargs:
            result = translator.translate_content(
                content_text=kwargs['content_text'],
                target_languages=kwargs.get('languages', ['hi']),
                user_profile_id=kwargs.get('profile', 'general')
            )
            self.log_message(f"Translation: {len(result['translations'])} languages")
        else:
            self.log_message("Translation agent ready - provide content_text parameter")
    
    def _run_personalization_agent(self, **kwargs):
        """Run Personalization agent"""
        from agents.personalization_agent import get_personalization_agent
        
        personalizer = get_personalization_agent()
        
        if 'content_text' in kwargs:
            result = personalizer.personalize_content(
                content_text=kwargs['content_text'],
                user_profile_id=kwargs.get('profile', 'general'),
                target_tone=kwargs.get('tone', 'neutral')
            )
            self.log_message(f"Personalization: {result['target_tone']}")
        else:
            self.log_message("Personalization agent ready - provide content_text parameter")
    
    def _run_tts_agent(self, **kwargs):
        """Run TTS Simulator agent"""
        from agents.tts_simulator import get_tts_simulator
        
        tts = get_tts_simulator()
        
        if 'content_text' in kwargs:
            result = tts.simulate_tts_generation(
                content_text=kwargs['content_text'],
                language=kwargs.get('language', 'en'),
                voice_tag=kwargs.get('voice', 'neutral')
            )
            self.log_message(f"TTS simulation: {result['voice_tag']}")
        else:
            self.log_message("TTS agent ready - provide content_text parameter")
    
    def _run_strategy_agent(self, **kwargs):
        """Run Strategy Recommender agent"""
        from agents.strategy_recommender import get_strategy_recommender
        
        strategy = get_strategy_recommender()
        
        result = strategy.adjust_future_content_strategy(
            analysis_days=kwargs.get('days', 7)
        )
        self.log_message(f"Strategy analysis: {len(result['strategy_recommendations'])} recommendations")
    
    def show_logs(self, lines: int = 50):
        """Show recent log entries"""
        self.log_message(f"\n📋 RECENT LOGS (Last {lines} lines):")
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
                recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines
                
                for line in recent_lines:
                    print(line.strip())
        
        except FileNotFoundError:
            self.log_message("No log file found")
        except Exception as e:
            self.log_message(f"Error reading logs: {e}", "ERROR")
    
    def kill_process(self, process_id: str):
        """Kill a running process"""
        if process_id not in self.running_processes:
            self.log_message(f"❌ Process not found: {process_id}", "ERROR")
            return False
        
        try:
            process_info = self.running_processes[process_id]
            # In a real implementation, you would kill the actual process
            # For now, just remove from tracking
            del self.running_processes[process_id]
            self.log_message(f"🛑 Killed process: {process_id}")
            return True
        
        except Exception as e:
            self.log_message(f"❌ Error killing process {process_id}: {e}", "ERROR")
            return False
    
    def emergency_shutdown(self):
        """Emergency shutdown of all processes"""
        self.log_message("🚨 EMERGENCY SHUTDOWN INITIATED", "WARNING")
        
        # Kill all running processes
        for process_id in list(self.running_processes.keys()):
            self.kill_process(process_id)
        
        # Activate kill switch
        try:
            kill_switch_path = os.path.join(self.base_dir, "kill_switch.py")
            if os.path.exists(kill_switch_path):
                subprocess.run([sys.executable, kill_switch_path], check=True)
                self.log_message("✅ Kill switch activated")
            else:
                self.log_message("⚠️ Kill switch not found", "WARNING")
        
        except Exception as e:
            self.log_message(f"❌ Error activating kill switch: {e}", "ERROR")
        
        self.log_message("🛑 Emergency shutdown completed")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Vaani Sentinel X Command Center")
    parser.add_argument("command", choices=["status", "run", "logs", "kill", "emergency"], 
                       help="Command to execute")
    parser.add_argument("--agent", help="Agent name to run")
    parser.add_argument("--content", help="Content text for agent")
    parser.add_argument("--platform", help="Target platform")
    parser.add_argument("--language", help="Content language")
    parser.add_argument("--tone", help="Content tone")
    parser.add_argument("--lines", type=int, default=50, help="Number of log lines to show")
    parser.add_argument("--process", help="Process ID to kill")
    
    args = parser.parse_args()
    
    command_center = CommandCenter()
    
    if args.command == "status":
        command_center.show_status()
    
    elif args.command == "run":
        if not args.agent:
            print("❌ Agent name required for run command")
            return
        
        kwargs = {}
        if args.content:
            kwargs['content_text'] = args.content
        if args.platform:
            kwargs['platform'] = args.platform
        if args.language:
            kwargs['language'] = args.language
        if args.tone:
            kwargs['tone'] = args.tone
        
        command_center.run_agent(args.agent, **kwargs)
    
    elif args.command == "logs":
        command_center.show_logs(args.lines)
    
    elif args.command == "kill":
        if not args.process:
            print("❌ Process ID required for kill command")
            return
        command_center.kill_process(args.process)
    
    elif args.command == "emergency":
        command_center.emergency_shutdown()

if __name__ == "__main__":
    main()
