"""模型路由层：模型池 + 标签匹配 + 失败降级。

每个模型是一个独立 OpenAI 兼容端点（OpenClaw 网关作为其一，可加 DeepSeek/Kimi 直连）。
按请求 mode/tool 的标签匹配选主模型，失败时按 priority 降级到池内备用模型。
手动指定模型仍优先（且不降级）。
"""
from dataclasses import dataclass, field

from app.config import settings


@dataclass
class ModelSpec:
    name: str
    model: str
    base_url: str = ""
    api_key: str = ""
    tags: list[str] = field(default_factory=list)
    priority: int = 0


class ModelRouter:
    def _default_spec(self) -> ModelSpec:
        return ModelSpec(
            name="default",
            model=settings.openclaw_model,
            base_url=settings.openclaw_base_url,
            api_key=settings.openclaw_api_key,
            tags=["default"],
            priority=0,
        )

    def _pool(self) -> list[ModelSpec]:
        specs: list[ModelSpec] = []
        for item in settings.model_pool:
            if not isinstance(item, dict) or not item.get("model"):
                continue
            specs.append(
                ModelSpec(
                    name=str(item.get("name") or item["model"]),
                    model=str(item["model"]),
                    base_url=str(item.get("base_url") or settings.openclaw_base_url),
                    api_key=str(item.get("api_key") or settings.openclaw_api_key),
                    tags=[str(t) for t in (item.get("tags") or [])],
                    priority=int(item.get("priority", 0) or 0),
                )
            )
        return specs

    def _request_tags(self, mode: str, tool: str | None) -> list[str]:
        if tool == "search":
            return ["search", "work", "default"]
        if tool == "homework":
            return ["homework", "work", "default"]
        if mode == "work":
            return ["work", "default"]
        return ["talk", "default"]

    def resolve(
        self,
        mode: str = "talk",
        tool: str | None = None,
        manual_model: str | None = None,
        manual_base_url: str | None = None,
        manual_api_key: str | None = None,
    ) -> list[ModelSpec]:
        """返回有序候选模型（主选 + 降级序列）。"""
        # 1. 手动覆盖优先：用户指定即尊重，不降级
        if manual_model:
            return [
                ModelSpec(
                    name="manual",
                    model=manual_model,
                    base_url=manual_base_url or settings.openclaw_base_url,
                    api_key=manual_api_key or settings.openclaw_api_key,
                    tags=[],
                    priority=0,
                )
            ]

        pool = self._pool()
        if not pool:
            return [self._default_spec()]

        ordered = sorted(pool, key=lambda s: (s.priority, s.name))

        # 2. 标签匹配主选
        primary: ModelSpec | None = None
        for tag in self._request_tags(mode, tool):
            for spec in ordered:
                if tag in spec.tags:
                    primary = spec
                    break
            if primary is not None:
                break
        if primary is None:
            primary = ordered[0]

        # 3. 降级序列 = 主选 + 其余按 priority
        rest = [s for s in ordered if s.name != primary.name]
        return [primary] + rest


model_router = ModelRouter()
