# Best Practices for LLM Pre-Prompts and Task Instructions

Based on research and analysis of effective LLM prompting patterns, the following best practices should be incorporated into pre-prompts:

## Core Structure Principles

1. **Clear Mission Statement**: Begin with a concise goal or outcome that the LLM should achieve, not the procedure to get there.

2. **Contextual Foundation**: Provide necessary background information, project status, and rationale for tasks to give the LLM proper context.

3. **Explicit Rules and Constraints**: Define boundaries, technical requirements, and specific objectives that must be followed.

4. **Structured Instructions**: Break down tasks into clear, actionable steps with logical sequencing.

5. **Input/Output Specifications**: Clearly define what input to expect and the required format for outputs.

## Effective Prompt Patterns

### Role-Based Prompting
- Assign a specific role to the LLM (e.g., "Act as a senior Python developer")
- Include expertise level and constraints
- Define the scope of authority and decision-making

### Step-by-Step Reasoning
- Encourage the LLM to think through problems methodically
- Use explicit reasoning frameworks
- Break complex tasks into smaller, manageable components

### Output Formatting Requirements
- Specify exact formatting needs (JSON, XML, markdown, etc.)
- Define length constraints
- Include examples of desired output format
- Specify handling of edge cases

## Key Optimization Strategies

1. **Precision over Brevity**: While concise prompts are valuable, clarity and completeness are more important for complex tasks.

2. **Iterative Refinement**: Design prompts to be improved over time based on performance.

3. **Error Prevention**: Anticipate common failure modes and include preventative instructions.

4. **Validation Requirements**: Specify how outputs should be verified or tested.

## Critical Success Factors

- **Specificity**: Vague prompts lead to inconsistent results
- **Completeness**: Include all necessary context and constraints
- **Unambiguity**: Avoid language that could be interpreted in multiple ways
- **Actionability**: Ensure instructions can be directly executed
- **Testability**: Design prompts so their effectiveness can be measured
