# Detect double click via ZHA  single click events.
# hass api docs - https://developers.home-assistant.io/docs/dev_101_hass/

#hass.bus.fire("some-source-name", {"wow": "from a Python script!"})
#hass.services.call("light", "turn_on", {"key": "value"}, False)
import time

async def handle(hass, data, logger):
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

    state_value = await hass.states.get(state_id)

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


async def reset_state(hass, logger, state_id, device_id):
    """
    Helper to reset the state.
    """
    logger.info("Reseting state for {}.".format(device_id))
    state_value = '{},{}'.format(time.time(), device_id)
    await hass.states.set(state_id, state_value)


await handle(hass, data, logger)

