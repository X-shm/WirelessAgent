"""Task handler registry for the background worker."""
import asyncio


async def demo_echo(task_id, parameters, update_progress, is_cancelled):
    """Return the task parameters unchanged (proves the queue works end-to-end)."""
    await update_progress(30, "echoing")
    return {"task_id": task_id, "echo": parameters}


async def demo_countdown(task_id, parameters, update_progress, is_cancelled):
    """Count down with progress; checks cancellation on every step."""
    steps = max(1, int(parameters.get("steps", 5)))
    for i in range(steps):
        if await is_cancelled():
            raise asyncio.CancelledError()
        pct = int((i + 1) / steps * 100)
        await update_progress(pct, f"step {i + 1}/{steps}")
        await asyncio.sleep(0.02)
    return {"steps_done": steps}


async def ble_power_distance_v1(task_id, parameters, update_progress, is_cancelled):
    """BLE 功率-距离扫描（继承自原 BLE 切片，依赖 packages.agent.ble_coverage）。

    本处理器未在本机单独验证（该包随 main 存在）；合并后需在预发环境跑一次验证。
    """
    from pathlib import Path

    try:
        from packages.agent.ble_coverage import run_ble_power_distance
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"BLE 仿真能力不可用（packages.agent.ble_coverage 未安装）：{exc}")

    loop = asyncio.get_running_loop()
    attempt_dir = Path(".runtime") / "tasks" / task_id / "attempt_000"
    attempt_dir.mkdir(parents=True, exist_ok=True)

    def progress(percent, payload):
        stage = payload.get("stage") if isinstance(payload, dict) else None
        loop.create_task(update_progress(int(percent), stage))

    result = await run_ble_power_distance(
        task_id,
        parameters,
        attempt_dir,
        lambda _kind, _payload: None,
        progress,
    )
    return result


REGISTRY = {
    "demo_echo": demo_echo,
    "demo_countdown": demo_countdown,
    "ble_power_distance_v1": ble_power_distance_v1,
}