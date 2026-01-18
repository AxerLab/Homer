# PPT-ai: AWS 10,000 AIdeas Competition Pitch

## 1. Category

**Workplace efficiency**

---

## 2. Elevator Pitch

Stop wasting half your day fighting with text boxes and layout alignment. PPT-ai turns your technical docs or a simple prompt into an actual, editable .pptx file or a pro-grade LaTeX PDF in seconds.

---

## 3. Vision

We're building a multi-agent system that handles the entire slide-making pipeline. It's not just a wrapper for a chat model.

- **Multi-Agent Loop**: A Generator agent drafts the slides, a Correction agent catches schema errors, and an Iterator agent handles your specific "make this slide shorter" feedback.
- **Smart RAG**: You upload a 50-page technical PDF. The system chunks it, embeds it, and pulls specific context to ensure the slides actually reflect your data, not just LLM hallucinations.
- **Dual Export Engines**: You get a real .pptx file (using `python-pptx`) that you can open and edit in PowerPoint. For the academic crowd, it outputs pro-quality Beamer PDFs via LaTeX.
- **Automated Visuals**: It uses Tavily to find relevant images based on slide content so you don't have to go hunting for stock photos.

---

## 4. Impact

Devs, researchers, and students spend hours on "the blank slide problem." They have the information in their heads or in a document, but the manual labor of formatting is a massive time sink.

PPT-ai solves the 80% of the work that is pure friction. It gives you a high-quality first draft that is structurally sound and contextually accurate. This enables teams to ship ideas faster without getting bogged down in the "PowerPoint tax."

The killer feature: you can upload your own documents. Have a 40-page research paper? A technical spec? Meeting notes? Drop them in, and the AI pulls context directly from YOUR content—not generic internet knowledge. Your slides actually reflect your data, your findings, your work.

---

## 5. Game Plan

Building this from scratch, AWS-native from day one.

- **Week 1**: Set up the multi-agent backbone using Kiro. Define three agents: Generator (creates slide structure), Corrector (catches validation errors and retries), Iterator (handles per-slide edits). Get basic prompt-to-JSON working with Bedrock Nova.
- **Week 2**: Build the RAG pipeline with Bedrock AgentCore. Document upload → chunking → embedding → retrieval. Wire it into the Generator agent so uploaded PDFs actually inform slide content.
- **Week 3**: PPTX export engine. Take the validated JSON structure and produce real .pptx files. Store everything in S3. Build the React frontend—simple form, live preview, download button.
- **Week 4**: LaTeX/Beamer export path for academic-quality PDFs. Spin up a Lambda function to run pdflatex. Add Tavily image search so slides get relevant visuals automatically.
- **Week 5**: Slide-level editing flow. User clicks a slide, types feedback, Iterator agent regenerates just that slide. Hook up PostgreSQL (RDS) for session persistence.
- **Week 6**: Polish. Error handling, loading states, theme support (dark/light templates). Stress test cold starts, optimize Lambda memory settings, write the Builder Center article.

---

## 6. AWS AI Services

- **Bedrock (Nova)**: We need the huge context window to ingest large PDFs and the speed of Nova for real-time slide generation.
- **Kiro**: Our three-agent system (Generator, Corrector, Iterator) needs a robust framework for orchestration and debugging. Kiro is the perfect fit for managing this state.
- **Bedrock AgentCore**: This handles the RAG heavy lifting—chunking, embedding, and retrieval—without us having to manage a dedicated vector database manually.

---

## 7. Other AWS Free Tier Services

- **S3**: To store user-uploaded source documents and the final generated presentation files.
- **AWS Lambda**: Perfect for our Go-based microservices that convert PPTX and TeX files to PDF. It's cost-effective and scales to zero.
- **RDS (PostgreSQL)**: To keep track of user sessions, document metadata, and presentation history.
- **App Runner**: To host the FastAPI backend and React frontend with minimal configuration.
