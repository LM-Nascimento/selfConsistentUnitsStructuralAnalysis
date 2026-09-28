# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import ifcopenshell

    import bonsai.tool as tool


def assign_scene_units(ifc: type[tool.Ifc], unit: type[tool.Unit]) -> None:
    units = []
    for unit_type in ["LENGTHUNIT", "AREAUNIT", "VOLUMEUNIT", "MASSUNIT", "TIMEUNIT"]:
        if name := unit.get_scene_unit_name(unit_type):
            if unit.is_si_unit(name):
                units.append(
                    ifc.run("unit.add_si_unit", unit_type=unit_type, prefix=unit.get_scene_unit_si_prefix(name))
                )
            else:
                units.append(ifc.run("unit.add_conversion_based_unit", name=name))
    if units:
        ifc.run("unit.assign_unit", units=units)

def assign_derived_scene_units(ifc: type[tool.Ifc], unit: type[tool.Unit]) -> None:
    si_units_args = [("LENGTHUNIT",None),
                          ("AREAUNIT",None),
                          ("VOLUMEUNIT",None),
                          ("MASSUNIT","KILO"), 
                          ("TIMEUNIT",None), 
                          ("PLANEANGLEUNIT",None), 
                          ("FORCEUNIT",None), 
                          ("PRESSUREUNIT",None)]
    
    file = ifc.get()
    units = []
    assigned_units = file.by_type("IfcProject")[0].UnitsInContext.Units

    for args in si_units_args:
        installed = [u for u in assigned_units if u.UnitType == args[0]]
        if len(installed):
            units.append(installed[0])
            continue
        units.append(
                    ifc.run("unit.add_si_unit", unit_type=args[0], prefix=args[1])
                )
    length = units[0]
    area = units[1]
    volume = units[2]
    mass = units[3]
    time = units[4]
    angle = units[5]
    force = units[6]
    derived_units_args = [("LINEARFORCEUNIT",{force: 1, length: -1},"N/m"),
                          ("LINEARMOMENTUNIT",{force: 1, length: 1, length:-1},"N.m/m"),
                          ("LINEARSTIFFNESSUNIT",{force: 1, length: -1,},"N/m"),
                          ("MASSDENSITYUNIT",{mass: 1, volume:-1},"kg/m³"),
                          ("MASSPERLENGTHUNIT",{mass:1,length:-1},"kg/m"),
                          ("MODULUSOFELASTICITYUNIT",{force:1,area:-1},"Pa"),
                          ("MOMENTOFINERTIAUNIT",{length:4},"m^4"),
                          ("PLANARFORCEUNIT",{force:1,area:-1},"N/m²"),
                          ("ROTATIONALMASSUNIT",{mass:1,area:1},"kg.m²"),
                          ("ROTATIONALSTIFFNESSUNIT",{force:1,length:1,angle:-1},"N.m/rad"),
                          ("SECTIONAREAINTEGRALUNIT",{length:5},"m^5"),
                          ("SECTIONMODULUSUNIT",{length:3},"m³"),
                          ("SHEARMODULUSUNIT",{force:1,area:-1},"N/m²")]
    for args in derived_units_args:
        installed = [u for u in assigned_units if u.UnitType == args[0]]
        if len(installed):
            units.append(installed[0])
            continue
        new_unit = ifc.run("unit.add_derived_unit", unit_type=args[0], userdefinedtype=None, attributes=args[1])
        units.append(new_unit)

    if units:
        ifc.run("unit.assign_unit", units=units)

def assign_unit(ifc: type[tool.Ifc], unit_tool: type[tool.Unit], unit: ifcopenshell.entity_instance) -> None:
    ifc.run("unit.assign_unit", units=[unit])
    unit_tool.import_units()


def unassign_unit(ifc: type[tool.Ifc], unit_tool: type[tool.Unit], unit: ifcopenshell.entity_instance) -> None:
    ifc.run("unit.unassign_unit", units=[unit])
    unit_tool.import_units()


def load_units(unit: type[tool.Unit]) -> None:
    unit.import_units()
    unit.enable_editing_units()


def disable_unit_editing_ui(unit: type[tool.Unit]) -> None:
    unit.disable_editing_units()


def remove_unit(ifc: type[tool.Ifc], unit_tool: type[tool.Unit], unit: ifcopenshell.entity_instance) -> None:
    ifc.run("unit.remove_unit", unit=unit)
    unit_tool.import_units()


def add_monetary_unit(ifc: type[tool.Ifc], unit: type[tool.Unit]) -> ifcopenshell.entity_instance:
    result = ifc.run("unit.add_monetary_unit")
    unit.import_units()
    return result


def add_si_unit(ifc: type[tool.Ifc], unit: type[tool.Unit], unit_type: str) -> ifcopenshell.entity_instance:
    result = ifc.run("unit.add_si_unit", unit_type=unit_type)
    unit.import_units()
    return result


def add_context_dependent_unit(
    ifc: type[tool.Ifc], unit: type[tool.Unit], unit_type: str, name: str
) -> ifcopenshell.entity_instance:
    result = ifc.run("unit.add_context_dependent_unit", unit_type=unit_type, name=name)
    unit.import_units()
    return result


def add_conversion_based_unit(ifc: type[tool.Ifc], unit: type[tool.Unit], name: str) -> ifcopenshell.entity_instance:
    result = ifc.run("unit.add_conversion_based_unit", name=name)
    unit.import_units()
    return result


def enable_editing_unit(unit_tool: type[tool.Unit], unit: ifcopenshell.entity_instance) -> None:
    unit_tool.set_active_unit(unit)
    unit_tool.import_unit_attributes(unit)


def disable_editing_unit(unit: type[tool.Unit]) -> None:
    unit.clear_active_unit()


def edit_unit(ifc: type[tool.Ifc], unit_tool: type[tool.Unit], unit: ifcopenshell.entity_instance) -> None:
    attributes = unit_tool.export_unit_attributes()
    if unit_tool.is_unit_class(unit, "IfcMonetaryUnit"):
        ifc.run("unit.edit_monetary_unit", unit=unit, attributes=attributes)
    elif unit_tool.is_unit_class(unit, "IfcDerivedUnit"):
        ifc.run("unit.edit_derived_unit", unit=unit, attributes=attributes)
    elif unit_tool.is_unit_class(unit, "IfcNamedUnit"):
        ifc.run("unit.edit_named_unit", unit=unit, attributes=attributes)
    unit_tool.import_units()
    unit_tool.clear_active_unit()
