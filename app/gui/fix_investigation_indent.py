from pathlib import Path

path = Path("app/gui/investigation.py")
lines = path.read_text(encoding="utf-8").splitlines()

start = None
end = None

for i, line in enumerate(lines):
    if line.strip() == "# SCROLLABLE PAGE":
        start = i
    elif start is not None and line.startswith("    def start_review"):
        end = i
        break

if start is None or end is None:
    raise RuntimeError("Could not find the GUI block to fix.")

for i in range(start, end):
    lines[i] = lines[i][4:] if lines[i].startswith("    ")
else lines[i]

path.write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)

print("Investigation GUI indentation fixed.")