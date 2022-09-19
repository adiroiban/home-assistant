"""
Detect double click via ZHA  single click events.
hass api docs - https://developers.home-assistant.io/docs/dev_101_hass/
Check the source code for what you are allowed
https://github.com/home-assistant/core/blob/dev/homeassistant/components/python_script/__init__.py

async usage is not allowed.

builtins with limited access (see sourcce code)
* datetime
* sorted
* time - which is TimeWrapper()
* dt_util
* min
* max
* sum
* any
* all
* enumerate


hass.bus.fire("some-source-name", {"wow": "from a Python script!"})
hass.services.call("light", "turn_on", {"key": "value"}, False)
"""

def handle(hass, data, logger):
    """
    Handle the script invocation.
    """
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

    state_value = state_value.value
    try:
        last_time, target = state_value.split(',')
        last_time = float(last_time)
    except Exception:
        logger.info("Failed to parse state: '{}'".format(state_value))
        return reset_state(hass, logger, state_id, device_id)

    duration = time.time() - last_time
    if duration > 1:
        logger.info("Long double click after {}.".format(duration))
        return reset_state(hass, logger, state_id, device_id)

    logger.info("Trigger double click after {}.".format(duration))
    hass.bus.fire("some-source-name", {"wow": "Double click detected"})
    return reset_state(hass, logger, state_id, device_id)


def reset_state(hass, logger, state_id, device_id):
    """
    Helper to reset the state.
    """
    state_value = '{},{}'.format(time.time(), device_id)
    hass.states.set(state_id, state_value)


handle(hass, data, logger)
