from pathlib import Path
from typing import Iterable


class DocumentGenerator:
    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_lesson(self, content: str, filename: str = "final_lesson.md") -> str:
        target = self.output_dir / filename
        target.write_text(content, encoding="utf-8")
        return str(target)

    def build_markdown(self, title: str, sections: Iterable[tuple[str, str]]) -> str:
        lines = [f"# {title}", ""]
        for heading, body in sections:
            lines.append(f"## {heading}")
            lines.append("")
            lines.append(body.strip())
            lines.append("")
        return "\n".join(lines).strip() + "\n"
