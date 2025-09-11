├─ pyproject.toml
├─ uv.lock
├─ README.md
├─ .gitignore
├─ .env.example
├─ scripts/
│  ├─ run_local.sh
│  ├─ format.sh
│  └─ lint.sh
├─ src/
│  ├─ aislides/
        main.py # basic entrypoint
        config/ # env var loading code and logging
        core/
            models/ # data structures for slide components
            llm/ # llm wrappers
            agent/ # pydantic agent definitions
                agent.py # core agent initilization
                prompts.py # agent prompts
            slide_generator/ # slide generator code (prompt to JSON)
            engines/
                tex/
                pptx/
                pdf/
        api/ # endpoints (explore gRPC)
├─ tests/
│  ├─ aislides/
        end_to_end.py
        config/ # env var loading code
        core/
            models/ # test slide components
            llm/ # test llm wrappers
            slide_generator/ # test slide generator code (prompt to JSON)
            engines/
                tex/
                pptx/
                pdf/
        api/ # test endpoints
