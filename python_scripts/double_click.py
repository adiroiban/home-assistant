"""
Detect double click via ZHA  single click events.
hass api docs - https://developers.home-assistant.io/docs/dev_101_hass/
Check the source code for what you are allowed
https://github.com/home-assistant/core/blob/dev/homeassistant/components/python_script/__init__.py

async usage is not allowed.

builtins with limited access (see sourcce code)
        "datetime": datetime,
        "sorted": sorted,
        "time": TimeWrapper(),
        "dt_util": dt_util,
        "min": min,
        "max": max,
        "sum": sum,
        "any": any,
        "all": all,
        "enumerate": enumerate,


hass.bus.fire("some-source-name", {"wow": "from a Python script!"})
hass.services.call("light", "turn_on", {"key": "value"}, False)
"""

def handle(hass, data, logger):
    """
    Handle the script invocation.
    """
    logger.info("Called at {}.".format(time.time()))

    state_id = data.get('entity_id', None)
    device_id = data.get('device_id', None)
    if not state_id:
        logger.info("No entity_id found in input data")
        return

    if not device_id:
        logger.info("No device_id found in input data")
        return

    state_value = hass.states.get(state_id)

    if not state_value:
        return reset_state(hass, logger, state_id, device_id)

    try:
        last_time, target = state_value.split(',')
        last_time = float(last_time)
    except Exception:
        logger.info("Failed to parse state: '{}'".format(state_value))
        return

    duration = time.time() - last_time
    if duration > 1:
        return reset_state(hass, logger, state_id, device_id)

    hass.bus.fire("some-source-name", {"wow": "Double click detected"})
    return reset_state(hass, logger, state_id, device_id)


def reset_state(hass, logger, state_id, device_id):
    """
    Helper to reset the state.
    """
    logger.info("Reseting state for {}.".format(device_id))
    state_value = '{},{}'.format(time.time(), device_id)
    hass.states.set(state_id, state_value)


logger.info("Called at {}.".format(time.time()))
handle(hass, data, logger)
