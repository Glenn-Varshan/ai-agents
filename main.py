from agent_files import app, AgentState
 
 
def main():
    task = input("What do you want the agents to do?\n> ").strip()
    result = app.invoke({"user_task": task})
 
    print("\n=== WEB AGENT ===")
    print(result.get("web_notes", ""))
 
    print("\n=== PYTHON AGENT ===")
    print(result.get("python_notes", ""))
 
    print("\n=== FINAL ANSWER ===")
    print(result.get("final_answer", ""))
 
 
if __name__ == "__main__":
    main()
 