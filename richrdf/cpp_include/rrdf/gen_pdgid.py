from particle.pdgid import literals as lid
from particle.pdgid import PDGID
from particle import Particle


output_file = "pdgid.h"

lines = [
    "#ifndef _RRDF_PDGID_H_",
    "#define _RRDF_PDGID_H_",
    "// Auto-generated from gen_pdgid.py using particle.pdgid.literals",
    "// Do not edit manually",
    "",
    "namespace rrdf {",
    "namespace PID {",
]

for name in dir(lid):
    if name.startswith("_"):
        continue
    attr = getattr(lid, name)
    if isinstance(attr, PDGID):
        lines.append(f"constexpr int {name} = {int(attr)};    // {Particle.from_pdgid(attr).name}")

lines.append("} // namespace PID")
lines.append("} // namespace rrdf")
lines.append("#endif // _RRDF_PDGID_H_")
lines.append("")
lines.append("")

with open(output_file, "w") as f:
    f.write("\n".join(lines))

print("pdgid.h generated!")
