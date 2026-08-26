from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class FieldMapping:
    respondent_id: str | None
    operating_system: str | None
    country: str | None
    age: str | None
    employment: str | None
    developer_type: str | None
    professional_experience: str | None


FIELD_CANDIDATES = {
    "respondent_id": ("ResponseId", "Respondent", "RespondentID", "ResponseID"),
    "operating_system": (
        "OpSysProfessional use",
        "OpSysPersonal use",
        "OpSys",
        "NEWOpSys",
        "OperatingSystem",
        "Operating System",
    ),
    "country": ("Country", "CountryLive", "CountryRemote"),
    "age": ("Age",),
    "employment": ("Employment", "EmploymentStatus"),
    "developer_type": ("DevType", "DeveloperType"),
    "professional_experience": ("YearsCodePro", "WorkExp", "YearsCode"),
}


def _compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def _find_exact(columns: list[str], candidates: tuple[str, ...]) -> str | None:
    by_compact = {_compact(column): column for column in columns}
    for candidate in candidates:
        found = by_compact.get(_compact(candidate))
        if found:
            return found
    return None


def _find_operating_system_fallback(columns: list[str]) -> str | None:
    scored: list[tuple[int, str]] = []
    for column in columns:
        compact = _compact(column)
        lower = column.casefold()
        if "opsys" in compact or "operatingsystem" in compact:
            score = 10
            if "professional" in lower:
                score += 5
            if "personal" in lower:
                score += 2
            scored.append((score, column))
    if not scored:
        return None
    scored.sort(key=lambda item: (-item[0], item[1]))
    return scored[0][1]


def infer_mapping(columns: list[str]) -> FieldMapping:
    values: dict[str, str | None] = {}
    for field, candidates in FIELD_CANDIDATES.items():
        values[field] = _find_exact(columns, candidates)
    if values["operating_system"] is None:
        values["operating_system"] = _find_operating_system_fallback(columns)
    return FieldMapping(**values)


def possible_fields(columns: list[str]) -> dict[str, list[str]]:
    keywords = {
        "sistema operacional": ("opsys", "operatingsystem"),
        "pais": ("country", "nation"),
        "profissao": ("devtype", "developer", "profession", "mainbranch"),
        "idade": ("age",),
        "experiencia": ("yearscode", "workexp", "experience"),
        "emprego": ("employment", "employmentaddl", "employ"),
    }
    result: dict[str, list[str]] = {}
    for label, words in keywords.items():
        matches = []
        for column in columns:
            compact = _compact(column)
            lower = column.casefold()
            if label == "idade":
                if compact == "age":
                    matches.append(column)
                continue
            if any(word in compact or word in lower for word in words):
                matches.append(column)
        result[label] = matches
    return result
