#!/usr/bin/env python3
"""
Part 9 starter CLI.

WHAT'S NEW IN PART 9
Our very first new module! And... we are finally again adding new functionality.
"""

from typing import List
import time
from .constants import BANNER, HELP
from .models import SearchResult, LineMatch, Sonnet
from .file_utilities import Configuration, load_config, load_sonnets

def print_results(
    query: str,
    results: List[SearchResult],
    highlight: bool,
    highlight_mode: str,
    query_time_ms: float | None = None,
) -> None:
    total_docs = len(results)
    matched = [r for r in results if r.matches > 0]

    line = f'{len(matched)} out of {total_docs} sonnets contain "{query}".'
    if query_time_ms is not None:
        line += f" Your query took {query_time_ms:.2f}ms."
    print(line)

    for idx, r in enumerate(matched, start=1):
        r.print(idx, highlight, len(matched), highlight_mode)

# ---------- CLI loop ----------

def main() -> None:
    print(BANNER)
    config = load_config()

    # Load sonnets (from cache or API)
    start = time.perf_counter()
    sonnets = load_sonnets()

    elapsed = (time.perf_counter() - start) * 1000
    print(f"Loading sonnets took: {elapsed:.3f} [ms]")

    print(f"Loaded {len(sonnets)} sonnets.")

    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not raw:
            continue

        # commands
        if raw.startswith(":"):
            if raw == ":quit":
                print("Bye.")
                break

            if raw == ":help":
                print(HELP)
                continue

            if raw.startswith(":highlight"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].lower() in ("on", "off"):
                    config.highlight = parts[1].lower() == "on"
                    print("Highlighting", "ON" if config.highlight else "OFF")
                    config.save()
                else:
                    print("Usage: :highlight on|off")
                continue

            if raw.startswith(":search-mode"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].upper() in ("AND", "OR"):
                    config.search_mode = parts[1].upper()
                    print("Search mode set to", config.search_mode)
                    config.save()
                else:
                    print("Usage: :search-mode AND|OR")
                continue

            if raw.startswith(":hl-mode"):
                parts = raw.split()
                if len(parts) == 2 and parts[1].upper() in ("DEFAULT", "GREEN"):
                    config.highlight_mode = parts[1].upper()
                    print("Highlight mode set to", config.highlight_mode)
                    config.save()
                else:
                    print("Usage: :hl-mode DEFAULT|GREEN")
                continue

            print("Unknown command. Type :help for commands.")
            continue

        # ---------- Query evaluation ----------
        words = raw.split()
        if not words:
            continue

        start = time.perf_counter()

        # query
        combined_results = []

        words = raw.split()

        for word in words:
            # Searching for the word in all sonnets
            # ToDo 0:You will need to adapt the call to search_sonnet
            results = [s.search_for(word) for s in sonnets]

            if not combined_results:
                # No results yet. We store the first list of results in combined_results
                combined_results = results
            else:
                # We have an additional result, we have to merge the two results: loop all sonnets
                for i in range(len(combined_results)):
                    # Checking each sonnet individually
                    combined_result = combined_results[i]
                    result = results[i]

                    if config.search_mode == "AND":
                        if combined_result.matches > 0 and result.matches > 0:
                            # Only if we have matches in both results, we consider the sonnet (logical AND!)
                            combined_results[i] = combined_result.combine_with(result)
                        else:
                            # Not in both. No match!
                            combined_result.matches = 0
                    elif config.search_mode == "OR":
                        combined_results[i] = combined_result.combine_with(result)

        # Initialize elapsed_ms to contain the number of milliseconds the query evaluation took
        elapsed_ms = (time.perf_counter() - start) * 1000

        # ToDo 2: You will need to pass the new setting, the highlight_mode to print_results and use it there
        print_results(raw, combined_results, config.highlight, config.highlight_mode, elapsed_ms)

if __name__ == "__main__":
    main()
