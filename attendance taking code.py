import asyncio
import logging
import mini.mini_sdk as MiniSdk
from mini.apis.api_observe import ObserveFaceRecognise
from mini.apis.api_sound import StartPlayTTS
from mini.dns.dns_browser import WiFiDevice
from mini.pb2.codemao_facerecognise_pb2 import FaceRecogniseResponse
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


class FaceRecognitionAttendance:
    def __init__(self):
        self.attendance_list = []
        self.students = {
            "Venky": "0b1ac0fa-7f7e-4c79-9e63-6cc3279c9f89", # enter your registered name here
            "Pansy": "b1f3b411-c87f-4736-8741-3802c69faa2f",

        }
        self.current_student_index = 0
        self.observe = ObserveFaceRecognise()
        self.observe.set_handler(self.handler)

    async def speak(self, text):
        block: StartPlayTTS = StartPlayTTS(text=text)
        response = await block.execute()
        print(f'speak: {response}')

    async def ask_presence(self, student_name):
        await self.speak(f"{student_name}, are you present?")
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        with microphone as source:
            print("Listening for response...")
            audio = recognizer.listen(source)

        try:
            response = recognizer.recognize_google(audio)
            print(f"You said: {response}")
            return response.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            await self.speak("Sorry, I did not understand that. Please repeat.")
            return await self.ask_presence(student_name)
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service.")
            await self.speak("Sorry, I am having trouble understanding. Please repeat.")
            return await self.ask_presence(student_name)

    def handler(self, msg: FaceRecogniseResponse):
        print(f'handler: {msg}')
        face_infos = msg.faceInfos
        if face_infos and len(face_infos) > 0:
            face_id = face_infos[0].id if face_infos[0].id else None
            print(f"Extracted face ID: {face_id}")
            if face_id:
                asyncio.create_task(self.process_recognition(face_id))

    async def process_recognition(self, face_id):
        student_name = next((name for name, id in self.students.items() if id == face_id), None)
        if student_name:
            if student_name not in self.attendance_list:
                self.attendance_list.append(student_name)
                await self.speak(f"{student_name}, you are marked present.")
                await self.move_to_next_student()
            else:
                await self.speak(f"{student_name}, you are already marked present.")

    async def move_to_next_student(self):
        self.current_student_index += 1
        if self.current_student_index < len(self.students):
            await self.ask_current_student()
        else:
            await self.report_attendance()
            await self.stop_recognition()
            await self.speak("Thank you, now we are moving on to our first lesson.")

    async def ask_current_student(self):
        student_name = list(self.students.keys())[self.current_student_index]
        response = await self.ask_presence(student_name)
        if response in ["yes", "present"]:
            await self.speak("Please look at the camera for recognition.")
        else:
            await self.speak(f"{student_name}, you are marked absent.")
            await self.move_to_next_student()

    async def start_recognition(self):
        await self.speak("Welcome to Alpha Mini Academy, I am your teaching assistant Mini. Today we are going to learn three lessons, nice to meet you.")
        await self.speak("Now I am going to take your attendance.")
        await self.ask_current_student()
        self.observe.start()
        await asyncio.sleep(0)

    async def stop_recognition(self):
        self.observe.stop()

    async def report_attendance(self):
        total_attended = len(self.attendance_list)
        await self.speak(f"Total number of people attended: {total_attended}")


async def connect_and_run():
    while True:
        try:
            device: WiFiDevice = await test_get_device_by_name()
            if device:
                if await test_connect(device):
                    await test_start_run_program()
                    attendance_system = FaceRecognitionAttendance()
                    await attendance_system.start_recognition()
                    await asyncio.sleep(300)  # Keep the program running for 5 minutes to recognize faces
                    await attendance_system.stop_recognition()
                    await attendance_system.report_attendance()
                    await shutdown()
                    break
        except Exception as e:
            print(f"An error occurred: {e}. Reconnecting...")
            await asyncio.sleep(5)  # Wait before attempting to reconnect


if __name__ == '__main__':
    MiniSdk.set_log_level(logging.INFO)
    MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)
    asyncio.run(connect_and_run())
