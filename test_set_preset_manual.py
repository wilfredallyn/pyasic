"""Manual test for set_preset() against a live LuxOS miner.

Usage:
    python test_set_preset_manual.py                # Read-only: show state
    python test_set_preset_manual.py --switch 190   # Switch preset (fuzzy match)
    python test_set_preset_manual.py --restore      # Restore original preset

Environment:
    MINER_IP  - miner IP address (default: 192.168.1.237)
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add pyasic to path for branch testing
sys.path.insert(0, str(Path(__file__).parent))

from pyasic import get_miner

MINER_IP = os.environ.get("MINER_IP", "192.168.1.237")
STATE_FILE = Path(__file__).parent / ".test_preset_state.json"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def save_state(data: dict):
    STATE_FILE.write_text(json.dumps(data, indent=2))
    log.info(f"State saved to {STATE_FILE}")


def load_state() -> dict | None:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return None


async def show_state(miner):
    """Read and display current miner state. No changes made."""
    print(f"\n{'='*60}")
    print(f"  MINER STATE: {miner.ip}")
    print(f"  Type: {type(miner).__name__}")
    print(f"{'='*60}\n")

    # Get config
    config = await miner.get_config()

    # ATM status
    atm = await miner.atm_enabled()
    print(f"  ATM enabled:      {atm}")

    # Mining mode
    mode = config.mining_mode
    active = getattr(mode, "active_preset", None)
    available = getattr(mode, "available_presets", [])

    print(f"  Active preset:    {active.name if active else 'N/A'}")
    if active:
        print(f"    Power:          {active.power}W")
        print(f"    Frequency:      {active.frequency}MHz")
        print(f"    Hashrate:       {active.hashrate} TH/s")
        print(f"    Voltage:        {active.voltage}V")
        print(f"    Tuned:          {active.tuned}")

    print(f"\n  Available presets ({len(available)}):")
    for i, p in enumerate(available):
        tuned = "TUNED" if p.tuned else "     "
        marker = " <<< ACTIVE" if active and p.name == active.name else ""
        print(f"    [{i:>2}] {p.name:>10}  {p.power:>5}W  {p.frequency:>4}MHz  {p.hashrate:>5} TH/s  {tuned}{marker}")

    print()
    return {
        "atm_enabled": atm,
        "active_preset": active.name if active else None,
        "available_presets": [p.name for p in available],
    }


def fuzzy_match_preset(query: str, available: list[str]) -> str | None:
    """Match a user query to a preset name, case-insensitive and partial.

    Matches if the query appears anywhere in the preset name.
    Examples: "190" matches "190MHz", "565mhz" matches "565MHz".
    Returns None if zero or multiple matches.
    """
    q = query.lower()
    matches = [name for name in available if q in name.lower()]
    if len(matches) == 1:
        return matches[0]
    return None


async def switch_preset(miner, query: str):
    """Switch to a named preset and verify."""
    print(f"\n--- Reading current state before switch ---")
    before = await show_state(miner)

    # Save state for --restore
    save_state(before)

    # Fuzzy match the input to an actual preset name
    target_name = fuzzy_match_preset(query, before["available_presets"])
    if target_name is None:
        print(f"\nCould not match '{query}' to a single preset.")
        print(f"Available: {before['available_presets']}")
        return False

    if target_name == before["active_preset"]:
        print(f"\nAlready on preset '{target_name}'. Pick a different one.")
        return False

    print(f"\n{'='*60}")
    print(f"  SWITCHING: {before['active_preset']} -> {target_name}")
    print(f"{'='*60}")
    print(f"  ATM is {'ON - will be toggled off/on' if before['atm_enabled'] else 'OFF - no ATM toggle needed'}")
    print()

    result = await miner.set_preset(target_name)
    print(f"  set_preset() returned: {result}")

    if not result:
        print("\n  FAILED - set_preset returned False")
        return False

    # Brief pause for miner to settle
    print("\n  Waiting 3s for miner to settle...")
    await asyncio.sleep(3)

    print(f"\n--- Reading state after switch ---")
    after = await show_state(miner)

    # Verify
    print(f"\n{'='*60}")
    print(f"  VERIFICATION")
    print(f"{'='*60}")

    passed = True

    if after["active_preset"] == target_name:
        print(f"  [PASS] Active preset is now '{target_name}'")
    else:
        print(f"  [FAIL] Active preset is '{after['active_preset']}', expected '{target_name}'")
        passed = False

    if before["atm_enabled"] and after["atm_enabled"]:
        print(f"  [PASS] ATM was re-enabled after switch")
    elif before["atm_enabled"] and not after["atm_enabled"]:
        print(f"  [FAIL] ATM was ON before but is now OFF (re-enable failed)")
        passed = False
    elif not before["atm_enabled"] and not after["atm_enabled"]:
        print(f"  [PASS] ATM was OFF and stayed OFF (correct)")
    else:
        print(f"  [INFO] ATM changed from OFF to ON unexpectedly")

    print()
    return passed


async def restore_preset(miner):
    """Restore the preset saved before the last --switch."""
    state = load_state()
    if not state:
        print("No saved state found. Run --switch first.")
        return False

    original = state["active_preset"]
    print(f"Restoring to: {original}")
    return await switch_preset(miner, original)


async def main():
    args = sys.argv[1:]

    print(f"Connecting to miner at {MINER_IP}...")
    miner = await get_miner(MINER_IP)

    if miner is None:
        print(f"Could not connect to miner at {MINER_IP}")
        print("Check: is the miner online? Can this container reach it?")
        sys.exit(1)

    print(f"Connected: {type(miner).__name__}")

    if len(args) == 0:
        # Read-only mode
        await show_state(miner)
        print("Usage:")
        print(f"  python {sys.argv[0]}                # Show state (read-only)")
        print(f"  python {sys.argv[0]} --switch 190   # Switch preset (fuzzy match)")
        print(f"  python {sys.argv[0]} --restore      # Restore original preset")

    elif args[0] == "--switch" and len(args) >= 2:
        target = args[1]
        ok = await switch_preset(miner, target)
        sys.exit(0 if ok else 1)

    elif args[0] == "--restore":
        ok = await restore_preset(miner)
        sys.exit(0 if ok else 1)

    else:
        print(f"Unknown args: {args}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
