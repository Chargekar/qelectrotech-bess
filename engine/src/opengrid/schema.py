"""Typed canonical topology. No AI model is allowed to bypass these invariants."""
from __future__ import annotations

import re
from enum import Enum
from typing import Literal

import networkx as nx
from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = str
ID_PATTERN = r"^[A-Za-z][A-Za-z0-9_]*$"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class State(str, Enum):
    EXISTING = "existing"
    PROPOSED = "proposed"


class Tagged(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    status: State = State.EXISTING
    evidence: list[str] = Field(default_factory=list)
    # User-reviewed is separate from parser's confidence.
    verified: bool = False


class Bus(Tagged):
    voltage_ll_kv: float = Field(gt=0)
    phases: Literal["ABC"] = "ABC"  # MVP: balanced three-phase feeders only
    label: str = ""


class GridSource(Tagged):
    bus: Identifier
    voltage_pu: float = Field(default=1.0, gt=0, le=1.2)


class Feeder(Tagged):
    from_bus: Identifier
    to_bus: Identifier
    length_km: float = Field(gt=0)
    r1_ohm_per_km: float | None = Field(default=None, ge=0)
    x1_ohm_per_km: float | None = Field(default=None, ge=0)
    r0_ohm_per_km: float | None = Field(default=None, ge=0)
    x0_ohm_per_km: float | None = Field(default=None, ge=0)
    ampacity_a: float | None = Field(default=None, gt=0)


class Load(Tagged):
    bus: Identifier
    p_kw: float = Field(ge=0)
    q_kvar: float = Field(default=0, ge=0)


class PV(Tagged):
    bus: Identifier
    ac_kw: float = Field(gt=0)
    inverter_kva: float = Field(gt=0)

    @model_validator(mode="after")
    def check_kva(self):
        if self.ac_kw > self.inverter_kva:
            raise ValueError("PV AC kW must not exceed inverter kVA")
        return self


class Battery(Tagged):
    bus: Identifier
    energy_kwh: float = Field(gt=0)
    pcs_kw: float = Field(gt=0)
    initial_soc_pct: float = Field(default=50.0, ge=0, le=100)
    roundtrip_efficiency_pct: float = Field(default=90, gt=0, le=100)


class Wind(Tagged):
    bus: Identifier
    rated_kw: float = Field(gt=0)


class Project(StrictModel):
    schema_version: Literal["0.1"] = "0.1"
    id: str = Field(pattern=ID_PATTERN)
    title: str
    description: str = ""
    source: GridSource
    buses: list[Bus] = Field(min_length=1)
    feeders: list[Feeder] = Field(default_factory=list)
    loads: list[Load] = Field(default_factory=list)
    pv: list[PV] = Field(default_factory=list)
    batteries: list[Battery] = Field(default_factory=list)
    wind: list[Wind] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_topology(self):
        objects = [self.source, *self.buses, *self.feeders, *self.loads,
                   *self.pv, *self.batteries, *self.wind]
        ids = [obj.id for obj in objects]
        if len(ids) != len(set(ids)):
            raise ValueError("Equipment IDs must be globally unique")
        bus_map = {bus.id: bus for bus in self.buses}
        if self.source.bus not in bus_map:
            raise ValueError(f"Unknown source bus: {self.source.bus}")
        for obj in [*self.loads, *self.pv, *self.batteries, *self.wind]:
            if obj.bus not in bus_map:
                raise ValueError(f"{obj.id} references unknown bus {obj.bus}")
        graph = nx.Graph()
        graph.add_nodes_from(bus_map)
        for line in self.feeders:
            if line.from_bus not in bus_map or line.to_bus not in bus_map:
                raise ValueError(f"{line.id} references an unknown bus")
            if line.from_bus == line.to_bus:
                raise ValueError(f"{line.id} is a self-connected feeder")
            a = bus_map[line.from_bus].voltage_ll_kv
            b = bus_map[line.to_bus].voltage_ll_kv
            if abs(a-b) > 1e-6:
                raise ValueError(f"{line.id} crosses voltage levels; transformer not yet supported")
            if graph.has_edge(line.from_bus, line.to_bus):
                raise ValueError(f"Duplicate physical feeder between {line.from_bus} and {line.to_bus}")
            graph.add_edge(line.from_bus, line.to_bus)
        if not nx.is_tree(graph):
            raise ValueError("MVP only supports a single connected radial electrical network")
        return self


def ensure_simulation_ready(project: Project) -> None:
    """Block studies on unknown or unverified circuit impedances and ratings."""
    incomplete = []
    for line in project.feeders:
        missing = [name for name in (
            "r1_ohm_per_km", "x1_ohm_per_km", "r0_ohm_per_km",
            "x0_ohm_per_km", "ampacity_a"
        ) if getattr(line, name) is None]
        if missing:
            incomplete.append(f"{line.id}: missing {', '.join(missing)}")
    if incomplete:
        raise ValueError("Simulation blocked by missing electrical properties: " + "; ".join(incomplete))
