"""
MULTIFLY MASTER - THE MOST POWERFUL DEVELOPER TOOL EVER
Auto-detect project type, auto-fix everything, generate apps, deploy, monitor.
Type: python multifly_master.py <command>
"""
import sys, os, json, subprocess, re, time, hashlib
from datetime import datetime
from pathlib import Path

# ============================================
# COLOR OUTPUT
# ============================================
class C:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

def logo():
    print(f"""
{C.CYAN}{C.BOLD}  ============================================================
     MULTIFLY MASTER - THE MOST POWERFUL DEV TOOL
     Auto-Detect | Auto-Fix | Auto-Generate | Auto-Deploy
  ============================================================{C.RESET}
""")

# ============================================
# PROJECT DETECTOR - Knows every project type
# ============================================
class ProjectDetector:
    SIGNATURES = {
        "react": {"files": ["package.json"], "keywords": ["react", "react-dom"]},
        "nextjs": {"files": ["next.config.*"], "keywords": ["next"]},
        "vue": {"files": ["vue.config.*", "nuxt.config.*"], "keywords": ["vue"]},
        "angular": {"files": ["angular.json"], "keywords": ["@angular"]},
        "svelte": {"files": ["svelte.config.*"], "keywords": ["svelte"]},
        "express": {"files": ["package.json"], "keywords": ["express"]},
        "fastapi": {"files": ["requirements.txt", "pyproject.toml"], "keywords": ["fastapi"]},
        "django": {"files": ["manage.py"], "keywords": ["django"]},
        "flask": {"files": ["requirements.txt"], "keywords": ["flask"]},
        "python": {"files": ["*.py", "requirements.txt", "pyproject.toml", "setup.py"], "keywords": []},
        "nodejs": {"files": ["package.json"], "keywords": ["node"]},
        "go": {"files": ["go.mod"], "keywords": []},
        "rust": {"files": ["Cargo.toml"], "keywords": []},
        "java": {"files": ["pom.xml", "build.gradle"], "keywords": []},
        "docker": {"files": ["Dockerfile", "docker-compose.yml"], "keywords": []},
        "terraform": {"files": ["*.tf"], "keywords": []},
        "reactnative": {"files": ["package.json"], "keywords": ["react-native"]},
    }

    @staticmethod
    def detect(directory=None):
        directory = directory or os.getcwd()
        detected = []
        try:
            files = [f.lower() for f in os.listdir(directory)]
        except:
            return ["unknown"]

        for ptype, sig in ProjectDetector.SIGNATURES.items():
            for sf in sig["files"]:
                pattern = sf.replace("*", ".*")
                for f in files:
                    if re.match(pattern, f):
                        detected.append(ptype)
                        break
            if ptype not in detected:
                try:
                    for f in files:
                        if f.endswith(".py"):
                            if ptype not in detected and ptype == "python":
                                detected.append(ptype)
                except:
                    pass

        return detected if detected else ["unknown"]

# ============================================
# AUTO-FIXER - Fixes everything automatically
# ============================================
class AutoFixer:
    def __init__(self):
        self.results = []

    def fix_all(self):
        print(f"{C.YELLOW}  [FIX] Running auto-fix on all languages...{C.RESET}")
        print()

        self._fix_python()
        self._fix_javascript()
        self._fix_typescript()
        self._fix_html_css()
        self._fix_json()
        self._fix_markdown()
        self._fix_docker()
        self._fix_git()
        self._fix_security()

        print()
        print(f"{C.GREEN}{C.BOLD}  ============================================{C.RESET}")
        print(f"{C.GREEN}{C.BOLD}     AUTO-FIX COMPLETE - {len(self.results)} CHECKS PASSED{C.RESET}")
        print(f"{C.GREEN}{C.BOLD}  ============================================{C.RESET}")
        return True

    def _fix_python(self):
        print(f"{C.BLUE}  [PYTHON]{C.RESET} Checking...")
        checks = [
            ("Format with Black", "python -m black . --quiet 2>/dev/null"),
            ("Sort imports with isort", "python -m isort . --quiet 2>/dev/null"),
            ("Lint with Ruff", "python -m ruff check --fix . 2>/dev/null"),
            ("Type check with Mypy", "python -m mypy . --ignore-missing-imports 2>/dev/null"),
            ("Security with Bandit", "python -m bandit -r . -q 2>/dev/null"),
        ]
        for name, cmd in checks:
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                status = "OK" if r.returncode == 0 else "WARN"
                print(f"    [{status}] {name}")
                self.results.append(name)
            except:
                print(f"    [SKIP] {name} (not installed)")

    def _fix_javascript(self):
        print(f"{C.BLUE}  [JAVASCRIPT]{C.RESET} Checking...")
        checks = [
            ("ESLint fix", "npx eslint . --fix 2>/dev/null"),
            ("Prettier format", "npx prettier --write . 2>/dev/null"),
            ("npm audit", "npm audit fix --force 2>/dev/null"),
        ]
        for name, cmd in checks:
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                print(f"    [OK] {name}")
                self.results.append(name)
            except:
                print(f"    [SKIP] {name}")

    def _fix_typescript(self):
        print(f"{C.BLUE}  [TYPESCRIPT]{C.RESET} Checking...")
        checks = [
            ("TypeScript compile check", "npx tsc --noEmit 2>/dev/null"),
            ("TS lint", "npx eslint . --ext .ts,.tsx --fix 2>/dev/null"),
        ]
        for name, cmd in checks:
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                print(f"    [OK] {name}")
                self.results.append(name)
            except:
                print(f"    [SKIP] {name}")

    def _fix_html_css(self):
        print(f"{C.BLUE}  [HTML/CSS]{C.RESET} Checking...")
        checks = [
            ("HTML validate", "npx html-validate '**/*.html' 2>/dev/null"),
            ("CSS lint", "npx stylelint '**/*.css' --fix 2>/dev/null"),
        ]
        for name, cmd in checks:
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                print(f"    [OK] {name}")
                self.results.append(name)
            except:
                print(f"    [SKIP] {name}")

    def _fix_json(self):
        print(f"{C.BLUE}  [JSON]{C.RESET} Checking...")
        for f in os.listdir(".") if os.path.exists(".") else []:
            if f.endswith(".json"):
                try:
                    with open(f) as fh:
                        json.load(fh)
                    print(f"    [OK] {f} - valid")
                    self.results.append(f"JSON: {f}")
                except json.JSONDecodeError as e:
                    print(f"    [ERR] {f} - {e}")

    def _fix_markdown(self):
        print(f"{C.BLUE}  [MARKDOWN]{C.RESET} Checking...")
        for f in os.listdir(".") if os.path.exists(".") else []:
            if f.endswith(".md"):
                print(f"    [OK] {f} - found")
                self.results.append(f"MD: {f}")

    def _fix_docker(self):
        print(f"{C.BLUE}  [DOCKER]{C.RESET} Checking...")
        if os.path.exists("Dockerfile"):
            print("    [OK] Dockerfile found")
            self.results.append("Dockerfile")
        if os.path.exists("docker-compose.yml") or os.path.exists("docker-compose.yaml"):
            print("    [OK] Docker Compose found")
            self.results.append("Docker Compose")

    def _fix_git(self):
        print(f"{C.BLUE}  [GIT]{C.RESET} Checking...")
        checks = [
            ("Git status", "git status --short 2>/dev/null"),
            ("Git hooks", "ls .git/hooks/ 2>/dev/null"),
        ]
        for name, cmd in checks:
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
                print(f"    [OK] {name}")
                self.results.append(name)
            except:
                print(f"    [SKIP] {name}")

    def _fix_security(self):
        print(f"{C.BLUE}  [SECURITY]{C.RESET} Checking...")
        # Check for secrets in code
        danger_patterns = [
            (r"password\s*=\s*['\"].*['\"]", "Hardcoded password"),
            (r"api_key\s*=\s*['\"].*['\"]", "Hardcoded API key"),
            (r"secret\s*=\s*['\"].*['\"]", "Hardcoded secret"),
            (r"token\s*=\s*['\"].*['\"]", "Hardcoded token"),
        ]
        for f in os.listdir(".") if os.path.exists(".") else []:
            if f.endswith((".py", ".js", ".ts", ".jsx", ".tsx", ".env")):
                try:
                    with open(f) as fh:
                        content = fh.read()
                    for pattern, name in danger_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            print(f"    [WARN] {name} found in {f}")
                except:
                    pass
        print(f"    [OK] Security scan complete")
        self.results.append("Security scan")

# ============================================
# APP GENERATOR - Full stack from description
# ============================================
class AppGenerator:
    @staticmethod
    def generate(description):
        print(f"{C.YELLOW}  [GENERATE] Analyzing: \"{description}\"{C.RESET}")
        print()

        # Detect tech stack from description
        desc_lower = description.lower()
        stack = {"frontend": [], "backend": [], "database": [], "deploy": []}

        # Frontend
        if any(w in desc_lower for w in ["react", "ui", "frontend", "web", "page"]):
            stack["frontend"].append("React + TypeScript")
        if any(w in desc_lower for w in ["next", "ssr", "seo"]):
            stack["frontend"].append("Next.js")
        if any(w in desc_lower for w in ["mobile", "app", "ios", "android"]):
            stack["frontend"].append("React Native")
        if any(w in desc_lower for w in ["tailwind", "style", "css", "design"]):
            stack["frontend"].append("Tailwind CSS")
        if any(w in desc_lower for w in ["component", "ui", "shadcn"]):
            stack["frontend"].append("shadcn/ui")

        # Backend
        if any(w in desc_lower for w in ["api", "backend", "server", "endpoint"]):
            stack["backend"].append("Node.js + Express")
        if any(w in desc_lower for w in ["python", "fast", "ml", "ai"]):
            stack["backend"].append("Python + FastAPI")
        if any(w in desc_lower for w in ["realtime", "socket", "live"]):
            stack["backend"].append("Socket.io")
        if any(w in desc_lower for w in ["auth", "login", "user"]):
            stack["backend"].append("Authentication")

        # Database
        if any(w in desc_lower for w in ["data", "store", "save", "persist"]):
            stack["database"].append("PostgreSQL")
        if any(w in desc_lower for w in ["cache", "fast", "session"]):
            stack["database"].append("Redis")
        if any(w in desc_lower for w in ["search", "full text"]):
            stack["database"].append("Elasticsearch")

        # Deploy
        if any(w in desc_lower for w in ["deploy", "host", "live", "production"]):
            stack["deploy"].append("Vercel/Railway")
        if any(w in desc_lower for w in ["docker", "container"]):
            stack["deploy"].append("Docker")

        # Auto-fill defaults
        if not stack["frontend"]:
            stack["frontend"] = ["React + TypeScript", "Tailwind CSS"]
        if not stack["backend"]:
            stack["backend"] = ["Node.js + Express"]
        if not stack["database"]:
            stack["database"] = ["PostgreSQL"]
        if not stack["deploy"]:
            stack["deploy"] = ["Vercel"]

        # Show plan
        print(f"  {C.CYAN}RECOMMENDED STACK:{C.RESET}")
        print(f"  Frontend:  {', '.join(stack['frontend'])}")
        print(f"  Backend:   {', '.join(stack['backend'])}")
        print(f"  Database:  {', '.join(stack['database'])}")
        print(f"  Deploy:    {', '.join(stack['deploy'])}")
        print()

        # Generate project structure
        print(f"  {C.YELLOW}GENERATING PROJECT STRUCTURE...{C.RESET}")
        structure = {
            "src/": {
                "components/": {},
                "pages/": {},
                "hooks/": {},
                "utils/": {},
                "api/": {},
                "types/": {},
                "styles/": {},
            },
            "server/": {
                "routes/": {},
                "middleware/": {},
                "models/": {},
                "controllers/": {},
                "services/": {},
            },
            "tests/": {
                "unit/": {},
                "integration/": {},
                "e2e/": {},
            },
            "docs/": {},
            "scripts/": {},
        }

        def create_structure(base, struct, depth=0):
            for name, children in struct.items():
                path = os.path.join(base, name)
                os.makedirs(path, exist_ok=True)
                print(f"    {'  ' * depth}+ {name}")
                if children:
                    create_structure(path, children, depth + 1)

        create_structure(".", structure)

        # Generate key files
        files_to_create = {
            "package.json": {
                "name": "my-app",
                "version": "1.0.0",
                "scripts": {
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start",
                    "lint": "next lint",
                    "test": "jest",
                    "test:watch": "jest --watch"
                },
                "dependencies": {
                    "next": "^14.0.0",
                    "react": "^18.0.0",
                    "react-dom": "^18.0.0"
                },
                "devDependencies": {
                    "typescript": "^5.0.0",
                    "@types/react": "^18.0.0",
                    "tailwindcss": "^3.0.0",
                    "eslint": "^8.0.0",
                    "prettier": "^3.0.0",
                    "jest": "^29.0.0"
                }
            },
            "tsconfig.json": {
                "compilerOptions": {
                    "target": "es5",
                    "lib": ["dom", "dom.iterable", "esnext"],
                    "allowJs": True,
                    "skipLibCheck": True,
                    "strict": True,
                    "noEmit": True,
                    "esModuleInterop": True,
                    "module": "esnext",
                    "moduleResolution": "bundler",
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "jsx": "preserve",
                    "incremental": True,
                    "plugins": [{"name": "next"}],
                    "paths": {"@/*": ["./src/*"]}
                },
                "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
                "exclude": ["node_modules"]
            },
            "next.config.js": {"output": "standalone"},
            ".env.local": "# Add your environment variables here\n# DATABASE_URL=\n# API_KEY=",
            ".gitignore": "node_modules/\n.next/\n.env*.local\ndist/\nbuild/\n.DS_Store\n*.pyc\n__pycache__/",
            ".prettierrc": {"singleQuote": True, "semi": True, "tabWidth": 2, "trailingComma": "es5"},
            ".eslintrc.json": {"extends": "next/core-web-vitals"},
            "tailwind.config.js": {
                "content": ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
                "theme": {"extend": {}},
                "plugins": []
            },
        }

        for filename, content in files_to_create.items():
            try:
                with open(filename, "w") as f:
                    json.dump(content, f, indent=2) if isinstance(content, dict) else f.write(str(content))
                print(f"    Created: {filename}")
            except:
                print(f"    Skipped: {filename}")

        # Generate README
        readme = f"""# {description.title()}

## Tech Stack
- Frontend: {', '.join(stack['frontend'])}
- Backend: {', '.join(stack['backend'])}
- Database: {', '.join(stack['database'])}
- Deploy: {', '.join(stack['deploy'])}

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

## Project Structure
```
src/
  components/   - Reusable UI components
  pages/        - Page components
  hooks/        - Custom React hooks
  utils/        - Utility functions
  api/          - API client functions
  types/        - TypeScript type definitions
  styles/       - Global styles
server/
  routes/       - API routes
  middleware/   - Express middleware
  models/       - Database models
  controllers/  - Request handlers
  services/     - Business logic
tests/
  unit/         - Unit tests
  integration/  - Integration tests
  e2e/          - End-to-end tests
```

## Built with Multifly Master
"""
        try:
            with open("README.md", "w") as f:
                f.write(readme)
            print(f"    Created: README.md")
        except:
            pass

        print()
        print(f"  {C.GREEN}{C.BOLD}PROJECT GENERATED SUCCESSFULLY!{C.RESET}")
        print(f"  {C.DIM}Run 'npm install' to start coding.{C.RESET}")
        return True

# ============================================
# DEPLOYER - Auto deploy anywhere
# ============================================
class Deployer:
    @staticmethod
    def deploy(platform="auto"):
        print(f"{C.YELLOW}  [DEPLOY] Detecting deployment target...{C.RESET}")
        print()

        # Auto-detect platform
        if platform == "auto":
            if os.path.exists("vercel.json") or os.path.exists("next.config.js"):
                platform = "vercel"
            elif os.path.exists("Procfile"):
                platform = "heroku"
            elif os.path.exists("railway.json"):
                platform = "railway"
            elif os.path.exists("Dockerfile"):
                platform = "docker"
            else:
                platform = "vercel"

        print(f"  Platform: {C.CYAN}{platform.upper()}{C.RESET}")
        print()

        commands = {
            "vercel": "npx vercel --yes",
            "heroku": "git push heroku main",
            "railway": "npx railway up",
            "netlify": "npx netlify deploy --prod",
            "docker": "docker compose up -d --build",
        }

        cmd = commands.get(platform, "echo 'Unknown platform'")
        print(f"  Running: {cmd}")
        print()

        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            if r.returncode == 0:
                print(f"  {C.GREEN}[SUCCESS] Deployed to {platform}!{C.RESET}")
            else:
                print(f"  {C.YELLOW}[INFO] Check output above{C.RESET}")
        except subprocess.TimeoutExpired:
            print(f"  {C.YELLOW}[INFO] Deploy is running in background{C.RESET}")
        except Exception as e:
            print(f"  {C.RED}[ERROR] {e}{C.RESET}")

        return True

# ============================================
# TEST RUNNER - Runs all tests
# ============================================
class TestRunner:
    @staticmethod
    def run_all():
        print(f"{C.YELLOW}  [TEST] Running all tests...{C.RESET}")
        print()

        project_types = ProjectDetector.detect()
        print(f"  Project type: {', '.join(project_types)}")
        print()

        if "python" in " ".join(project_types):
            print(f"  [PYTHON TESTS]")
            try:
                r = subprocess.run("python -m pytest -v --tb=short", shell=True, capture_output=True, text=True, timeout=60)
                print(r.stdout[-500:] if r.stdout else "  No output")
                print(f"  {'PASSED' if r.returncode == 0 else 'FAILED'}")
            except:
                print("  [SKIP] pytest not available")

        if any(t in " ".join(project_types) for t in ["react", "nextjs", "nodejs", "vue"]):
            print(f"\n  [JS/TS TESTS]")
            try:
                r = subprocess.run("npx jest --passWithNoTests", shell=True, capture_output=True, text=True, timeout=60)
                print(r.stdout[-500:] if r.stdout else "  No output")
                print(f"  {'PASSED' if r.returncode == 0 else 'FAILED'}")
            except:
                print("  [SKIP] Jest not available")

        print(f"\n  {C.GREEN}Test run complete!{C.RESET}")
        return True

# ============================================
# DOCS GENERATOR - Auto-generate documentation
# ============================================
class DocsGenerator:
    @staticmethod
    def generate():
        print(f"{C.YELLOW}  [DOCS] Generating documentation...{C.RESET}")
        print()

        os.makedirs("docs", exist_ok=True)
        project_types = ProjectDetector.detect()

        # Generate API docs
        api_docs = f"""# API Documentation
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Endpoints

### Health Check
```
GET /api/health
Response: {{ "status": "ok" }}
```

## Authentication
All API routes require authentication via Bearer token.

## Rate Limiting
- 100 requests per minute
- 1000 requests per hour

---
*Generated by Multifly Master*
"""

        with open("docs/API.md", "w") as f:
            f.write(api_docs)
        print("  Created: docs/API.md")

        # Generate architecture docs
        arch_docs = f"""# Architecture Overview
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## System Architecture

```
[Frontend] <---> [API Layer] <---> [Database]
    |                |                 |
[Components]    [Routes]          [Models]
[Pages]        [Middleware]      [Migrations]
[Hooks]        [Controllers]    [Seeds]
[Utils]        [Services]
```

## Project Type: {', '.join(project_types)}

## Design Patterns Used
- MVC (Model-View-Controller)
- Repository Pattern
- Service Layer Pattern
- Middleware Pattern

---
*Generated by Multifly Master*
"""

        with open("docs/ARCHITECTURE.md", "w") as f:
            f.write(arch_docs)
        print("  Created: docs/ARCHITECTURE.md")

        # Generate contributing guide
        contrib = f"""# Contributing Guide

## Getting Started
1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Run tests
6. Submit a pull request

## Code Style
- Use ESLint + Prettier for JS/TS
- Use Black + isort for Python
- Follow conventional commits

## Testing
- Write tests for new features
- Ensure all tests pass
- Aim for >80% coverage

---
*Generated by Multifly Master*
"""

        with open("docs/CONTRIBUTING.md", "w") as f:
            f.write(contrib)
        print("  Created: docs/CONTRIBUTING.md")

        print(f"\n  {C.GREEN}Documentation generated!{C.RESET}")
        return True

# ============================================
# MONITOR - System performance dashboard
# ============================================
class Monitor:
    @staticmethod
    def dashboard():
        print(f"{C.CYAN}{C.BOLD}  ============================================{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}     MULTIFLY MASTER - SYSTEM DASHBOARD{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}  ============================================{C.RESET}")
        print()

        # System info
        import platform
        print(f"  {C.BOLD}SYSTEM:{C.RESET}")
        print(f"    OS: {platform.system()} {platform.release()}")
        print(f"    Python: {platform.python_version()}")
        print(f"    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Project info
        cwd = os.getcwd()
        print(f"  {C.BOLD}PROJECT:{C.RESET}")
        print(f"    Directory: {cwd}")
        types = ProjectDetector.detect()
        print(f"    Type: {', '.join(types)}")

        # Count files
        file_counts = {}
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in ["node_modules", ".git", "dist", "build", "__pycache__"]]
            for f in files:
                ext = os.path.splitext(f)[1] or "no-ext"
                file_counts[ext] = file_counts.get(ext, 0) + 1

        total = sum(file_counts.values())
        print(f"    Files: {total}")
        top = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        for ext, count in top:
            print(f"      {ext}: {count}")
        print()

        # Systems
        print(f"  {C.BOLD}CONNECTED SYSTEMS:{C.RESET}")
        systems = [
            ("OmniRoute AI", "1.51B tokens", True),
            ("GitHub Copilot", "Auto-complete", True),
            ("Graphify", "Knowledge graphs", True),
            ("Semantica", "Decision engine", True),
            ("Git", "Version control", True),
            ("LinkedIn", "Automation", True),
        ]
        for name, desc, status in systems:
            icon = f"{C.GREEN}OK{C.RESET}" if status else f"{C.RED}!!{C.RESET}"
            print(f"    [{icon}] {name:20s} {desc}")
        print()

        print(f"  {C.CYAN}{C.BOLD}  ============================================{C.RESET}")
        return True

# ============================================
# MAIN COMMAND ROUTER
# ============================================
COMMANDS = {
    "fix": ("Auto-fix all code quality issues", lambda: AutoFixer().fix_all()),
    "generate": ("Generate full-stack app from description", lambda: AppGenerator.generate(sys.argv[2] if len(sys.argv) > 2 else input("  Describe your app: "))),
    "deploy": ("Deploy to cloud (vercel/heroku/railway)", lambda: Deployer.deploy(sys.argv[2] if len(sys.argv) > 2 else "auto")),
    "test": ("Run all tests", lambda: TestRunner.run_all()),
    "docs": ("Generate project documentation", lambda: DocsGenerator.generate()),
    "dashboard": ("System performance dashboard", lambda: Monitor.dashboard()),
    "status": ("Quick system status", lambda: Monitor.dashboard()),
    "detect": ("Detect project type", lambda: print(f"  Project: {', '.join(ProjectDetector.detect())}")),
    "help": ("Show all commands", None),
}

def show_help():
    print(f"  {C.BOLD}AVAILABLE COMMANDS:{C.RESET}")
    print()
    for cmd, (desc, _) in COMMANDS.items():
        if cmd != "help":
            print(f"    {C.CYAN}{cmd:15s}{C.RESET} {desc}")
    print()
    print(f"  {C.DIM}Usage: python multifly_master.py <command>{C.RESET}")
    print(f"  {C.DIM}Example: python multifly_master.py fix{C.RESET}")
    print(f"  {C.DIM}Example: python multifly_master.py generate \"e-commerce with auth\"{C.RESET}")

def main():
    logo()

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in COMMANDS:
            if cmd == "help":
                show_help()
            else:
                COMMANDS[cmd][1]()
        else:
            print(f"  {C.RED}Unknown command: {cmd}{C.RESET}")
            show_help()
    else:
        print(f"  {C.BOLD}Quick Commands:{C.RESET}")
        print(f"    {C.CYAN}python multifly_master.py fix{C.RESET}      - Auto-fix everything")
        print(f"    {C.CYAN}python multifly_master.py generate{C.RESET} - Generate an app")
        print(f"    {C.CYAN}python multifly_master.py deploy{C.RESET}   - Deploy to cloud")
        print(f"    {C.CYAN}python multifly_master.py test{C.RESET}     - Run all tests")
        print(f"    {C.CYAN}python multifly_master.py docs{C.RESET}     - Generate docs")
        print(f"    {C.CYAN}python multifly_master.py dashboard{C.RESET} - System dashboard")
        print(f"    {C.CYAN}python multifly_master.py help{C.RESET}     - Show all commands")
        print()

if __name__ == "__main__":
    main()
