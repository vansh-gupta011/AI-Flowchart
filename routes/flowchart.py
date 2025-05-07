# ROUTES for Mermaid and D2 Flowchart Generation
from fastapi import APIRouter
from fastapi import HTTPException
from dto.flowchart import FlowchartRequest
import re

from utils.openai import get_openai_client

import os
import sys
from openai import OpenAI


router = APIRouter()
client = get_openai_client()
print("-----------client:",client,"________________-")

# /flowchart/mermaid
@router.post("/mermaid")
async def generate_flowchart(request: FlowchartRequest):
    try:
        flow_direction = "TB" if request.direction == "Top-to-Bottom" else "LR"

        system_prompt = f"""
        You are a Flowchart Generator. Your task is to create a {request.complexity.lower()} flowchart using only valid MermaidJS syntax (v10.9.3) that adheres strictly to the visual conventions and rules below.

        📌 Symbol Rules (Match UI and standard flowchart conventions):
        1. Use these shapes only:
        - Start/End       →  ([Text])      → Oval shape
        - Process         →  [Text]        → Rectangle
        - Decision        →  {{Text}}      → Diamond
        - Input           →  [/Text/]      → Right-slanted parallelogram
        - Output          →  [\\Text\\]    → Left-slanted parallelogram

        2. Connect shapes with arrows:
        - Standard arrow: -->
        - Decision branches: -->|Yes| or -->|No|

        3. All nodes must use **unique IDs** (e.g., start1, step2, decision3, input4, output5)

        📾 Formatting Instructions:
        - First line must be: flowchart {flow_direction}
        - Output only MermaidJS code that can render **without any syntax error**
        - No Markdown (no triple backticks), no titles, no explanation, no comments
        - Maintain logical, readable flow
        - Follow standard flowchart meaning for each shape (per image reference)

        🧐 Use Case Context:
        {request.prompt}
        """

        user_message = f"Create a flowchart: {request.prompt}"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_message.strip()}
            ],
            temperature=0.5
        )

        mermaid_code = response.choices[0].message.content.strip()

        # Clean up any markdown artifacts
        for bad in ["```mermaid", "```", "“", "”"]:
            mermaid_code = mermaid_code.replace(bad, "")
        mermaid_code = mermaid_code.strip()

        # Ensure the correct start
        expected_prefix = f"flowchart {flow_direction}"
        if not mermaid_code.startswith(expected_prefix):
            mermaid_code = f"{expected_prefix}\n{mermaid_code}"

        # Validate Mermaid node shapes
        shape_pattern = re.compile(r"\w+\s*(=|\()\s*(\(\[.+\]\)|\[.+\]|\{.+\}|\[/.*?/\]|\[\\.*?\\\])")
        if not shape_pattern.search(mermaid_code):
            raise HTTPException(status_code=400, detail="Generated Mermaid code has invalid node shapes.")

        return {"mermaid_code": mermaid_code}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# /flowchart/d2
@router.post("/d2")
async def generate_d2(request: FlowchartRequest):
    try:
        flow_direction = "down" if request.direction == "Top-to-Bottom" else "right"

        system_prompt = f"""
You are a D2 Flowchart Generator. Your job is to generate valid and complete D2 code (https://d2lang.com/) for a {request.complexity.lower()} flowchart that strictly follows all formatting and structural rules.

🧠 RULES FOR FLOW STRUCTURE:

1. Start with: direction: {flow_direction}

2. NODES:
- Start: name = "start"; shape: oval; style.fill: "#f0f9ff"; icon: "play-circle.svg"; label: "Start"
- End: name = "end"; shape: oval; style.fill: "#f0f9ff"; icon: "stop-circle.svg"; label: "End"
- Process: shape: rectangle; style.fill: "#f8fafc"; label must be descriptive
- Decision: shape: diamond; style.fill: "#fff7f0"; must have exactly two outgoing paths labeled "Yes" and "No"
- Input/Output: shape: parallelogram; style.fill: "#f8fafc"; icon: "file-earmark-text.svg"
- Database: shape: cylinder; icon: "database.svg"
- User: icon: "person.svg"
- Merge Node: shape: circle; must reconnect paths from all branches

3. NODE DEFINITION:
- Each node must be explicitly defined in this format:

  node_id: {{
    shape: [oval|rectangle|diamond|parallelogram|circle|cylinder]
    style.fill: "[hex_color]"
    icon: "[icon_file]" (if applicable)
    label: "[Descriptive label]"
  }}

- Every node must have a unique node_id (use snake_case)

4. CONNECTIONS:
- Use ONLY `->` syntax (e.g., `node1 -> node2: "Yes"`)
- Do NOT use shorthand or alternative edge notations
- Every node (except end) must have at least one outgoing connection
- Every node (except start) must have at least one incoming connection
- Decision nodes must have both "Yes" and "No" branches explicitly labeled using `: "Yes"` and `: "No"` syntax
- All branches after a decision must reconnect via a **single merge node**
- Only the merge node must connect to the next node in the flow (e.g., End or further processes)
- Do NOT create redundant edges that connect the same node both before and after the merge node
- Do NOT connect the same node (like update_ticket_status) directly and through the merge node; use the merge node as the only rejoining point

5. VALIDATION:
- Ensure all nodes are connected (no disconnected or floating nodes)
- All paths from `start` must reach `end`
- No duplicated node IDs
- No ambiguous labels or shorthand
- No Markdown, comments, or explanations — only pure D2 code

6. OUTPUT FORMAT:
- First line: `direction: {flow_direction}`
- Then: explicit node definitions
- Finally: all `->` connections, with labels where needed
- Return ONLY valid D2 syntax — do NOT include Markdown or extra formatting


📄 Generate flowchart for:
{request.prompt}
"""

        print(system_prompt)

        user_message = f"Create a flowchart with images where appropriate: {request.prompt}"
        print(user_message)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_message.strip()}
            ],
            temperature=0.5
        )

        d2_code = response.choices[0].message.content.strip()

        # Clean up any markdown artifacts
        for bad in ["```d2", "```", "“", "”"]:
            d2_code = d2_code.replace(bad, "")
        d2_code = d2_code.strip()

        if not d2_code.startswith(f"direction: {flow_direction}"):
            d2_code = f"direction: {flow_direction}\n{d2_code}"
        
        return {"d2_code": d2_code}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))