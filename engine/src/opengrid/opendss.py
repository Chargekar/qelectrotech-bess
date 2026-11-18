"""Generate deterministic OpenDSS models; optional native solver integration.

IMPORTANT: The models are simplified steady-state equivalents. They are not
protection, transient, arc-flash, islanding, or code-compliance assessments.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json

from .schema import Project, ensure_simulation_ready

SCENARIOS = ("baseline", "peak-load", "max-solar", "bess-charging", "bess-discharging")


def render_dss(project: Project, scenario: str = "baseline") -> str:
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario {scenario}; use one of {SCENARIOS}")
    ensure_simulation_ready(project)
    buses = {bus.id: bus for bus in project.buses}
    src = project.source
    base_kv = buses[src.bus].voltage_ll_kv
    lines = [
        f"! OpenGrid Engineer | {project.id} | scenario={scenario}",
        "! Synthetic example is NOT a permit-ready electrical design.",
        "Clear",
        f"New Circuit.{project.id} Bus1={src.bus}.1.2.3 Phases=3 BasekV={base_kv:g} PU={src.voltage_pu:g}",
        "Set Frequency=60",
        f"Set VoltageBases=[{base_kv:g}]",
    ]
    for feeder in sorted(project.feeders, key=lambda x: x.id):
        # A three-phase, constant-parameter line model; zero-sequence data supplied explicitly.
        lines.append(
            f"New Line.{feeder.id} Bus1={feeder.from_bus}.1.2.3 "
            f"Bus2={feeder.to_bus}.1.2.3 Phases=3 Length={feeder.length_km:g} "
            f"Units=km R1={feeder.r1_ohm_per_km:g} X1={feeder.x1_ohm_per_km:g} "
            f"R0={feeder.r0_ohm_per_km:g} X0={feeder.x0_ohm_per_km:g} "
            f"C1=0 C0=0 NormAmps={feeder.ampacity_a:g}"
        )
    load_multiplier = 1.2 if scenario == "peak-load" else 1.0
    for load in sorted(project.loads, key=lambda x: x.id):
        bus_kv = buses[load.bus].voltage_ll_kv
        lines.append(
            f"New Load.{load.id} Bus1={load.bus}.1.2.3 Phases=3 Conn=Wye "
            f"kV={bus_kv:g} kW={load.p_kw * load_multiplier:g} "
            f"kvar={load.q_kvar * load_multiplier:g} Model=1"
        )
    for pv in sorted(project.pv, key=lambda x: x.id):
        enabled = "Yes" if scenario == "max-solar" else "No"
        lines.append(
            f"New PVSystem.{pv.id} Bus1={pv.bus}.1.2.3 Phases=3 Conn=Wye "
            f"kV={buses[pv.bus].voltage_ll_kv:g} kVA={pv.inverter_kva:g} "
            f"Pmpp={pv.ac_kw:g} Irradiance=1 Enabled={enabled}"
        )
    for wind in sorted(project.wind, key=lambda x: x.id):
        # Fixed generator injection is a placeholder until windpowerlib profiles are added.
        lines.append(
            f"New Generator.{wind.id} Bus1={wind.bus}.1.2.3 Phases=3 "
            f"kV={buses[wind.bus].voltage_ll_kv:g} kW={wind.rated_kw:g} "
            f"PF=1 Model=1 Enabled=No"
        )
    for battery in sorted(project.batteries, key=lambda x: x.id):
        state = {"bess-charging": "CHARGING", "bess-discharging": "DISCHARGING"}.get(
            scenario, "IDLING"
        )
        # Simplified PCS model. kW sign handled by state, not kW sign.
        lines.append(
            f"New Storage.{battery.id} Bus1={battery.bus}.1.2.3 Phases=3 "
            f"Conn=Wye kV={buses[battery.bus].voltage_ll_kv:g} "
            f"kWrated={battery.pcs_kw:g} kWhrated={battery.energy_kwh:g} "
            f"%stored={battery.initial_soc_pct:g} kW={battery.pcs_kw:g} "
            f"State={state} %EffCharge={battery.roundtrip_efficiency_pct ** 0.5 * 10:g} "
            f"%EffDischarge={battery.roundtrip_efficiency_pct ** 0.5 * 10:g}"
        )
    lines.extend(["CalcVoltageBases", "Set Mode=Snap", "Solve", ""])
    return "\n".join(lines)


def compile_dss(project: Project, out: Path, scenario: str = "baseline") -> dict:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    content = render_dss(project, scenario)
    out.write_text(content, encoding="utf-8")
    return {"model": str(out), "sha256": sha256(content.encode()).hexdigest(),
            "scenario": scenario, "model_id": project.id, "result": "compiled_only"}


def simulate(project: Project, scenario: str = "baseline") -> dict:
    """Solve in a new isolated DSS engine context where dependency is available.

    Raises actionable error if the optional DSS-Python package is missing.
    """
    script = render_dss(project, scenario)
    try:
        from dss import DSS
    except ImportError as exc:
        raise RuntimeError('OpenDSS backend unavailable; install pip extra: pip install ".[sim]"') from exc

    engine = DSS.NewContext()
    # DSS interprets a command block as successive commands.
    engine(script)
    circuit = engine.ActiveCircuit
    if not circuit.Solution.Converged:
        raise RuntimeError(f"OpenDSS power flow did not converge: {scenario}")
    voltages = {}
    for bus in sorted(project.buses, key=lambda x: x.id):
        circuit.SetActiveBus(bus.id)
        mag_angles = list(circuit.ActiveBus.puVmagAngle)
        mags = [float(x) for x in mag_angles[::2] if float(x) > 0]
        if not mags:
            raise RuntimeError(f"No phase voltages returned for bus {bus.id}")
        voltages[bus.id] = {"min_pu": min(mags), "max_pu": max(mags)}
    currents = {}
    for feeder in sorted(project.feeders, key=lambda x: x.id):
        circuit.SetActiveElement(f"Line.{feeder.id}")
        amps = list(circuit.ActiveCktElement.CurrentsMagAng)[::2]
        max_amps = max(float(x) for x in amps)
        currents[feeder.id] = {
            "max_amps": max_amps,
            "ampacity_amps": feeder.ampacity_a,
            "loading_pct": round(max_amps / feeder.ampacity_a * 100, 2),
        }
    violations = [
        {"bus": key, "type": "voltage_outside_study_limits", "values": value}
        for key, value in voltages.items()
        if value["min_pu"] < 0.95 or value["max_pu"] > 1.05
    ]
    violations.extend(
        {"feeder": key, "type": "ampacity_exceeded", "values": value}
        for key, value in currents.items() if value["loading_pct"] > 100
    )
    return {"project": project.id, "scenario": scenario, "converged": True,
            "study_limits": {"voltage_min_pu": .95, "voltage_max_pu": 1.05},
            "buses": voltages, "feeders": currents, "violations": violations,
            "model_sha256": sha256(script.encode()).hexdigest(),
            "limitations": ["Steady-state balanced three-phase model only",
                            "Not an NEC/CEC, arc-flash, protection coordination, or safety approval"]}
