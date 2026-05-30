import json

log_file = "/home/mvt/.gemini/antigravity/brain/1df958c0-c4d3-4d4e-84e2-cc2338aaa63a/.system_generated/logs/overview.txt"
target_file = "/home/mvt/mAIvt/Go/Fundamental/gin-guide.html"

def recover():
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get("step_index") == 95 and data.get("source") == "MODEL":
                    tool_calls = data.get("tool_calls", [])
                    if tool_calls and tool_calls[0]["name"] == "write_to_file":
                        code_content = tool_calls[0]["args"]["CodeContent"]
                        
                        # Sometimes it is nested double json strings
                        if code_content.startswith('"') and code_content.endswith('"'):
                            try:
                                code_content = json.loads(code_content)
                            except:
                                pass
                                
                        with open(target_file, "w", encoding="utf-8") as out:
                            out.write(code_content)
                        print("Successfully recovered pristine gin-guide.html!")
                        return True
            except Exception as e:
                pass
    print("Failed to find step_index 95 in overview logs.")
    return False

if __name__ == "__main__":
    recover()
