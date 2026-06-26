"""The 10 monitored rivers and their baseline water-quality statistics.

Baselines are real: pulled from USGS NWIS instantaneous-values
(waterservices.usgs.gov/nwis/iv) for these exact gauges on 2026-06-26.
Where a gauge doesn't report a given parameter (most WA gauges report
temperature and turbidity but not dissolved oxygen or pH), the baseline
falls back to a typical-for-the-region value -- noted per field below --
rather than a real reading, since not every parameter is instrumented
at every site.

`std` is *not* observed variance (a single instantaneous reading can't
give you that) -- it's a deliberately chosen spread used to generate
plausible synthetic time series around the real baseline. Treat the
mean as real, the spread as a simulation knob.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParamBaseline:
    mean: float
    std: float


@dataclass(frozen=True)
class River:
    id: str
    name: str
    usgs_site: str
    lat: float
    lon: float
    temp_c: ParamBaseline
    dissolved_oxygen_mgl: ParamBaseline
    ph: ParamBaseline
    turbidity_fnu: ParamBaseline


# Regional typical-range fallbacks for gauges that don't instrument a
# given parameter (PNW lowland/foothill rivers, summer baseline).
_TYPICAL_DO = ParamBaseline(mean=10.0, std=1.2)
_TYPICAL_PH = ParamBaseline(mean=7.6, std=0.3)

RIVERS: tuple[River, ...] = (
    River(
        "bogachiel", "Bogachiel River", "12042800", 47.8944, -124.3571,
        temp_c=ParamBaseline(15.6, 1.8), dissolved_oxygen_mgl=_TYPICAL_DO,
        ph=_TYPICAL_PH, turbidity_fnu=ParamBaseline(2.8, 1.5),
    ),
    River(
        "calawah", "Calawah River", "12043000", 47.9601, -124.3930,
        temp_c=ParamBaseline(14.0, 1.6), dissolved_oxygen_mgl=_TYPICAL_DO,
        ph=_TYPICAL_PH, turbidity_fnu=ParamBaseline(0.4, 0.4),
    ),
    River(
        "white", "White River", "12098700", 47.1698, -122.0026,
        temp_c=ParamBaseline(9.4, 1.2), dissolved_oxygen_mgl=ParamBaseline(10.6, 0.8),
        ph=ParamBaseline(7.4, 0.2), turbidity_fnu=ParamBaseline(1.4, 1.0),
    ),
    River(
        "duwamish", "Duwamish River", "12113390", 47.4790, -122.2587,
        temp_c=ParamBaseline(17.5, 2.0), dissolved_oxygen_mgl=_TYPICAL_DO,
        ph=_TYPICAL_PH, turbidity_fnu=ParamBaseline(4.8, 2.5),
    ),
    River(
        "cedar", "Cedar River", "12114500", 47.3420, -121.5490,
        temp_c=ParamBaseline(10.7, 1.3), dissolved_oxygen_mgl=_TYPICAL_DO,
        ph=_TYPICAL_PH,
        # USGS reported -999999 (its missing-data sentinel) for turbidity
        # at this gauge on the day baselines were pulled -- regional
        # typical used instead of treating the sentinel as a real value.
        turbidity_fnu=ParamBaseline(1.8, 1.2),
    ),
    River(
        "skykomish", "South Fork Skykomish River", "12131500", 47.7110, -121.3607,
        temp_c=ParamBaseline(12.5, 1.5), dissolved_oxygen_mgl=_TYPICAL_DO,
        ph=_TYPICAL_PH, turbidity_fnu=ParamBaseline(2.4, 1.3),
    ),
    River(
        "tolt", "North Fork Tolt River", "12147500", 47.7123, -121.7887,
        temp_c=ParamBaseline(11.2, 1.1), dissolved_oxygen_mgl=_TYPICAL_DO,
        ph=_TYPICAL_PH, turbidity_fnu=ParamBaseline(0.6, 0.5),
    ),
    River(
        "similkameen", "Similkameen River", "12442500", 48.9846, -119.6184,
        temp_c=ParamBaseline(18.0, 2.2), dissolved_oxygen_mgl=ParamBaseline(8.6, 0.7),
        ph=ParamBaseline(8.0, 0.2), turbidity_fnu=ParamBaseline(5.8, 2.8),
    ),
    River(
        "columbia", "Columbia River (Richland)", "1247351910", 46.3833, -119.2644,
        temp_c=ParamBaseline(9.9, 1.0), dissolved_oxygen_mgl=ParamBaseline(11.6, 0.6),
        ph=ParamBaseline(8.0, 0.15), turbidity_fnu=ParamBaseline(3.9, 1.8),
    ),
    River(
        "yakima", "Yakima River (Kiona)", "12510500", 46.2535, -119.4781,
        temp_c=ParamBaseline(23.2, 2.5), dissolved_oxygen_mgl=ParamBaseline(12.5, 0.9),
        ph=ParamBaseline(9.0, 0.2), turbidity_fnu=ParamBaseline(1.2, 0.9),
    ),
)

RIVERS_BY_ID: dict[str, River] = {r.id: r for r in RIVERS}
