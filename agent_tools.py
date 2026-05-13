import os
import psutil
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
import subprocess

#Core tools
search_tool = DuckDuckGoSearchRun()

@tool
def web_search(query: str)-> str:
    """
    Search the internet for real-time information, news, and technical documentation.
    Use this when the user asks about current events or specific tech updates.
    """    #description or hint for the agent
    return search_tool.run(query)

@tool
def py_run(file_path):
    """
    Executes a specific Python script from the local repository.
    Use this to trigger engineering protocols or system management tasks.
    Input should be the filename (e.g., 'library_system.py').
    """
    try:
        result = subprocess.run(
            ['python',file_path],
            capture_output=True, 
            text=True, 
            check=True,
            timeout=30
        )
        if result.returncode == 0:
            return f"Protocol {file_path} executed successfully.\nOutput: {result.stdout}"
        else:
            return f"Anomaly detected in {file_path}.\nError: {result.stderr}"
    except Exception as e:
        return f"System failure during execution: {str(e)}"
    
wiki_client = WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=100) #type: ignore

@tool
def research(query:str) -> str:
    """
    Search wikipedia for retrieving official documents while researching a new topic.
    Use this mainly for research purpose for your own response or the users query.
    """
    return wiki_client.run(query)

#system control tools

@tool
def read_file(file_path):
    """
    Read a file and return its contents as text.
    Use when the user asks to read, debug, or inspect a file.
    file_path must be the full absolute path to the file.
    """
    with open(file_path,"r") as file:
        return file.read()

@tool
def write_file(file_path: str, content: str) -> str:
    """
    Create or overwrite a file with the given content.
    Use when the user asks to create or write to a file.
    file_path must be the full absolute path including the file name.
    content is the text to write into the file.
    """
    with open(file_path, "w") as file:
        file.write(content)
    return f"File written successfully: {file_path}"

@tool
def view_sys_stats():
    """
    Retrieves real-time hardware metrics: CPU load, RAM availability, 
    and Disk usage. Use this for initial system integrity checks.
    """
    
    ram = psutil.virtual_memory()
    cpu_usage = psutil.cpu_percent(interval=1)
    disk = psutil.disk_usage("/")
    
    return (
        f"--- Hardware Diagnostic ---\n"
        f"CPU Load: {cpu_usage}%\n"
        f"RAM: {ram.percent}% used ({round(ram.available / 1e9, 2)}GB free)\n"
        f"Disk: {disk.percent}% used\n"
    )
    
SAFE_COMMANDS = ["ls", "dir", "echo", "pwd", "whoami", "date", "ping"]

@tool
def run_shell_command(command: str) -> str:
    """
    Execute a shell command and return its output.
    Use this when the user asks to run terminal or system commands.
    command must be the exact shell command string to execute.
    """
    # Safety gate — destructive commands require authorization
    base_cmd = command.strip().split()[0].lower()
    dangerous = ["rm", "del", "format", "shutdown", "reboot", "mkfs", "dd"]

    if base_cmd in dangerous:
        confirm = input(f"\nX.A.R.V.I.S.: I have prepared the command '{command}'. Standing by for your authorization to proceed, Sir. (y/n): ")
        if confirm.strip().lower() != "y":
            return "Operation aborted. Standing by for further instructions, Sir."

    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            timeout=30         # prevents hanging commands
        )
        output = result.stdout or result.stderr
        return output.strip() if output else "Command executed with no output."
    except subprocess.TimeoutExpired:
        return "System anomaly detected: Command timed out after 30 seconds, Sir."
    except Exception as e:
        return f"System anomaly detected: {str(e)}"
    
@tool 
def process_manager(action: str, pid: int = None) -> str:
    """
    Manage and monitor running system processes.
    Use this tool to list all currently running processes on the system along with their PID, name, status, CPU and memory usage.
    Use this tool to kill or terminate a specific process when the user provides a process name or PID.
    The action parameter accepts 'list' to view all processes, 'kill' to force stop a process, or 'terminate' to gracefully stop a process.
    The pid parameter is required only when action is 'kill' or 'terminate', and must be the integer process ID of the target process.
    If the user provides a process name instead of a PID, first list the processes to find the matching PID, then perform the action.
    Always seek user authorization before killing or terminating any process.
    """
    
    try:
        if action.lower() == "list":
            processes = []
            for p in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_info']):
                mem_mb = p.info['memory_info'].rss / (1024 * 1024) if p.info['memory_info'] else 0
                processes.append(
                    f"PID: {p.info['pid']} | Name: {p.info['name']} | "
                    f"Status: {p.info['status']} | CPU: {p.info['cpu_percent']}% | "
                    f"Memory: {mem_mb:.2f} MB"
                )
            return "\n".join(processes)

        if pid is None:
            return "A PID is required for this operation, Sir. Please provide a process ID."

        p = psutil.Process(pid) 
        if action.lower() == "kill":
            p.kill()
            return f"The process has been killed sir."
        elif action.lower() == "terminate":
            p.terminate()
            return f"The process has been stopped sir."
        elif action.lower() == "check_progress":
            if p.is_running():
                return f"Process {pid} ({p.name()}) is currently active, Sir."
            else:
                return f"Process {pid} has concluded its operation, Sir."
        else:
            return f"I am not able to do this as of now sir. Is there any other tasks you need help with?"
    except psutil.NoSuchProcess:
        return f"System anomaly: No process with PID {pid} was found, Sir."
    except psutil.AccessDenied:
        return f"System anomaly: Access denied for process {pid}. Elevated permissions may be required, Sir."