from flask import Flask, render_template, request
import google.generativeai as genai
import markdown

app = Flask(__name__)

genai.configure(api_key="YOUR_API_KEY_HERE")

model = genai.GenerativeModel("models/gemini-2.5-pro") # if it gives you an error or reached the limit, try "models/gemini-2.5-flash"

@app.route('/', methods=['GET', 'POST'])
def index():
    response_html = ""
    user_scenario = ""
    
    if request.method == 'POST':
        user_scenario = request.form['prompt']
        
        system_instruction = f"""
        Role: You are a Senior Incident Responder and SOC Manager acting as an automated playbook generator.
        
        Task: 
        1. Analyze the network security scenario provided by the user below and generate a professional Incident Response (IR) Playbook.
        
        Strictly structure your response into these 5 phases (NIST/SANS framework). Use Markdown headers (###) for phases and bullet points (*) for steps.
        
        1. **Identification & Scoping:**
           - Determine the type of attack.
           - List logs/tools to check.
           - Assess severity.
           
        2. **Containment:**
           - Short-term actions.
           - Long-term actions.
           
        3. **Eradication:**
           - Steps to remove root cause.
           
        4. **Recovery:**
           - Steps to restore systems.
           - Validation checks.
           
        5. **Lessons Learned:**
           - Root cause analysis summary.
           - Recommendations.
        
        2. Create a Mermaid.js flowchart that visually summarizes the full 5-Phase NIST process described above.
        
        IMPORTANT For Mermaid Diagram, use STRICT format:
        - The entire mermaid code must be inside a single, standard markdown code block.
        - Start with `graph TD`
        - **Use Inline Styling only (`:::className`)**. Do NOT use the old `class A, B, C process;` syntax.
        
        - **Styling Requirements:**
          1. Define the following classes at the end of the mermaid code:
             classDef DECISION fill:#330000,stroke:#ff0000,stroke-width:2px,color:#fff;
             classDef ACTION fill:#001a00,stroke:#00ff00,stroke-width:2px,color:#fff;
             classDef START_END fill:#1a1a1a,stroke:#fff,stroke-width:2px,color:#fff;
          
          2. Apply styles correctly:
             - Use `:::DECISION` for decisions (Diamonds, questions).
             - Use `:::ACTION` for process steps (Rectangles).
             - Use `:::START_END` for Start and End nodes (Circles/Ovals).
        
        Example of syntax to follow (The model MUST generate the content of the diagram, not copy this example):
        ```mermaid
        graph TD
            A((Alert Received)):::START_END --> B[Identification & Scoping]:::ACTION
            B --> C{{Evidence Confirmed?}}:::DECISION
            C -- Yes --> D[Containment Actions]:::ACTION
            C -- No --> Z((Close Incident)):::START_END
            D --> E[Eradication & Cleanup]:::ACTION
            E --> F[Recovery & Validation]:::ACTION
            F --> G[Lessons Learned]:::ACTION
            G --> End((Process Complete)):::START_END
            
            %% Define Class Styles (Must be at the end of the diagram code)
            classDef DECISION fill:#330000,stroke:#ff0000,stroke-width:2px,color:#fff;
            classDef ACTION fill:#001a00,stroke:#00ff00,stroke-width:2px,color:#fff;
            classDef START_END fill:#1a1a1a,stroke:#fff,stroke-width:2px,color:#fff;
        ```

        Input Scenario:
        "{user_scenario}"
        """

        try:
            response = model.generate_content(system_instruction)
            if response and response.candidates:
                raw_markdown = response.text
                response_html = markdown.markdown(raw_markdown, extensions=['fenced_code'])
            else:
                 response_html = "<p>⚠️ No response was received.</p>"
        except Exception as e:
            response_html = f"<p>❌ An error occurred:<br>{e}</p>"
            
    return render_template('index.html', response_text=response_html, original_prompt=user_scenario)

if __name__ == '__main__':
    app.run(debug=True)
    