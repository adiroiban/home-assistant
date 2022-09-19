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
    single_click_id = data.get('single_click_id', None)
    if not state_id:
        logger.info("No entity_id found in input data")
        return

    if not single_click_id:
        logger.info("No single_click_id found in input data")
        return

    state_value = hass.states.get(state_id)

    if not state_value:
        return schedule_single(single_click_id, state_id)

    state_value = state_value.state
    try:
        last_time = float(state_value)
    except Exception:
        logger.info("Failed to parse state: '{}'".format(state_value))
        return schedule_single(single_click_id, state_id)

    duration = time.time() - last_time
    if duration > 1:
        logger.info("Long double click after {}.".format(duration))
        # Start a new double-click counter.
        return schedule_single(single_click_id, state_id)

    logger.info("Trigger double click after {}.".format(duration))
    hass.services.call(
        "timer",
        "cancel",
        {"entity_id": single_click_id},
        False,
        )

    hass.bus.fire("double_click", {"entity_id": state_id})
    return reset_state(state_id)


def schedule_single(single_click_id, state_id):
    hass.services.call(
        "timer",
        "start",
        {"entity_id": single_click_id, "duration": 1},
        False,
        )
    reset_state(state_id)


def reset_state(state_id):
    """
    Helper to reset the state.
    """
    hass.states.set(state_id, str(time.time()))


logger.info("Services {}".format(hass.services.services['timer']))
handle(hass, data, logger)
