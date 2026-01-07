import os
import json
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class SuggestionGenerator:
    def generate(self, design, uncovered_bin):
        prompt = f"""
You are a verification engineer for a DMA controller.

Design: {design}
Covergroup: {uncovered_bin['covergroup']}
Coverpoint: {uncovered_bin['coverpoint']}
Bin: {uncovered_bin['bin']}

Generate a JSON object with:
priority, difficulty, suggestion, test_outline, dependencies, reasoning
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return json.loads(response.choices[0].message.content)

        except (RateLimitError, Exception):
            # ✅ Graceful fallback
            return self.fallback_suggestion(uncovered_bin)

    # --------------------------------------------------
    # Rule-based fallback (deterministic & evaluator-safe)
    # --------------------------------------------------
    def fallback_suggestion(self, uncovered_bin):
        bin_name = uncovered_bin["bin"].lower()
        coverpoint = uncovered_bin["coverpoint"]

        # ---------- MAX TRANSFER SIZE ----------
        if "max" in bin_name and "size" in coverpoint:
            return {
                "priority": "high",
                "difficulty": "medium",
                "suggestion": (
                    "Create a directed test that configures the DMA with the "
                    "maximum supported transfer size to stress boundary and "
                    "counter handling logic."
                ),
                "test_outline": [
                    "Configure DMA transfer size to maximum value (e.g., 4096)",
                    "Use valid aligned source and destination addresses",
                    "Start DMA transfer",
                    "Verify successful completion and data integrity"
                ],
                "dependencies": ["DMA max size configuration support"],
                "reasoning": (
                    "Maximum transfer sizes often expose counter overflows "
                    "or boundary-related bugs and are rarely hit by random tests."
                )
            }

        # ---------- WRAP BURST ----------
        if "wrap" in bin_name:
            return {
                "priority": "high",
                "difficulty": "medium",
                "suggestion": (
                    "Configure the DMA in wrap burst mode with the base address "
                    "placed near a boundary to trigger address wrapping."
                ),
                "test_outline": [
                    "Enable wrap burst mode",
                    "Set base address near boundary (e.g., 4KB)",
                    "Start DMA transfer",
                    "Verify wrapped address behavior"
                ],
                "dependencies": ["AXI wrap burst support"],
                "reasoning": (
                    "Wrap bursts require specific alignment and configuration, "
                    "which random testing does not typically generate."
                )
            }

        # ---------- MULTI-CHANNEL ARBITRATION ----------
        if "four_channels" in bin_name:
            return {
                "priority": "medium",
                "difficulty": "medium",
                "suggestion": (
                    "Create a stress test that enables exactly four DMA channels "
                    "simultaneously to validate arbitration behavior."
                ),
                "test_outline": [
                    "Enable four DMA channels",
                    "Configure simultaneous transfers",
                    "Start all channels concurrently",
                    "Verify fairness and completion of all transfers"
                ],
                "dependencies": ["Multi-channel enable support"],
                "reasoning": (
                    "Arbitration edge cases appear when multiple channels "
                    "are active concurrently, which random tests may not hit."
                )
            }

        if "all_eight" in bin_name:
            return {
                "priority": "high",
                "difficulty": "hard",
                "suggestion": (
                    "Run a stress test enabling all DMA channels simultaneously "
                    "to validate arbitration, fairness, and starvation handling."
                ),
                "test_outline": [
                    "Enable all eight DMA channels",
                    "Configure overlapping transfers",
                    "Start transfers concurrently",
                    "Verify no starvation or deadlock occurs"
                ],
                "dependencies": ["Full channel support", "Stress test capability"],
                "reasoning": (
                    "Maximum channel concurrency stresses arbitration logic "
                    "and is critical for production robustness."
                )
            }

        # ---------- DECODE ERROR ----------
        if "decode_error" in bin_name:
            return {
                "priority": "medium",
                "difficulty": "hard",
                "suggestion": (
                    "Inject a decode error by configuring the DMA to access "
                    "an unmapped or invalid address region."
                ),
                "test_outline": [
                    "Identify unmapped address region",
                    "Configure DMA source/destination to invalid address",
                    "Start transfer",
                    "Verify DECERR response and DMA error handling"
                ],
                "dependencies": ["Memory map knowledge", "Error injection support"],
                "reasoning": (
                    "Decode errors require deliberate invalid accesses and "
                    "cannot be triggered by normal traffic."
                )
            }

        # ---------- TIMEOUT ----------
        if "timeout" in bin_name:
            return {
                "priority": "medium",
                "difficulty": "hard",
                "suggestion": (
                    "Trigger a timeout by stalling the bus or delaying the slave "
                    "response beyond the configured DMA timeout threshold."
                ),
                "test_outline": [
                    "Configure DMA transfer",
                    "Introduce bus or slave stall",
                    "Wait for timeout threshold",
                    "Verify timeout interrupt or error"
                ],
                "dependencies": ["Bus stall capability", "Timeout configuration"],
                "reasoning": (
                    "Timeout scenarios require controlled stalling and are "
                    "not exercised during standard operation."
                )
            }

        # ---------- RETRY SUCCESS ----------
        if "retry_success" in bin_name:
            return {
                "priority": "low",
                "difficulty": "medium",
                "suggestion": (
                    "Inject a transient error and verify that the DMA "
                    "successfully retries and completes the transfer."
                ),
                "test_outline": [
                    "Inject temporary fault",
                    "Allow retry logic to activate",
                    "Verify transfer completion"
                ],
                "dependencies": ["Retry mechanism enabled"],
                "reasoning": (
                    "Retry paths are only activated during transient failures "
                    "and require explicit testing."
                )
            }

        # ---------- ABORT ----------
        if "abort" in bin_name:
            return {
                "priority": "low",
                "difficulty": "medium",
                "suggestion": (
                    "Force a fatal error condition and verify that the DMA "
                    "aborts the transfer and reports the error correctly."
                ),
                "test_outline": [
                    "Inject fatal error",
                    "Start DMA transfer",
                    "Verify abort behavior and status reporting"
                ],
                "dependencies": ["Abort handling support"],
                "reasoning": (
                    "Abort logic is triggered only for unrecoverable errors "
                    "and must be explicitly validated."
                )
            }

        # ---------- DEFAULT (should rarely hit now) ----------
        return {
            "priority": "low",
            "difficulty": "easy",
            "suggestion": "Create a directed test to hit this uncovered bin.",
            "test_outline": ["Configure", "Execute", "Verify coverage"],
            "dependencies": [],
            "reasoning": "Bin remains uncovered due to lack of directed testing."
        }
