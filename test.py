from gtts import gTTS
from pydub import AudioSegment


def _create_exercise_instruction_text(exercise: str, duration: int, reps: int = None) -> str:
    if reps:
        text = f"{reps} {exercise} in {duration} seconds"
    else:
        text = f"{exercise} for {duration} seconds"
    return text


def _create_exercise_mp3(text: str, filename: str, language: str = "en", slow: bool = False) -> gTTS:
    speech = gTTS(text=text, lang=language, slow=slow)
    speech.save(filename)
    return filename


def join_audio_files_with_silences(files: list, intervals: list) -> AudioSegment:
    joined_audio = None
    exercises = zip(files, intervals)
    for exercise in exercises:
        speech = AudioSegment.from_mp3(exercise[0])
        silence = AudioSegment.silent(exercise[1] * 1000)
        new_exercise = speech + silence
        if joined_audio:
            joined_audio += new_exercise
        else:
            joined_audio = new_exercise
    return joined_audio


text = _create_exercise_instruction_text("jumping jacks", reps=30, duration=20)
_create_exercise_mp3(text, "new.mp3")
text = _create_exercise_instruction_text("burpees", duration=1000000)
_create_exercise_mp3(text, "new2.mp3")
text = _create_exercise_instruction_text("sleep", duration=20)
_create_exercise_mp3(text, "new3.mp3")

files = ["new.mp3", "new2.mp3", "new3.mp3"]
intervals = [2, 7, 5]
full_audio = join_audio_files_with_silences(files, intervals)
full_audio.export("mashup.mp3", format="mp3",
                  tags={'artist': 'Various artists', 'album': 'Best of 2011', 'comments': 'This album is awesome!'})
