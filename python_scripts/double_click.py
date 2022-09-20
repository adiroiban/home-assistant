"""
Detect double click via ZHA single click events.

This is an ugly hack that doesn't work for very quick clicks.
As HA will not execute the script that fast.

The single and double click events are implemented using a hack via timers.

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
"""


def handle(hass, data, logger):
    """
    Handle the script invocation.
    """
    single_click_id = data.get('entity_id', None)
    if not single_click_id:
        logger.info("No entity_id found in input data")
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
    # Cancel the initial single click.
    hass.services.call(
        "timer",
        "cancel",
        {"entity_id": single_click_id},
        False,
        )


handle(hass, data, logger)
