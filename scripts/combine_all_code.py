import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
output_file = os.path.join(base_dir, "ALL_CODE.md")

files_to_include = [
    # Config & Documentation
    "README.md",
    ".env.example",
    ".gitignore",
    "scripts/train_anomaly_backbone.py",
    
    # Backend Core & Config
    "backend/requirements.txt",
    "backend/app/main.py",
    "backend/app/database/session.py",
    "backend/app/models/__init__.py",
    "backend/app/models/product.py",
    "backend/app/models/inspection.py",
    "backend/app/models/model_metadata.py",
    "backend/app/schemas/product.py",
    "backend/app/schemas/inspection.py",
    "backend/app/schemas/dashboard.py",
    "backend/app/schemas/model_info.py",
    
    # Vision & ML
    "backend/app/vision/measurement.py",
    "backend/app/ml/feature_extractor.py",
    "backend/app/ml/reference_bank.py",
    "backend/app/ml/anomaly_detector.py",
    
    # Services
    "backend/app/services/inspection_engine.py",
    "backend/app/services/report_generator.py",
    "backend/app/services/seed_data.py",
    
    # API Routers
    "backend/app/api/health.py",
    "backend/app/api/dashboard.py",
    "backend/app/api/products.py",
    "backend/app/api/inspections.py",
    "backend/app/api/model.py",
    
    # Tests
    "backend/tests/test_inspectai.py",
    
    # Frontend Config
    "frontend/package.json",
    "frontend/vite.config.ts",
    "frontend/index.html",
    "frontend/src/index.css",
    "frontend/src/main.tsx",
    "frontend/src/App.tsx",
    "frontend/src/types/index.ts",
    "frontend/src/services/api.ts",
    
    # Frontend Components & Pages
    "frontend/src/components/Navbar.tsx",
    "frontend/src/components/StatusBadge.tsx",
    "frontend/src/pages/DashboardPage.tsx",
    "frontend/src/pages/NewInspectionPage.tsx",
    "frontend/src/pages/InspectionResultsPage.tsx",
    "frontend/src/pages/ProductRegistrationPage.tsx",
    "frontend/src/pages/InspectionHistoryPage.tsx",
    "frontend/src/pages/ModelStatusPage.tsx",
]

def get_lang(filename):
    ext = os.path.splitext(filename)[1].lower()
    mapping = {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".js": "javascript",
        ".json": "json",
        ".html": "html",
        ".css": "css",
        ".md": "markdown",
        ".txt": "text",
        ".example": "bash"
    }
    return mapping.get(ext, "text")

with open(output_file, "w", encoding="utf-8") as out:
    out.write("# InspectAI — Complete Consolidated Codebase\n\n")
    out.write("This document aggregates all source code files for **InspectAI — Universal AI Quality Inspection System** into a single consolidated file.\n\n")
    out.write("## Table of Contents\n\n")
    for idx, rel_path in enumerate(files_to_include, 1):
        anchor = rel_path.replace("/", "").replace(".", "").replace("-", "").lower()
        out.write(f"{idx}. [{rel_path}](#{anchor})\n")
    out.write("\n---\n\n")

    for rel_path in files_to_include:
        full_path = os.path.join(base_dir, rel_path)
        anchor = rel_path.replace("/", "").replace(".", "").replace("-", "").lower()
        out.write(f"## `{rel_path}`\n\n")
        out.write(f'<a id="{anchor}"></a>\n\n')
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            lang = get_lang(rel_path)
            out.write(f"```{lang}\n{content}\n```\n\n---\n\n")
        else:
            out.write(f"*File not found: {rel_path}*\n\n---\n\n")

print(f"Successfully generated {output_file} with {len(files_to_include)} files!")
