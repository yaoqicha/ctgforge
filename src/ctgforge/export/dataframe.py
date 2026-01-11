from collections.abc import Sequence

import pandas as pd

from ..models.core import TrialCore


def to_dataframe(trials: Sequence[TrialCore]) -> pd.DataFrame:
    rows = []
    for t in trials:
        row = t.model_dump()

        # Flatten lead_sponsor and collaborators
        row["lead_sponsor"] = t.lead_sponsor.name if t.lead_sponsor else None
        row["collaborators"] = (
            "; ".join(c.name for c in t.collaborators) if t.collaborators else None
        )

        # Flatten interventions and conditions into semicolon-separated strings
        row["conditions"] = "; ".join(c.name for c in t.conditions)
        row["arm_groups"] = "; ".join(ag.label for ag in t.arm_groups)
        row["interventions"] = "; ".join(i.name for i in t.interventions)

        # Flatten date structs to just date strings
        row["start_date"] = t.start_date.date if t.start_date else None
        row["completion_date"] = t.completion_date.date if t.completion_date else None
        row["primary_completion_date"] = (
            t.primary_completion_date.date if t.primary_completion_date else None
        )
        rows.append(row)
    return pd.DataFrame(rows)
