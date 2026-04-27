# test_workflow.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from graph.workflow import build_workflow
from langchain_core.messages import HumanMessage

app = build_workflow()
question = "Que dit le Coran sur la patience ?"
result = app.invoke({"question": question, "messages": [HumanMessage(content=question)]})
print(result["messages"][-1].content)