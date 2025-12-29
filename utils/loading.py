"""
This module contains utility functions for displaying loading indicators.
"""
import asyncio
from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn
)

async def loading_bar(total: int = 30, delay: float = 0.005):
    """Async helper that displays a short progress bar (used by UI flows).
    """
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn()
    )
    task = progress.add_task("Loading.. .", total=total)
    with progress:
        for _ in range(total):
            progress.update(task, advance=1)
            await asyncio.sleep(delay)