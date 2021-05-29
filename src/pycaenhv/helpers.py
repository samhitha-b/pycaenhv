from time import sleep
from typing import Any, Dict

from . import parameters as par
from .wrappers import get_channel_parameter, get_channel_parameter_property, get_channel_parameters
from .errors import CAENHVError


def format_numeric(param_info: Dict[str, Any]) -> str:
    props = param_info['properties']
    value = param_info['value']
    mode = param_info['mode']
    exponent = par.ExpShortValues[props['Exp']]
    unit = par.UnitShortValues[props['Unit']]
    return f"{value} {exponent}{unit} ({props['Minval']}:{props['Maxval']}) [{mode}]"


def format_chstatus(param_info: Dict[str, Any]) -> str:
    pass


ParameterDecoder = {0: format_numeric}


def get_parameter_information(handle: int, slot: int, channel: int,
                              parameter: str) -> Dict[str, Any]:
    value = get_channel_parameter(handle, slot, channel, parameter)
    param_type = get_channel_parameter_property(handle, slot, channel,
                                                parameter, 'Type')
    param_mode = get_channel_parameter_property(handle, slot, channel,
                                                parameter, 'Mode')

    mode = par.Modes[param_mode]
    type_ = par.ParameterTypes[param_type]
    properties = dict()

    for prop_name, prop_type in par.ParameterProperties[param_type].items():
        r = get_channel_parameter_property(handle, slot, channel, parameter,
                                           prop_name)
        properties[prop_name] = r
    result = dict(value=value,
                  mode=mode,
                  type=param_type,
                  properties=properties)
    return result


def channel_info(handle, slot, channel):
    """ Returns all information about a channel
    """
    parameters = get_channel_parameters(handle, slot, channel)
    for param in parameters:
        param_info = get_parameter_information(handle, slot, channel, param)
        formatter = ParameterDecoder.get(param_info['type'], lambda a: a)
        print(param, formatter(param_info))


def check_channel_parameter(handle, slot, channel, parameter) -> bool:
    """ Check if parameter is supported by the channel
    """
    parameters = get_channel_parameters(handle, slot, channel)
    return parameter in parameters


def cast_parameter_value(handle, slot, channel, parameter, value) -> Any:
    """ Cast parameter value to the appropriate type
    """
    _type = get_channel_parameter_property(handle, slot, channel, parameter,
                                           'Type')
    return par.ParameterTypes[_type](par.ParameterPythonTypes[_type](value))


def check_channel_parameter_value(handle, slot, channel, parameter,
                                  value) -> bool:
    """
    """
    value_ = cast_parameter_value(handle, slot, channel, parameter,
                                  value).value
    type_ = get_channel_parameter_property(handle, slot, channel, parameter,
                                           'Type')
    if type_ == 0:
        min_value = get_channel_parameter_property(handle, slot, channel,
                                                   parameter, 'Minval')
        max_value = get_channel_parameter_property(handle, slot, channel,
                                                   parameter, 'Maxval')
        if (min_value > value_) or (max_value < value_):
            return False
    return True


def is_parameter_readonly(handle, slot, channel, parameter) -> bool:
    return get_channel_parameter_property(handle, slot, channel, parameter,
                                          'Mode') == 0