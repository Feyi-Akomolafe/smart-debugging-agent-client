import json
import os
import re
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class DebugAnalyzer:
    def __init__(self):
        self.history_path = Path("data/debug_history.json")
        self.history_path.parent.mkdir(exist_ok=True)

    def analyze(self, payload):
        error_message = payload.get("error_message", "")
        stack_trace = payload.get("stack_trace", "")
        code_snippet = payload.get("code_snippet", "")
        language = payload.get("language", "")

        rule_result = self._rule_based_analysis(error_message, stack_trace, code_snippet, language)
        ai_result = self._optional_ai_analysis(payload)

        result = {
            "summary": ai_result.get("summary") if ai_result else rule_result["summary"],
            "probable_root_cause": ai_result.get("probable_root_cause") if ai_result else rule_result["probable_root_cause"],
            "explanation": ai_result.get("explanation") if ai_result else rule_result["explanation"],
            "suggested_fix": ai_result.get("suggested_fix") if ai_result else rule_result["suggested_fix"],
            "test_steps": ai_result.get("test_steps") if ai_result else rule_result["test_steps"],
            "confidence": ai_result.get("confidence") if ai_result else rule_result["confidence"],
            "impacted_location": self._extract_location(stack_trace),
            "used_ai": bool(ai_result),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        self._save_history(payload, result)
        return result

    def _rule_based_analysis(self, error_message, stack_trace, code_snippet, language):
        text = f"{error_message}\n{stack_trace}\n{code_snippet}".lower()

        if "cannot read properties of undefined" in text or "undefined" in text:
            return {
                "summary": "A value is being used before the program confirms it exists.",
                "probable_root_cause": "The code is accessing a property or method on an undefined value.",
                "explanation": "This usually happens when data is missing, an API response does not match the expected shape, or a function returns undefined.",
                "suggested_fix": "Add input validation, check the object before accessing its properties, and confirm where the missing value should be created.",
                "test_steps": [
                    "Log the variable before the failing line.",
                    "Check the function or API response that creates the variable.",
                    "Add a guard condition before accessing nested properties."
                ],
                "confidence": "High"
            }

        if "module not found" in text or "cannot find module" in text or "no module named" in text:
            return {
                "summary": "The project cannot find a dependency or file it needs.",
                "probable_root_cause": "A package is missing, the import path is wrong, or the virtual environment is not active.",
                "explanation": "This often happens after moving folders, cloning a repo, or forgetting to install dependencies.",
                "suggested_fix": "Install dependencies, verify the import path, and run the command from the project root folder.",
                "test_steps": [
                    "Run the package install command.",
                    "Check that the file or package exists.",
                    "Restart the server or terminal after installing."
                ],
                "confidence": "High"
            }

        if "address already in use" in text or "eaddrinuse" in text:
            return {
                "summary": "The server cannot start because the port is already being used.",
                "probable_root_cause": "Another process is already running on the same port.",
                "explanation": "This happens when a previous server instance is still running.",
                "suggested_fix": "Stop the old process or use a different port.",
                "test_steps": [
                    "Run: lsof -i :PORT_NUMBER",
                    "Kill the old process if needed.",
                    "Restart the app."
                ],
                "confidence": "High"
            }

        if "syntaxerror" in text or "unexpected token" in text:
            return {
                "summary": "The code has invalid syntax.",
                "probable_root_cause": "A bracket, comma, quote, import, or language-specific syntax rule is incorrect.",
                "explanation": "The program cannot run because the code cannot be parsed.",
                "suggested_fix": "Inspect the line mentioned in the stack trace and check the surrounding lines.",
                "test_steps": [
                    "Check the exact line number from the stack trace.",
                    "Look one or two lines above the reported line.",
                    "Run a formatter or linter."
                ],
                "confidence": "Medium"
            }

        return {
            "summary": "The error requires deeper project-specific debugging.",
            "probable_root_cause": "The issue may involve incorrect assumptions, missing data, dependency mismatch, or flawed control flow.",
            "explanation": "The agent could not match a direct known pattern, so it recommends checking the stack trace, recent changes, and input data.",
            "suggested_fix": "Trace the error from the failing line backward to where the data or function was created.",
            "test_steps": [
                "Reproduce the error with the smallest possible input.",
                "Add logs before the failing line.",
                "Check recent code changes.",
                "Run tests after each fix."
            ],
            "confidence": "Medium"
        }

    def _optional_ai_analysis(self, payload):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None

        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

            prompt = (
                "You are a senior software debugging assistant. "
                "Analyze this developer issue and return ONLY valid JSON with these keys: "
                "summary, probable_root_cause, explanation, suggested_fix, test_steps, confidence.\\n\\n"
                f"Developer issue:\\n{json.dumps(payload, indent=2)}"
            )

            response = client.responses.create(
                model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
                input=prompt,
                temperature=0.1,
            )

            raw = response.output_text.strip()
            cleaned = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)

        except Exception:
            return None

    def _extract_location(self, stack_trace):
        if not stack_trace:
            return "No stack trace location provided."

        match = re.search(r"([A-Za-z0-9_./\\-]+\.(py|js|ts|java|c|cpp|go|rs)):(\d+):?(\d+)?", stack_trace)
        if not match:
            return "No exact file and line number detected."

        return f"{match.group(1)} line {match.group(3)}"

    def _save_history(self, payload, result):
        history = self.load_history()
        history.insert(0, {
            "error_message": payload.get("error_message", ""),
            "probable_root_cause": result.get("probable_root_cause", ""),
            "confidence": result.get("confidence", ""),
            "created_at": result.get("created_at", "")
        })

        with self.history_path.open("w", encoding="utf-8") as file:
            json.dump(history[:50], file, indent=2)

    def load_history(self):
        if not self.history_path.exists():
            return []

        try:
            with self.history_path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return []
