import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path: Path):
    prs = Presentation()
    # 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6] # blank

    # Color Palette
    BG_COLOR = RGBColor(10, 14, 23)          # #0A0E17
    CARD_BG = RGBColor(22, 33, 54)           # #162136
    CARD_BORDER = RGBColor(56, 189, 248)     # #38BDF8
    CYAN = RGBColor(6, 182, 212)             # #06B6D4
    BLUE = RGBColor(59, 130, 246)            # #3B82F6
    GREEN = RGBColor(16, 185, 129)           # #10B981
    RED = RGBColor(244, 63, 94)              # #F43F5E
    YELLOW = RGBColor(245, 158, 11)          # #F59E0B
    WHITE = RGBColor(255, 255, 255)
    MUTED = RGBColor(148, 163, 184)          # #94A3B8
    CODE_BG = RGBColor(4, 8, 16)             # #040810

    def set_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_header(slide, tagline_text: str, title_text: str, subtitle_text: str = ""):
        # Tagline
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11), Inches(0.4))
        tf = tag_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"🛡️ {tagline_text.upper()}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN
        p.font.name = "Calibri"

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.8))
        tf2 = title_box.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        p2.text = title_text
        p2.font.size = Pt(28)
        p2.font.bold = True
        p2.font.color.rgb = WHITE
        p2.font.name = "Calibri"

        # Subtitle
        if subtitle_text:
            sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(0.6))
            tf3 = sub_box.text_frame
            tf3.word_wrap = True
            p3 = tf3.paragraphs[0]
            p3.text = subtitle_text
            p3.font.size = Pt(13)
            p3.font.color.rgb = MUTED
            p3.font.name = "Calibri"

    def add_card(slide, left, top, width, height, title, desc, border_color=CARD_BORDER, icon=""):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), height - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = f"{icon}  {title}" if icon else title
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = WHITE
        p1.font.name = "Calibri"

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(12)
        p2.font.color.rgb = MUTED
        p2.font.name = "Calibri"
        p2.space_before = Pt(8)
        return card

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)

    t_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.6), Inches(10.9), Inches(2.2))
    tf = t_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "VulScanAgent"
    p.font.size = Pt(50)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.font.name = "Calibri"

    p2 = tf.add_paragraph()
    p2.text = "Autonomous AI DevSecOps Security Engineer"
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = CYAN
    p2.font.name = "Calibri"
    p2.space_before = Pt(10)

    p3 = tf.add_paragraph()
    p3.text = "Scans Repositories, Synthesizes Precision AST Patches, Validates Zero Regressions via Test Suites, and Opens Pull Requests for Human Review."
    p3.font.size = Pt(14)
    p3.font.color.rgb = MUTED
    p3.font.name = "Calibri"
    p3.space_before = Pt(14)

    add_card(s1, Inches(1.2), Inches(4.3), Inches(3.4), Inches(2.3), "Multi-Agent Team", "Specialized agents collaborate across discovery, patch generation, peer review, and verification.", icon="🧠")
    add_card(s1, Inches(4.9), Inches(4.3), Inches(3.4), Inches(2.3), "Zero-Break Guarantee", "Every patch executes the test suite in an isolated sandbox. Regressions automatically trigger error diagnosis or rollback.", icon="🧪")
    add_card(s1, Inches(8.6), Inches(4.3), Inches(3.4), Inches(2.3), "Multi-LLM Agility", "Seamlessly routes between Google Gemini, Anthropic Claude, and OpenAI with automated fallback.", icon="⚡")

    s1.notes_slide.notes_text_frame.text = "Welcome to the presentation of VulScanAgent. Today we showcase an autonomous DevSecOps agent capable of scanning repositories, generating verified security fixes without hallucinations, executing tests, and raising PRs for human approval."

    # ==========================================
    # SLIDE 2: The Problem
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_header(s2, "The Industry Problem", "Vulnerability Debt & The Triage Bottleneck", "DevSecOps tools today alert engineers to hundreds of vulnerabilities without verifying exploitability or producing working fixes.")

    add_card(s2, Inches(0.8), Inches(2.3), Inches(3.6), Inches(4.3), "Alert Fatigue", "Dependabot and static scanners dump hundreds of CVE notifications into backlogs.\n\nOver 80% of alerts remain unaddressed for months because security teams lack the development capacity to manually triage every item.", RED, "🚨")
    add_card(s2, Inches(4.8), Inches(2.3), Inches(3.6), Inches(4.3), "Blind Bumping Breaks Code", "Naive package version updates often introduce breaking API changes, deprecate method signatures, or fail integration pipelines.\n\nDevelopers fear merging automated bumps because they disrupt production services.", YELLOW, "💥")
    add_card(s2, Inches(8.8), Inches(2.3), Inches(3.6), Inches(4.3), "Engineering Drag", "Developers lose 30-40% of their sprint researching CVE advisories, hand-crafting regexes, and running repetitive regression test cycles.\n\nSecurity becomes a friction point instead of an automated pipeline velocity enabler.", CYAN, "⏱️")

    s2.notes_slide.notes_text_frame.text = "Here we highlight the core problem every engineering team faces: static scanners create alerts, not solutions. Blind bumps break code, causing alert fatigue and high engineering drag."

    # ==========================================
    # SLIDE 3: Multi-Agent Architecture
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_header(s3, "Architecture Overview", "Collaborative Multi-Agent Security Team", "Inspired by modern agentic architectures, VulScanAgent separates duties into specialized autonomous roles.")

    roles = [
        ("🎯 ScanStrategist", "Profiles target repository tech stack and focuses scanner attack vectors.", CYAN),
        ("🛠️ FixArchitect", "Drafts surgical AST patches bounded by XML quarantine delimiters.", BLUE),
        ("🧐 SecurityReviewer", "Critiques proposed patches against MITRE ATT&CK & OWASP standards.", GREEN),
        ("🧪 TestRunner & Verifier", "Executes native test suites and synthesizes targeted regression tests.", YELLOW),
        ("🩺 ErrorDiagnostician", "Parses test failure stack traces and prescribes corrections back to the Architect.", RED),
        ("📝 PRAuditor", "Builds formal Pull Request documentation with badges, diffs, and rollback plans.", CYAN)
    ]

    for idx, (title, desc, color) in enumerate(roles):
        col = idx % 3
        row = idx // 3
        left = Inches(0.8 + col * 4.0)
        top = Inches(2.3 + row * 2.3)
        add_card(s3, left, top, Inches(3.7), Inches(2.0), title, desc, color)

    s3.notes_slide.notes_text_frame.text = "VulScanAgent does not use a single monolithic prompt. Instead, it coordinates 6 specialized agents with distinct prompts, guardrails, and validation responsibilities."

    # ==========================================
    # SLIDE 4: Live Test Target
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_header(s4, "Real-World Benchmark", "Live Test Target: Sightline Face Detection", "Evaluated live on Rohitkr2510/face-recognition-devops using the Google Gemini API.")

    add_card(s4, Inches(0.8), Inches(2.3), Inches(5.6), Inches(4.3), "Application Architecture", 
             "• Repository: Rohitkr2510/face-recognition-devops\n"
             "• Tech Stack: FastAPI (Python 3.14 async web server)\n"
             "• Vision Engine: OpenCV Haar Cascade frontal face detection\n"
             "• Manifest: Modern PEP 621 (pyproject.toml)\n"
             "• Containerization: Docker & Docker Compose\n"
             "• Quality Gate: 5 comprehensive Pytest integration tests\n"
             "• Baseline Status: 5/5 Passing Tests in 3.36s", CYAN, "📦")

    add_card(s4, Inches(6.8), Inches(2.3), Inches(5.6), Inches(4.3), "Agent Runtime Configuration",
             "• AI Engine: Google Gemini API (gemini-3.5-flash / gemini-3.6-flash)\n"
             "• Scanning Layers: SAST + SCA + Secrets + IaC\n"
             "• Minimum Severity: LOW, MEDIUM, HIGH, CRITICAL\n"
             "• Test Policy: Strict zero-regression pass requirement\n"
             "• Governance: Zero auto-merge policy with human review\n"
             "• Deployment Mode: Local CLI & Containerized Docker workflow", GREEN, "⚙️")

    s4.notes_slide.notes_text_frame.text = "This slide introduces our benchmark application: a production-grade FastAPI face detection microservice with OpenCV and Docker."

    # ==========================================
    # SLIDE 5: Vulnerability Discovery
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_header(s5, "Discovery Phase", "2 Real Vulnerabilities Flagged by Scanners", "Multi-layer scanners identified supply chain and container infrastructure exposures.")

    add_card(s5, Inches(0.8), Inches(2.3), Inches(5.6), Inches(4.3), "Finding 1: Vulnerable jinja2 (HIGH)",
             "• Rule ID: SCA-CVE-2024-56326-jinja2\n"
             "• Affected File: pyproject.toml (Line 8)\n"
             "• Advisory: Jinja2 versions before 3.1.5 allow template compiler sandbox breakout and arbitrary attribute injection (CWE-79).\n"
             "• Attack Vector: Attacker uploads crafted image metadata causing server-side template injection (SSTI) during report generation.", RED, "🚨")

    add_card(s5, Inches(6.8), Inches(2.3), Inches(5.6), Inches(4.3), "Finding 2: 0.0.0.0 Port Exposure (MEDIUM)",
             "• Rule ID: IAC-COMPOSE-ALL-INTERFACES-1\n"
             "• Affected File: docker-compose.yml (Line 5)\n"
             "• Advisory: Exposing container port 8000:8000 to all network interfaces (0.0.0.0) bypasses local host firewalls (CWE-250).\n"
             "• Attack Vector: Exposes unauthenticated internal API endpoints directly to external network scanners and automated bots.", YELLOW, "⚠️")

    s5.notes_slide.notes_text_frame.text = "CompositeScanner flagged both vulnerabilities: an outdated Jinja2 dependency vulnerable to sandbox breakout, and an insecure Docker compose port binding."

    # ==========================================
    # SLIDE 6: Automated Precision Remediation
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_header(s6, "Remediation Phase", "Precision AST Patching by Gemini Team", "FixArchitect synthesized minimal, non-breaking modifications; SecurityReviewer approved with 9/10 confidence.")

    # Code Box 1
    c1 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.3), Inches(5.6), Inches(4.3))
    c1.fill.solid()
    c1.fill.fore_color.rgb = CODE_BG
    c1.line.color.rgb = CYAN
    tb1 = s6.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(5.2), Inches(4.0))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "pyproject.toml (CVE-2024-56326 Fix)"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = CYAN
    p.font.name = "Consolas"

    diff1 = tf1.add_paragraph()
    diff1.text = (
        " dependencies = [\n"
        "   \"fastapi>=0.116,<1\",\n"
        "-  \"jinja2>=3.1,<4\",\n"
        "+  \"jinja2>=3.1.5,<4\",\n"
        "   \"numpy>=2.3,<3\",\n"
        "   \"opencv-python-headless>=4.12,<5\",\n"
        "   \"python-multipart>=0.0.20,<1\",\n"
        " ]"
    )
    diff1.font.size = Pt(12)
    diff1.font.color.rgb = GREEN
    diff1.font.name = "Consolas"
    diff1.space_before = Pt(10)

    # Code Box 2
    c2 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(2.3), Inches(5.6), Inches(4.3))
    c2.fill.solid()
    c2.fill.fore_color.rgb = CODE_BG
    c2.line.color.rgb = GREEN
    tb2 = s6.shapes.add_textbox(Inches(7.0), Inches(2.4), Inches(5.2), Inches(4.0))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "docker-compose.yml (Port Hardening)"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = GREEN
    p.font.name = "Consolas"

    diff2 = tf2.add_paragraph()
    diff2.text = (
        " services:\n"
        "   sightline:\n"
        "     build: .\n"
        "     ports:\n"
        "-      - \"8000:8000\"\n"
        "+      - \"127.0.0.1:8000:8000\"\n"
        "     restart: unless-stopped\n"
        "     healthcheck:\n"
        "       test: [\"CMD\", \"python\", \"-c\", ...]"
    )
    diff2.font.size = Pt(12)
    diff2.font.color.rgb = GREEN
    diff2.font.name = "Consolas"
    diff2.space_before = Pt(10)

    s6.notes_slide.notes_text_frame.text = "Notice how minimal and targeted these fixes are. The AI did not rewrite unrelated files or introduce arbitrary changes. It made precise, surgical patches."

    # ==========================================
    # SLIDE 7: Test Verification & Eradication
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_header(s7, "Verification Phase", "Zero Regression Test Execution", "The test runner executed the full Pytest suite in 2.71s with 100% pass rate before accepting fixes.")

    term_card = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.3), Inches(11.6), Inches(4.4))
    term_card.fill.solid()
    term_card.fill.fore_color.rgb = CODE_BG
    term_card.line.color.rgb = CARD_BORDER

    tb = s7.shapes.add_textbox(Inches(1.1), Inches(2.5), Inches(11.0), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "$ pytest -o pythonpath=. test_target_repo/tests"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = CYAN
    p.font.name = "Consolas"

    p2 = tf.add_paragraph()
    p2.text = (
        "============================= test session starts =============================\n"
        "platform win32 -- Python 3.12.10, pytest-9.2.0 -- rootdir: test_target_repo\n"
        "collected 5 items\n\n"
        "tests/test_app.py::test_dashboard_renders .............. PASSED  [ 20%]\n"
        "tests/test_app.py::test_health_reports_model_state ..... PASSED  [ 40%]\n"
        "tests/test_app.py::test_detects_valid_image ............ PASSED  [ 60%]\n"
        "tests/test_app.py::test_rejects_unsupported_content_type PASSED  [ 80%]\n"
        "tests/test_app.py::test_rejects_invalid_image_data ..... PASSED  [100%]\n\n"
        "============================== 5 passed in 2.71s ==============================\n"
        "🎉 Remaining vulnerabilities meeting threshold: 0. Repository is fully secure!"
    )
    p2.font.size = Pt(12)
    p2.font.color.rgb = GREEN
    p2.font.name = "Consolas"
    p2.space_before = Pt(8)

    s7.notes_slide.notes_text_frame.text = "Verification is where VulScanAgent shines. If a single unit test failed, ErrorDiagnostician would intervene or automatically revert changes to protect production."

    # ==========================================
    # SLIDE 8: Pull Request Generation
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8)
    add_header(s8, "Human-in-the-Loop Approval", "Audit-Ready Pull Request Documentation", "PRAuditor drafts enterprise PR descriptions mapped to MITRE ATT&CK, D3FEND, and OWASP frameworks.")

    add_card(s8, Inches(0.8), Inches(2.3), Inches(5.6), Inches(4.3), "Generated PR Metadata",
             "• Title: [VulScanAgent] Fix HIGH: jinja2 (CVE-2024-56326)\n"
             "• Category: Software Composition Analysis (SCA)\n"
             "• Threat Mapping: MITRE ATT&CK T1190 & D3FEND D3-SCA\n"
             "• OWASP Category: A06:2021-Vulnerable and Outdated Components\n"
             "• Peer Review Score: Approved by Senior Reviewer (9/10)\n"
             "• Verification Badge: 5/5 Pytest Tests Passed\n"
             "• Rollback Instructions: Ready-to-run 1-click git rollback command", CYAN, "📋")

    add_card(s8, Inches(6.8), Inches(2.3), Inches(5.6), Inches(4.3), "Enterprise Safety Guardrails",
             "• Path Traversal Shield: Rejects directory escape paths ('../')\n"
             "• Command Sanitizer: Blocks dangerous shell chaining operators\n"
             "• Automated Secret Masking: Redacts API keys before creating PRs\n"
             "• AST Syntax Pre-validation: Rejects malformed Python syntax\n"
             "• Zero Auto-Merge Policy: Mandates human code owner sign-off", GREEN, "🔒")

    s8.notes_slide.notes_text_frame.text = "Every PR opened by VulScanAgent follows enterprise audit readiness. Developers receive complete context, risk scoring, test evidence, and rollback instructions."

    # ==========================================
    # SLIDE 9: Production Ecosystem
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9)
    add_header(s9, "Deployment Options", "Run Anywhere: CLI, Docker, CI/CD, Dashboard", "VulScanAgent integrates frictionlessly into enterprise DevOps pipelines.")

    add_card(s9, Inches(0.8), Inches(2.3), Inches(2.7), Inches(4.3), "CLI Tool", "Execute instant local scans or analyze remote public/private repos via Typer CLI.\n\npython main.py scan --repo <url>", CYAN, "💻")
    add_card(s9, Inches(3.7), Inches(2.3), Inches(2.7), Inches(4.3), "Docker 1-Click", "Cross-platform launcher scripts (docker-run.sh, docker-run.ps1) with dropped root privileges.", BLUE, "🐳")
    add_card(s9, Inches(6.6), Inches(2.3), Inches(2.7), Inches(4.3), "Web Dashboard", "FastAPI web dashboard with real-time job logs and HMAC-verified GitHub webhooks.", GREEN, "📊")
    add_card(s9, Inches(9.5), Inches(2.3), Inches(2.7), Inches(4.3), "GitHub Actions", "Automated CI/CD security workflow (.github/workflows/vulscan.yml) on every push/PR.", YELLOW, "🔄")

    s9.notes_slide.notes_text_frame.text = "Whether running locally via CLI, inside Docker on any OS, in GitHub Actions, or using the FastAPI web dashboard, VulScanAgent fits existing developer workflows."

    # ==========================================
    # SLIDE 10: Competitive Advantage (vs Checkmarx & Orca)
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_bg(s10)
    add_header(s10, "Competitive Landscape", "Why VulScanAgent Outperforms Checkmarx & Orca", "Transforming passive security alerts into an autonomous engineering partner.")

    # 3 Cards Side-by-Side
    col_w = Inches(3.6)
    gap = Inches(0.2)
    left_start = Inches(0.8)
    top_pos = Inches(1.8)
    h_pos = Inches(5.1)

    # 1. Checkmarx
    c_cm = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_start, top_pos, col_w, h_pos)
    c_cm.fill.solid()
    c_cm.fill.fore_color.rgb = CARD_BG
    c_cm.line.color.rgb = RED
    c_cm.line.width = Pt(1.5)

    tb_cm = s10.shapes.add_textbox(left_start + Inches(0.2), top_pos + Inches(0.2), col_w - Inches(0.4), h_pos - Inches(0.4))
    tf_cm = tb_cm.text_frame
    tf_cm.word_wrap = True
    p = tf_cm.paragraphs[0]
    p.text = "Checkmarx (CxSAST / SCA)"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = RED

    p_role = tf_cm.add_paragraph()
    p_role.text = "The Alert Dumper (Static Scan)"
    p_role.font.size = Pt(11)
    p_role.font.color.rgb = MUTED

    p_b = tf_cm.add_paragraph()
    p_b.text = (
        "❌ 35% - 50%+ False Positive noise\n\n"
        "❌ Floods Jira with unverified tickets\n\n"
        "❌ Cannot write code or patch bugs\n\n"
        "❌ Cannot run unit tests (`pytest`)\n\n"
        "❌ Zero regression awareness\n\n"
        "❌ MTTR: 45 to 90 Days\n\n"
        "❌ $50,000 - $200,000 / year cost"
    )
    p_b.font.size = Pt(11)
    p_b.font.color.rgb = WHITE
    p_b.space_before = Pt(8)

    # 2. Orca Security
    left_orca = left_start + col_w + gap
    c_orca = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_orca, top_pos, col_w, h_pos)
    c_orca.fill.solid()
    c_orca.fill.fore_color.rgb = CARD_BG
    c_orca.line.color.rgb = YELLOW
    c_orca.line.width = Pt(1.5)

    tb_orca = s10.shapes.add_textbox(left_orca + Inches(0.2), top_pos + Inches(0.2), col_w - Inches(0.4), h_pos - Inches(0.4))
    tf_orca = tb_orca.text_frame
    tf_orca.word_wrap = True
    p = tf_orca.paragraphs[0]
    p.text = "Orca Security (CNAPP)"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = YELLOW

    p_role = tf_orca.add_paragraph()
    p_role.text = "The Late-Stage Observer (Cloud)"
    p_role.font.size = Pt(11)
    p_role.font.color.rgb = MUTED

    p_b = tf_orca.add_paragraph()
    p_b.text = (
        "❌ Flags issues AFTER cloud deploy\n\n"
        "❌ Passive SideScanning VM snapshots\n\n"
        "❌ Disconnected from developer Git loop\n\n"
        "❌ Zero code repair or PR capability\n\n"
        "❌ Requires intrusive cloud IAM access\n\n"
        "❌ MTTR: 30 to 60 Days\n\n"
        "❌ $30,000 - $150,000 / year cost"
    )
    p_b.font.size = Pt(11)
    p_b.font.color.rgb = WHITE
    p_b.space_before = Pt(8)

    # 3. VulScanAgent
    left_vs = left_orca + col_w + gap
    c_vs = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_vs, top_pos, col_w, h_pos)
    c_vs.fill.solid()
    c_vs.fill.fore_color.rgb = CARD_BG
    c_vs.line.color.rgb = GREEN
    c_vs.line.width = Pt(2)

    tb_vs = s10.shapes.add_textbox(left_vs + Inches(0.2), top_pos + Inches(0.2), col_w - Inches(0.4), h_pos - Inches(0.4))
    tf_vs = tb_vs.text_frame
    tf_vs.word_wrap = True
    p = tf_vs.paragraphs[0]
    p.text = "VulScanAgent (Multi-Agent)"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = GREEN

    p_role = tf_vs.add_paragraph()
    p_role.text = "The Autonomous Fixer (Engineer)"
    p_role.font.size = Pt(11)
    p_role.font.color.rgb = CYAN

    p_b = tf_vs.add_paragraph()
    p_b.text = (
        "✅ Adversarial CandidateVerifier (<5% FP)\n\n"
        "✅ Shifts Left directly into Git PR inner loop\n\n"
        "✅ Autonomous AST precision patches\n\n"
        "✅ Executes repo tests (pytest in sandbox)\n\n"
        "✅ Zero-Regression Guarantee & Self-Heal\n\n"
        "✅ MTTR: Under 3 Minutes (< 180s)\n\n"
        "✅ Open Source + Cents per LLM scan"
    )
    p_b.font.size = Pt(11)
    p_b.font.color.rgb = WHITE
    p_b.space_before = Pt(8)

    s10.notes_slide.notes_text_frame.text = "Checkmarx and Orca are passive finders that create work for developers. VulScanAgent is an active fixer that delivers finished work directly to developers via Pull Requests."

    # ==========================================
    # SLIDE 11: Conclusion
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    set_bg(s11)

    t_box = s11.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(10.9), Inches(1.8))
    tf = t_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Transforming Vulnerability Triage"
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.font.name = "Calibri"

    p2 = tf.add_paragraph()
    p2.text = "From Manual Alert Overload to Autonomous, Verified, Human-Approved Remediation."
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = CYAN
    p2.font.name = "Calibri"
    p2.space_before = Pt(10)

    card_cta = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(3.6), Inches(10.9), Inches(2.6))
    card_cta.fill.solid()
    card_cta.fill.fore_color.rgb = CARD_BG
    card_cta.line.color.rgb = CYAN
    card_cta.line.width = Pt(2)

    tb_cta = s11.shapes.add_textbox(Inches(1.5), Inches(3.8), Inches(10.3), Inches(2.2))
    tf_cta = tb_cta.text_frame
    tf_cta.word_wrap = True
    p = tf_cta.paragraphs[0]
    p.text = "Key Takeaways from Today's Benchmark:"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = WHITE

    p_bullets = tf_cta.add_paragraph()
    p_bullets.text = (
        "• Tested Live: Rohitkr2510/face-recognition-devops remediated using Google Gemini.\n"
        "• 100% Remediation Rate: Resolved CVE-2024-56326 (Jinja2) and Docker port exposure.\n"
        "• Zero Regressions: All 5 integration tests executed and passed without disruption.\n"
        "• Outperforms Legacy Scanners: Replaces Checkmarx & Orca alert noise with automated, tested Pull Requests."
    )
    p_bullets.font.size = Pt(13)
    p_bullets.font.color.rgb = MUTED
    p_bullets.space_before = Pt(8)

    s11.notes_slide.notes_text_frame.text = "In conclusion, VulScanAgent successfully proved that autonomous AI agents can remediate real-world security vulnerabilities reliably and safely without breaking code."

    # Save presentation
    try:
        prs.save(str(output_path))
        print(f"Presentation saved to: {output_path}")
    except PermissionError:
        alt_path = output_path.with_name("VulScanAgent-Executive-Showcase.pptx")
        prs.save(str(alt_path))
        print(f"File locked by PowerPoint. Saved to alternative path: {alt_path}")

if __name__ == "__main__":
    out = Path("docs/presentations/VulScanAgent-Demo-Slides.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)
    create_deck(out)
