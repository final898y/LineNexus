from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from loguru import logger


class PromptEngine:
    def __init__(self, prompts_dir: Optional[Path] = None):
        if prompts_dir is None:
            # 預設路徑：src/lineaihelper/prompts
            prompts_dir = Path(__file__).parent / "prompts"

        self.prompts_dir = prompts_dir
        self.env = Environment(
            loader=FileSystemLoader(str(self.prompts_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def get_prompt(
        self, name: str, version: str = "latest"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        載入 Prompt 模板與其 Metadata。
        name 範例: "stock"
        """
        file_path = f"{name}/{version}.md"
        try:
            # 取得原始內容以解析 YAML Frontmatter
            full_path = self.prompts_dir / file_path
            if not full_path.exists():
                raise FileNotFoundError(f"Prompt file not found: {full_path}")

            content = full_path.read_text(encoding="utf-8")
            metadata, body = self._parse_frontmatter(content)

            return body, metadata
        except Exception as e:
            logger.error(f"Failed to load prompt {name}:{version}: {e}")
            raise

    def render(
        self, name: str, variables: Dict[str, Any], version: str = "latest"
    ) -> str:
        """
        載入並渲染 Prompt。
        """
        try:
            # 先讀取 metadata 用於 logging
            body, metadata = self.get_prompt(name, version)
            ver_info = metadata.get("version", version)
            logger.info(f"Rendering prompt [{name}] version: {ver_info}")

            temp = self.env.from_string(body)
            return temp.render(**variables)

        except TemplateNotFound:
            logger.error(f"Template not found: {name}/{version}.md")
            raise
        except Exception as e:
            logger.error(f"Error rendering prompt {name}: {e}")
            raise

    def _parse_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """
        解析 Markdown 檔頭的 YAML。
        """
        content = content.strip()
        if content.startswith("---"):
            # 尋找第二個 ---
            try:
                # 略過第一個 ---
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1]) or {}
                    body = parts[2].strip()
                    return metadata, body
            except Exception as e:
                logger.warning(f"Failed to parse metadata: {e}")

        return {}, content
