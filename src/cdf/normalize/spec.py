# src/cdf/normalize/spec.py
from __future__ import annotations

import copy
import os
import re
import warnings
from collections.abc import Mapping
from pathlib import Path
from typing import Any

try:
    from rdflib import Graph
    from rdflib.namespace import OWL, RDF, SKOS
except Exception:  # pragma: no cover - rdflib is a project dependency, keep fallback for safety
    Graph = None
    OWL = RDF = SKOS = None

"""
Single source of truth for CDF canonical columns.

Each entry defines:
- unit: pint-compatible canonical unit
- label_template: preferred label, with "{unit}" placeholder
- required: bool (True for core required, False otherwise)
- mr_name: machine-readable snake name (official)
- iri: canonical IRI (official)
- synonyms: list[str] of base-name slugs mapping vendor headers to this quantity

Notes:
- Slugs are lowercase with non-alnum -> "-" (same slugger as normalizer).
- Synonyms are unit-agnostic ("voltage" not "voltage#v"); the normalizer parses units.
"""

_BDA_IRI = "https://w3id.org/battery-data-alliance/ontology/battery-data-format#"
_CDF_IRI = "https://w3id.org/catalysis-data-format/ontology/catalysis-data-format#"

_STATIC_COLUMNS: dict[str, dict] = {
    # -------------------------
    # Required quantities
    # -------------------------
    "test_time_second": {
        "unit": "s",
        "label_template": "Test Time / {unit}",
        "required": True,
        "mr_name": "test_time_second",
        "iri": f"{_BDA_IRI}test_time_second",
        "synonyms": ["test-time", "time", "program-duration", "elapsed-time"],
    },
    "voltage_volt": {
        "unit": "V",
        "label_template": "Voltage / {unit}",
        "required": True,
        "mr_name": "voltage_volt",
        "iri": f"{_BDA_IRI}voltage_volt",
        "synonyms": ["voltage", "u", "cell-voltage"],
    },
    "current_ampere": {
        "unit": "A",
        "label_template": "Current / {unit}",
        "required": True,
        "mr_name": "current_ampere",
        "iri": f"{_BDA_IRI}current_ampere",
        "synonyms": ["current", "i", "cell-current"],
    },

    # -------------------------
    # Recommended quantities
    # -------------------------
    "unix_time_second": {
        "unit": "s",
        "label_template": "Unix Time / {unit}",
        "required": False,
        "mr_name": "unix_time_second",
        "iri": f"{_BDA_IRI}unix_time_second",
        "synonyms": ["unix-time", "timestamp", "date-time", "datetime"],
    },
    "charge_coulomb": {
        "unit": "C",
        # label hardcoded: pint uses "C" (coulombs), display convention uses "As"
        "label_template": "Charge / As",
        "required": False,
        "mr_name": "charge_coulomb",
        "iri": f"{_CDF_IRI}charge_coulomb",
        "synonyms": ["charge", "q", "electric-charge"],
    },
    "temperature_celsius": {
        "unit": "degC",
        # label hardcoded: pint uses "degC", display convention uses "°C"
        "label_template": "Temperature / °C",
        "required": False,
        "mr_name": "temperature_celsius",
        "iri": f"{_CDF_IRI}temperature_celsius",
        "synonyms": ["temperature", "temp", "t"],
    },
    "electrolyte_ph": {
        "unit": "1",
        "label_template": "pH / {unit}",
        "required": False,
        "mr_name": "electrolyte_ph",
        "iri": f"{_CDF_IRI}electrolyte_ph",
        "synonyms": ["ph", "electrolyte-ph", "solution-ph"],
    },
    "inlet_flow_rate_ml_min": {
        "unit": "mL/min",
        "label_template": "Inlet Flow Rate / {unit}",
        "required": False,
        "mr_name": "inlet_flow_rate_ml_min",
        "iri": f"{_CDF_IRI}inlet_flow_rate_ml_min",
        "synonyms": ["inlet-flow-rate", "inlet-flow", "flow-in"],
    },
    "outlet_flow_rate_ml_min": {
        "unit": "mL/min",
        # label hardcoded: display convention uses "smL/min" (standard mL/min)
        "label_template": "Outlet Flow Rate / smL/min",
        "required": False,
        "mr_name": "outlet_flow_rate_ml_min",
        "iri": f"{_CDF_IRI}outlet_flow_rate_ml_min",
        "synonyms": ["outlet-flow-rate", "outlet-flow", "flow-out"],
    },
}

# Per-product columns: Faradaic Efficiency, Outlet Mole Fraction, Outlet Molar Flow
_PRODUCTS = [
    "1-propanol", "Acetaldehyde", "Acetone", "Ammonia",
    "C2H4", "C2H6", "C3H6", "C3H8", "CH4", "CO", "CO2",
    "EtOH", "H2", "H2O", "MeOH", "N2", "N2O", "O2", "Propionaldehyde",
]
for _p in _PRODUCTS:
    _pk = re.sub(r"[^a-z0-9]+", "_", _p.lower()).strip("_")
    _ps = re.sub(r"[^a-z0-9]+", "-", _p.lower()).strip("-")
    _STATIC_COLUMNS[f"faradaic_efficiency_{_pk}"] = {
        "unit": "1",
        "label_template": f"Faradaic Efficiency {_p} / {{unit}}",
        "required": False,
        "mr_name": f"faradaic_efficiency_{_pk}",
        "iri": f"{_CDF_IRI}faradaic_efficiency_{_pk}",
        "synonyms": [f"faradaic-efficiency-{_ps}", f"fe-{_ps}"],
    }
    _STATIC_COLUMNS[f"outlet_mole_fraction_{_pk}_percent"] = {
        "unit": "%",
        "label_template": f"Outlet Mole Fraction {_p} / {{unit}}",
        "required": False,
        "mr_name": f"outlet_mole_fraction_{_pk}_percent",
        "iri": f"{_CDF_IRI}outlet_mole_fraction_{_pk}_percent",
        "synonyms": [f"outlet-mole-fraction-{_ps}", f"mole-fraction-{_ps}", f"mf-{_ps}"],
    }
    _STATIC_COLUMNS[f"outlet_molar_flow_{_pk}_mol_s"] = {
        "unit": "mol/s",
        "label_template": f"Outlet Molar Flow {_p} / {{unit}}",
        "required": False,
        "mr_name": f"outlet_molar_flow_{_pk}_mol_s",
        "iri": f"{_CDF_IRI}outlet_molar_flow_{_pk}_mol_s",
        "synonyms": [f"outlet-molar-flow-{_ps}", f"molar-flow-{_ps}", f"flow-{_ps}"],
    }
del _p, _pk, _ps

# --------- Ontology-backed runtime columns ----------

_SLUG = re.compile(r"[^a-z0-9]+")
_REQUIRED_DEFAULT = {"test_time_second", "voltage_volt", "current_ampere"}
_UNIT_ALIAS = {
    "celsius": "degC",
    "degree celsius": "degC",
    "degree_celsius": "degC",
    "deg c": "degC",
    "℃": "degC",
}
_CACHED_SIGNATURE: tuple[str, float | None] | None = None
_CACHED_COLUMNS: dict[str, dict[str, Any]] | None = None
_WARNED_ONTOLOGY_SOURCES: set[str] = set()


def _slugify(text: str) -> str:
    return _SLUG.sub("-", text.lower()).strip("-")


def _normalize_unit(unit: str) -> str:
    key = unit.strip()
    if not key:
        return key
    return _UNIT_ALIAS.get(key.lower(), key)


def _split_pref_label(label: str) -> tuple[str, str] | None:
    text = str(label).strip()
    if " / " not in text:
        return None
    base, unit = text.split(" / ", 1)
    base = base.strip()
    unit = _normalize_unit(unit.strip())
    if not base or not unit:
        return None
    return base, unit


def _pick_labels(graph: Graph, subject, predicate) -> list[str]:
    out: list[str] = []
    for lit in graph.objects(subject, predicate):
        try:
            text = str(lit)
        except Exception:
            continue
        if getattr(lit, "language", None) not in (None, "en"):
            continue
        if text:
            out.append(text)
    return out


def _ontology_source() -> str:
    return (os.getenv("CDF_ONTOLOGY_PATH") or os.getenv("CDF_ONTOLOGY") or "").strip()


def _source_signature(source: str) -> tuple[str, float | None]:
    if not source:
        return "", None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        p = Path(source).expanduser()
    if p.exists():
        return str(p.resolve()), p.stat().st_mtime
    return source, None


def _warn_ontology_once(source: str, message: str) -> None:
    if source in _WARNED_ONTOLOGY_SOURCES:
        return
    _WARNED_ONTOLOGY_SOURCES.add(source)
    warnings.warn(message, stacklevel=2)


def _build_from_ontology(source: str) -> dict[str, dict[str, Any]]:
    if not source or Graph is None:
        return {}
    try:
        g = Graph()
        g.parse(source)
    except Exception as exc:
        _warn_ontology_once(source, f"Failed to load ontology spec from '{source}': {exc}")
        return {}

    out: dict[str, dict[str, Any]] = {}
    for subject in g.subjects(RDF.type, OWL.Class):
        iri = str(subject)
        if "#" not in iri:
            continue
        mr_name = iri.rsplit("#", 1)[-1]
        pref_labels = _pick_labels(g, subject, SKOS.prefLabel)
        if not pref_labels:
            continue
        deprecated = False
        for lit in g.objects(subject, OWL.deprecated):
            try:
                deprecated = str(lit).lower() == "true"
            except Exception:
                continue
        parsed = _split_pref_label(pref_labels[0])
        if not parsed:
            continue
        base, unit = parsed
        notations = _pick_labels(g, subject, SKOS.notation)
        notation = ""
        for n in notations:
            s = str(n).strip()
            if s:
                notation = s
                break
        if not notation:
            notation = mr_name

        syns: set[str] = {_slugify(base), _slugify(mr_name)}
        for alias in _pick_labels(g, subject, SKOS.altLabel) + _pick_labels(g, subject, SKOS.notation):
            alias_text = alias.split(" / ", 1)[0].strip()
            slug = _slugify(alias_text.replace("/", " ").replace("#", " ").replace("_", " "))
            if slug:
                syns.add(slug)

        out[mr_name] = {
            "unit": unit,
            "label_template": f"{base} / {{unit}}",
            "required": mr_name in _REQUIRED_DEFAULT,
            "mr_name": mr_name,
            "notation": notation,
            "iri": iri,
            "deprecated": deprecated,
            "synonyms": sorted(s for s in syns if s),
        }
    return out


def _merge_columns(
    base: dict[str, dict[str, Any]],
    ontology: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    merged = copy.deepcopy(base)
    for _quantity, current in merged.items():
        current.setdefault("deprecated", False)
    for quantity, item in ontology.items():
        if quantity in merged:
            current = merged[quantity]
            incoming_deprecated = bool(item.get("deprecated"))
            # Deprecated ontology entries are read-compat only: do not let them
            # redefine canonical labels/units for existing quantities.
            if not incoming_deprecated:
                current["unit"] = item.get("unit", current.get("unit"))
                current["label_template"] = item.get("label_template", current.get("label_template"))
                current["iri"] = item.get("iri", current.get("iri"))
            current["mr_name"] = quantity
            current["notation"] = item.get("notation", current.get("notation", quantity))
            current["deprecated"] = bool(current.get("deprecated", False)) or incoming_deprecated
            current["required"] = bool(current.get("required", False))
            syns = set(current.get("synonyms", [])) | set(item.get("synonyms", []))
            current["synonyms"] = sorted(s for s in syns if s)
            continue
        item = dict(item)
        item.setdefault("deprecated", False)
        merged[quantity] = item

    ordered: dict[str, dict[str, Any]] = {}
    for quantity in base:
        ordered[quantity] = merged[quantity]
    for quantity in sorted(q for q in merged if q not in ordered):
        ordered[quantity] = merged[quantity]
    return ordered


def _build_columns() -> dict[str, dict[str, Any]]:
    base = copy.deepcopy(_STATIC_COLUMNS)
    source = _ontology_source()
    if not source:
        return base
    ontology = _build_from_ontology(source)
    if not ontology:
        return base
    return _merge_columns(base, ontology)


def _current_columns(*, refresh: bool = False) -> dict[str, dict[str, Any]]:
    global _CACHED_COLUMNS, _CACHED_SIGNATURE
    signature = _source_signature(_ontology_source())
    if refresh or _CACHED_COLUMNS is None or signature != _CACHED_SIGNATURE:
        _CACHED_COLUMNS = _build_columns()
        _CACHED_SIGNATURE = signature
    return _CACHED_COLUMNS


def refresh_columns() -> None:
    _current_columns(refresh=True)


class _ColumnsProxy(Mapping[str, dict[str, Any]]):
    def __getitem__(self, key: str) -> dict[str, Any]:
        return _current_columns()[key]

    def __iter__(self):
        return iter(_current_columns())

    def __len__(self) -> int:
        return len(_current_columns())


COLUMNS: Mapping[str, dict[str, Any]] = _ColumnsProxy()


# --------- Helpers consumed by the normalizer ----------

def _label_for(quantity: str) -> str:
    col = _current_columns()[quantity]
    return col["label_template"].format(unit=col["unit"])


def notation_for(quantity: str) -> str:
    col = _current_columns()[quantity]
    notation = str(col.get("notation") or col.get("mr_name") or quantity).strip()
    return notation or quantity


def unit_for(quantity: str) -> str:
    return _current_columns()[quantity]["unit"]


def required_labels() -> tuple[str, ...]:
    return tuple(
        _label_for(q) for q, s in _current_columns().items() if s["required"] and not bool(s.get("deprecated"))
    )


def optional_labels() -> tuple[str, ...]:
    return tuple(
        _label_for(q) for q, s in _current_columns().items() if not s["required"] and not bool(s.get("deprecated"))
    )


def base_synonym_index() -> dict[str, str]:
    """
    Build a mapping from base-name slug to quantity key (machine-readable name).
    """
    idx: dict[str, str] = {}
    for q, s in _current_columns().items():
        if bool(s.get("deprecated")):
            continue
        left = str(s.get("label_template", "")).split(" / ", 1)[0]
        left_slug = _slugify(left)
        if left_slug:
            idx.setdefault(left_slug, q)
        notation_slug = _slugify(notation_for(q))
        if notation_slug:
            idx.setdefault(notation_slug, q)
        for base in s.get("synonyms", []):
            slug = _slugify(str(base))
            if slug:
                idx.setdefault(slug, q)
    return idx

