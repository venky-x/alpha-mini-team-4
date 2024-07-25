import asyncio
import logging
import mini.mini_sdk as MiniSdk
from mini.dns.dns_browser import WiFiDevice
import speech_recognition as sr


class MiniAlphaQuiz:
    def __init__(self):
        self.score = 0
        self.questions = [
            {"question": "What is the capital of France?", "answer": "Paris"},
            {"question": "What is the capital of Japan?", "answer": "Tokyo"},
            {"question": "What is the capital of Australia?", "answer": "Canberra"},
            {"question": "What is the capital of Canada?", "answer": "Ottawa"},
            {"question": "What is the capital of Brazil?", "answer": "Brasilia"},
            {"question": "What is the capital of India?", "answer": "New Delhi"},
            {"question": "What is the capital of Germany?", "answer": "Berlin"},
            {"question": "What is the capital of Russia?", "answer": "Moscow"},
            {"question": "What is the capital of South Africa?", "answer": "Pretoria"},
            {"question": "What is the capital of Egypt?", "answer": "Cairo"}
        ]
        # Initialize the robot
        self.robot = MiniSdk

    async def speak(self, text):
        # Using the correct TTS method from the SDK
        await self.robot.play_tts(text)

    async def ask_question(self, question):
        # Make the robot ask the question
        await self.speak(question["question"])
        user_answer = self.listen_for_answer()
        return user_answer

    def listen_for_answer(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        with microphone as source:
            print("Listening for your answer...")
            audio = recognizer.listen(source)

        try:
            user_answer = recognizer.recognize_google(audio)
            print(f"You said: {user_answer}")
            return user_answer
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service.")
            return ""

    async def check_answer(self, question, user_answer):
        if user_answer.lower() == question["answer"].lower():
            self.score += 1
            # Make the robot give positive feedback
            await self.speak("Correct!")
        else:
            # Make the robot give negative feedback and tell the correct answer
            await self.speak(f"Wrong answer. The correct answer is {question['answer']}.")

    async def start_quiz(self):
        # Make the robot say the lesson message
        lesson_message = (
            "Lesson 1. I am going to test you on your general knowledge based on world capitals."
        )
        await self.speak(lesson_message)
        await asyncio.sleep(2)  # Give a short pause

        for question in self.questions:
            user_answer = await self.ask_question(question)
            await self.check_answer(question, user_answer)

        # Make the robot announce the final score
        final_score_msg = f"Quiz over! Your final score is {self.score}/{len(self.questions)}."
        await self.speak(final_score_msg)

        # Announce the end of lesson one and transition to lesson two
        await self.speak("Now we have come to the end of lesson one, now we are moving on to lesson two.")


async def test_get_device_by_name():
    """Search for devices based on the suffix of the robot serial number

    To search for the robot with the specified serial number (behind the robot's butt), you can enter only the tail characters of the serial number, any length, it is recommended that more than 5 characters can be matched accurately, and a timeout of 10 seconds

    Returns:
        WiFiDevice: Contains information such as robot name, ip, port, etc.
    """
    result: WiFiDevice = await MiniSdk.get_device_by_name("000352", 10)
    print(f"test_get_device_by_name result:{result}")
    return result


async def test_get_device_list():
    """Search all devices

    Search all devices, return results after 10s

    Returns:
        [WiFiDevice]: All searched devices, WiFiDevice array

    """
    results = await MiniSdk.get_device_list(10)
    print(f"test_get_device_list results = {results}")
    return results


async def test_connect(dev: WiFiDevice) -> bool:
    """Connect the device

    Connect the specified device

    Args:
        dev (WiFiDevice): The specified device object WiFiDevice

    Returns:
        bool: Whether the connection is successful

    """
    return await MiniSdk.connect(dev)


async def test_start_run_program():
    """Enter programming mode demo

    Make the robot enter the programming mode, wait for the reply result, and delay 6 seconds, let the robot finish "Enter programming mode"

    Returns:
        None:

    """
    await MiniSdk.enter_program()
    await asyncio.sleep(6)


async def shutdown():
    """Disconnect and release resources

    Disconnect the currently connected device and release resources

    """
    await MiniSdk.quit_program()
    await MiniSdk.release()


# The default log level is Warning, set to INFO
MiniSdk.set_log_level(logging.INFO)
# Set robot type
MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)


async def main():
    device: WiFiDevice = await test_get_device_by_name()
    if device:
        if await test_connect(device):
            await test_start_run_program()
            quiz = MiniAlphaQuiz()
            await quiz.start_quiz()
            await shutdown()


if __name__ == '__main__':
    asyncio.run(main())

