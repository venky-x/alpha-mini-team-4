import asyncio
import logging
import mini.mini_sdk as MiniSdk
from mini.apis.api_sound import StartPlayTTS
from mini.apis.api_action import PlayAction, PlayActionResponse
from mini.apis.base_api import MiniApiResultType
from mini.dns.dns_browser import WiFiDevice
from test_connect import test_get_device_by_name


async def speak(text):
    block: StartPlayTTS = StartPlayTTS(text=text)
    response = await block.execute()
    print(f'speak: {response}')


# Test to perform an action
async def test_play_action(action_name, count):
    """Perform an action demo

     Control the robot to execute a local (built-in/custom) action with a specified name and wait for the execution result to reply

     Action name can be obtained with GetActionList

     #PlayActionResponse.isSuccess: Is it successful

     #PlayActionResponse.resultCode: Return code

     """
    for i in range(count):
        block: PlayAction = PlayAction(action_name=action_name)
        (resultType, response) = await block.execute()

        print(f'test_play_action {action_name} repetition={i + 1} result:{response}')

        assert resultType == MiniApiResultType.Success, f'test_play_action {action_name} repetition={i + 1} timeout'
        assert response is not None and isinstance(response,
                                                   PlayActionResponse), f'test_play_action {action_name} repetition={i + 1} result unavailable'
        assert response.isSuccess, f'play_action {action_name} repetition={i + 1} failed'


async def main():
    device: WiFiDevice = await test_get_device_by_name()
    if device:
        await MiniSdk.connect(device)
        await MiniSdk.enter_program()

        # Say the initial message for the physical education lesson
        await speak("Now we have come to our last lesson, physical education. Please follow my moves.")

        # Repeat each action 3 times
        await test_play_action('012', 1)
        await test_play_action('016', 3)
        await test_play_action('017', 3)

        # Say the final message
        await speak("And thus we have come to the end of all our lessons. Hope you had a good day. Bye bye.")

        await MiniSdk.quit_program()
        await MiniSdk.release()


if __name__ == '__main__':
    MiniSdk.set_log_level(logging.INFO)
    MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)
    asyncio.run(main())
