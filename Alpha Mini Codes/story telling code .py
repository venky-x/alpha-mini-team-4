import asyncio
import logging
import mini.mini_sdk as MiniSdk
from mini.apis.api_sound import StartPlayTTS
from mini.dns.dns_browser import WiFiDevice
import speech_recognition as sr


async def test_get_device_by_name():
    """Search for devices based on the suffix of the robot serial number."""
    result: WiFiDevice = await MiniSdk.get_device_by_name("000352", 10)
    print(f"test_get_device_by_name result: {result}")
    return result


async def test_connect(dev: WiFiDevice) -> bool:
    """Connect the device."""
    return await MiniSdk.connect(dev)


async def test_start_run_program():
    """Enter programming mode demo."""
    await MiniSdk.enter_program()
    await asyncio.sleep(6)


async def shutdown():
    """Disconnect and release resources."""
    await MiniSdk.quit_program()
    await MiniSdk.release()


class PhilosophicalStory:
    def __init__(self):
        self.story = {
            "title": "The Wise Turtle and the Hare",
            "content": [
                "Once upon a time, in a lush green forest, there lived a wise old turtle and a speedy hare.",
                "The hare, known for his incredible speed, loved to boast about his abilities.",
                "The turtle, on the other hand, was slow but steady, always taking his time to think and plan.",
                "One sunny day, the hare challenged the turtle to a race, confident of his victory.",
                "The race began, and the hare swiftly darted ahead, leaving the turtle far behind.",
                "Feeling overly confident, the hare decided to take a nap under a tree, believing he had plenty of time.",
                "Meanwhile, the turtle kept plodding along, never giving up.",
                "When the hare woke up, he was shocked to see the turtle near the finish line.",
                "With a burst of speed, the hare rushed towards the finish, but it was too late.",
                "The slow and steady turtle had won the race, teaching the hare a valuable lesson in humility and perseverance."
            ],
            "questions": [
                {"question": "Who challenged the turtle to a race?", "answer": "The hare"},
                {"question": "What was the hare known for?", "answer": "Speed"},
                {"question": "Who won the race in the end?", "answer": "The turtle"},
                {"question": "What lesson did the hare learn?", "answer": "Humility and perseverance"}
            ]
        }

    async def speak(self, text):
        block: StartPlayTTS = StartPlayTTS(text=text)
        response = await block.execute()
        print(f'speak: {response}')

    async def tell_story(self):
        await self.speak(f"Let me tell you a story. This is '{self.story['title']}'")
        for part in self.story['content']:
            await self.speak(part)

    async def ask_questions(self):
        for question_data in self.story['questions']:
            question = question_data["question"]
            await self.speak(question)
            user_answer = await self.listen_for_answer()
            await self.check_answer(question_data, user_answer)

    async def listen_for_answer(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        with microphone as source:
            print("Listening for an answer...")
            audio = recognizer.listen(source)

        try:
            user_answer = recognizer.recognize_google(audio)
            print(f"Recognized answer: {user_answer}")
            return user_answer
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            await self.speak("I couldn't understand that. Could you please repeat?")
            return await self.listen_for_answer()
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            await self.speak("I'm having trouble understanding you. Let's move to the next question.")
            return ""

    async def check_answer(self, question_data, user_answer):
        answer = question_data["answer"].lower()
        if user_answer.lower() == answer:
            await self.speak("Correct!")
        else:
            await self.speak(f"Wrong answer. The correct answer is '{answer}'.")

    async def start_interaction(self):
        lesson_message = (
            "Lesson 2, philosophical story telling. Now I am going to tell you a philosophical story about the turtle and the hare, "
            "and later I am going to test you on what you have learnt so far."
        )
        await self.speak(lesson_message)
        await asyncio.sleep(2)  # Give a short pause
        await self.tell_story()
        await asyncio.sleep(1)  # Wait a bit before asking questions
        await self.ask_questions()

        # Announce the end of lesson two and transition to the final lesson
        await self.speak("We have come to the end of lesson two. We are now moving on to our last and final lesson for the day.")


async def main():
    device: WiFiDevice = await test_get_device_by_name()
    if device:
        if await test_connect(device):
            await test_start_run_program()
            story_teller = PhilosophicalStory()
            await story_teller.start_interaction()
            await shutdown()


if __name__ == '__main__':
    MiniSdk.set_log_level(logging.INFO)
    MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)
    asyncio.run(main())

