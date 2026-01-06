class CoverageParser:
    def __init__(self, report_text: str):
        self.text = report_text.replace("\r", "")

    def parse_design(self):
        for line in self.text.split("\n"):
            if line.strip().startswith("Design:"):
                return line.split(":", 1)[1].strip()
        return None

    def parse_overall_coverage(self):
        for line in self.text.split("\n"):
            if "Overall Coverage" in line:
                return float(line.split(":")[1].replace("%", "").strip())
        return None

    def parse_uncovered_bins(self):
        uncovered = []
        current_covergroup = None
        current_coverpoint = None
        inside_cross = False

        for raw_line in self.text.split("\n"):
            line = raw_line.strip()

            if line.startswith("Cross Coverage"):
                inside_cross = True
                continue

            if line.startswith("Covergroup"):
                inside_cross = False
                current_covergroup = line.split(":", 1)[1].strip()

            elif line.startswith("Coverpoint"):
                current_coverpoint = line.split(":", 1)[1].strip()

            elif "UNCOVERED" in line and not inside_cross and not line.startswith("<"):
                uncovered.append({
                    "covergroup": current_covergroup,
                    "coverpoint": current_coverpoint,
                    "bin": line.split("hits")[0].strip()
                })

        return uncovered

    def parse_cross_coverage(self):
        crosses = []
        current_cross = None

        for raw_line in self.text.split("\n"):
            line = raw_line.strip()

            if line.startswith("Cross Coverage"):
                current_cross = {
                    "name": line.split(":", 1)[1].strip(),
                    "uncovered": []
                }
                crosses.append(current_cross)

            elif current_cross and line.startswith("<") and "UNCOVERED" in line:
                current_cross["uncovered"].append(
                    line.split("hits")[0].strip()
                )

        return crosses

    def parse_all(self):
        return {
            "design": self.parse_design(),
            "overall_coverage": self.parse_overall_coverage(),
            "uncovered_bins": self.parse_uncovered_bins(),
            "cross_coverage": self.parse_cross_coverage()
        }
