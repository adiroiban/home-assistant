"""
Detect double click via ZHA  single click events.

It needs a timer to track the double clicks.
The timer is cancelled if a double click is observed.
The timer is left to finalize for a single click.

There is a hardcoded 2 seconds delay.
As pressing the button to fast will not help.

To trigger an action on single click or double click, trigger events based
on the timer.finalized or timer.cancelled events.

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

    timer_state = hass.states.get(single_click_id)
    if not timer_state:
        logger.info("No timer found to track double clicks.")
        return

    timer_state = timer_state.state
    logger.info("Trigger state {}.".format(timer_state))
    if timer_state == 'idle':
        # No previous click trigerred.
        hass.services.call(
            "timer",
            "start",
            {"entity_id": single_click_id, "duration": 2},
            False,
            )
        return

    # Most probably active.
    # So we have a second click.
    hass.services.call(
        "timer",
        "cancel",
        {"entity_id": single_click_id},
        False,
        )


handle(hass, data, logger)
